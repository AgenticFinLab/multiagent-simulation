# Noise traders and uninformed liquidity participants

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Noise traders and uninformed liquidity participants |
| Merged profiles | 28 |
| Scenarios | AnchoringEffect, AsianFinancialCrisis, AssetBubble, AvailabilityBias, BlackMonday1987, CarryTradeUnwind, ConfirmationBias, CreditCycle, CurrencyCrisis, EndowmentEffect, EquityPremium, FlashCrash2010, FramingEffect, GamblerFallacy, HerdEffect, HerdingInformation, HindsightBias, LiquidityDryup, MentalAccounting, OverconfidenceBias, RepresentativenessBias, ReversalEffect, SorosPound, SouthSeaBubble, StatusQuoBias, SunkCostFallacy, TulipMania, VolatilityClustering |
| Observed names | Noise Trader |

## Consolidated Definition and Goals

- **AnchoringEffect / Noise Trader**: NoiseTrader represents the uninformed retail participant who trades on impulse, rumour, and random sentiment rather than any systematic signal. In the AnchoringEffect simulation, NoiseTrader serves a specific design purpose: it prevents anchoring-induced mispricings from being too "clean" (perfect exponential decay), adds realistic background volatility, and provides liquidity that allows other agents to execute their strategies. NoiseTrader's random direction means its aggregate effect on mean pricing is near zero, but its high trade volume (100-500 shares vs. 20 shares for other agents) means it has disproportionate short-term price impact.
- **AsianFinancialCrisis / Noise Trader**: NoiseTrader represents uninformed retail FX speculators and random order flow participants who trade on impulse, rumour, and random sentiment rather than any systematic signal. In the AsianFinancialCrisis simulation, NoiseTrader serves a specific design purpose: it prevents crisis-driven mispricings from following overly smooth paths, adds realistic background volatility consistent with emerging-market FX noise, and provides liquidity that allows other agents to execute their strategies. NoiseTrader's random direction means its aggregate effect on mean pricing is near zero, but its activity rate (`trade_probability = 0.30`) is higher than in developed-market scenarios, reflecting the elevated noise in crisis-era EM currency markets.
- **AssetBubble / Noise Trader**: - **Citation**: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703-738. https://doi.org/10.1086/261703 - **Core Insight**: Uninformed traders acting on noise (sentiment, rumour, trend extrapolation) create systematic and persistent deviations from fundamental value. Their irrational behaviour introduces a risk that rational arbitrageurs cannot diversify away -- if sentiment becomes more bullish, mispricings can widen, causing rational arbitrageurs to lose money before the eventual correction. This "noise trader risk" is itself a cost that limits arbitrage and sustains bubbles. - **Mathematical Formulation**: ``` total_sentiment(t) = random_noise(t) + herding_weight x price_return(t) x 10 where random_noise ~ N(0, sentiment_volatility²)
- **AvailabilityBias / Noise Trader**: The NoiseTrader is a random, uninformed participant whose trades are unconnected to any market signal -- fundamental or cognitive bias. In the availability bias context, the NoiseTrader models background retail investors who trade based on personal liquidity needs, random news interpretation, or behavioral impulses unrelated to either fundamentals or the specific availability heuristic being studied. Its primary role is to ensure the simulation does not converge to a perfectly deterministic price path, enabling meaningful statistical analysis across runs.
- **BlackMonday1987 / Noise Trader**: The NoiseTrader represents the heterogeneous mass of retail investors and smaller institutions who trade on perceived signals, rumors, or emotional reactions rather than systematic strategies. On October 19, 1987, retail participation was a small fraction of total volume (dominated by institutional program trading), but retail traders contributed to the liquidity drought by withdrawing buy-side orders. The NoiseTrader's role in the simulation is to add stochastic variation to net demand -- preventing the simulation from converging to a perfectly deterministic cascade and ensuring variance across simulation runs that is necessary for meaningful statistical analysis.
- **CarryTradeUnwind / Noise Trader**: The NoiseTrader provides background FX order flow -- representing importers, exporters, portfolio managers, and retail FX participants whose trades are unconnected to carry trade positioning. In FX markets, non-speculative flow accounts for approximately 60-70% of daily volume, providing the liquidity that makes carry trades executable. trade_probability = 0.30 is calibrated to a higher value than BlackMonday1987 (0.05) because FX markets have substantially more non-speculative background activity.
- **ConfirmationBias / Noise Trader**: Random, uninformed background trader -- provides stochastic variation and background liquidity. Identical design to other behavioral bias simulations.
- **CreditCycle / Noise Trader**: **4.5.1 Economic Role**: Random, uninformed trader whose orders are independent of credit cycle fundamentals.
- **CurrencyCrisis / Noise Trader**: **4.5.1 Economic Role**: Random, uninformed FX trader whose orders are independent of crisis dynamics.
- **EndowmentEffect / Noise Trader**: An uninformed random trader who provides background volume and prevents the market from being trivially predictable. Embodies noise trading theory.
- **EquityPremium / Noise Trader**: **Information set**: `stock_price` (used only for portfolio constraint)
- **FlashCrash2010 / Noise Trader**: **Role:** Uninformed background participant.
- **FramingEffect / Noise Trader**: **Summary**: The NoiseTrader provides baseline random liquidity, trading 30% of rounds with 100-500 shares in a random direction. Its role is to prevent determinism and occasionally amplify framing-induced moves (noise trader risk per De Long et al., 1990), increasing the uncertainty faced by rational agents and thereby reducing their optimal position sizes (consistent with Section 2 Theory 3).
- **GamblerFallacy / Noise Trader**: **Summary**: Random uninformed trader providing baseline liquidity. Activates with 30% probability each round, trading 100-500 shares in a random direction. Critical role: noise trader's random buys and sells create apparent "streaks" in short price sequences that activate the gambler's fallacy and hot-hand beliefs in Section 4.1 and Section 4.2, making this agent the indirect trigger of the phenomenon.
- **HerdEffect / Noise Trader**: **Summary**: Implements De Long et al. (1990) noise trader risk model. Random bid price near market; mean-reverting quantity. Stochastic trigger for emergent herding -- accidental herd initiator.
- **HerdingInformation / Noise Trader**: **Summary**: Implements Black (1986) noise trader model. Random direction with configurable trade probability. Background liquidity provider -- can accidentally trigger CascadeFollower's cascade_count via random price deviations.
- **HindsightBias / Noise Trader**: **Summary**: Implements Black (1986) uninformed noise trading -- the agent trades randomly with no fundamental signal, providing baseline liquidity and ensuring non-trivial price volatility even in the absence of bias agents.
- **LiquidityDryup / Noise Trader**: **Summary**: Submits random Gaussian order flow that provides baseline liquidity and masks informed trading signals. During a dry-up, noise trading is the only source of trading volume when market makers withdraw, but its random direction provides no stabilising force.

