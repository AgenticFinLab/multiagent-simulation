"""Abstract base classes for canonical, scenario-agnostic agents.

Two bases are exported:

* :class:`CanonicalRulePlayer` — for deterministic, formula-driven agents.
  Subclasses implement :meth:`CanonicalRulePlayer.decide_order` returning an
  order dict; this base handles ``extras`` parsing, ``custom_state``
  bookkeeping, the perceive→decide→act lifecycle, and outbound-message
  dispatch.

* :class:`CanonicalLLMPlayer` — for LLM-driven agents.  Reads ``extras["llm"]``
  (``lm_name``, ``generation_config``, ``sys_message``, ``user_message``),
  loads prompts via dotted ``module:VAR`` references, formats the user
  template against :class:`StandardMarketState`, calls
  :class:`LangChainAPIInference`, parses ``<analysis>``/``<decision>``
  responses, and falls back to ``hold`` when the LLM is unavailable.

Both bases derive from :class:`masim.player.general.GeneralPlayer` so they
plug into the existing simulator without further wiring.
"""

from __future__ import annotations

import importlib
import logging
import os
from typing import Any, Dict, List, Optional

from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
from masim.utils.history import HistoryBuffer
from masim.format.order import validate_order
from masim.agents._state import StandardMarketState

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


# ---------------------------------------------------------------------------
# Rule base
# ---------------------------------------------------------------------------


