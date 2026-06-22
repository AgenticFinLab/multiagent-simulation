# Passive, institutional, conservative, and long-horizon investors

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Passive, institutional, conservative, and long-horizon investors |
| Merged profiles | 12 |
| Scenarios | AssetBubble, DispositionEffect, EquityPremium, MarketCrash, MomentumEffect, ReversalEffect, ShortSqueeze |
| Observed names | Conservative Holder, Conservative Investor, Index Fund, Index Holder, Index Tracker, Institutional Holder, Institutional Investor, Long Horizon Investor, Long Term Investor, Passive Investor, Rag Institutional Investor |

## Consolidated Definition and Goals

- **AssetBubble / Conservative Holder**: ConservativeHolder is the stabilizing allocation agent. It does not chase momentum, does not short mispricing, and does not use leverage. Instead, it maintains a strategic target position and rebalances slowly when its holdings drift away from that target. This provides a weak but persistent stabilizing flow that prevents the simulated market from being composed only of aggressive speculators and arbitrageurs.
- **DispositionEffect / Index Holder**: `IndexHolder` is the passive buy-and-hold baseline. It does not actively trade, so it has no realized-gain or realized-loss timing bias.
- **DispositionEffect / Institutional Investor**: `InstitutionalInvestor` is the professional active manager. It still tracks position outcomes, but uses symmetric sell discipline rather than asymmetric retail loss aversion.
- **DispositionEffect / Rag Institutional Investor**: RAG-enhanced institutional investor.
- **EquityPremium / Conservative Investor**: **Information set**: `stock_price`
- **EquityPremium / Institutional Investor**: LLM-driven institutional investor -- balanced allocation using risk-neutral framework. Theory: simulation-bases.md Section 4.3.
- **EquityPremium / Long Horizon Investor**: **Information set**: `stock_price` only (no rolling evaluation)
- **EquityPremium / Long Term Investor**: LLM-driven long-horizon investor -- accepts more equity risk via extended evaluation window. Theory: simulation-bases.md Section 4.2.
- **MarketCrash / Passive Investor**: **Summary**: A slow stabilizing allocator that rebalances occasionally. **Theoretical and Empirical Basis**: Long-horizon rebalancing creates delayed demand after price dislocations. **Design Purpose**: Provide weak mean-reverting demand in the Rule baseline. **Behavioral Framework**: Uses rebalance frequency and target position. **Decision Process**: Remain inactive most rounds; on rebalance rounds, trade toward target exposure. **Worked Numerical Example**: If target position is 30 and current position is 20 on a rebalance round, the investor buys part of the 10-share gap. **Academic References**: Gârleanu and Pedersen (2013, DOI: 10.1093/rfs/hhs083); rebalancing literature.
- **MomentumEffect / Index Fund**: **Summary**: Maintains a target equity allocation. **Theoretical and Empirical Basis**: Passive portfolio rebalancing. **Design Purpose**: Add slow baseline flow that is not trend-seeking. **Behavioral Framework**: Rule uses `target_allocation=0.6` and `rebalance_threshold=0.05`. **Decision Process**: Rebalance gradually when portfolio allocation drifts too far from target. **Worked Numerical Example**: If equity allocation falls below target by more than 5%, the fund buys part of the gap. **Academic References**: Portfolio rebalancing and constant-mix allocation literature; Perold and Sharpe (1988).
- **ReversalEffect / Index Tracker**: **Summary**: Rebalances toward target exposure. **Theoretical and Empirical Basis**: Passive allocation and benchmark rebalancing. **Design Purpose**: Add slow stabilizing demand in the Rule baseline. **Behavioral Framework**: Uses `target_position` and `rebalance_threshold`. **Decision Process**: Buy or sell when inventory drifts beyond the rebalance band. **Worked Numerical Example**: If current position is materially below target, the agent buys the gap subject to threshold rules. **Academic References**: Index rebalancing and passive-investment literature; Perold and Sharpe (1988).
- **ShortSqueeze / Institutional Holder**: **Summary**: Holds a large long position and releases supply only under selected conditions. **Theoretical and Empirical Basis**: Float scarcity and concentrated ownership increase squeeze risk when short interest is high. **Design Purpose**: Reduce available float and intensify price impact from buy orders. **Behavioral Framework**: Uses `initial_position` and variant-specific sell/hold logic. **Decision Process**: Usually hold; may sell gradually when price is far above fundamental or when prompt/rules judge profit-taking appropriate. **Worked Numerical Example**: Holding 100 shares through a rally keeps supply scarce, so short-cover orders have greater price impact. **Academic References**: Duffie, Garleanu, and Pedersen (2002), DOI: 10.1111/1540-6261.00461; Volkswagen 2008 and GameStop 2021 case evidence.

