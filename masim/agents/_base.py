"""Abstract base classes for canonical, scenario-agnostic agents.

Two bases are exported:

* :class:`CanonicalRulePlayer` — for deterministic, formula-driven agents.
  Subclasses implement :meth:`CanonicalRulePlayer.decide_order` returning an
  :class:`~masim.format.order.InvestorOrder` (or, for backwards compatibility,
  a partial dict which is normalised via
  :meth:`~masim.format.order.InvestorOrder.from_dict`).  This base handles
  ``extras`` parsing, ``custom_state`` bookkeeping, the perceive→decide→act
  lifecycle, and outbound-message dispatch.

* :class:`CanonicalLLMPlayer` — for LLM-driven agents.  Reads ``extras["llm"]``
  (``lm_name``, ``generation_config``, ``sys_message``, ``user_message``),
  loads prompts via dotted ``module:VAR`` references, formats the user
  template against :class:`StandardMarketState`, calls
  :class:`LangChainAPIInference`, parses ``<analysis>``/``<decision>``
  responses, and turns the parsed dict into an
  :class:`~masim.format.order.InvestorOrder` via
  :meth:`~masim.format.order.InvestorOrder.from_llm_decision`.

Both bases derive from :class:`masim.player.general.GeneralPlayer` so they
plug into the existing simulator without further wiring.

Format contract (single source of truth: :mod:`masim.format.order`)
-------------------------------------------------------------------

Every order that leaves an agent is built through
:class:`~masim.format.order.InvestorOrder`'s factory classmethods and
serialised via :meth:`~masim.format.order.InvestorOrder.to_dict`.  Raw dicts
are never constructed by hand in this module — even the outbound-message
payload comes from a ``.to_dict()`` call — so the wire format is guaranteed
to match what :func:`~masim.format.order.validate_order` enforces.
"""

from __future__ import annotations

import dataclasses
import importlib
import importlib.util
import logging
import os
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Optional, Union

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer
from masim.format.order import (
    BUY,
    HOLD,
    SELL,
    InvestorOrder,
)
from masim.format.finalize import (
    emit_order_envelope,
    finalize_llm_order,
    finalize_rule_order,
)
from masim.format.state import StandardMarketState

logger = logging.getLogger("masim.agents")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _project_root() -> Path:
    """Return the project root (parent of ``masim/``)."""
    # masim/agents/_base.py → parents[0]=agents, [1]=masim, [2]=project root
    return Path(__file__).resolve().parents[2]


_bundle_module_cache: dict[str, ModuleType] = {}


def _load_module_by_file(module_path: str) -> ModuleType:
    """Load a module by resolving its dotted path to a file under project root.

    Necessary for ``CUSTOMIZED_SIMULATION`` bundles whose directory names
    contain hyphens (e.g. ``team-foo-bar-a4fc6d93-HerdEffect``) — those names
    are illegal in Python ``import`` syntax, so :func:`importlib.import_module`
    cannot resolve them.  We map the dotted path to
    ``<project_root>/<part1>/<part2>/…/<partN>.py`` and load it via
    :func:`importlib.util.spec_from_file_location`.

    **NOT registered in sys.modules** — this is intentional.  Ray workers are
    separate processes that don't share sys.modules with the driver.  If the
    module were registered there, cloudpickle would serialize classes by
    reference (just storing module-name + class-name), and workers would crash
    with ``ModuleNotFoundError`` when they tried to reimport.  By keeping the
    module out of sys.modules, cloudpickle detects it as "dynamic" and pickles
    classes **by value** (full bytecode), which workers can deserialize without
    any special import hooks.

    Cached in a private module-level dict keyed on ``file_path:mtime_ns`` so
    repeated calls within the same process (e.g. multiple players sharing one
    ``players.py``) reuse the same module object and honour Save-to-disk edits.
    """
    root = _project_root()
    parts = module_path.split(".")
    file_path = root.joinpath(*parts).with_suffix(".py")
    if not file_path.exists():
        raise ModuleNotFoundError(
            f"Cannot locate module {module_path!r} on-disk; "
            f"expected {file_path} to exist."
        )
    # Include mtime in the cache key so that Save-to-disk edits (which rewrite
    # prompts.py under the same path) invalidate the cached module. Without
    # this, a UI Save + Launch cycle would keep serving the pre-edit prompts
    # until the interpreter is restarted.
    mtime_ns = file_path.stat().st_mtime_ns
    cache_key = f"{file_path}:{mtime_ns}"
    cached = _bundle_module_cache.get(cache_key)
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location(module_path, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not build import spec for {file_path} (module {module_path!r})"
        )
    module = importlib.util.module_from_spec(spec)
    # Set a readable __name__ matching the original dotted path (tracebacks)
    # but do NOT register in sys.modules — keeps cloudpickle in by-value mode.
    module.__name__ = module_path
    spec.loader.exec_module(module)
    _bundle_module_cache[cache_key] = module
    return module


