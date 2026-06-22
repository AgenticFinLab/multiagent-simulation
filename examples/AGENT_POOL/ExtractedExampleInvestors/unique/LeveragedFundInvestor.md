# Leveraged funds, hedge funds, and concentrated position investors

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Leveraged funds, hedge funds, and concentrated position investors |
| Merged profiles | 10 |
| Scenarios | ArchegosCollapse, AssetBubble, CarryTradeUnwind, EuropeanDebtCrisis, GFC2008, LTCMCollapse, MarketCrash, SorosPound |
| Observed names | Concentrated Fund, Hedged Fund, Leverage Trader, Leveraged Buyer, Leveraged Carry Fund, Leveraged Fund, Leveraged Hedge Fund, Leveraged Investor, Leveraged Speculator, Macro Hedge Fund |

## Consolidated Definition and Goals

- **ArchegosCollapse / Concentrated Fund**: The `ConcentratedFund` represents a highly leveraged family office holding large synthetic equity exposure through Total Return Swaps -- modeled directly on Archegos Capital Management's operational structure. This investor is the primary cascade initiator: its forced selling, when triggered by a maintenance margin breach, provides the initial large negative demand shock that drives prices below the prime brokers' liquidation thresholds. Without this agent, no cascade occurs -- it is the single necessary precondition for the entire phenomenon. Its distinguishing feature compared to other investors is the combination of (1) extreme position size (the largest holder in the market), (2) leverage-forced selling (no discretion once triggered), and (3) sudden, large-block liquidation that no other agent type exhibits.
- **AssetBubble / Leveraged Buyer**: LeveragedBuyer represents the procyclical, momentum-driven participant who uses 3x leverage to amplify returns in a rising market. This agent models the margin investor who buys aggressively during the bubble's escalation phase, boosting demand and pushing prices higher. The critical feature that makes LeveragedBuyer a crash catalyst rather than merely a bubble driver is the margin call mechanism: when the equity ratio falls below 70% of initial equity, LeveragedBuyer is forced to sell 50% of its long position immediately, with no discretion. This forced selling is synchronised across multiple LeveragedBuyer instances (all face the same equity threshold) and provides the sudden coordinated selling pressure that triggers the Phase 3 crash.
- **AssetBubble / Leveraged Speculator**: LLM leveraged speculator. Theory: simulation-bases.md Section 4.5 -- LeveragedBuyer.
- **CarryTradeUnwind / Leveraged Carry Fund**: The LeveragedCarryFund is a highly leveraged institutional fund -- a hedge fund or proprietary trading desk -- that has accumulated a large carry position using maximum available leverage. Unlike the CarryTrader (who unwinds gradually as deviation worsens), the LeveragedCarryFund has an explicit stop_loss trigger: when the deviation crosses -3%, the fund's risk management system forces immediate complete liquidation. This forced selling generates the bulk of the cascade's price impact. The LeveragedCarryFund is the simulation's primary crash amplifier: its position is large, its exit is forced and rapid, and its selling volume far exceeds the stabilizing capacity of FundingCurrencyBuyer.
- **EuropeanDebtCrisis / Hedged Fund**: The `HedgedFund` is a relative-value arbitrageur that buys undervalued peripheral bonds and sells when the spread closes. It partially stabilizes the market but is bounded by capital and timing risk.
- **GFC2008 / Leveraged Investor**: `LeveragedInvestor` represents highly leveraged balance sheets funded against structured-credit collateral. When price deviation breaches the margin trigger, it sells part of its position and amplifies the fall.
- **LTCMCollapse / Leverage Trader**: The `LeverageTrader` represents balance-sheet-constrained investors whose actions are dominated by leverage and margin pressure. Under normal undervaluation the trader may buy; under equity erosion it must deleverage.
- **MarketCrash / Leveraged Fund**: LLM LeveragedHedgeFund. Theory: simulation-bases.md Section 4.2.
- **MarketCrash / Leveraged Hedge Fund**: **Summary**: A leveraged investor subject to margin calls and liquidation. **Theoretical and Empirical Basis**: Margin spirals force deleveraging into drawdowns; see Brunnermeier and Pedersen (2009, DOI: 10.1093/rfs/hhn098). **Design Purpose**: Create forced selling after losses and balance-sheet stress. **Behavioral Framework**: Uses leverage, margin-call threshold, liquidation threshold, and momentum sensitivity. **Decision Process**: Mark portfolio equity to market; if equity ratio crosses margin thresholds, sell to reduce leverage; otherwise trade with momentum. **Worked Numerical Example**: If equity ratio falls from 0.6 to 0.45, below a 0.5 margin-call level, the fund sells part of its position to restore leverage. **Academic References**: Brunnermeier and Pedersen (2009); Adrian and Shin (2010, DOI: 10.1016/j.jfineco.2010.02.001).
- **SorosPound / Macro Hedge Fund**: **Summary**: A global macro speculator that attacks a peg when misalignment is large enough to justify a directional position.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.1 -- ConcentratedFund
- Theoretical basis: Total Return Swap Leverage (Becketti, 2021); Hidden Leverage
- (SEC, 2021 Archegos Report).
- LLM-driven concentrated fund -- TRS-leveraged, slow to react to margin calls. Theory: simulation-bases.md Section 4.1.
- RuleLLM concentrated fund -- TRS-leveraged, margin call driven. Theory: simulation-bases.md Section 4.1.
- RAG-augmented concentrated fund -- TRS-leveraged, margin call driven. Theory: simulation-bases.md Section 4.1.
- Theory: simulation-bases.md Section 4.5 -- LeveragedBuyer
- Theory: Leverage amplifies both gains and losses
- Behavior:
- - Uses leverage to increase position sizes
- - Faces margin calls when prices fall
- - Forced to sell during downturns (procyclical)
- Effect: STRONGLY DESTABILIZING - Amplifies both bubbles and crashes
- Formula:
- -> simulation-bases.md Section 4.5 -- LeveragedBuyer (Rule-Based Behavior)
- Hybrid leverage rules with LLM reasoning. Theory: simulation-bases.md Section 4.5 -- LeveragedBuyer.
- RAG-augmented leverage rules with retrieved knowledge. Theory: simulation-bases.md Section 4.5 -- LeveragedBuyer.
- LLM leveraged speculator. Theory: simulation-bases.md Section 4.5 -- LeveragedBuyer.
- Theory: simulation-bases.md Section 4.2 -- LeveragedCarryFund
- Theoretical basis: Leveraged currency positions (Plantin & Shin, 2018);
- LLM-driven leveraged carry fund -- forced rapid unwind on margin calls. Theory: simulation-bases.md Section 4.2.
- RuleLLM-driven leveraged carry fund -- forced rapid unwind on margin calls. Theory: simulation-bases.md Section 4.2.
- RAG-augmented leveraged carry fund -- forced rapid unwind on margin calls. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.5 -- HedgedFund
- Theoretical basis: Shleifer & Vishny (1997) limits to arbitrage; exploits
- LLM-driven hedge fund -- relative-value spread arbitrage via LLM reasoning. Theory: simulation-bases.md Section 4.5.
- RuleLLM hedge fund -- spread arbitrage rules with LLM relative-value reasoning. Theory: simulation-bases.md Section 4.5.
- RAG-augmented hedge fund -- relative-value spread arbitrage with crisis literature. Theory: simulation-bases.md Section 4.5.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| ArchegosCollapse | Concentrated Fund | [ArchegosCollapse__ConcentratedFund.md](../ArchegosCollapse__ConcentratedFund.md) |
| AssetBubble | Leveraged Buyer | [AssetBubble__LeveragedBuyer.md](../AssetBubble__LeveragedBuyer.md) |
| AssetBubble | Leveraged Speculator | [AssetBubble__LeveragedSpeculator.md](../AssetBubble__LeveragedSpeculator.md) |
| CarryTradeUnwind | Leveraged Carry Fund | [CarryTradeUnwind__LeveragedCarryFund.md](../CarryTradeUnwind__LeveragedCarryFund.md) |
| EuropeanDebtCrisis | Hedged Fund | [EuropeanDebtCrisis__HedgedFund.md](../EuropeanDebtCrisis__HedgedFund.md) |
| GFC2008 | Leveraged Investor | [GFC2008__LeveragedInvestor.md](../GFC2008__LeveragedInvestor.md) |
| LTCMCollapse | Leverage Trader | [LTCMCollapse__LeverageTrader.md](../LTCMCollapse__LeverageTrader.md) |
| MarketCrash | Leveraged Fund | [MarketCrash__LeveragedFund.md](../MarketCrash__LeveragedFund.md) |
| MarketCrash | Leveraged Hedge Fund | [MarketCrash__LeveragedHedgeFund.md](../MarketCrash__LeveragedHedgeFund.md) |
| SorosPound | Macro Hedge Fund | [SorosPound__MacroHedgeFund.md](../SorosPound__MacroHedgeFund.md) |

