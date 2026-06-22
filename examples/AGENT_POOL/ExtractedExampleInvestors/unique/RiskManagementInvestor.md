# Risk-management, risk-aversion, and portfolio-insurance investors

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Risk-management, risk-aversion, and portfolio-insurance investors |
| Merged profiles | 6 |
| Scenarios | BlackMonday1987, EquityPremium, HerdEffect, LTCMCollapse, MarketCrash |
| Observed names | Portfolio Insurer, Risk Averse Investor, Risk Averse Saver, Risk Manager, Risk Neutral Investor, Risk Parity Fund |

## Consolidated Definition and Goals

- **BlackMonday1987 / Portfolio Insurer**: The PortfolioInsurer is a large institutional fund manager who has adopted the Leland-Rubinstein portfolio insurance strategy -- a dynamic hedging technique that mechanically reduces equity exposure as prices fall and rebuilds it as prices rise. In 1987, approximately $90-100 billion in institutional assets were managed under such strategies. The PortfolioInsurer's role in the simulation is to generate the primary cascade mechanism: each decline triggers selling that drives prices further down, which triggers more selling. The PortfolioInsurer is not acting irrationally -- it is following its mandate to protect capital -- but the collective behavior of many such agents creates a self-fulfilling crash.
- **EquityPremium / Risk Averse Saver**: LLM-driven risk-averse saver -- strong bond preference with prospect theory reasoning. Theory: simulation-bases.md Section 4.4.
- **EquityPremium / Risk Neutral Investor**: **Information set**: `stock_return`, `bond_return`
- **HerdEffect / Risk Averse Investor**: **Summary**: Implements Markowitz (1952) mean-variance optimization. Target position inversely proportional to price variance. Gradually adjusts toward target at 30 %/round. Smallest position cap (±20).
- **LTCMCollapse / Risk Manager**: The `RiskManager` represents institutional risk-control desks that cut exposure when deviations exceed allowed risk limits. The agent is stabilizing at the individual-book level but can amplify systemic stress when many agents cut positions simultaneously.
- **MarketCrash / Risk Parity Fund**: **Summary**: A volatility-targeting institutional investor. **Theoretical and Empirical Basis**: Volatility-managed portfolios reduce risky exposure when volatility rises; see Moreira and Muir (2017, DOI: 10.1111/jofi.12575). **Design Purpose**: Add mechanical procyclical selling after volatility spikes. **Behavioral Framework**: Uses target volatility, recent volatility, rebalance speed, and base position to scale exposure. **Decision Process**: Estimate realized volatility; if volatility exceeds the target, reduce exposure; if volatility is calm, rebalance gradually. **Worked Numerical Example**: With target volatility 2.0, observed volatility 4.0, base position 50, and rebalance speed 0.3, desired exposure is roughly 25, so a current position of 50 produces a sell order near 7.5 shares. **Academic References**: Moreira and Muir (2017); Barroso and Santa-Clara (2015).

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.1 -- PortfolioInsurer
- Theoretical basis: Leland & Rubinstein (1980) portfolio insurance; sells equities
- LLM-driven portfolio insurer -- dynamic hedging seller. Theory: simulation-bases.md Section 4.1.
- RuleLLM-driven portfolio insurer -- dynamic hedging seller. Theory: simulation-bases.md Section 4.1.
- RAG-augmented portfolio insurer -- dynamic hedging seller. Theory: simulation-bases.md Section 4.1.
- LLM-driven risk-averse saver -- strong bond preference with prospect theory reasoning. Theory: simulation-bases.md Section 4.4.
- RuleLLM conservative saver allocator. Theory: simulation-bases.md Section 4.4.
- RAG conservative saver allocator. Theory: simulation-bases.md Section 4.4.
- Theory: simulation-bases.md Section 4.3 -- RiskNeutralInvestor
- Theoretical basis: Mehra & Prescott (1985) equity premium puzzle baseline; standard
- Theory: simulation-bases.md Section 4.3 -- RiskAverseInvestor
- Theoretical basis: Mean-variance optimization (Markowitz, 1952).
- Formula: Q = k / sigma² x cash / P; position adjusted toward target gradually.
- LLM-powered RiskAverseInvestor: volatility-sensitive mean-variance strategy. Theory: simulation-bases.md Section 4.3.
- Hybrid rule+LLM RiskAverseInvestor: managing volatility. Theory: simulation-bases.md Section 4.3.
- RAG-augmented RiskAverseInvestor: volatility-sensitive strategy with retrieved knowledge. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.3 -- RiskManager
- Theoretical basis: Jorion (2000) VaR and LTCM risk-management lessons.
- Theory: simulation-bases.md Section 4.3 -- RiskManager.
- RAG VaR-based position cutter. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.1.
- LLM RiskParityFund. Theory: simulation-bases.md Section 4.1.
- Hybrid RiskParityFund. Theory: simulation-bases.md Section 4.1.
- RAG RiskParityFund. Theory: simulation-bases.md Section 4.1.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| BlackMonday1987 | Portfolio Insurer | [BlackMonday1987__PortfolioInsurer.md](../BlackMonday1987__PortfolioInsurer.md) |
| EquityPremium | Risk Averse Saver | [EquityPremium__RiskAverseSaver.md](../EquityPremium__RiskAverseSaver.md) |
| EquityPremium | Risk Neutral Investor | [EquityPremium__RiskNeutralInvestor.md](../EquityPremium__RiskNeutralInvestor.md) |
| HerdEffect | Risk Averse Investor | [HerdEffect__RiskAverseInvestor.md](../HerdEffect__RiskAverseInvestor.md) |
| LTCMCollapse | Risk Manager | [LTCMCollapse__RiskManager.md](../LTCMCollapse__RiskManager.md) |
| MarketCrash | Risk Parity Fund | [MarketCrash__RiskParityFund.md](../MarketCrash__RiskParityFund.md) |