## Consolidated Financial Theory

- Theoretical basis: simulation-bases.md Section 2.6 (Black, 1986 -- Noise Trader Risk).
- Decision rule (simulation-bases.md Section 4.5 -- Rule-Based Behavior):
- LLM-driven noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5 -- NoiseTrader.
- RuleLLM noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5 -- NoiseTrader.
- RAG-augmented noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5 -- NoiseTrader.
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical Basis: Noise trader model (Black, 1986)
- LLM-driven noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5.
- RuleLLM noise trader with explicit trade probability rules. Theory: simulation-bases.md Section 4.5.
- RAG-augmented noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5.
- Noise trader driven by sentiment and crowd behavior.
- Theory: simulation-bases.md Section 4.3 -- NoiseTrader
- Theory: De Long et al. (1990) - Noise Trader Risk
- Behavior:
- - Trades based on "sentiment" (random with bias)
- - Tends to follow recent price direction (herding)
- - Can amplify bubbles by joining buying frenzy
- - Sentiment can flip, causing sudden selling
- Effect: DESTABILIZING - Amplifies bubbles through herding
- Formula:
- -> simulation-bases.md Section 4.3 -- NoiseTrader (Rule-Based Behavior)
- Hybrid sentiment rules with LLM reasoning. Theory: simulation-bases.md Section 4.3 -- NoiseTrader.
- RAG-augmented sentiment rules with retrieved knowledge. Theory: simulation-bases.md Section 4.3 -- NoiseTrader.
- Theoretical basis: Black (1986) -- Noise traders.
- RuleLLM noise trader -- uninformed random participant. Theory: simulation-bases.md Section 4.5.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AnchoringEffect | Noise Trader | [AnchoringEffect__NoiseTrader.md](../AnchoringEffect__NoiseTrader.md) |
| AsianFinancialCrisis | Noise Trader | [AsianFinancialCrisis__NoiseTrader.md](../AsianFinancialCrisis__NoiseTrader.md) |
| AssetBubble | Noise Trader | [AssetBubble__NoiseTrader.md](../AssetBubble__NoiseTrader.md) |
| AvailabilityBias | Noise Trader | [AvailabilityBias__NoiseTrader.md](../AvailabilityBias__NoiseTrader.md) |
| BlackMonday1987 | Noise Trader | [BlackMonday1987__NoiseTrader.md](../BlackMonday1987__NoiseTrader.md) |
| CarryTradeUnwind | Noise Trader | [CarryTradeUnwind__NoiseTrader.md](../CarryTradeUnwind__NoiseTrader.md) |
| ConfirmationBias | Noise Trader | [ConfirmationBias__NoiseTrader.md](../ConfirmationBias__NoiseTrader.md) |
| CreditCycle | Noise Trader | [CreditCycle__NoiseTrader.md](../CreditCycle__NoiseTrader.md) |
| CurrencyCrisis | Noise Trader | [CurrencyCrisis__NoiseTrader.md](../CurrencyCrisis__NoiseTrader.md) |
| EndowmentEffect | Noise Trader | [EndowmentEffect__NoiseTrader.md](../EndowmentEffect__NoiseTrader.md) |
| EquityPremium | Noise Trader | [EquityPremium__NoiseTrader.md](../EquityPremium__NoiseTrader.md) |
| FlashCrash2010 | Noise Trader | [FlashCrash2010__NoiseTrader.md](../FlashCrash2010__NoiseTrader.md) |
| FramingEffect | Noise Trader | [FramingEffect__NoiseTrader.md](../FramingEffect__NoiseTrader.md) |
| GamblerFallacy | Noise Trader | [GamblerFallacy__NoiseTrader.md](../GamblerFallacy__NoiseTrader.md) |
| HerdEffect | Noise Trader | [HerdEffect__NoiseTrader.md](../HerdEffect__NoiseTrader.md) |
| HerdingInformation | Noise Trader | [HerdingInformation__NoiseTrader.md](../HerdingInformation__NoiseTrader.md) |
| HindsightBias | Noise Trader | [HindsightBias__NoiseTrader.md](../HindsightBias__NoiseTrader.md) |
| LiquidityDryup | Noise Trader | [LiquidityDryup__NoiseTrader.md](../LiquidityDryup__NoiseTrader.md) |
| MentalAccounting | Noise Trader | [MentalAccounting__NoiseTrader.md](../MentalAccounting__NoiseTrader.md) |
| OverconfidenceBias | Noise Trader | [OverconfidenceBias__NoiseTrader.md](../OverconfidenceBias__NoiseTrader.md) |
| RepresentativenessBias | Noise Trader | [RepresentativenessBias__NoiseTrader.md](../RepresentativenessBias__NoiseTrader.md) |
| ReversalEffect | Noise Trader | [ReversalEffect__NoiseTrader.md](../ReversalEffect__NoiseTrader.md) |
| SorosPound | Noise Trader | [SorosPound__NoiseTrader.md](../SorosPound__NoiseTrader.md) |
| SouthSeaBubble | Noise Trader | [SouthSeaBubble__NoiseTrader.md](../SouthSeaBubble__NoiseTrader.md) |
| StatusQuoBias | Noise Trader | [StatusQuoBias__NoiseTrader.md](../StatusQuoBias__NoiseTrader.md) |
| SunkCostFallacy | Noise Trader | [SunkCostFallacy__NoiseTrader.md](../SunkCostFallacy__NoiseTrader.md) |
| TulipMania | Noise Trader | [TulipMania__NoiseTrader.md](../TulipMania__NoiseTrader.md) |
| VolatilityClustering | Noise Trader | [VolatilityClustering__NoiseTrader.md](../VolatilityClustering__NoiseTrader.md) |

