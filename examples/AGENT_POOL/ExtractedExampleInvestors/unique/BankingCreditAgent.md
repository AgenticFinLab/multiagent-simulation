# Banking, credit, lending, depositor, broker, and rating agents

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Banking, credit, lending, depositor, broker, and rating agents |
| Merged profiles | 12 |
| Scenarios | ArchegosCollapse, CreditCycle, EuropeanDebtCrisis, GFC2008, LUNACollapse, SVBBankRun |
| Observed names | Bank Manager, Bond Trader, Counter Cyclical Lender, Creditor Panicker, De Fi Lender, Depositor, MBS Originator, Minsky Borrower, Prime Broker 1, Prime Broker 2, Pro Cyclical Lender, Rating Agency |

## Consolidated Definition and Goals

- **ArchegosCollapse / Prime Broker 1**: `PrimeBroker1` represents the first-acting prime broker -- the counterparty that liquidates ahead of competitors, obtaining better prices. In the Archegos event, Morgan Stanley acted earliest (March 25-26) among the major prime brokers. PrimeBroker1 models the financially rational response to a creditor run: first-mover advantage means acting at threshold -0.10 (a less severe decline) rather than waiting for the more conservative threshold. This investor is the second link in the cascade chain: its large sell order, coming at prices still above PrimeBroker2's eventual selling price, amplifies the initial ConcentratedFund shock and pushes prices toward PrimeBroker2's trigger.
- **ArchegosCollapse / Prime Broker 2**: `PrimeBroker2` represents the second-acting prime broker -- the counterparty who acted later and received worse prices. In the Archegos event, Credit Suisse and Nomura delayed action (March 29), incurring losses of $5.5B and $2.9B respectively versus Morgan Stanley's ~$1B. PrimeBroker2 models the cost of second-mover disadvantage in a creditor cascade: it has a higher threshold (-0.15) reflecting greater loss tolerance or slower risk management processes, but this conservatism backfires -- by the time it acts, prices have already been depressed by ConcentratedFund and PrimeBroker1, and its sell orders occur at substantially worse prices.
- **CreditCycle / Counter Cyclical Lender**: **4.3.1 Economic Role**: Contrarian credit provider who accumulates reserves during booms and deploys liquidity during crises.
- **CreditCycle / Minsky Borrower**: **4.2.1 Economic Role**: Speculative-to-Ponzi borrower who increases leverage during periods of stability.
- **CreditCycle / Pro Cyclical Lender**: **4.1.1 Economic Role**: Pro-cyclical credit supplier whose lending standards move with asset prices.
- **EuropeanDebtCrisis / Creditor Panicker**: The `CreditorPanicker` represents bank creditors and funding providers that exit after sovereign stress becomes severe. It captures the sovereign-bank doom loop.
- **GFC2008 / MBS Originator**: `MBSOriginator` represents the originate-to-distribute pipeline that steadily sells securitized mortgage exposure. It supplies the market with risky securities even when prices weaken, reflecting fee-income incentives rather than long-horizon asset performance.
- **GFC2008 / Rating Agency**: - **Primary Citation**: Bolton, P., Freixas, X. & Shapiro, J. (2012). "The Credit Ratings Game." *Journal of Finance*, 67(1), 85-111. https://doi.org/10.1111/j.1540-6261.2011.01708.x - **Theory Status**: Canonical theoretical model -- provides rigorous equilibrium characterization of rating inflation under issuer-pays incentive - **Original Context**: Credit rating agency equilibrium model; issuer-pays vs. investor-pays; rating inflation and selective shopping
- **LUNACollapse / De Fi Lender**: **Summary**: A lending protocol participant that liquidates collateral after a sharp price decline.
- **SVBBankRun / Bank Manager**: **Summary**: Provides stabilizing support when the proxy price is under stress. **Theoretical and Empirical Foundation**: Asset-liability management under duration mismatch. **Design Purpose and Activation Scenarios**: Buys when `deviation < -0.05`. **Behavioral Framework**: Balance-sheet support constrained by available cash. **Mathematical Model**: **Decision Process Walkthrough**: Observe stress, deploy limited support if affordable. **Worked Example**: At price 95 and cash 3,000,000, stress triggers the cap of 500 buy units. **References**: Duration-risk and asset-liability management literature.
- **SVBBankRun / Bond Trader**: **Summary**: Trades the proxy based on rate-sensitive asset valuation. **Theoretical and Empirical Foundation**: Fixed-income duration and mark-to-market loss transmission. **Design Purpose and Activation Scenarios**: Reacts when `abs(deviation) > 0.03`. **Behavioral Framework**: Opportunistic rates specialist; buys undervaluation and sells overvaluation. **Mathematical Model**: **Decision Process Walkthrough**: Convert valuation deviation into bounded directional pressure. **Worked Example**: `deviation=-0.07` yields `qty=210`; the trader buys if cash permits. **References**: Fixed-income duration and crisis mark-to-market literature.
- **SVBBankRun / Depositor**: **Summary**: Withdraws when perceived bank health deteriorates. **Theoretical and Empirical Foundation**: Diamond-Dybvig coordination-run logic. **Design Purpose and Activation Scenarios**: Activates when `deviation < -withdrawal_threshold`. **Behavioral Framework**: Risk-averse liquidity protection; sell pressure is the proxy for withdrawal. **Mathematical Model**: **Decision Process Walkthrough**: Observe deviation, compare to threshold, sell available proxy units if stress is severe. **Worked Example**: With `withdrawal_threshold=0.1`, `deviation=-0.15`, and `position=600`, the depositor sells 600. **References**: Diamond and Dybvig (1983).

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.2 -- PrimeBroker1
- Theoretical basis: Creditor Run / Liquidation Race (Gorton & Metrick, 2012).
- LLM-driven prime broker 1 -- first-mover liquidator. Theory: simulation-bases.md Section 4.2.
- RuleLLM prime broker 1 -- first-mover liquidator. Theory: simulation-bases.md Section 4.2.
- RAG-augmented prime broker 1 -- first-mover liquidator. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.3 -- PrimeBroker2
- LLM-driven prime broker 2 -- delayed liquidator at worse prices. Theory: simulation-bases.md Section 4.3.
- RuleLLM prime broker 2 -- delayed liquidator at worse prices. Theory: simulation-bases.md Section 4.3.
- RAG-augmented prime broker 2 -- delayed liquidator at worse prices. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.3 -- CounterCyclicalLender
- Theoretical basis: Geanakoplos (2010) leverage cycle; counter-cyclical capital buffers
- LLM-driven counter-cyclical lender -- reserves in booms, liquidity injection in busts. Theory: simulation-bases.md Section 4.3.
- RuleLLM-driven counter-cyclical lender -- reserves in booms, liquidity in busts. Theory: simulation-bases.md Section 4.3.
- RAG-augmented counter-cyclical lender -- reserves in booms, liquidity in busts. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.2 -- MinskyBorrower
- Theoretical basis: Minsky (1986) financial instability hypothesis; periods of
- LLM-driven Minsky borrower -- accumulates leverage during stability, Ponzi phase. Theory: simulation-bases.md Section 4.2.
- RuleLLM-driven Minsky borrower -- accumulates leverage during stability, Ponzi phase. Theory: simulation-bases.md Section 4.2.
- RAG-augmented Minsky borrower -- accumulates leverage during stability, Ponzi phase. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.1 -- ProCyclicalLender
- Theoretical basis: Adrian & Shin (2010) pro-cyclical leverage; lending standards
- LLM-driven pro-cyclical lender -- expands credit in booms, tightens in busts. Theory: simulation-bases.md Section 4.1.
- RuleLLM-driven pro-cyclical lender -- expands credit in booms, tightens in busts. Theory: simulation-bases.md Section 4.1.
- RAG-augmented pro-cyclical lender -- expands credit in booms, tightens in busts. Theory: simulation-bases.md Section 4.1.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| ArchegosCollapse | Prime Broker 1 | [ArchegosCollapse__PrimeBroker1.md](../ArchegosCollapse__PrimeBroker1.md) |
| ArchegosCollapse | Prime Broker 2 | [ArchegosCollapse__PrimeBroker2.md](../ArchegosCollapse__PrimeBroker2.md) |
| CreditCycle | Counter Cyclical Lender | [CreditCycle__CounterCyclicalLender.md](../CreditCycle__CounterCyclicalLender.md) |
| CreditCycle | Minsky Borrower | [CreditCycle__MinskyBorrower.md](../CreditCycle__MinskyBorrower.md) |
| CreditCycle | Pro Cyclical Lender | [CreditCycle__ProCyclicalLender.md](../CreditCycle__ProCyclicalLender.md) |
| EuropeanDebtCrisis | Creditor Panicker | [EuropeanDebtCrisis__CreditorPanicker.md](../EuropeanDebtCrisis__CreditorPanicker.md) |
| GFC2008 | MBS Originator | [GFC2008__MBSOriginator.md](../GFC2008__MBSOriginator.md) |
| GFC2008 | Rating Agency | [GFC2008__RatingAgency.md](../GFC2008__RatingAgency.md) |
| LUNACollapse | De Fi Lender | [LUNACollapse__DeFiLender.md](../LUNACollapse__DeFiLender.md) |
| SVBBankRun | Bank Manager | [SVBBankRun__BankManager.md](../SVBBankRun__BankManager.md) |
| SVBBankRun | Bond Trader | [SVBBankRun__BondTrader.md](../SVBBankRun__BondTrader.md) |
| SVBBankRun | Depositor | [SVBBankRun__Depositor.md](../SVBBankRun__Depositor.md) |

