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
    InvestorOrder,
    validate_order,
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

__all__ = [
    # Schema constants — investor orders
    "INVESTOR_ORDER_REQUIRED_FIELDS",
    "INVESTOR_ORDER_ACTION_VALUES",
    "BUY",
    "SELL",
    "HOLD",
    # Structured order + validators
    "InvestorOrder",
    "validate_order",
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
]
