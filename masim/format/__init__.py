"""Format schemas, validation, and shared prompt components.

This package is the *single source of truth* for the shape of every message
that flows between agents and the market coordinator.  Concretely, it
exposes:

* :class:`InvestorOrder` and its factory classmethods — the structured
  decision payload every canonical Rule / LLM agent must emit.
* :func:`validate_order` — the legacy dict-based validator (still enforced
  at every emit site by :mod:`masim.agents._base`).
* :data:`INVESTOR_ORDER_REQUIRED_FIELDS`, :data:`INVESTOR_ORDER_ACTION_VALUES`,
  :data:`BUY`, :data:`SELL`, :data:`HOLD` — the format schema constants;
  agents should reference these rather than open-coding literals.
* :class:`MarketBroadcast` and :func:`validate_broadcast` — the structured
  broadcast payload every canonical market coordinator must emit.  Each
  archetype has a registered :class:`BroadcastSchema` in
  :data:`BROADCAST_SCHEMAS`; coordinators validate through this layer before
  emission (enforced at :meth:`CanonicalMarketCoordinator.decide`).
* LLM prompt scaffolding (:data:`DECISION_FORMAT_INSTRUCTION`,
  :func:`build_llm_system_prompt`, :func:`build_llm_user_template`, and
  the small library of reusable prompt strings in :mod:`.base_prompts`)
  — LLM agents compose their prompts through these builders so a schema
  change is a one-file edit.
"""

from .order import (
    INVESTOR_ORDER_REQUIRED_FIELDS,
    INVESTOR_ORDER_ACTION_VALUES,
    BUY,
    SELL,
    HOLD,
    normalize_action_quantity,
    signed_order_quantity,
    InvestorOrder,
    validate_order,
)
from .finalize import (
    require_positive_bid_price,
    clip_order_to_liquidity,
    finalize_rule_order,
    finalize_llm_order,
    emit_order_envelope,
)
from .state import (
    REQUIRED_BROADCAST_FIELDS,
    StandardMarketState,
)
from .broadcast import (
    FieldSpec,
    BroadcastSchema,
    BROADCAST_SCHEMAS,
    COORDINATOR_ACTION_TYPES,
    get_coordinator_action_types,
    STOCK_STANDARD_PRICE_IMPACT_SCHEMA,
    OPINION_ECHO_CHAMBER_CLUSTERING_SCHEMA,
    INFORMATION_SIS_CONTAGION_SCHEMA,
    FX_CURRENCY_PEG_AND_ATTACK_SCHEMA,
    BOND_YIELD_SPREAD_INVERSE_SCHEMA,
    CRYPTO_ALGOSTABLE_DEPEG_SCHEMA,
    DERIVATIVES_VOL_FEEDBACK_SCHEMA,
    DEPOSIT_BANK_RUN_DIAMOND_DYBVIG_SCHEMA,
    CREDIT_MINSKY_CYCLE_SCHEMA,
    validate_broadcast,
    MarketBroadcast,
    get_broadcast_schema,
)
from .order_prompts import (
    DECISION_FORMAT_INSTRUCTION,
    DECISION_FORMAT_INSTRUCTION_TPL,
    STANDARD_MARKET_STATE_BLOCK,
    build_llm_system_prompt,
    build_llm_user_template,
)
from .base_prompts import (
    ANALYSIS_DECISION_TAG,
    TRADING_CONSTRAINTS,
    MARKET_ACTION_QUESTION,
    RULELLM_APPLY_RULES,
    RAG_APPLY_RULES_WITH_KNOWLEDGE,
)

# ---------------------------------------------------------------------------
# Order-format categories
# ---------------------------------------------------------------------------
#
# Every LLM prompt in `examples/<Scenario>/LLM/prompts.py` composes its
# system message as
#
#     LLM_XXX_SYS = _XXX_PERSONA + "\n\n" + FORMAT_TAIL
#
# where ``FORMAT_TAIL`` is imported from one of these three category modules.
# The category to use is looked up by scenario slug in
# :data:`SCENARIO_ORDER_FORMAT`; runtime code (:mod:`masim.agents._base`) uses
# :func:`get_order_format` to plug ``validate_decision`` into
# :func:`masim.utils.llm_utils.robust_llm_call` so a schema-invalid LLM
# response is *retried*, never silently defaulted.
from . import limit_order, maker_taker_order, participation_order
from types import ModuleType
from typing import Any as _Any, Mapping as _Mapping