def _load_dotted(reference: str) -> str:
    """Resolve a ``module:VARIABLE`` reference and return the variable's value.

    Used by :class:`CanonicalLLMPlayer` to load prompt strings from a Python
    module attribute. The reference must contain exactly one ``:`` separator.

    Two lookup strategies are tried in order:

    1. Standard :func:`importlib.import_module` — works for shipped scenarios
       (``examples.HerdEffect.LLM.prompts``) and any importable package path.
    2. File-path fallback via :func:`_load_module_by_file` — required for
       ``CUSTOMIZED_SIMULATION`` bundle references whose directory names
       contain hyphens and are therefore not valid Python identifiers.
    """
    if ":" not in reference:
        raise ValueError(
            f"Prompt reference must use 'module:VARIABLE' form, got {reference!r}"
        )
    module_path, var_name = reference.rsplit(":", 1)
    try:
        module = importlib.import_module(module_path)
    except (ModuleNotFoundError, ImportError):
        module = _load_module_by_file(module_path)
    return getattr(module, var_name)


# Public alias — shipped ``examples/*/LLM/players.py`` files import this to
# resolve their ``sys_message`` / ``user_message`` references. Using the
# canonical loader means shipped scenarios get the same
# ``import_module → _load_module_by_file`` fallback that Customized bundles
# rely on, so a UI Save that rewrites a hyphenated bundle's ``prompts.py``
# still loads correctly regardless of whether the bundle's directory name is
# a valid Python identifier.
load_prompt = _load_dotted


def _scenario_from_sys_ref(sys_ref: str) -> str:
    """Extract the scenario slug from an LLM sys_message reference.

    Two reference shapes are supported — the return value is what
    :func:`masim.format.get_order_format` looks up in
    :data:`masim.format.SCENARIO_ORDER_FORMAT`:

    Shipped scenario::

        "examples.HerdEffect.LLM.prompts:LLM_MOMENTUM_SYS"
        → "HerdEffect"

    CUSTOMIZED_SIMULATION bundle (Build a Project)::

        "examples.CUSTOMIZED_SIMULATION.team-sijiatest-MyTest-a4fc6d93-HerdEffect.Default.LLM.prompts:LLM_MOMENTUM_SYS"
        → "HerdEffect"   (last hyphen-segment of the bundle name)

    Any other shape raises :class:`RuntimeError` — silent fallback would
    defeat the strict-validation regime that the whole refactor is built on.
    """
    if not sys_ref or ":" not in sys_ref:
        raise RuntimeError(
            f"Cannot derive scenario from sys_message reference "
            f"(missing ':' separator): {sys_ref!r}"
        )
    module_path = sys_ref.rsplit(":", 1)[0]
    parts = module_path.split(".")
    # Shipped:   examples.<Scenario>.<Variant>.prompts
    # Bundle:    examples.CUSTOMIZED_SIMULATION.<bundle>.Default.<Variant>.prompts
    if len(parts) >= 4 and parts[0] == "examples":
        if parts[1] == "CUSTOMIZED_SIMULATION":
            # bundle segment is index 2, scenario = last hyphen-segment
            bundle = parts[2]
            if "-" in bundle:
                return bundle.rsplit("-", 1)[1]
            raise RuntimeError(
                f"CUSTOMIZED_SIMULATION bundle name is missing the "
                f"trailing '-<Scenario>' segment: {bundle!r} in {sys_ref!r}"
            )
        return parts[1]
    raise RuntimeError(
        f"Unrecognised sys_message reference shape: {sys_ref!r}. "
        f"Expected 'examples.<Scenario>.<Variant>.prompts:CONST' or "
        f"'examples.CUSTOMIZED_SIMULATION.<bundle>.Default.<Variant>."
        f"prompts:CONST'."
    )


