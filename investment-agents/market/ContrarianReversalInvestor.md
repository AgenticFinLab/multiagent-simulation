# Contrarian and reversal-oriented investors

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Contrarian and reversal-oriented investors |
| Merged profiles | 9 |
| Scenarios | AnchoringEffect, ConfirmationBias, HerdEffect, HerdingInformation, HindsightBias, MomentumEffect, OverconfidenceBias, RepresentativenessBias, ReversalEffect |
| Observed names | Contrarian, Contrarian Investor, Contrarian Skeptic, Contrarian Statistical, Contrarian Trader |

## Consolidated Definition and Goals

- **AnchoringEffect / Contrarian Trader**: ContrarianTrader represents the disciplined mean-reversion investor who bets against recent trends without reference to fundamental value. Unlike RationalUpdater (who exploits the price-fundamental gap), ContrarianTrader uses purely statistical reasoning: when cumulative 10-round returns exceed ±5%, it trades in the opposite direction expecting mean reversion. This agent models the empirically documented overreaction-correction cycle (De Bondt & Thaler, 1985) and provides a correction mechanism distinct from fundamental arbitrage -- one that would operate even if F were unknown.
- **ConfirmationBias / Contrarian Trader**: The ContrarianTrader actively fades the consensus -- it sells when the market is above fundamental (betting that biased optimism will correct) and buys when the market is below fundamental (betting that biased pessimism will reverse). Unlike BalancedAnalyst (which corrects passively based on fundamental value), ContrarianTrader explicitly models the active strategy of trading against bias-driven consensus. It maintains the same 5% threshold as BalancedAnalyst but represents a different economic archetype: the short-seller who exploits overvaluation and the deep-discount buyer who exploits undervaluation.
- **HerdEffect / Contrarian Investor**: **Summary**: Implements De Bondt & Thaler (1985) mean-reversion contrarian strategy. Buys when P < F, sells when P > F. Bids around fundamental (from own extras, not broadcast). Primary stabilizing force.
- **HerdingInformation / Contrarian**: **Summary**: Implements De Bondt & Thaler (1985) deliberate contrarian strategy. Triggers on larger deviations than IndependentThinker. Pure crowd-counter -- no private signal model, just fundamental anchoring.
- **HindsightBias / Contrarian Skeptic**: **Summary**: Implements Roese & Vohs (2012) narrative skepticism -- the agent resists post-hoc consensus narratives and trades against deviations with a higher threshold, acting as a second rational stabilizer at |deviation| > 0.05.
- **MomentumEffect / Contrarian Trader**: **Summary**: Trades against recent momentum once the move is large enough. **Theoretical and Empirical Basis**: Overreaction and mean-reversion evidence. **Design Purpose**: Prevent unchecked continuation. **Behavioral Framework**: Rule uses `reversion_threshold=0.03`, `scale=2.0`, `max_position=80.0`. **Decision Process**: Convert the momentum signal into an opposite-side order when the absolute signal exceeds the threshold. **Worked Numerical Example**: A 5% positive momentum signal generates a sell signal. **Academic References**: De Bondt and Thaler (1985), DOI: 10.1111/j.1540-6261.1985.tb05004.x.
- **OverconfidenceBias / Contrarian Investor**: 1. **Summary**: ContrarianInvestor fades extreme overconfident moves. It is a stabilizing agent that opposes large deviations from fundamental value. 2. **Theoretical and Empirical Foundation**: De Bondt and Thaler (1985) support the overreaction-correction mechanism. 3. **Design Purpose and Activation Scenarios**: Activates only when `abs(deviation) > contrarian_threshold`. 4. **Behavioral Framework**: Sells overvaluation and buys undervaluation, with size capped by `base_size`, cash, and inventory. 5. **Decision Process Walkthrough**: Wait for a large deviation, trade against the direction, and provide mean-reversion pressure. 6. **Worked Numerical Example**: A 6% overvaluation with threshold 4% triggers a sell order up to the configured base size. 7. **Academic References**: De Bondt and Thaler (1985).
- **RepresentativenessBias / Contrarian Statistical**: **Summary**: A stabilizing arbitrageur that trades against pattern-driven mispricing. It is inactive for small deviations but corrects large biased pressure.
- **ReversalEffect / Contrarian Investor**: **Summary**: Trades against large recent moves. **Theoretical and Empirical Basis**: Mean-reversion evidence after investor overreaction. **Design Purpose**: Generate direct reversal pressure. **Behavioral Framework**: Uses lookback returns, `reversal_threshold`, `base_position_size`, and value sensitivity. **Decision Process**: Buy after excessive declines and sell after excessive rises. **Worked Numerical Example**: If the recent return is -15% and the threshold is 10%, the agent submits a buy order scaled by the excess move. **Academic References**: De Bondt and Thaler (1985), DOI: 10.1111/j.1540-6261.1985.tb05004.x; Lakonishok, Shleifer, and Vishny (1994), DOI: 10.1111/j.1540-6261.1994.tb04772.x.