class CanonicalRulePlayer(GeneralPlayer):
    """Base class for deterministic, formula-driven canonical agents.

    Subclasses MUST:
      * declare a class-level ``STRATEGY`` attribute (defaults to class name)
      * implement :meth:`decide_order` taking a :class:`StandardMarketState`
        and returning a partial order dict (``action``, ``quantity``,
        optional ``bid_price``).

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
            return self._noop_order()

        state = StandardMarketState.from_market_data(
            market_data,
            cash=self.state.custom_state["cash"],
            position=self.state.custom_state["position"],
        )

        order = self.decide_order(state)
        order = self._finalize_order(order, state)

        return {
            **order,
            "outbound_messages": [
                {"payload": order, "content_type": "investor_bid"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        action = decision_payload.get("action", "hold")
        quantity = float(decision_payload.get("quantity", 0.0) or 0.0)
        bid_price = float(decision_payload.get("bid_price") or 0.0)
        market_data = self.state.custom_state.get("market_data") or {}
        fill_price = bid_price if bid_price > 0 else float(market_data.get("price", 0.0))

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * fill_price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
            self.state.custom_state["cash"] += quantity * fill_price
            self.state.custom_state["position"] -= quantity

        return Action(
            action_type="investor_bid",
            payload=decision_payload,
            source_id=self.identity,
        )

    # -- override hooks ----------------------------------------------------

    def decide_order(self, state: StandardMarketState) -> Dict[str, Any]:
        """Return a partial order dict for the given market state.

        Subclasses MUST implement. The framework will fill in ``investor`` and
        ``strategy`` if missing.
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
        self, order: Dict[str, Any], state: StandardMarketState
    ) -> Dict[str, Any]:
        action = order.get("action", "hold")
        quantity = float(order.get("quantity", 0.0) or 0.0)
        bid_price = float(order.get("bid_price") or state.price)

        if action == "buy" and quantity > 0:
            affordable = state.cash / bid_price if bid_price > 0 else 0.0
            quantity = min(quantity, max(affordable, 0.0))
        elif action == "sell" and quantity > 0:
            quantity = min(quantity, max(state.position, 0.0))

        if quantity <= 0:
            action = "hold"
            quantity = 0.0

        finalized = {
            "action": action,
            "quantity": float(quantity),
            "bid_price": float(bid_price if bid_price > 0 else state.price),
            "investor": self.identity,
            "strategy": order.get("strategy", self.STRATEGY),
        }
        # Preserve any extra metadata the subclass attached.
        for k, v in order.items():
            finalized.setdefault(k, v)
        validate_order(finalized)
        return finalized

    def _noop_order(self) -> Dict[str, Any]:
        order = {
            "action": "hold",
            "quantity": 0.0,
            "bid_price": 0.01,
            "investor": self.identity,
            "strategy": self.STRATEGY,
        }
        return {
            **order,
            "outbound_messages": [
                {"payload": order, "content_type": "investor_bid"}
            ],
        }


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
    :func:`examples.llm_utils.parse_llm_response_with_thinking`. On any LLM
    failure the agent degrades gracefully to a ``hold`` order so a single
    network blip does not abort the whole simulation.

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
            return self._noop_order()

        state = StandardMarketState.from_market_data(
            market_data,
            cash=self.state.custom_state["cash"],
            position=self.state.custom_state["position"],
        )

        try:
            decision = self._run_llm(state)
        except Exception as exc:  # noqa: BLE001 — degrade gracefully, never abort
            logger.warning(
                "[%s] LLM call failed (%s); falling back to hold.",
                self.identity,
                exc,
            )
            return self._noop_order()

        action = decision.get("action", "hold")
        bid_price = float(decision.get("bid_price") or state.price)
        if bid_price <= 0:
            bid_price = state.price
        quantity = float(decision.get("quantity") or 0.0)

        if action == "buy" and quantity > 0:
            affordable = state.cash / bid_price if bid_price > 0 else 0.0
            quantity = min(quantity, max(affordable, 0.0))
        elif action == "sell" and quantity > 0:
            quantity = min(quantity, max(state.position, 0.0))

        if quantity <= 0:
            action = "hold"
            quantity = 0.0

        order = {
            "action": action,
            "quantity": float(quantity),
            "bid_price": float(bid_price),
            "investor": self.identity,
            "strategy": self.STRATEGY,
            "reasoning": str(decision.get("reasoning", ""))[:200],
            "analysis": str(decision.get("analysis", ""))[:1000],
        }
        validate_order(order)

        return {
            **order,
            "outbound_messages": [
                {"payload": {k: v for k, v in order.items() if k not in {"reasoning", "analysis"}},
                 "content_type": "investor_bid"}
            ],
        }

    async def act(self, decision_payload: Dict[str, Any]) -> Action:
        action = decision_payload.get("action", "hold")
        quantity = float(decision_payload.get("quantity", 0.0) or 0.0)
        bid_price = float(decision_payload.get("bid_price") or 0.0)
        market_data = self.state.custom_state.get("market_data") or {}
        fill_price = bid_price if bid_price > 0 else float(market_data.get("price", 0.0))

        if action == "buy" and quantity > 0:
            self.state.custom_state["cash"] -= quantity * fill_price
            self.state.custom_state["position"] += quantity
        elif action == "sell" and quantity > 0:
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
        if not lm_name:
            raise RuntimeError("extras.llm.lm_name is required for LLM agents")
        client = LangChainAPIInference(
            lm_name=lm_name,
            generation_config=self.state.custom_state.get("generation_config", {}),
        )
        self.state.custom_state["llm_client"] = client
        return client

    def _run_llm(self, state: StandardMarketState) -> Dict[str, Any]:
        from lmbase.inference.base import InferInput  # type: ignore
        from examples.llm_utils import parse_llm_response_with_thinking

        sys_ref = self.state.custom_state.get("sys_message_ref", "")
        user_ref = self.state.custom_state.get("user_message_ref", "")
        if not sys_ref or not user_ref:
            raise RuntimeError("extras.llm.sys_message and user_message are required")

        sys_prompt = _load_dotted(sys_ref)
        user_template = _load_dotted(user_ref)
        user_prompt = user_template.format(**state.template_vars())

        client = self._ensure_client()
        max_retries = 3
        last_error: Optional[BaseException] = None
        for attempt in range(max_retries):
            infer_input = InferInput(system_msg=sys_prompt, user_msg=user_prompt)
            try:
                infer_output = client.run([infer_input])
                return parse_llm_response_with_thinking(
                    infer_output.outputs[0].response
                )
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt < max_retries - 1:
                    logger.debug(
                        "[%s] LLM attempt %d failed: %s", self.identity, attempt + 1, exc
                    )
        raise RuntimeError(f"LLM call failed after {max_retries} retries: {last_error}")

    def _noop_order(self) -> Dict[str, Any]:
        order = {
            "action": "hold",
            "quantity": 0.0,
            "bid_price": 0.01,
            "investor": self.identity,
            "strategy": self.STRATEGY,
        }
        return {
            **order,
            "outbound_messages": [
                {"payload": order, "content_type": "investor_bid"}
            ],
        }


__all__ = [
    "CanonicalRulePlayer",
    "CanonicalLLMPlayer",
]
