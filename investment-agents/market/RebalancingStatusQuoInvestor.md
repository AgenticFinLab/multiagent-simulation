# Rebalancing, default-following, status-quo, and tax-aware investors

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Rebalancing, default-following, status-quo, and tax-aware investors |
| Merged profiles | 5 |
| Scenarios | DispositionEffect, StatusQuoBias |
| Observed names | Active Rebalancer, Default Follower, Inertial Holder, Rag Tax Aware Investor, Tax Aware Investor |

## Consolidated Definition and Goals

- **DispositionEffect / Rag Tax Aware Investor**: RAG-enhanced tax-aware investor.
- **DispositionEffect / Tax Aware Investor**: `TaxAwareInvestor` deliberately reverses the disposition effect by realizing losses for tax benefits and deferring gains.
- **StatusQuoBias / Active Rebalancer**: This investor represents portfolio managers who respond directly to valuation gaps and rebalance toward fundamental value.
- **StatusQuoBias / Default Follower**: This investor represents retirement-plan participants and passive allocators who accept a default portfolio unless drift is highly visible.
- **StatusQuoBias / Inertial Holder**: This investor represents households, trustees, and portfolio managers who prefer not to disturb an existing allocation unless the signal is extreme.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.3 -- TaxAwareInvestor
- Theoretical basis: Constantinides (1983) tax-loss harvesting; RAG retrieves tax strategy literature.
- Opposite of disposition effect for tax optimization:
- - Sells losers to harvest tax losses
- - Holds winners to defer capital gains tax
- Theoretical basis: Constantinides (1983) tax-loss harvesting; anti-disposition via economic incentive.
- LLM-driven tax-aware investor -- harvests losses, defers gains for tax optimization. Theory: simulation-bases.md Section 4.3.
- Hybrid rule+LLM tax-aware investor -- tax-loss harvesting rules embedded. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.3 -- ActiveRebalancer
- Theoretical basis: rational portfolio rebalancing benchmark.
- LLM-driven active rebalancer adjusting on new information. Theory: simulation-bases.md Section 4.3.
- RuleLLM active rebalancer adjusting on new information. Theory: simulation-bases.md Section 4.3.
- RagLLM active rebalancer adjusting on new information. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.2 -- DefaultFollower
- Theoretical basis: default bias and decision avoidance.
- LLM-driven default follower avoiding active decisions. Theory: simulation-bases.md Section 4.2.
- RuleLLM default follower avoiding active decisions. Theory: simulation-bases.md Section 4.2.
- RagLLM default follower avoiding active decisions. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.1 -- InertialHolder
- Theoretical basis: decision inertia (Samuelson & Zeckhauser, 1988).
- LLM-driven inertial holder with strong status quo bias. Theory: simulation-bases.md Section 4.1.
- RuleLLM inertial holder with strong status quo bias. Theory: simulation-bases.md Section 4.1.
- RagLLM inertial holder with strong status quo bias. Theory: simulation-bases.md Section 4.1.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| DispositionEffect | Rag Tax Aware Investor | [DispositionEffect__RagTaxAwareInvestor.md](../DispositionEffect__RagTaxAwareInvestor.md) |
| DispositionEffect | Tax Aware Investor | [DispositionEffect__TaxAwareInvestor.md](../DispositionEffect__TaxAwareInvestor.md) |
| StatusQuoBias | Active Rebalancer | [StatusQuoBias__ActiveRebalancer.md](../StatusQuoBias__ActiveRebalancer.md) |
| StatusQuoBias | Default Follower | [StatusQuoBias__DefaultFollower.md](../StatusQuoBias__DefaultFollower.md) |
| StatusQuoBias | Inertial Holder | [StatusQuoBias__InertialHolder.md](../StatusQuoBias__InertialHolder.md) |

