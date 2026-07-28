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
import logging
import os
from typing import Any, Dict, Optional, Union

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer
from masim.format.order import (
    BUY,
    HOLD,
    SELL,
    InvestorOrder,
    validate_order,
)
from masim.format.state import StandardMarketState

logger = logging.getLogger("masim.agents")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_dotted(reference: str) -> str:
    """Resolve a ``module:VARIABLE`` reference and return the variable's value.

    Used by :class:`CanonicalLLMPlayer` to load prompt strings from a Python
    module attribute. The reference must contain exactly one ``:`` separator.
    """
    if ":" not in reference:
        raise ValueError(
            f"Prompt reference must use 'module:VARIABLE' form, got {reference!r}"
        )
    module_path, var_name = reference.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)


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


def _emit(order: InvestorOrder) -> Dict[str, Any]:
    """Serialise an :class:`InvestorOrder` for the pipeline.

    Attaches the ``outbound_messages`` envelope required by the market
    coordinator; the inner payload is a *fresh* ``to_dict()`` snapshot so
    the wire format is decoupled from any local mutation.
    """
    payload = order.to_dict()
    # `validate_order` is idempotent; running it here means every code path
    # that reaches the network is guaranteed to match the schema regardless
    # of which factory produced the order.
    validate_order(payload)
    outbound_payload = {
        k: v for k, v in payload.items() if k not in {"reasoning", "analysis"}
    }
    return {
        **payload,
        "outbound_messages": [
            {"payload": outbound_payload, "content_type": "investor_bid"}
        ],
    }


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
        return _emit(order)

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        # decision_payload comes from _emit(order) where order is a fully
        # validated InvestorOrder — action/quantity/bid_price are guaranteed
        # to be present.  Missing keys here indicate an invariant violation
        # in the emission pipeline, not a routine "empty round".
        for required in ("action", "quantity", "bid_price"):
            if required not in decision_payload:
                raise KeyError(
                    f"CanonicalRulePlayer.act: decision_payload missing "
                    f"required field {required!r}. Payload keys: "
                    f"{sorted(decision_payload)}"
                )
        action = decision_payload["action"]
        quantity = float(decision_payload["quantity"])
        bid_price = float(decision_payload["bid_price"])

        if action in (BUY, SELL) and quantity > 0:
            # Buy/sell requires a fill price; bid_price is guaranteed positive
            # after _finalize_order (falls back to state.price when the raw
            # subclass output was <= 0).  If it is still non-positive here we
            # have a wire-format violation — refuse to fabricate a nonsense
            # cash update at fill_price=0.
            if bid_price <= 0:
                raise ValueError(
                    f"CanonicalRulePlayer.act: {action} order has "
                    f"bid_price={bid_price!r}; every non-hold order MUST "
                    f"carry a positive bid_price after _finalize_order."
                )
            fill_price = bid_price

            if action == BUY:
                self.state.custom_state["cash"] -= quantity * fill_price
                self.state.custom_state["position"] += quantity
            else:  # SELL
                self.state.custom_state["cash"] += quantity * fill_price
                self.state.custom_state["position"] -= quantity

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
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

        Returns a new :class:`InvestorOrder` (frozen; uses
        :func:`dataclasses.replace` to apply clipping) with the
        ``_clipped*`` bookkeeping flags populated whenever we had to shrink
        the intended size. An order clipped down to zero is converted to a
        ``hold`` but is still marked ``clipped_from`` so downstream metrics
        can distinguish it from an explicit hold decision.
        """
        original_action = order.action
        original_quantity = float(order.quantity or 0.0)

        # Fall back to reference price when the subclass omitted it (or
        # supplied a non-positive value; e.g. a legacy dict with
        # bid_price=0.0 for a hold).
        bid_price = float(order.bid_price) if order.bid_price > 0 else float(state.price)

        action = original_action
        quantity = original_quantity
        clipped = False
        clipped_reason = ""

        if action == BUY and quantity > 0:
            affordable = state.cash / bid_price if bid_price > 0 else 0.0
            new_qty = min(quantity, max(affordable, 0.0))
            if new_qty < quantity:
                clipped = True
                clipped_reason = "insufficient_cash"
            quantity = new_qty
        elif action == SELL and quantity > 0:
            new_qty = min(quantity, max(state.position, 0.0))
            if new_qty < quantity:
                clipped = True
                clipped_reason = "insufficient_position"
            quantity = new_qty

        # Preserve intent: an order clipped down to 0 from a genuine buy/sell
        # intent is NOT the same as an explicit hold decision. Downstream
        # behavioral metrics (action_frequency, decision_entropy) must be
        # able to distinguish them; silent masking previously inflated the
        # hold bucket and understated agent decisiveness.
        clipped_to_hold = False
        if quantity <= 0 and original_action in (BUY, SELL):
            clipped_to_hold = True
            if not clipped_reason:
                clipped_reason = "zero_quantity_after_clip"
            action = HOLD
            quantity = 0.0
        elif quantity <= 0 and action != HOLD:
            action = HOLD
            quantity = 0.0

        finalized = dataclasses.replace(
            order,
            action=action,
            quantity=float(quantity),
            bid_price=float(bid_price if bid_price > 0 else state.price),
            investor=self.identity,
            strategy=order.strategy or self.STRATEGY,
        )
        if clipped or clipped_to_hold:
            finalized = dataclasses.replace(
                finalized,
                clipped=True,
                clipped_from=original_action,
                clipped_intended_quantity=float(original_quantity),
                clipped_reason=clipped_reason or "unspecified",
            )
        # Every non-hold order MUST carry a strictly positive bid_price so
        # downstream cash bookkeeping cannot silently fabricate a fill at
        # price zero. If we get here with bid_price <= 0 on a buy/sell, the
        # broadcast lacked a usable price (state.price non-positive) — that
        # is a scenario configuration bug, not a runtime "no data" case.
        if finalized.action in (BUY, SELL) and float(finalized.bid_price) <= 0:
            raise ValueError(
                f"CanonicalRulePlayer._finalize_order: {finalized.action} "
                f"order emerges with bid_price={finalized.bid_price!r}. "
                f"state.price={state.price!r}, original bid_price="
                f"{order.bid_price!r}. Every non-hold order requires a "
                f"positive bid_price."
            )
        # Sanity-check via the legacy validator; keeps the format-drift
        # tests exercising the same code path as the wire format.
        validate_order(finalized.to_dict())
        return finalized

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
            market_price=state.price,
        )
        # Apply cash/inventory clipping through the same finaliser used by
        # Rule agents — reuse of the code path guarantees Rule / LLM parity
        # for the clipping semantics.
        order = self._finalize_llm_order(order, state)
        return _emit(order)

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        # Same contract as CanonicalRulePlayer.act — the payload is emitted
        # by _emit() from a validated InvestorOrder.  Missing keys or a
        # non-positive bid_price on a non-hold order indicate an invariant
        # violation upstream, not a benign empty round.
        for required in ("action", "quantity", "bid_price"):
            if required not in decision_payload:
                raise KeyError(
                    f"CanonicalLLMPlayer.act: decision_payload missing "
                    f"required field {required!r}. Payload keys: "
                    f"{sorted(decision_payload)}"
                )
        action = decision_payload["action"]
        quantity = float(decision_payload["quantity"])
        bid_price = float(decision_payload["bid_price"])

        if action in (BUY, SELL) and quantity > 0:
            if bid_price <= 0:
                raise ValueError(
                    f"CanonicalLLMPlayer.act: {action} order has "
                    f"bid_price={bid_price!r}; every non-hold order MUST "
                    f"carry a positive bid_price after _finalize_llm_order."
                )
            fill_price = bid_price

            if action == BUY:
                self.state.custom_state["cash"] -= quantity * fill_price
                self.state.custom_state["position"] += quantity
            else:  # SELL
                self.state.custom_state["cash"] += quantity * fill_price
                self.state.custom_state["position"] -= quantity

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )

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

    def _run_llm(self, state: StandardMarketState) -> Dict[str, Any]:
        from masim.utils.llm_utils import robust_llm_call

        sys_ref = self.state.custom_state.get("sys_message_ref", "")
        user_ref = self.state.custom_state.get("user_message_ref", "")
        if not sys_ref or not user_ref:
            raise RuntimeError("extras.llm.sys_message and user_message are required")

        sys_prompt = _load_dotted(sys_ref)
        user_template = _load_dotted(user_ref)
        user_prompt = user_template.format(**state.template_vars())

        client = self._ensure_client()
        max_retries = int(
            self.state.custom_state.get("max_llm_retries", 5)
        )
        fallback = self.state.custom_state.get("llm_failure_policy", "hold")

        return robust_llm_call(
            client,
            sys_prompt,
            user_prompt,
            max_retries=max_retries,
            fallback=fallback,
            identity=self.identity,
        )

    def _finalize_llm_order(
        self,
        order: InvestorOrder,
        state: StandardMarketState,
    ) -> InvestorOrder:
        """Apply cash/inventory clipping to an LLM-produced order.

        Mirrors :meth:`CanonicalRulePlayer._finalize_order` but skips the
        dict-normalisation step (the LLM path already lands in
        :class:`InvestorOrder` via
        :meth:`InvestorOrder.from_llm_decision`).
        """
        original_action = order.action
        original_quantity = float(order.quantity or 0.0)
        bid_price = float(order.bid_price) if order.bid_price > 0 else float(state.price)

        action = original_action
        quantity = original_quantity
        clipped = False
        clipped_reason = ""

        if action == BUY and quantity > 0:
            affordable = state.cash / bid_price if bid_price > 0 else 0.0
            new_qty = min(quantity, max(affordable, 0.0))
            if new_qty < quantity:
                clipped = True
                clipped_reason = "insufficient_cash"
            quantity = new_qty
        elif action == SELL and quantity > 0:
            new_qty = min(quantity, max(state.position, 0.0))
            if new_qty < quantity:
                clipped = True
                clipped_reason = "insufficient_position"
            quantity = new_qty

        clipped_to_hold = False
        if quantity <= 0 and original_action in (BUY, SELL):
            clipped_to_hold = True
            if not clipped_reason:
                clipped_reason = "zero_quantity_after_clip"
            action = HOLD
            quantity = 0.0

        finalized = dataclasses.replace(
            order,
            action=action,
            quantity=float(quantity),
            bid_price=float(bid_price if bid_price > 0 else state.price),
        )
        if clipped or clipped_to_hold:
            finalized = dataclasses.replace(
                finalized,
                clipped=True,
                clipped_from=original_action,
                clipped_intended_quantity=float(original_quantity),
                clipped_reason=clipped_reason or "unspecified",
            )
        # Mirror CanonicalRulePlayer._finalize_order: refuse to emit a non-hold
        # order with bid_price <= 0. LLM output that fails this check indicates
        # the parsing/from_llm_decision step let a bogus price through, which
        # would otherwise silently corrupt cash bookkeeping downstream.
        if finalized.action in (BUY, SELL) and float(finalized.bid_price) <= 0:
            raise ValueError(
                f"CanonicalLLMPlayer._finalize_llm_order: {finalized.action} "
                f"order emerges with bid_price={finalized.bid_price!r}. "
                f"state.price={state.price!r}, original bid_price="
                f"{order.bid_price!r}. Every non-hold order requires a "
                f"positive bid_price."
            )
        validate_order(finalized.to_dict())
        return finalized

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
