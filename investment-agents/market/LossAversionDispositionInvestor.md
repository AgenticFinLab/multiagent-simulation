# Loss-aversion, disposition-effect, and endowment-effect investors

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Loss-aversion, disposition-effect, and endowment-effect investors |
| Merged profiles | 12 |
| Scenarios | AnchoringEffect, DispositionEffect, EndowmentEffect, EquityPremium, LossAversion |
| Observed names | Break Even Trader, Disposition Biased, Disposition Investor, Disposition Trader, Endowed Holder, Loss Averse, Loss Averse Investor, Myopic Loss Averse, Myopic Loss Averse Investor, Rag Disposition Investor, Rag Loss Averse, Status Quo Seller |

## Consolidated Definition and Goals

- **AnchoringEffect / Disposition Trader**: DispositionTrader represents the retail investor who systematically sells winning positions too early and holds losing positions too long. This agent models the Disposition Effect (Shefrin & Statman, 1985) -- a behavioural pattern rooted in Prospect Theory (Kahneman & Tversky, 1979) where the asymmetric value function makes realised gains feel less painful to lock in while realised losses feel disproportionately aversive. In the AnchoringEffect simulation, DispositionTrader introduces asymmetric liquidity: when prices are elevated above its cost basis (a gain scenario), it sells quickly, adding downward pressure that partially offsets anchoring-driven overvaluation. When prices fall below cost basis (a loss scenario), it refuses to sell, removing potential liquidity and allowing mispricings to persist with less corrective flow.
- **DispositionEffect / Disposition Biased**: LLM-driven disposition-biased investor -- sells winners early, holds losers. Theory: simulation-bases.md Section 4.1.
- **DispositionEffect / Disposition Investor**: `DispositionInvestor` is the primary behavioral agent. It treats the original purchase price as a mental-accounting reference point, sells winners quickly, and realizes losers only after a larger drawdown.
- **DispositionEffect / Loss Averse**: LLM-driven extreme loss-averse investor -- very reluctant to realize losses. Theory: simulation-bases.md Section 4.1.
- **DispositionEffect / Rag Disposition Investor**: RAG-enhanced disposition-prone investor.
- **DispositionEffect / Rag Loss Averse**: RAG-enhanced extreme loss-averse investor.
- **EndowmentEffect / Endowed Holder**: A heavily endowed investor who values owned shares far above market price due to maximum ownership attachment. Sells only when price exceeds a large endowment premium threshold; creates persistent upward price pressure and suppresses trading volume. Embodies the strongest form of the endowment effect.
- **EndowmentEffect / Status Quo Seller**: A status-quo-biased seller who holds positions long due to inertia, demanding a premium significantly above fundamental before selling. Creates a secondary resistance layer below EndowedHolder, reflecting cognitive switching costs rather than pure ownership attachment.
- **EquityPremium / Myopic Loss Averse**: **Information set**: `stock_price`, `stock_history` (rolling `evaluation_window` entries), `stock_return`
- **LossAversion / Break Even Trader**: **Summary**: Operationalises CPT's prediction that investors in a loss position are in the convex (risk-seeking) region of the value function and therefore escalate their position to gamble back to break-even. Activation is triggered by a -5% loss threshold; intensity scales with loss depth.
- **LossAversion / Loss Averse Investor**: **Summary**: Implements Kahneman & Tversky's (1979) loss-aversion coefficient lambda = 2.25 in position-management decisions. Sells winners quickly at a small gain threshold and clings to losers far longer due to the asymmetric loss-pain multiplier.

## Consolidated Financial Theory