## Consolidated Financial Theory

- Theoretical basis: De Bondt & Thaler (1985); Jegadeesh (1990).
- Theory: simulation-bases.md Section 4.4 -- ContrarianTrader
- Theoretical basis: Rabin & Schrag (1999) -- rational traders exploit systematic
- LLM-driven contrarian -- exploits systematic bias errors of biased traders. Theory: simulation-bases.md Section 4.4.
- RuleLLM-driven contrarian -- exploits systematic bias errors of biased traders. Theory: simulation-bases.md Section 4.4.
- RAG-augmented contrarian -- exploits systematic bias errors of biased traders. Theory: simulation-bases.md Section 4.4.
- Theory: simulation-bases.md Section 4.2 -- ContrarianInvestor
- Theoretical basis: Contrarian / value strategy (De Bondt & Thaler, 1985).
- Formula: P = F + epsilon; Q = β x (F - P) / P x cash / P.
- LLM-powered ContrarianInvestor: value investing against the crowd. Theory: simulation-bases.md Section 4.2.
- Hybrid rule+LLM ContrarianInvestor: betting against the crowd. Theory: simulation-bases.md Section 4.2.
- RAG-augmented ContrarianInvestor: value investing with retrieved knowledge. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.4 -- Contrarian
- Theoretical basis: Anti-herding / contrarian strategy (Froot et al., 1992).
- LLM-driven contrarian investor. Theory: simulation-bases.md Section 4.4.
- RuleLLM-driven contrarian investor. Theory: simulation-bases.md Section 4.4.
- RagLLM-driven contrarian investor. Theory: simulation-bases.md Section 4.4.
- Theory: simulation-bases.md Section 4.4 -- ContrarianSkeptic
- Theoretical basis: Narrative skepticism (Roese & Vohs, 2012).
- LLM-driven ContrarianSkeptic: distrusts post-hoc narratives, takes contrarian positions. Theory: simulation-bases.md Section 4.4.
- RuleLLM ContrarianSkeptic: distrusts post-hoc narratives. Theory: simulation-bases.md Section 4.4.
- RAG ContrarianSkeptic: distrusts post-hoc narratives. Theory: simulation-bases.md Section 4.4.
- Theory: simulation-bases.md Section 4.2.
- Financial Theory:
- - Overreaction: Markets overshoot and correct
- - Mean reversion: Prices return to fundamentals
- LLM ContrarianTrader. Theory: simulation-bases.md Section 4.2.
- Hybrid ContrarianTrader. Theory: simulation-bases.md Section 4.2.
- RAG ContrarianTrader. Theory: simulation-bases.md Section 4.2.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AnchoringEffect | Contrarian Trader | [AnchoringEffect__ContrarianTrader.md](../AnchoringEffect__ContrarianTrader.md) |
| ConfirmationBias | Contrarian Trader | [ConfirmationBias__ContrarianTrader.md](../ConfirmationBias__ContrarianTrader.md) |
| HerdEffect | Contrarian Investor | [HerdEffect__ContrarianInvestor.md](../HerdEffect__ContrarianInvestor.md) |
| HerdingInformation | Contrarian | [HerdingInformation__Contrarian.md](../HerdingInformation__Contrarian.md) |
| HindsightBias | Contrarian Skeptic | [HindsightBias__ContrarianSkeptic.md](../HindsightBias__ContrarianSkeptic.md) |
| MomentumEffect | Contrarian Trader | [MomentumEffect__ContrarianTrader.md](../MomentumEffect__ContrarianTrader.md) |
| OverconfidenceBias | Contrarian Investor | [OverconfidenceBias__ContrarianInvestor.md](../OverconfidenceBias__ContrarianInvestor.md) |
| RepresentativenessBias | Contrarian Statistical | [RepresentativenessBias__ContrarianStatistical.md](../RepresentativenessBias__ContrarianStatistical.md) |
| ReversalEffect | Contrarian Investor | [ReversalEffect__ContrarianInvestor.md](../ReversalEffect__ContrarianInvestor.md) |