SCENARIO_ORDER_FORMAT: dict[str, str] = {
    # 🧠 Behavioral Biases — canonical limit-order market
    "HerdEffect":           "limit_order",
    "DispositionEffect":    "limit_order",
    "OverconfidenceBias":   "limit_order",
    "AnchoringEffect":      "limit_order",
    # 💥 Market Mechanisms
    "AssetBubble":          "limit_order",
    "MomentumEffect":       "limit_order",
    "FlashCrash2010":       "maker_taker_order",  # HFT: needs provides_liquidity
    "HerdingInformation":   "limit_order",
    # 📉 Historical Crises
    "DotComBubble":         "limit_order",
    "GFC2008":              "limit_order",
    "GameStopShortSqueeze": "limit_order",
    "SVBBankRun":           "participation_order",  # bank-run proxy: no bid_price
}

_ORDER_FORMAT_MODULES: dict[str, ModuleType] = {
    "limit_order": limit_order,
    "maker_taker_order": maker_taker_order,
    "participation_order": participation_order,
}


def get_order_format(scenario_or_name: str) -> ModuleType:
    """Return the category module for a scenario slug OR a raw category name.

    Callers can pass either a scenario slug ("HerdEffect") or the category
    name directly ("limit_order"). Raises :class:`KeyError` if neither
    matches — no silent fallback, so a missing registry entry surfaces
    immediately.
    """
    if scenario_or_name in _ORDER_FORMAT_MODULES:
        return _ORDER_FORMAT_MODULES[scenario_or_name]
    if scenario_or_name in SCENARIO_ORDER_FORMAT:
        return _ORDER_FORMAT_MODULES[SCENARIO_ORDER_FORMAT[scenario_or_name]]
    raise KeyError(
        f"No order-format category registered for {scenario_or_name!r}. "
        f"Known scenarios: {sorted(SCENARIO_ORDER_FORMAT)}; "
        f"known categories: {sorted(_ORDER_FORMAT_MODULES)}."
    )


def validate_llm_decision(
    scenario_or_name: str, decision: _Mapping[str, _Any]
) -> None:
    """Dispatch a decision-dict to the correct category validator.

    This is what :func:`masim.utils.llm_utils.robust_llm_call` receives as
    ``validate_fn`` (bound to the current scenario at agent-setup time).
    Every category validator raises :class:`ValueError` on any missing /
    malformed field, so the LLM is retried until it emits a fully-specified
    decision. Silent defaulting is forbidden by design.
    """
    get_order_format(scenario_or_name).validate_decision(decision)

__all__ = [
    # Schema constants — investor orders
    "INVESTOR_ORDER_REQUIRED_FIELDS",
    "INVESTOR_ORDER_ACTION_VALUES",
    "BUY",
    "SELL",
    "HOLD",
    "normalize_action_quantity",
    "signed_order_quantity",
    # Structured order + validators
    "InvestorOrder",
    "validate_order",
    # Centralised order-finalisation helpers (single site for the
    # clip → validate → emit pipeline; enforces the fail-loud rules)
    "require_positive_bid_price",
    "clip_order_to_liquidity",
    "finalize_rule_order",
    "finalize_llm_order",
    "emit_order_envelope",
    # Standard broadcast-read model consumed by canonical agents
    "StandardMarketState",
    "REQUIRED_BROADCAST_FIELDS",
    # Schema constants — coordinator broadcasts
    "FieldSpec",
    "BroadcastSchema",
    "BROADCAST_SCHEMAS",
    "COORDINATOR_ACTION_TYPES",
    "get_coordinator_action_types",
    "STOCK_STANDARD_PRICE_IMPACT_SCHEMA",
    "OPINION_ECHO_CHAMBER_CLUSTERING_SCHEMA",
    "INFORMATION_SIS_CONTAGION_SCHEMA",
    "FX_CURRENCY_PEG_AND_ATTACK_SCHEMA",
    "BOND_YIELD_SPREAD_INVERSE_SCHEMA",
    "CRYPTO_ALGOSTABLE_DEPEG_SCHEMA",
    "DERIVATIVES_VOL_FEEDBACK_SCHEMA",
    "DEPOSIT_BANK_RUN_DIAMOND_DYBVIG_SCHEMA",
    "CREDIT_MINSKY_CYCLE_SCHEMA",
    # Structured broadcast + validators
    "validate_broadcast",
    "MarketBroadcast",
    "get_broadcast_schema",
    # LLM prompt scaffolding
    "DECISION_FORMAT_INSTRUCTION",
    "DECISION_FORMAT_INSTRUCTION_TPL",
    "STANDARD_MARKET_STATE_BLOCK",
    "build_llm_system_prompt",
    "build_llm_user_template",
    # Reusable prompt strings
    "ANALYSIS_DECISION_TAG",
    "TRADING_CONSTRAINTS",
    "MARKET_ACTION_QUESTION",
    "RULELLM_APPLY_RULES",
    "RAG_APPLY_RULES_WITH_KNOWLEDGE",
    # Order-format categories (definition-site concatenation model)
    "limit_order",
    "maker_taker_order",
    "participation_order",
    "SCENARIO_ORDER_FORMAT",
    "get_order_format",
    "validate_llm_decision",
]
