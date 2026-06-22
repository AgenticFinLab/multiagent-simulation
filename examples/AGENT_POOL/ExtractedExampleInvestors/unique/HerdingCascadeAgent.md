# Herding, contagion, cascade, reputation, and social-proof agents

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Herding, contagion, cascade, reputation, and social-proof agents |
| Merged profiles | 4 |
| Scenarios | AsianFinancialCrisis, HerdingInformation, TulipMania |
| Observed names | Cascade Follower, Contagion Trader, Reputation Herder, Social Proof Follower |

## Consolidated Definition and Goals

- **AsianFinancialCrisis / Contagion Trader**: ContagionTrader represents the cross-border investor who spreads financial stress from one market to related regional markets, modelling the contagion transmission channel documented in Kaminsky & Reinhart (1999). Unlike HotMoneyFunder who responds purely to absolute deviation, ContagionTrader uses a composite signal that combines fundamental stress (deviation) with momentum (price_return). This dual-signal design implements the Kaminsky-Reinhart finding that contagion spreads through both fundamental linkages and investor panic/portfolio rebalancing simultaneously.
- **HerdingInformation / Cascade Follower**: **Summary**: Implements Bikhchandani et al. (1992) information cascade model. Ignores private signal once cascade_count reaches cascade_trigger threshold. Primary cascade amplifier -- follows deviation direction unconditionally after lock-in.
- **HerdingInformation / Reputation Herder**: **Summary**: Implements Scharfstein & Stein (1990) reputation/career-concern herding. Follows consensus direction to protect professional reputation. Lower activation threshold than CascadeFollower -- activates before full cascade lock-in.
- **TulipMania / Social Proof Follower**: **Summary**: Enters the speculative trade because crowd participation validates the story. **Theoretical and Empirical Basis**: Herding, social proof, and informational cascades. **Design Purpose**: Amplify the same price move through a different behavioral channel than pure trend following. **Behavioral Framework**: Treats positive deviation as evidence that others are participating. **Decision Process**: Uses the same threshold and quantity formula as TrendChaser: `abs(deviation) > 0.02`, `quantity = min(800, int(abs(deviation) * 5000))`, buy on positive deviation and sell on negative deviation. **Worked Numerical Example**: A 10% premium to intrinsic value produces a 500-unit buy before portfolio constraints. **Academic References**: Herding and social-proof literature in financial markets and crowd psychology.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.2 -- ContagionTrader
- Theoretical Basis: Financial contagion (Kaminsky & Reinhart, 1999)
- LLM-driven contagion trader -- spreads selling across borders. Theory: simulation-bases.md Section 4.2.
- RuleLLM contagion trader with explicit signal formula rules. Theory: simulation-bases.md Section 4.2.
- RAG-augmented contagion trader -- spreads selling across borders. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.1 -- CascadeFollower
- Theoretical basis: Information cascade theory (Bikhchandani et al., 1992).
- LLM-driven information cascade follower. Theory: simulation-bases.md Section 4.1.
- RuleLLM-driven information cascade follower. Theory: simulation-bases.md Section 4.1.
- RagLLM-driven information cascade follower. Theory: simulation-bases.md Section 4.1.
- Theory: simulation-bases.md Section 4.2 -- ReputationHerder
- Theoretical basis: Reputation-based herding (Scharfstein & Stein, 1990).
- LLM-driven reputation-based herder. Theory: simulation-bases.md Section 4.2.
- RuleLLM-driven reputation-based herder. Theory: simulation-bases.md Section 4.2.
- RagLLM-driven reputation-based herder. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.2
- Theoretical Basis: Social proof and crowd psychology (Mackay, 1841)
- LLM social proof follower joining speculative positions due to crowd behavior.
- Rule+LLM social proof follower joining speculative positions due to crowd behavior.
- RAG-augmented social proof follower joining speculative positions due to crowd behavior.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AsianFinancialCrisis | Contagion Trader | [AsianFinancialCrisis__ContagionTrader.md](../AsianFinancialCrisis__ContagionTrader.md) |
| HerdingInformation | Cascade Follower | [HerdingInformation__CascadeFollower.md](../HerdingInformation__CascadeFollower.md) |
| HerdingInformation | Reputation Herder | [HerdingInformation__ReputationHerder.md](../HerdingInformation__ReputationHerder.md) |
| TulipMania | Social Proof Follower | [TulipMania__SocialProofFollower.md](../TulipMania__SocialProofFollower.md) |

