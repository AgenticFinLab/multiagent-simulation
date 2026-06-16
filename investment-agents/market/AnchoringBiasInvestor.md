# Anchoring and reference-point biased investors

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Anchoring and reference-point biased investors |
| Merged profiles | 4 |
| Scenarios | AnchoringEffect, ConfirmationBias, LUNACollapse |
| Observed names | Anchor Depositor, Anchored Trader, Belief Anchor, Historical Anchor |

## Consolidated Definition and Goals

- **AnchoringEffect / Anchored Trader**: AnchoredTrader represents the archetypal retail investor or buy-side analyst who anchors strongly to the first price they observed and adjusts toward fundamental value by only a fraction of the necessary amount. This agent directly models the Tversky-Kahneman anchoring-and-adjustment heuristic: it knows the fundamental value but cannot bring itself to use it fully, believing its biased "perceived target" to be the true fair value. AnchoredTrader is the primary driver of persistent mispricing in the simulation -- its refusal to trade at the true fundamental price is what keeps prices elevated above F for extended periods.
- **AnchoringEffect / Historical Anchor**: HistoricalAnchor represents the sophisticated analyst or institutional investor who anchors to a long-run price average rather than a fixed first-observation point. This agent models the "reversion to historical mean" heuristic: it uses 60 rounds of price history as its reference, dampening its perceived deviation from that average by `(1 - anchor_weight)`. When a new price regime begins -- for instance, when fundamental value shifts -- HistoricalAnchor's 60-round historical average takes many rounds to update, creating a regime-transition anchoring effect that resists the new equilibrium for an extended period.
- **ConfirmationBias / Belief Anchor**: The BeliefAnchor is a strongly opinionated investor who has formed a definitive view about market direction (initially bullish, belief = +1.0) and updates this belief asymmetrically: confirming evidence (market moving in the direction of belief) amplifies the belief, while disconfirming evidence only slowly erodes it. This investor is the simulation's primary source of persistent mispricing: once the belief state locks into a direction, BeliefAnchor continues buying (or selling) regardless of fundamental value, creating sustained one-directional demand that rational agents cannot fully overcome. The BeliefAnchor is unique among all agents in this simulation suite because it maintains a persistent internal state variable (`belief`) that compounds across rounds -- modeling the psychological reality that confirmation bias strengthens convictions over time rather than resetting each period.
- **LUNACollapse / Anchor Depositor**: **Summary**: A yield depositor who exits when confidence in the yield ecosystem falls.

## Consolidated Financial Theory

- Theoretical basis: simulation-bases.md Section 2.1 (Tversky & Kahneman, 1974).
- Decision rule (simulation-bases.md Section 4.1 -- Rule-Based Behavior):
- LLM-driven anchored trader -- anchors to initial price, adjusts insufficiently. Theory: simulation-bases.md Section 4.1 -- AnchoredTrader.
- RuleLLM anchored trader -- anchors to initial price, adjusts insufficiently. Theory: simulation-bases.md Section 4.1 -- AnchoredTrader.
- RAG-augmented anchored trader -- anchors to initial price, adjusts insufficiently. Theory: simulation-bases.md Section 4.1 -- AnchoredTrader.
- Theoretical basis: simulation-bases.md Section 2.2 (Northcraft & Neale, 1987).
- Decision rule (simulation-bases.md Section 4.2 -- Rule-Based Behavior):
- LLM-driven historical anchor -- anchors to historical average price. Theory: simulation-bases.md Section 4.2 -- HistoricalAnchor.
- RuleLLM historical anchor -- anchors to historical average price. Theory: simulation-bases.md Section 4.2 -- HistoricalAnchor.
- RAG-augmented historical anchor -- anchors to historical average price. Theory: simulation-bases.md Section 4.2 -- HistoricalAnchor.
- Theory: simulation-bases.md Section 4.1 -- BeliefAnchor
- Theoretical basis: Nickerson (1998) confirmation bias; overweights information
- LLM-driven belief anchor -- strong prior, selectively filters confirming signals. Theory: simulation-bases.md Section 4.1.
- RuleLLM-driven belief anchor -- strong prior, selectively filters confirming signals. Theory: simulation-bases.md Section 4.1.
- RAG-augmented belief anchor -- strong prior, selectively filters confirming signals. Theory: simulation-bases.md Section 4.1.
- Theory: simulation-bases.md Section 4.4 -- AnchorDepositor
- Theoretical Basis: Bank run dynamics in DeFi yield protocols
- LLM-driven yield depositor exit agent. Theory: simulation-bases.md Section 4.4.
- RuleLLM yield depositor exit agent. Theory: simulation-bases.md Section 4.4.
- RAG yield depositor exit agent. Theory: simulation-bases.md Section 4.4.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AnchoringEffect | Anchored Trader | [AnchoringEffect__AnchoredTrader.md](../AnchoringEffect__AnchoredTrader.md) |
| AnchoringEffect | Historical Anchor | [AnchoringEffect__HistoricalAnchor.md](../AnchoringEffect__HistoricalAnchor.md) |
| ConfirmationBias | Belief Anchor | [ConfirmationBias__BeliefAnchor.md](../ConfirmationBias__BeliefAnchor.md) |
| LUNACollapse | Anchor Depositor | [LUNACollapse__AnchorDepositor.md](../LUNACollapse__AnchorDepositor.md) |