## Consolidated Financial Theory

- Theory: simulation-bases.md Section 4.6 -- ConservativeHolder
- Behavior:
- - Holds steady position
- - Rarely trades
- - Provides small stabilizing force
- - Rebalances slowly
- Effect: VERY WEAKLY STABILIZING
- Formula:
- -> simulation-bases.md Section 4.6 -- ConservativeHolder (Rule-Based Behavior)
- LLM conservative holder. Theory: simulation-bases.md Section 4.6 -- ConservativeHolder.
- Hybrid rebalancing rules with LLM reasoning. Theory: simulation-bases.md Section 4.6 -- ConservativeHolder.
- RAG-augmented rebalancing rules with retrieved knowledge. Theory: simulation-bases.md Section 4.6 -- ConservativeHolder.
- Theory: simulation-bases.md Section 4.4 -- IndexHolder
- Theoretical basis: Sharpe (1991) passive investing; zero disposition effect by design.
- Professional money managers show weaker disposition effect
- Theory: simulation-bases.md Section 4.5 -- InstitutionalInvestor
- Theoretical basis: Shapira & Venezia (2001) professional discipline; symmetric thresholds reduce disposition bias.
- LLM-driven institutional investor -- professional symmetric thresholds, weak disposition. Theory: simulation-bases.md Section 4.5.
- Hybrid rule+LLM institutional investor -- symmetric gain/loss rules embedded. Theory: simulation-bases.md Section 4.5.
- Theoretical basis: Shapira & Venezia (2001) professional discipline; RAG retrieves institutional risk-control evidence.
- Theory: simulation-bases.md Section 4.4 -- ConservativeInvestor
- Theoretical basis: Kahneman & Tversky (1979) prospect theory; heightened loss
- LLM-driven institutional investor -- balanced allocation using risk-neutral framework. Theory: simulation-bases.md Section 4.3.
- RuleLLM risk-neutral institutional allocator. Theory: simulation-bases.md Section 4.3.
- RAG risk-neutral institutional allocator. Theory: simulation-bases.md Section 4.3.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AssetBubble | Conservative Holder | [AssetBubble__ConservativeHolder.md](../AssetBubble__ConservativeHolder.md) |
| DispositionEffect | Index Holder | [DispositionEffect__IndexHolder.md](../DispositionEffect__IndexHolder.md) |
| DispositionEffect | Institutional Investor | [DispositionEffect__InstitutionalInvestor.md](../DispositionEffect__InstitutionalInvestor.md) |
| DispositionEffect | Rag Institutional Investor | [DispositionEffect__RagInstitutionalInvestor.md](../DispositionEffect__RagInstitutionalInvestor.md) |
| EquityPremium | Conservative Investor | [EquityPremium__ConservativeInvestor.md](../EquityPremium__ConservativeInvestor.md) |
| EquityPremium | Institutional Investor | [EquityPremium__InstitutionalInvestor.md](../EquityPremium__InstitutionalInvestor.md) |
| EquityPremium | Long Horizon Investor | [EquityPremium__LongHorizonInvestor.md](../EquityPremium__LongHorizonInvestor.md) |
| EquityPremium | Long Term Investor | [EquityPremium__LongTermInvestor.md](../EquityPremium__LongTermInvestor.md) |
| MarketCrash | Passive Investor | [MarketCrash__PassiveInvestor.md](../MarketCrash__PassiveInvestor.md) |
| MomentumEffect | Index Fund | [MomentumEffect__IndexFund.md](../MomentumEffect__IndexFund.md) |
| ReversalEffect | Index Tracker | [ReversalEffect__IndexTracker.md](../ReversalEffect__IndexTracker.md) |
| ShortSqueeze | Institutional Holder | [ShortSqueeze__InstitutionalHolder.md](../ShortSqueeze__InstitutionalHolder.md) |

