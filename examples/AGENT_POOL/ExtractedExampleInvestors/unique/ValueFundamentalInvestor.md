# Value, fundamental, distressed, and bottom-fishing investors

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Value, fundamental, distressed, and bottom-fishing investors |
| Merged profiles | 23 |
| Scenarios | AnchoringEffect, AsianFinancialCrisis, AssetBubble, AvailabilityBias, BlackMonday1987, CreditCycle, CurrencyCrisis, DotComBubble, FlashCrash, FlashCrash2010, GFC2008, GameStopShortSqueeze, LUNACollapse, LiquidityDryup, MarketCrash, MomentumEffect, ReversalEffect, ShortSqueeze, TulipMania, VolatilityClustering |
| Observed names | Bottom Fisher, Distressed Buyer, Fundamental Analyst, Fundamental Anchor, Fundamental Hedger, Fundamental Investor, Fundamental Trader, Fundamentalist, Institutional Value, Intrinsic Value Trader, Skeptical Value Investor, Value Buyer, Value Contrarian, Value Investor, Value Trader |

## Consolidated Definition and Goals

- **AnchoringEffect / Fundamental Analyst**: FundamentalAnalyst represents the institutional investor who knows the true fundamental value exists but incorporates it only gradually -- modelling the conservatism bias documented by Barberis, Shleifer & Vishny (1998). Unlike RationalUpdater (who uses F directly with no delay), FundamentalAnalyst maintains a `belief` that exponentially smooths toward F at rate lambda_b = 0.05 per round. This means it takes approximately 40-60 rounds for FundamentalAnalyst's belief to converge within 90% of the true fundamental. The result is a gradually strengthening correction force that is weak early in the simulation (when anchoring dominates) but increasingly effective in later rounds -- modelling how institutional research slowly incorporates new information.
- **AsianFinancialCrisis / Value Contrarian**: ValueContrarian represents the private-sector fundamental investor who seeks to exploit deep crisis-driven discounts to fundamental value. This agent models long-horizon institutional investors -- hedge funds, sovereign wealth funds, private equity -- who are willing to buy assets during crisis but require a larger discount than the IMF (which has sovereign backing and can tolerate lower expected returns). ValueContrarian provides the second layer of price floor support after IMFRescuer and eventually profits from crisis recovery.
- **AssetBubble / Fundamental Investor**: FundamentalInvestor represents the patient, value-oriented long-term investor who anchors decisions to intrinsic value and acts infrequently, modelling the discipline of institutional value managers (Graham, Buffett tradition). This agent is intentionally slow-reacting -- it trades only every 5 rounds -- which means it cannot prevent bubble formation in the short term but provides a persistent, low-frequency anchoring force. In the long run, FundamentalInvestor is the agent most likely to outperform if the simulation is run long enough for prices to revert to fundamental.
- **AssetBubble / Value Investor**: LLM value investor. Theory: simulation-bases.md Section 4.4 -- FundamentalInvestor.
- **AvailabilityBias / Value Trader**: The ValueTrader is a patient, fundamental-focused investor who trades only when the price-fundamental gap is large enough to represent a clear margin of safety. Unlike the SystematicAnalyst (who responds to 3% deviations), the ValueTrader requires a 5% deviation before acting -- a higher bar that ensures it is not distracted by the smallest noise-level mispricings. The ValueTrader embodies Graham's value investing discipline applied to a market distorted by cognitive bias: it waits for bias-driven overreaction to create meaningful bargains (deviation < -5%) or clear overvaluation (deviation > +5%) and then acts with fixed position sizing.
- **BlackMonday1987 / Value Investor**: The ValueInvestor is a patient institutional buyer -- modeled on Graham-style value investing as practiced by firms like Berkshire Hathaway -- who stands ready to buy when prices fall significantly below intrinsic value. The ValueInvestor's defining characteristic is the margin of safety: a predetermined discount to fundamental value (15% below fair value) below which equities are considered attractively priced regardless of near-term momentum. The ValueInvestor is the simulation's sole stabilizing force during the crash: when deviation crosses -0.15, it begins absorbing the supply from portfolio insurers and program traders, providing the price floor that prevents complete market collapse.
- **CreditCycle / Value Investor**: **4.4.1 Economic Role**: Fundamental-value anchor who buys undervalued and sells overvalued credit assets.
- **CurrencyCrisis / Fundamental Hedger**: **4.4.1 Economic Role**: Hedger who trades based on fundamental value, not speculative expectations.
- **DotComBubble / Skeptical Value Investor**: Fundamental investor that sells extreme overvaluation and buys post-crash undervaluation. It is stabilizing but can be early.
- **FlashCrash / Fundamental Trader**: **Role:** Value buyer; provides the recovery force.
- **FlashCrash2010 / Fundamental Trader**: **Role:** Value-based contrarian; stabilising and recovery force.
- **GFC2008 / Distressed Buyer**: `DistressedBuyer` represents capital prepared to buy deeply discounted structured-credit assets after forced selling. It is stabilizing but activates only after severe discounts.
- **GameStopShortSqueeze / Institutional Value**: `InstitutionalValue` represents a fundamental investor that sells into extreme overvaluation. It is the main stabilizing seller, but its inventory is finite.
- **LUNACollapse / Value Buyer**: **Summary**: A contrarian buyer that attempts to buy deep discounts but is often too small to stop the spiral.
- **LiquidityDryup / Value Investor**: Momentum-style LLM investor using the legacy class name. Theory: simulation-bases.md Section 4.4
- **LiquidityDryup / Value Trader**: **Summary**: Fundamental-anchored investor who buys when price is below fundamental and sells when above, providing stabilising liquidity when market prices deviate significantly. During a dry-up, `ValueTrader` acts as the last line of defence against extreme price dislocation.
- **MarketCrash / Bottom Fisher**: **Summary**: A contrarian buyer that enters after large discounts. **Theoretical and Empirical Basis**: Contrarian and value demand can absorb forced sales after large deviations. **Design Purpose**: Test whether opportunistic capital stabilizes the crash. **Behavioral Framework**: Uses crash-buy threshold, discount threshold, buy size, and lookback window. **Decision Process**: Wait until price is sufficiently discounted or recent returns indicate a crash; then submit buy orders subject to cash constraints. **Worked Numerical Example**: If price is 15% below fundamental and the discount threshold is 10%, the agent submits a buy order of the configured size. **Academic References**: Lakonishok, Shleifer, and Vishny (1994, DOI: 10.1111/j.1540-6261.1994.tb04772.x).
- **MomentumEffect / Fundamental Anchor**: **Summary**: Trades against mispricing relative to fundamental value. **Theoretical and Empirical Basis**: Fundamental-value anchoring and limits of arbitrage. **Design Purpose**: Provide long-run gravity against trend overshoot. **Behavioral Framework**: Rule uses `value_threshold=0.05`, `scale=1.5`, `max_position=50.0`. **Decision Process**: Buy undervaluation and sell overvaluation once mispricing exceeds threshold. **Worked Numerical Example**: Price 8% below fundamental triggers a buy. **Academic References**: Shleifer and Vishny (1997), DOI: 10.1111/j.1540-6261.1997.tb03807.x.

