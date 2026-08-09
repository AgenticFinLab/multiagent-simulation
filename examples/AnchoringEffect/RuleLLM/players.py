"""AnchoringEffect RuleLLM Simulation — pure canonical re-export.

The RuleLLM variant differs from the plain LLM variant only in the
system-prompt content (rule-embedded personas live in
``examples.AnchoringEffect.RuleLLM.prompts``); the LLM plumbing itself
is identical, so every class here is a thin alias to the shipped
``LLM<Camel>`` implementation in :mod:`masim.agents`.

Runtime behaviour
-----------------

At scenario-run time, ``configs/AnchoringEffect/RuleLLM/players.yml``
passes each investor's ``sys_message`` reference through
``extras["llm"]["sys_message"]``.  :class:`masim.agents.CanonicalLLMPlayer`
resolves the reference via :func:`masim.agents._base.load_prompt`, so
the RuleLLM personas are picked up transparently — no additional plumbing
is needed here.

Historical yaml references
--------------------------

``configs/AnchoringEffect/RuleLLM/players.yml`` still pins each class by
``"examples.AnchoringEffect.RuleLLM.players:RuleLLM<Camel>"``.  The
aliases below preserve those exact names.
"""

from __future__ import annotations

from masim.agents import CanonicalLLMPlayer as RuleLLMInvestor
from masim.agents import (
    LLMAnchoredTrader as RuleLLMAnchoredTrader,
    LLMContrarianTrader as RuleLLMContrarianTrader,
    LLMDispositionTrader as RuleLLMDispositionTrader,
    LLMFundamentalAnalyst as RuleLLMFundamentalAnalyst,
    LLMHistoricalAnchor as RuleLLMHistoricalAnchor,
    LLMLiquidityProvider as RuleLLMLiquidityProvider,
    LLMMomentumTrader as RuleLLMMomentumTrader,
    LLMNoiseTrader as RuleLLMNoiseTrader,
    LLMRationalUpdater as RuleLLMRationalUpdater,
)

# Coordinator (rule-executed) — inherited from the Rule module which
# re-exports :class:`masim.agents.MarketStockStandardPriceImpact`.
from examples.AnchoringEffect.Rule.players import Market

__all__ = [
    "Market",
    "RuleLLMInvestor",
    "RuleLLMAnchoredTrader",
    "RuleLLMHistoricalAnchor",
    "RuleLLMRationalUpdater",
    "RuleLLMMomentumTrader",
    "RuleLLMNoiseTrader",
    "RuleLLMDispositionTrader",
    "RuleLLMContrarianTrader",
    "RuleLLMFundamentalAnalyst",
    "RuleLLMLiquidityProvider",
]