def _coerce_to_order(
    candidate: Union[InvestorOrder, Dict[str, Any]],
    *,
    investor: str,
    strategy: str,
) -> InvestorOrder:
    """Normalise a subclass return value to :class:`InvestorOrder`.

    Subclasses may either construct an :class:`InvestorOrder` directly (the
    preferred path) or return a partial dict (legacy path). This helper
    guarantees the finaliser always operates on an ``InvestorOrder`` and
    fills in ``investor``/``strategy`` when the subclass omitted them.
    """
    if isinstance(candidate, InvestorOrder):
        order = candidate
    elif isinstance(candidate, dict):
        order = InvestorOrder.from_dict(candidate)
    else:
        raise TypeError(
            "decide_order must return InvestorOrder or dict, got "
            f"{type(candidate).__name__}"
        )
    updates: Dict[str, Any] = {}
    if not order.investor:
        updates["investor"] = investor
    if not order.strategy:
        updates["strategy"] = strategy
    return dataclasses.replace(order, **updates) if updates else order


def _emit(
    order: InvestorOrder,
    *,
    agent_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Serialise an :class:`InvestorOrder` for the pipeline.

    Thin delegate around :func:`masim.format.finalize.emit_order_envelope`
    — the wire-format logic (schema validation, ``outbound_messages``
    envelope, ``analysis`` stripping, ``agent_state`` injection) lives in
    a single place so scenario code that reimplements the perceive/decide
    skeleton can obtain the same behaviour with a single import.

    ``agent_state`` — when supplied, keys (typically ``cash`` / ``position``
    / ``agent_type``) are merged into both the top-level result dict AND
    every outbound message payload so market coordinators see truthful
    portfolio state, never fabricated defaults.
    """
    return emit_order_envelope(
        order,
        strip_analysis=True,
        agent_state=agent_state,
    )


def _apply_fill_and_emit_action(
    agent: GeneralPlayer,
    decision_payload: Dict[str, Any],
    *,
    class_name: str,
) -> Action:
    """Shared ``act()`` implementation for canonical Rule / LLM / RAG bases.

    Historically each canonical base carried its own ~30 line copy of
    this logic (key-presence guard → positive-``bid_price`` guard →
    cash/inventory bookkeeping → :class:`Action` construction).  The
    only inter-class delta was the error-message prefix, which we now
    thread through ``class_name`` so every bases produces exactly one
    taxonomy of failures — routed through
    :func:`~masim.format.finalize.require_positive_bid_price` — and
    the two bases can never drift on cash-update semantics.

    Post-fill hook (:meth:`GeneralPlayer.on_fill` on canonical bases,
    no-op by default) is invoked *after* validation + cash/position
    mutation, with the already-validated ``(action, quantity, bid_price)``
    tuple.  This is the single, design-level extension point for
    archetype-specific bookkeeping (VWAP anchors, entry-time counters,
    disposition thresholds, …).  Subclasses that need per-fill state
    updates MUST override ``on_fill`` — they MUST NOT override
    :meth:`~CanonicalRulePlayer.act`; the raw payload never reaches
    subclasses so silent-fill against a zero ``bid_price`` (or a
    ``market_data.price`` fallback) is impossible by construction.
    """
    from masim.format.finalize import require_positive_bid_price

    for required in ("action", "quantity", "bid_price"):
        if required not in decision_payload:
            raise KeyError(
                f"{class_name}.act: decision_payload missing required "
                f"field {required!r}. Payload keys: {sorted(decision_payload)}"
            )
    action = decision_payload["action"]
    quantity = float(decision_payload["quantity"])
    bid_price = float(decision_payload["bid_price"])

    if action in (BUY, SELL) and quantity > 0:
        # Defence-in-depth: emit_order_envelope + finalize_* already
        # invoked require_positive_bid_price on this record. If a
        # subclass short-circuited the finalizer this second call still
        # fires with a stable error format so operators can trace the
        # invariant break to a single site.
        require_positive_bid_price(
            bid_price, action, context=f"{class_name}.act"
        )
        fill_price = bid_price

        if action == BUY:
            agent.state.custom_state["cash"] -= quantity * fill_price
            agent.state.custom_state["position"] += quantity
        else:  # SELL
            agent.state.custom_state["cash"] += quantity * fill_price
            agent.state.custom_state["position"] -= quantity

    # Post-fill hook — archetypes update anchor / VWAP / counters here.
    # ``on_fill`` is a no-op on the canonical bases; only archetypes
    # that need per-fill bookkeeping override it. The hook always sees
    # a validated bid_price (``> 0`` for BUY/SELL) or the raw value for
    # HOLD (which archetypes typically filter out).
    on_fill = getattr(agent, "on_fill", None)
    if callable(on_fill):
        on_fill(action, quantity, bid_price)

    return Action(
        action_type="investor_bid",
        payload=decision_payload,
        source_id=agent.identity,
    )


# ---------------------------------------------------------------------------
# Rule base
# ---------------------------------------------------------------------------


class CanonicalRulePlayer(GeneralPlayer):
    """Base class for deterministic, formula-driven canonical agents.

    Subclasses MUST:
      * declare a class-level ``STRATEGY`` attribute (defaults to class name)
      * implement :meth:`decide_order` taking a :class:`StandardMarketState`
        and returning either an :class:`InvestorOrder` (preferred) or a
        partial order dict (bridged to :class:`InvestorOrder` via
        :meth:`InvestorOrder.from_dict`).

    Subclasses MAY override :meth:`init_extras` to read additional parameters
    from ``self.config.extras`` once on the first ``perceive`` call.

    Class-level metadata consumed by the customized-simulation discovery layer
    (``masim.interface.customized.agent_catalog``):
      * ``STRATEGY`` — archetype identifier; must match the LLM sibling.
      * ``DISPLAY_NAME`` — UI label shown in the marketplace card.
      * ``SUMMARY`` — one-line description shown under the card title.
      * ``REQUIRES_FEATURES`` — tuple of feature names from
        ``scenario_features.yml`` this archetype needs from the scenario
        (empty = portable to any scenario).
    """

    STRATEGY: str = "CanonicalRulePlayer"
    DISPLAY_NAME: str = ""
    SUMMARY: str = ""
    REQUIRES_FEATURES: tuple = ()

    # -- lifecycle ---------------------------------------------------------

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_state()

        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload or {}
                if "price" in payload:
                    self.state.custom_state["market_data"] = payload
                    history = self.state.custom_state.get("price_history")
                    if history is not None:
                        history.append(payload["price"])
                    self.on_market_data(payload)

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state.get("market_data")
        if market_data is None:
            # Round 0 / no market signal yet — return a no-op order.
            return _emit(self._noop_order())

        state = StandardMarketState.from_market_data(
            market_data,
            cash=self.state.custom_state["cash"],
            position=self.state.custom_state["position"],
        )

        raw = self.decide_order(state)
        order = _coerce_to_order(
            raw,
            investor=self.identity,
            strategy=self.STRATEGY,
        )
        order = self._finalize_order(order, state)
        # Inject truthful agent state into outbound so Market coordinators
        # receive real data for clearing/logging — never fabricate defaults.
        return _emit(
            order,
            agent_state={
                "cash": state.cash,
                "position": state.position,
                "agent_type": self.STRATEGY,  # alias for backward compat
            },
        )

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        # The whole body (key-presence guard, positive-bid_price guard via
        # require_positive_bid_price, cash/inventory bookkeeping, and the
        # Action envelope) lives in the shared helper so this base and
        # CanonicalLLMPlayer cannot drift on wire semantics.
        return _apply_fill_and_emit_action(
            self, decision_payload, class_name="CanonicalRulePlayer"
        )

    # -- override hooks ----------------------------------------------------

    def decide_order(
        self, state: StandardMarketState
    ) -> Union[InvestorOrder, Dict[str, Any]]:
        """Return an :class:`InvestorOrder` for the given market state.

        Subclasses MUST implement. Preferred return type is
        :class:`~masim.format.order.InvestorOrder`; a partial dict is
        accepted for backwards compatibility (bridged via
        :meth:`InvestorOrder.from_dict`). The framework will fill in
        ``investor`` and ``strategy`` when the subclass omits them.
        """
        raise NotImplementedError

    def init_extras(self, extras: Dict[str, Any]) -> None:
        """Hook for subclasses to read archetype-specific parameters.

        Called once on the first ``perceive`` call. The default implementation
        is a no-op — common bookkeeping (``cash``, ``position``,
        ``price_history``) is handled by the base class.
        """
        return None

    def on_market_data(self, market_data: Dict[str, Any]) -> None:
        """Hook fired whenever a fresh market broadcast arrives.

        Useful for agents that maintain a rolling window or anchor price.
        Default: no-op.
        """
        return None

    def on_fill(
        self, action: str, quantity: float, bid_price: float
    ) -> None:
        """Post-fill hook — the ONLY sanctioned extension point for
        archetype-specific bookkeeping after an order clears.

        Called by :func:`_apply_fill_and_emit_action` *after* the shared
        base has:

          1. Verified ``decision_payload`` carries
             ``action`` / ``quantity`` / ``bid_price``.
          2. Enforced ``require_positive_bid_price`` for BUY / SELL.
          3. Mutated ``self.state.custom_state['cash']`` and
             ``self.state.custom_state['position']``.

        The tuple passed in is therefore **already validated** — for a
        BUY/SELL fill ``bid_price > 0`` is guaranteed. Archetypes that
        need to update VWAP anchors, cost basis, purchase price,
        entry-time counters or similar per-fill state MUST override
        this hook. They MUST NOT override :meth:`act` — the raw
        ``decision_payload`` is intentionally hidden from subclasses so
        the classic silent-fill pattern (``fill_price = bid_price if
        bid_price > 0 else market_data['price']``) becomes unwriteable
        by construction.

        The hook fires for every action including ``hold`` so subclasses
        can observe every step; most archetypes filter for
        ``action == 'buy'``. Exceptions raised here propagate — do not
        swallow them.

        Parameters
        ----------
        action : str
            One of the canonical action tags (``'buy'``, ``'sell'``,
            ``'hold'``) — already normalised by the base.
        quantity : float
            Filled quantity. Always ``>= 0`` for BUY/SELL.
        bid_price : float
            The executed price. For BUY/SELL this is guaranteed
            ``> 0`` — the wire-format guard blocks any lower value.

        Notes
        -----
        The pre-fill ``position`` can be recovered from the post-fill
        state as ``new_pos - quantity`` for BUY and ``new_pos +
        quantity`` for SELL — the framework has already applied the
        mutation before invoking this hook.
        """
        return None

    # -- helpers -----------------------------------------------------------

    def _initialize_state(self) -> None:
        extras = self.config.extras
        record_path = extras.get("record_path", "")
        hot_limit = extras.get("custom_state_hot_limit", 1000)

        self.state.custom_state["cash"] = float(extras.get("initial_cash", 0.0))
        self.state.custom_state["position"] = float(extras.get("initial_position", 0.0))
        if record_path:
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )
        self.init_extras(extras)

    def _finalize_order(
        self,
        order: InvestorOrder,
        state: StandardMarketState,
    ) -> InvestorOrder:
        """Clip buy/sell orders to available cash/inventory and validate.

        Thin delegate around :func:`masim.format.finalize.finalize_rule_order`
        — the semantics are documented at the helper site.  Rule agents
        historically fill ``bid_price`` from ``state.price`` when the
        subclass returned an order with ``bid_price <= 0`` (a common
        pattern for HOLD orders in hand-rolled Rule code); this is
        preserved.  Non-hold orders that would emerge with a non-positive
        ``bid_price`` after that fallback trigger a ``ValueError`` so a
        broadcast bug is surfaced rather than papered over with a
        ``fill_price = 0`` cash update.

        An order clipped down to zero from a genuine BUY/SELL intent is
        converted to a ``hold`` but marked ``clipped_from`` so downstream
        behavioural metrics (action_frequency, decision_entropy) can
        distinguish it from an explicit hold decision.
        """
        return finalize_rule_order(
            order,
            state=state,
            investor=self.identity,
            strategy=order.strategy or self.STRATEGY,
        )

    def _noop_order(self, reason: str = "no_market_data") -> InvestorOrder:
        """Bootstrap-round placeholder.

        NOT a real decision. Marked ``skipped=True`` so downstream
        audit/metrics can exclude it from statistics (herding CV,
        action-frequency, decision-entropy, bid-convergence).
        """
        return InvestorOrder.noop(
            investor=self.identity,
            strategy=self.STRATEGY,
            reason=reason,
        )


# ---------------------------------------------------------------------------
# LLM base
# ---------------------------------------------------------------------------


class CanonicalLLMPlayer(GeneralPlayer):
    """Base class for LLM-driven canonical agents.

    Reads from ``self.config.extras["llm"]``:
      * ``lm_name``: language model identifier (e.g. ``"doubao-1-5-pro-32k"``)
      * ``generation_config``: dict forwarded to the inference client
      * ``sys_message``: ``module:VAR`` reference resolving to the system prompt
      * ``user_message``: ``module:VAR`` reference resolving to the user template

    The user template is formatted against :class:`StandardMarketState` every
    round. The LLM response is parsed with
    :func:`masim.utils.llm_utils.parse_llm_response_with_thinking` and turned
    into an :class:`InvestorOrder` via
    :meth:`InvestorOrder.from_llm_decision`. On any LLM failure the round is
    aborted (fail-loud) so a silent synthetic hold never pollutes downstream
    behavioural metrics.

    Subclasses are usually empty apart from class-level prompt defaults — they
    exist so the bundle's ``players.yml`` can reference a class name that
    conveys the persona (e.g. ``LLMNoiseTrader``). The persona itself lives in
    the prompt strings.

    Class-level metadata consumed by the customized-simulation discovery layer:
      * ``STRATEGY`` — archetype identifier; must match the Rule sibling.
      * ``DEFAULT_SYS_PROMPT`` — canonical, scenario-free system prompt the
        marketplace pre-populates into the prompt editor.
      * ``DEFAULT_USER_PROMPT`` — canonical, scenario-free user prompt template
        (uses :meth:`StandardMarketState.template_vars` placeholders).
    """

    STRATEGY: str = "CanonicalLLMPlayer"
    DEFAULT_SYS_PROMPT: str = ""
    DEFAULT_USER_PROMPT: str = ""

    # -- lifecycle ---------------------------------------------------------

    async def perceive(
        self,
        observation: Observation,
        prev_result: Optional[StepResult] = None,
    ) -> None:
        round_num = observation.round
        self.state.custom_state["round"] = round_num

        if "cash" not in self.state.custom_state:
            self._initialize_state()

        if observation.inbounds:
            for inb in observation.inbounds:
                payload = inb.payload or {}
                if "price" in payload:
                    self.state.custom_state["market_data"] = payload
                    history = self.state.custom_state.get("price_history")
                    if history is not None:
                        history.append(payload["price"])

    async def decide(self) -> Dict[str, Any]:
        market_data = self.state.custom_state.get("market_data")
        if market_data is None:
            return _emit(self._noop_order())

        state = StandardMarketState.from_market_data(
            market_data,
            cash=self.state.custom_state["cash"],
            position=self.state.custom_state["position"],
        )

        try:
            decision = self._run_llm(state)
        except Exception as exc:  # noqa: BLE001
            # Even with fallback="raise", we catch here to prevent a single
            # agent from crashing the entire simulation.  Log loudly and skip.
            logger.error(
                "[%s] LLM call failed (%s); emitting noop for this round.",
                self.identity,
                exc,
            )
            return _emit(self._noop_order())

        # Fallback hold from robust_llm_call — emit as noop so metrics exclude it
        if decision.get("_fallback"):
            logger.warning(
                "[%s] Using fallback hold (LLM unavailable this round).",
                self.identity,
            )
            return _emit(self._noop_order())

        order = InvestorOrder.from_llm_decision(
            decision,
            investor=self.identity,
            strategy=self.STRATEGY,
        )
        # Apply cash/inventory clipping through the same finaliser used by
        # Rule agents — reuse of the code path guarantees Rule / LLM parity
        # for the clipping semantics.
        order = self._finalize_llm_order(order, state)
        # Inject truthful agent state into outbound (same as Rule variant).
        return _emit(
            order,
            agent_state={
                "cash": state.cash,
                "position": state.position,
                "agent_type": self.STRATEGY,
            },
        )

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        # Shared implementation with CanonicalRulePlayer.act — see
        # _apply_fill_and_emit_action for the full contract.
        return _apply_fill_and_emit_action(
            self, decision_payload, class_name="CanonicalLLMPlayer"
        )

    def on_fill(
        self, action: str, quantity: float, bid_price: float
    ) -> None:
        """Post-fill hook — LLM/RAG variant of
        :meth:`CanonicalRulePlayer.on_fill`.

        Semantics are identical to the Rule variant — see that
        docstring for the full contract. The hook is defined here
        (rather than inherited from a common base) because
        :class:`CanonicalLLMPlayer` and :class:`CanonicalRulePlayer`
        are siblings under :class:`GeneralPlayer`, not a shared
        canonical mixin. :class:`CanonicalRagPlayer` (defined in
        :mod:`masim.agents._rag_base`) subclasses this LLM base and
        therefore inherits ``on_fill`` transparently.
        """
        return None

    # -- pickling: drop the live LLM client --------------------------------

    def __getstate__(self):
        state = self.__dict__.copy()
        if "state" in state and hasattr(state["state"], "custom_state"):
            custom = dict(state["state"].custom_state)
            custom.pop("llm_client", None)
            state["state"].custom_state = custom
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Lazy reconstruction handled inside _run_llm.

    # -- helpers -----------------------------------------------------------

    def _initialize_state(self) -> None:
        extras = self.config.extras
        record_path = extras.get("record_path", "")
        hot_limit = extras.get("custom_state_hot_limit", 1000)

        self.state.custom_state["cash"] = float(extras.get("initial_cash", 0.0))
        self.state.custom_state["position"] = float(extras.get("initial_position", 0.0))
        if record_path:
            self.state.custom_state["price_history"] = HistoryBuffer(
                folder=os.path.join(record_path, self.config.identity, "price"),
                entry_limit=hot_limit,
            )

        llm_cfg = extras.get("llm", {}) or {}
        self.state.custom_state["lm_name"] = llm_cfg.get("lm_name", "")
        self.state.custom_state["generation_config"] = llm_cfg.get(
            "generation_config", {}
        )
        self.state.custom_state["sys_message_ref"] = llm_cfg.get("sys_message", "")
        self.state.custom_state["user_message_ref"] = llm_cfg.get("user_message", "")

    def _ensure_client(self):
        client = self.state.custom_state.get("llm_client")
        if client is not None:
            return client
        try:
            from dotenv import load_dotenv  # type: ignore

            load_dotenv()
        except Exception:  # noqa: BLE001
            pass

        from lmbase.inference.api_call import LangChainAPIInference  # type: ignore

        lm_name = self.state.custom_state.get("lm_name", "")

        # --- Multi-key rotation: pick a random key from numbered variants ---
        if lm_name and "/" in lm_name:
            import os, random  # noqa: E401
            _provider = lm_name.split("/", 1)[0].upper()
            _key_var = f"{_provider}_API_KEY"
            _candidates = [
                v for k, v in os.environ.items()
                if k.startswith(f"{_key_var}_") and k[len(_key_var) + 1:].isdigit() and v
            ]
            if _candidates:
                os.environ[_key_var] = random.choice(_candidates)
        if not lm_name:
            raise RuntimeError("extras.llm.lm_name is required for LLM agents")
        client = LangChainAPIInference(
            lm_name=lm_name,
            generation_config=self.state.custom_state.get("generation_config", {}),
        )
        self.state.custom_state["llm_client"] = client
        return client

    def _order_format_category(self) -> str:
        """Return this LLM agent's order-format category name.

        The category (``"limit_order"`` / ``"maker_taker_order"`` /
        ``"participation_order"``) is derived from ``sys_message_ref`` via
        :func:`_scenario_from_sys_ref` + :func:`masim.format.get_order_format`
        and cached in ``custom_state`` so subsequent calls (e.g. from
        :meth:`_finalize_llm_order`) are O(1).

        Raises :class:`RuntimeError` if ``sys_message_ref`` is missing —
        there is no silent fallback here because downstream branch logic
        (bid_price validation) depends on knowing the exact category.
        """
        cached = self.state.custom_state.get("order_format_category")
        if isinstance(cached, str) and cached:
            return cached
        from masim.format import get_order_format

        sys_ref = self.state.custom_state.get("sys_message_ref", "")
        if not sys_ref:
            raise RuntimeError(
                "Cannot determine order-format category: "
                "extras.llm.sys_message is empty."
            )
        scenario = _scenario_from_sys_ref(sys_ref)
        category = get_order_format(scenario).NAME
        self.state.custom_state["order_format_category"] = category
        return category

    def _run_llm(self, state: StandardMarketState) -> Dict[str, Any]:
        from masim.utils.llm_utils import robust_llm_call
        from masim.format import get_order_format

        sys_ref = self.state.custom_state.get("sys_message_ref", "")
        user_ref = self.state.custom_state.get("user_message_ref", "")
        if not sys_ref or not user_ref:
            raise RuntimeError("extras.llm.sys_message and user_message are required")

        sys_prompt = _load_dotted(sys_ref)
        user_template = _load_dotted(user_ref)
        user_prompt = self._format_user_prompt(user_template, state)

        # Scenario-aware strict schema validation: the LLM must return a
        # decision-dict that matches the category advertised in the prompt's
        # FORMAT_TAIL.  If it doesn't, robust_llm_call retries (up to
        # max_retries).  There is NO silent defaulting anywhere downstream.
        scenario = _scenario_from_sys_ref(sys_ref)
        order_format = get_order_format(scenario)
        # Warm the category cache so _finalize_llm_order avoids re-parsing
        # sys_ref on every order.
        self.state.custom_state.setdefault(
            "order_format_category", order_format.NAME
        )

        client = self._ensure_client()
        max_retries = int(
            self.state.custom_state.get("max_llm_retries", 5)
        )
        fallback = self.state.custom_state.get("llm_failure_policy", "hold")

        return robust_llm_call(
            client,
            sys_prompt,
            user_prompt,
            validate_fn=order_format.validate_decision,
            max_retries=max_retries,
            fallback=fallback,
            identity=self.identity,
        )

    def _format_user_prompt(
        self,
        user_template: str,
        state: StandardMarketState,
    ) -> str:
        """Render the LLM user template against the current market state.

        Default implementation formats ``user_template`` with
        :meth:`StandardMarketState.template_vars`.  Subclasses that need
        to inject additional template variables (for example
        :class:`CanonicalRagPlayer` supplying ``rag_context``) override
        this hook rather than duplicating the whole :meth:`_run_llm`
        skeleton.  Any string returned here is passed straight to
        :func:`robust_llm_call` as the user message; there is no further
        transformation.
        """
        return user_template.format(**state.template_vars())

    def _finalize_llm_order(
        self,
        order: InvestorOrder,
        state: StandardMarketState,
    ) -> InvestorOrder:
        """Apply cash/inventory clipping to an LLM-produced order.

        Thin delegate around :func:`masim.format.finalize.finalize_llm_order`
        — mirrors :meth:`CanonicalRulePlayer._finalize_order` but skips
        the dict-normalisation step (the LLM path already lands in
        :class:`InvestorOrder` via
        :meth:`InvestorOrder.from_llm_decision`).

        Bid-price semantics are **category-aware** (see helper docstring
        for the full contract):

        * ``limit_order`` / ``maker_taker_order`` — every non-hold order MUST
          carry ``bid_price > 0``.  The category ``validate_decision`` already
          enforces this at LLM output; any ``BUY``/``SELL`` reaching this
          method with ``bid_price <= 0`` triggers :class:`ValueError`.
        * ``participation_order`` — this category intentionally omits
          ``bid_price`` at the LLM/schema layer; the helper records
          ``state.price`` on the finalised order **explicitly** so
          downstream cash bookkeeping still has a numeric reference.
        """
        return finalize_llm_order(
            order,
            state=state,
            category=self._order_format_category(),
            strategy=order.strategy or self.STRATEGY,
        )

    def _noop_order(self, reason: str = "no_market_data") -> InvestorOrder:
        """Bootstrap-round placeholder for the LLM path.

        Same semantics as :meth:`CanonicalRulePlayer._noop_order`: emit a
        skipped-marker order so downstream metrics can exclude it.
        """
        return InvestorOrder.noop(
            investor=self.identity,
            strategy=self.STRATEGY,
            reason=reason,
        )


__all__ = [
    "CanonicalRulePlayer",
    "CanonicalLLMPlayer",
]