## Consolidated Financial Theory

- Theoretical basis: Barberis, Shleifer & Vishny (1998); Shleifer & Vishny (1997).
- Theory: simulation-bases.md Section 4.4 -- ValueContrarian
- Theoretical Basis: Contrarian crisis investing (Radelet & Sachs, 1998 baseline)
- LLM-driven value contrarian -- buys oversold crisis assets. Theory: simulation-bases.md Section 4.4.
- RuleLLM value contrarian with explicit oversold/overbought threshold rules. Theory: simulation-bases.md Section 4.4.
- RAG-augmented value contrarian -- buys oversold crisis assets. Theory: simulation-bases.md Section 4.4.
- Theory: simulation-bases.md Section 4.4 -- FundamentalInvestor
- Theory: Traditional value investing
- Behavior:
- - Compares price to fundamental value
- - Buys undervalued, sells overvalued
- - Very patient, trades slowly
- - Provides weak anchoring force
- Effect: WEAKLY STABILIZING - Too slow to prevent bubbles
- Formula:
- -> simulation-bases.md Section 4.4 -- FundamentalInvestor (Rule-Based Behavior)
- LLM value investor. Theory: simulation-bases.md Section 4.4 -- FundamentalInvestor.
- Hybrid value rules with LLM reasoning. Theory: simulation-bases.md Section 4.4 -- FundamentalInvestor.
- RAG-augmented value rules with retrieved knowledge. Theory: simulation-bases.md Section 4.4 -- FundamentalInvestor.
- Theory: simulation-bases.md Section 4.4 -- ValueTrader
- Theoretical basis: Graham (1949); Baker & Wurgler (2007) -- Value investing discipline.
- LLM-driven value trader -- fundamentals only, ignores media narratives. Theory: simulation-bases.md Section 4.4.
- RuleLLM value trader -- fundamentals only, ignores media narratives. Theory: simulation-bases.md Section 4.4.
- RAG-augmented value trader -- fundamentals only. Theory: simulation-bases.md Section 4.4.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AnchoringEffect | Fundamental Analyst | [AnchoringEffect__FundamentalAnalyst.md](../AnchoringEffect__FundamentalAnalyst.md) |
| AsianFinancialCrisis | Value Contrarian | [AsianFinancialCrisis__ValueContrarian.md](../AsianFinancialCrisis__ValueContrarian.md) |
| AssetBubble | Fundamental Investor | [AssetBubble__FundamentalInvestor.md](../AssetBubble__FundamentalInvestor.md) |
| AssetBubble | Value Investor | [AssetBubble__ValueInvestor.md](../AssetBubble__ValueInvestor.md) |
| AvailabilityBias | Value Trader | [AvailabilityBias__ValueTrader.md](../AvailabilityBias__ValueTrader.md) |
| BlackMonday1987 | Value Investor | [BlackMonday1987__ValueInvestor.md](../BlackMonday1987__ValueInvestor.md) |
| CreditCycle | Value Investor | [CreditCycle__ValueInvestor.md](../CreditCycle__ValueInvestor.md) |
| CurrencyCrisis | Fundamental Hedger | [CurrencyCrisis__FundamentalHedger.md](../CurrencyCrisis__FundamentalHedger.md) |
| DotComBubble | Skeptical Value Investor | [DotComBubble__SkepticalValueInvestor.md](../DotComBubble__SkepticalValueInvestor.md) |
| FlashCrash | Fundamental Trader | [FlashCrash__FundamentalTrader.md](../FlashCrash__FundamentalTrader.md) |
| FlashCrash2010 | Fundamental Trader | [FlashCrash2010__FundamentalTrader.md](../FlashCrash2010__FundamentalTrader.md) |
| GFC2008 | Distressed Buyer | [GFC2008__DistressedBuyer.md](../GFC2008__DistressedBuyer.md) |
| GameStopShortSqueeze | Institutional Value | [GameStopShortSqueeze__InstitutionalValue.md](../GameStopShortSqueeze__InstitutionalValue.md) |
| LUNACollapse | Value Buyer | [LUNACollapse__ValueBuyer.md](../LUNACollapse__ValueBuyer.md) |
| LiquidityDryup | Value Investor | [LiquidityDryup__ValueInvestor.md](../LiquidityDryup__ValueInvestor.md) |
| LiquidityDryup | Value Trader | [LiquidityDryup__ValueTrader.md](../LiquidityDryup__ValueTrader.md) |
| MarketCrash | Bottom Fisher | [MarketCrash__BottomFisher.md](../MarketCrash__BottomFisher.md) |
| MomentumEffect | Fundamental Anchor | [MomentumEffect__FundamentalAnchor.md](../MomentumEffect__FundamentalAnchor.md) |
| MomentumEffect | Fundamental Trader | [MomentumEffect__FundamentalTrader.md](../MomentumEffect__FundamentalTrader.md) |
| ReversalEffect | Value Investor | [ReversalEffect__ValueInvestor.md](../ReversalEffect__ValueInvestor.md) |
| ShortSqueeze | Value Investor | [ShortSqueeze__ValueInvestor.md](../ShortSqueeze__ValueInvestor.md) |
| TulipMania | Intrinsic Value Trader | [TulipMania__IntrinsicValueTrader.md](../TulipMania__IntrinsicValueTrader.md) |
| VolatilityClustering | Fundamentalist | [VolatilityClustering__Fundamentalist.md](../VolatilityClustering__Fundamentalist.md) |

