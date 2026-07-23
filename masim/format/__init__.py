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
    # Schema constants
    "INVESTOR_ORDER_REQUIRED_FIELDS",
    "INVESTOR_ORDER_ACTION_VALUES",
    "BUY",
    "SELL",
    "HOLD",
    # Structured order + validators
    "InvestorOrder",
    "validate_order",
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