- Sells winners too early, holds losers too long -- Prospect Theory asymmetry.
- Theoretical basis: Shefrin & Statman (1985); Kahneman & Tversky (1979).
- LLM-driven disposition-biased investor -- sells winners early, holds losers. Theory: simulation-bases.md Section 4.1.
- Hybrid rule+LLM disposition-biased investor -- Prospect Theory rules embedded. Theory: simulation-bases.md Section 4.1.
- Disposition Effect Investor (Prospect Theory).
- Behavior:
- - Sells winners quickly (gain_threshold ~10%)
- - Holds losers stubbornly (loss_threshold ~30%)
- Theory: simulation-bases.md Section 4.1 -- DispositionInvestor
- Theoretical basis: Kahneman & Tversky (1979) Prospect Theory; asymmetric gain/loss treatment with lambda = 2.25.
- LLM-driven extreme loss-averse investor -- very reluctant to realize losses. Theory: simulation-bases.md Section 4.1.
- Hybrid rule+LLM extreme loss-averse investor -- high lambda rules embedded. Theory: simulation-bases.md Section 4.1.
- Has access to Prospect Theory and behavioral finance literature
- through RAG, but still exhibits disposition effect tendencies
- Theoretical basis: Kahneman & Tversky (1979) Prospect Theory; RAG retrieves disposition effect studies.
- Theoretical basis: Prospect Theory loss aversion; RAG retrieves loss-aversion and disposition-effect studies.
- Theory: simulation-bases.md Section 4.1 -- EndowedHolder
- Theoretical basis: Kahneman, Knetsch & Thaler (1990) endowment effect; ownership
- LLM-driven endowed holder -- attachment bias suppresses selling via LLM reasoning. Theory: simulation-bases.md Section 4.1.
- RuleLLM endowed holder -- ownership premium suppresses selling below threshold. Theory: simulation-bases.md Section 4.1.
- RAG-augmented endowed holder -- ownership premium with historical ownership bias literature. Theory: simulation-bases.md Section 4.1.
- Theory: simulation-bases.md Section 4.2 -- StatusQuoSeller
- Theoretical basis: Samuelson & Zeckhauser (1988) status quo bias; inertia
- LLM-driven status-quo-biased seller -- inertia and loss aversion modeled via LLM. Theory: simulation-bases.md Section 4.2.
- RuleLLM status-quo-biased seller -- inertia rules require large premium before selling. Theory: simulation-bases.md Section 4.2.
- RAG-augmented status quo seller -- inertia-driven holding with status quo bias literature. Theory: simulation-bases.md Section 4.2.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AnchoringEffect | Disposition Trader | [AnchoringEffect__DispositionTrader.md](../AnchoringEffect__DispositionTrader.md) |
| DispositionEffect | Disposition Biased | [DispositionEffect__DispositionBiased.md](../DispositionEffect__DispositionBiased.md) |
| DispositionEffect | Disposition Investor | [DispositionEffect__DispositionInvestor.md](../DispositionEffect__DispositionInvestor.md) |
| DispositionEffect | Loss Averse | [DispositionEffect__LossAverse.md](../DispositionEffect__LossAverse.md) |
| DispositionEffect | Rag Disposition Investor | [DispositionEffect__RagDispositionInvestor.md](../DispositionEffect__RagDispositionInvestor.md) |
| DispositionEffect | Rag Loss Averse | [DispositionEffect__RagLossAverse.md](../DispositionEffect__RagLossAverse.md) |
| EndowmentEffect | Endowed Holder | [EndowmentEffect__EndowedHolder.md](../EndowmentEffect__EndowedHolder.md) |
| EndowmentEffect | Status Quo Seller | [EndowmentEffect__StatusQuoSeller.md](../EndowmentEffect__StatusQuoSeller.md) |
| EquityPremium | Myopic Loss Averse | [EquityPremium__MyopicLossAverse.md](../EquityPremium__MyopicLossAverse.md) |
| EquityPremium | Myopic Loss Averse Investor | [EquityPremium__MyopicLossAverseInvestor.md](../EquityPremium__MyopicLossAverseInvestor.md) |
| LossAversion | Break Even Trader | [LossAversion__BreakEvenTrader.md](../LossAversion__BreakEvenTrader.md) |
| LossAversion | Loss Averse Investor | [LossAversion__LossAverseInvestor.md](../LossAversion__LossAverseInvestor.md) |

