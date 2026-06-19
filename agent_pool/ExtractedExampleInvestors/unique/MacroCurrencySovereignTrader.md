# Macro, currency, sovereign-bond, and carry-trade agents

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Macro, currency, sovereign-bond, and carry-trade agents |
| Merged profiles | 8 |
| Scenarios | AsianFinancialCrisis, CarryTradeUnwind, CurrencyCrisis, EuropeanDebtCrisis |
| Observed names | Carry Trader, Core Bond Buyer, Funding Currency Buyer, Hedged Carry Trader, Hot Money Funder, Periphery Bond Seller, Self Fulfilling Trader, Speculative Attacker |

## Consolidated Definition and Goals

- **AsianFinancialCrisis / Hot Money Funder**: HotMoneyFunder represents the archetypal short-term foreign capital investor who provides liquidity and return-chasing flows during benign periods but reverses rapidly and aggressively at the first sign of currency stress. This agent models the foreign institutional investors -- primarily hedge funds and money market funds -- who provided the capital inflows that fuelled Asian growth in 1994-1997, then executed sudden, large-scale reversals in 1997. HotMoneyFunder is the primary crisis initiator: its 60% position liquidation at the -2% threshold creates the initial selling wave that triggers the contagion cascade.
- **CarryTradeUnwind / Carry Trader**: - **Citation**: Brunnermeier, M. K., Nagel, S., & Pedersen, L. H. (2009). "Carry trades and currency crashes." *NBER Macroeconomics Annual*, 23(1), 313-347. DOI: 10.1086/593088 - **Core Insight**: Carry trades earn positive returns on average (the "carry premium") but exhibit severe negative skewness -- they are vulnerable to sudden, large losses when risk sentiment reverses and funding currencies appreciate sharply. Brunnermeier et al. document a pattern they call "going up by the stairs and coming down by the elevator": slow carry accumulation during risk-on periods, sudden violent unwind during risk-off. The crash occurs because all carry traders unwind simultaneously, creating herding sell pressure on target currencies. - **Mathematical Formulation**: Expected carry return: E[r_carry] = i_high - i_low (interest rate differential). Crash risk: Prob(unwind | risk_off) x DeltaP_unwind >> E[r_carry]. The carry crash skewness κ < -1, meaning crash losses are systematically larger than normal gains. Leverage amplification: effective price move = lambda x (N_carry x sell_qty), where N_carry = number of carry traders. - **Empirical Evidence**: Brunnermeier et al. (2009) document that carry trade returns have skewness of -1.5 to -2.0, with crash months averaging -5% to -15% returns vs. normal months of +0.3% to +0.8%. The 2008 JPY carry unwind saw USD/JPY fall from 110 to 88 (-20%) in 6 weeks, consistent with the simulation's target drawdown of 10-25%. - **Relevance to Investor Taxonomy**: CarryTrader represents the slow accumulation phase; LeveragedCarryFund represents the violent unwind; their interaction generates the asymmetric crash pattern documented by Brunnermeier et al.
- **CarryTradeUnwind / Funding Currency Buyer**: The FundingCurrencyBuyer is a risk-averse investor -- pension fund, central bank reserve manager, or safe-haven-seeking institutional -- who buys the funding currency (e.g., JPY, CHF) when carry trade stress exceeds a threshold. This safe-haven demand provides the natural counter-pressure to forced carry trade unwinding. However, the FundingCurrencyBuyer's position size (500 units) is deliberately small relative to LeveragedCarryFund's forced selling (4000 units), representing the real-world situation where safe-haven demand is insufficient to fully absorb a large carry crash. The FundingCurrencyBuyer is the simulation's primary stabilizing force -- it limits but cannot prevent the crash.
- **CarryTradeUnwind / Hedged Carry Trader**: The HedgedCarryTrader is a sophisticated carry fund that incorporates volatility risk management: it carries a FX options hedge (modeled as hedge_ratio = 0.30 of position) and adjusts its directional exposure based on rolling volatility. When FX volatility is low, the HedgedCarryTrader accumulates carry positions (but with 30% hedge reducing net exposure); when volatility spikes above threshold, it exits. This investor represents the more sophisticated "smart carry" strategies documented by Menkhoff et al. (2012) -- carry trades that adapt to the volatility environment rather than mechanically holding.
- **CurrencyCrisis / Self Fulfilling Trader**: **4.2.1 Economic Role**: Expectation-driven seller whose behavior is based on beliefs about what others will do.
- **CurrencyCrisis / Speculative Attacker**: **4.1.1 Economic Role**: Short-seller of the vulnerable currency; profits from forced devaluation.
- **EuropeanDebtCrisis / Core Bond Buyer**: The `CoreBondBuyer` represents flight-to-quality capital reallocating toward safer core assets. In the normalized periphery market, it buys during stress and sells after recovery, modelling safe-asset rotation pressure.
- **EuropeanDebtCrisis / Periphery Bond Seller**: The `PeripheryBondSeller` represents investors selling peripheral sovereign debt when market stress appears. It is the first crisis amplifier because selling lowers bond prices and raises implied yields.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.1 -- HotMoneyFunder
- Theoretical Basis: Hot money reversal (Radelet & Sachs, 1998)
- LLM-driven hot money funder -- rapidly reverses at first crisis signal. Theory: simulation-bases.md Section 4.1.
- RuleLLM hot money funder with explicit reversal threshold rules. Theory: simulation-bases.md Section 4.1.
- RAG-augmented hot money funder -- rapidly reverses at first crisis signal. Theory: simulation-bases.md Section 4.1.
- Theory: simulation-bases.md Section 4.1 -- CarryTrader
- Theoretical basis: Uncovered interest parity deviation (Brunnermeier et al., 2009);
- LLM-driven carry trader -- borrows low-yield, invests high-yield. Theory: simulation-bases.md Section 4.1.
- RuleLLM-driven carry trader -- borrows low-yield, invests high-yield. Theory: simulation-bases.md Section 4.1.
- RAG-augmented carry trader -- borrows low-yield, invests high-yield. Theory: simulation-bases.md Section 4.1.
- Theory: simulation-bases.md Section 4.3 -- FundingCurrencyBuyer
- Theoretical basis: Safe haven currency dynamics (Menkhoff et al., 2012);
- LLM-driven funding currency buyer -- safe-haven counter-cyclical flow. Theory: simulation-bases.md Section 4.3.
- RuleLLM-driven funding currency buyer -- safe-haven counter-cyclical flow. Theory: simulation-bases.md Section 4.3.
- RAG-augmented funding currency buyer -- safe-haven counter-cyclical flow. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.4 -- HedgedCarryTrader
- Theoretical basis: Volatility-adjusted carry (Menkhoff et al., 2012);
- LLM-driven hedged carry trader -- volatility-adjusted carry positions. Theory: simulation-bases.md Section 4.4.
- RuleLLM-driven hedged carry trader -- volatility-adjusted carry positions. Theory: simulation-bases.md Section 4.4.
- RAG-augmented hedged carry trader -- volatility-adjusted carry positions. Theory: simulation-bases.md Section 4.4.
- Theory: simulation-bases.md Section 4.2 -- SelfFulfillingTrader
- Theoretical basis: Obstfeld (1996) second-generation model; crises arise from
- LLM-driven self-fulfilling trader -- sells on expectation others will sell. Theory: simulation-bases.md Section 4.2.
- RuleLLM-driven self-fulfilling trader -- sells on expectation others will sell. Theory: simulation-bases.md Section 4.2.
- RAG-augmented self-fulfilling trader -- sells on expectation others will sell. Theory: simulation-bases.md Section 4.2.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AsianFinancialCrisis | Hot Money Funder | [AsianFinancialCrisis__HotMoneyFunder.md](../AsianFinancialCrisis__HotMoneyFunder.md) |
| CarryTradeUnwind | Carry Trader | [CarryTradeUnwind__CarryTrader.md](../CarryTradeUnwind__CarryTrader.md) |
| CarryTradeUnwind | Funding Currency Buyer | [CarryTradeUnwind__FundingCurrencyBuyer.md](../CarryTradeUnwind__FundingCurrencyBuyer.md) |
| CarryTradeUnwind | Hedged Carry Trader | [CarryTradeUnwind__HedgedCarryTrader.md](../CarryTradeUnwind__HedgedCarryTrader.md) |
| CurrencyCrisis | Self Fulfilling Trader | [CurrencyCrisis__SelfFulfillingTrader.md](../CurrencyCrisis__SelfFulfillingTrader.md) |
| CurrencyCrisis | Speculative Attacker | [CurrencyCrisis__SpeculativeAttacker.md](../CurrencyCrisis__SpeculativeAttacker.md) |
| EuropeanDebtCrisis | Core Bond Buyer | [EuropeanDebtCrisis__CoreBondBuyer.md](../EuropeanDebtCrisis__CoreBondBuyer.md) |
| EuropeanDebtCrisis | Periphery Bond Seller | [EuropeanDebtCrisis__PeripheryBondSeller.md](../EuropeanDebtCrisis__PeripheryBondSeller.md) |

