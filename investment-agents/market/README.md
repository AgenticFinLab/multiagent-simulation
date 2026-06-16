# Deduplicated Market Agent Catalog

This folder is the market-level, cross-scenario deduplicated view of `investment-agents/`.

- Source scenario-specific profiles: 261
- Deduplicated market archetypes: 29
- Method: each scenario profile was compared by role name, decision behavior, and financial theory, then merged into an existing market archetype when the role was materially similar.
- The original scenario-level files remain one directory up; links in each archetype point back to them.

## Archetype Index

| Market archetype | Merged profiles | Scenarios | File |
| --- | --- | --- | --- |
| Algorithmic, high-frequency, and program-trading agents | 3 | 2 | [AlgorithmicHighFrequencyTrader.md](AlgorithmicHighFrequencyTrader.md) |
| Anchoring and reference-point biased investors | 4 | 3 | [AnchoringBiasInvestor.md](AnchoringBiasInvestor.md) |
| Arbitrage, convergence, and relative-value agents | 11 | 11 | [Arbitrageur.md](Arbitrageur.md) |
| Banking, credit, lending, depositor, broker, and rating agents | 12 | 6 | [BankingCreditAgent.md](BankingCreditAgent.md) |
| Contrarian and reversal-oriented investors | 9 | 9 | [ContrarianReversalInvestor.md](ContrarianReversalInvestor.md) |
| Stablecoin, DeFi, and crypto-market participants | 1 | 1 | [CryptoDeFiAgent.md](CryptoDeFiAgent.md) |
| Framing-effect investors and framing arbitrageurs | 2 | 1 | [FramingEffectTrader.md](FramingEffectTrader.md) |
| Herding, contagion, cascade, reputation, and social-proof agents | 4 | 3 | [HerdingCascadeAgent.md](HerdingCascadeAgent.md) |
| Informed, insider, block-trade, IPO-flipping, and opportunistic traders | 5 | 4 | [InformedOpportunisticTrader.md](InformedOpportunisticTrader.md) |
| Leveraged funds, hedge funds, and concentrated position investors | 10 | 8 | [LeveragedFundInvestor.md](LeveragedFundInvestor.md) |
| Loss-aversion, disposition-effect, and endowment-effect investors | 12 | 5 | [LossAversionDispositionInvestor.md](LossAversionDispositionInvestor.md) |
| Macro, currency, sovereign-bond, and carry-trade agents | 8 | 4 | [MacroCurrencySovereignTrader.md](MacroCurrencySovereignTrader.md) |
| Market makers, liquidity providers, and liquidity demanders | 12 | 9 | [MarketMakerLiquidityAgent.md](MarketMakerLiquidityAgent.md) |
| Mental-accounting, house-money, sunk-cost, and opportunity-cost agents | 6 | 2 | [MentalAccountingSunkCostTrader.md](MentalAccountingSunkCostTrader.md) |
| Momentum, trend-following, and aggressive return-chasing traders | 21 | 15 | [MomentumTrendTrader.md](MomentumTrendTrader.md) |
| Noise traders and uninformed liquidity participants | 28 | 28 | [NoiseTrader.md](NoiseTrader.md) |
| Overconfidence, hindsight, and representativeness-biased traders | 7 | 4 | [OverconfidenceAndRepresentativenessTrader.md](OverconfidenceAndRepresentativenessTrader.md) |
| Panic sellers, forced sellers, early-exit, and stop-loss agents | 5 | 5 | [PanicForcedSeller.md](PanicForcedSeller.md) |
| Passive, institutional, conservative, and long-horizon investors | 12 | 7 | [PassiveInstitutionalLongHorizonInvestor.md](PassiveInstitutionalLongHorizonInvestor.md) |
| Regulators, central banks, policy defenders, and rescue/backstop agents | 7 | 7 | [PolicyBackstopAgent.md](PolicyBackstopAgent.md) |
| Rational, Bayesian, calibrated, skeptical, and systematic analysts | 17 | 16 | [RationalAnalystInvestor.md](RationalAnalystInvestor.md) |
| Rebalancing, default-following, status-quo, and tax-aware investors | 5 | 2 | [RebalancingStatusQuoInvestor.md](RebalancingStatusQuoInvestor.md) |
| Retail, coordinated, and crowd-trading agents | 4 | 3 | [RetailCoordinatedTrader.md](RetailCoordinatedTrader.md) |
| Risk-management, risk-aversion, and portfolio-insurance investors | 6 | 5 | [RiskManagementInvestor.md](RiskManagementInvestor.md) |
| Sentiment, narrative, media, and selective-attention traders | 7 | 6 | [SentimentNarrativeTrader.md](SentimentNarrativeTrader.md) |
| Short sellers and short-volatility traders | 4 | 4 | [ShortSellerAndShortVolTrader.md](ShortSellerAndShortVolTrader.md) |
| Non-financial social information participants | 11 | 2 | [SocialInformationAgents.md](SocialInformationAgents.md) |
| Value, fundamental, distressed, and bottom-fishing investors | 23 | 20 | [ValueFundamentalInvestor.md](ValueFundamentalInvestor.md) |
| Volatility-product, volatility-management, and equity de-risking agents | 5 | 2 | [VolatilityProductTrader.md](VolatilityProductTrader.md) |

## Largest Merges

| Market archetype | Merged profiles | Example scenario agents |
| --- | --- | --- |
| Noise traders and uninformed liquidity participants | 28 | AnchoringEffect/Noise Trader, AsianFinancialCrisis/Noise Trader, AssetBubble/Noise Trader, AvailabilityBias/Noise Trader, BlackMonday1987/Noise Trader, CarryTradeUnwind/Noise Trader, ConfirmationBias/Noise Trader, CreditCycle/Noise Trader |
| Value, fundamental, distressed, and bottom-fishing investors | 23 | AnchoringEffect/Fundamental Analyst, AsianFinancialCrisis/Value Contrarian, AssetBubble/Fundamental Investor, AssetBubble/Value Investor, AvailabilityBias/Value Trader, BlackMonday1987/Value Investor, CreditCycle/Value Investor, CurrencyCrisis/Fundamental Hedger |
| Momentum, trend-following, and aggressive return-chasing traders | 21 | AnchoringEffect/Momentum Trader, AssetBubble/Greater Fool Speculator, AssetBubble/Momentum Speculator, DotComBubble/Momentum Follower, FlashCrash2010/Momentum Chaser, GamblerFallacy/Hot Hand Trader, GamblerFallacy/Streak Reversal Trader, GameStopShortSqueeze/Momentum Retail |
| Rational, Bayesian, calibrated, skeptical, and systematic analysts | 17 | AnchoringEffect/Rational Updater, AvailabilityBias/Systematic Analyst, ConfirmationBias/Balanced Analyst, DispositionEffect/Rag Rational Investor, DispositionEffect/Rational Investor, EndowmentEffect/New Buyer, EquityPremium/Rational Optimizer, FramingEffect/Frame Invariant Trader |
| Loss-aversion, disposition-effect, and endowment-effect investors | 12 | AnchoringEffect/Disposition Trader, DispositionEffect/Disposition Biased, DispositionEffect/Disposition Investor, DispositionEffect/Loss Averse, DispositionEffect/Rag Disposition Investor, DispositionEffect/Rag Loss Averse, EndowmentEffect/Endowed Holder, EndowmentEffect/Status Quo Seller |
| Market makers, liquidity providers, and liquidity demanders | 12 | AnchoringEffect/Liquidity Provider, FlashCrash/Flash Market Maker, FlashCrash/Market Maker, FlashCrash2010/HFT Market Maker, GameStopShortSqueeze/Market Maker Gamma, LTCMCollapse/Liquidity Provider, LiquidityDryup/Liquidity Demander, LiquidityDryup/Liquidity Seeker |
| Banking, credit, lending, depositor, broker, and rating agents | 12 | ArchegosCollapse/Prime Broker 1, ArchegosCollapse/Prime Broker 2, CreditCycle/Counter Cyclical Lender, CreditCycle/Minsky Borrower, CreditCycle/Pro Cyclical Lender, EuropeanDebtCrisis/Creditor Panicker, GFC2008/MBS Originator, GFC2008/Rating Agency |
| Passive, institutional, conservative, and long-horizon investors | 12 | AssetBubble/Conservative Holder, DispositionEffect/Index Holder, DispositionEffect/Institutional Investor, DispositionEffect/Rag Institutional Investor, EquityPremium/Conservative Investor, EquityPremium/Institutional Investor, EquityPremium/Long Horizon Investor, EquityPremium/Long Term Investor |
| Arbitrage, convergence, and relative-value agents | 11 | AssetBubble/Rational Arbitrageur, BlackMonday1987/Index Arbitrageur, EndowmentEffect/Rational Arbitrageur, FramingEffect/Arbitrage Framer, GamblerFallacy/Arbitrageur, LTCMCollapse/Convergence Arbitrageur, LUNACollapse/Arbitrageur, LiquidityDryup/Arbitrageur |
| Non-financial social information participants | 11 | EchoChamber/Bridge Builder, EchoChamber/Conformist, EchoChamber/Critical Thinker, EchoChamber/Ideologue, EchoChamber/Passive Bystander, EchoChamber/Passive Follower, RumorSpread/Distorting Relayer, RumorSpread/Fact Checker |
| Leveraged funds, hedge funds, and concentrated position investors | 10 | ArchegosCollapse/Concentrated Fund, AssetBubble/Leveraged Buyer, AssetBubble/Leveraged Speculator, CarryTradeUnwind/Leveraged Carry Fund, EuropeanDebtCrisis/Hedged Fund, GFC2008/Leveraged Investor, LTCMCollapse/Leverage Trader, MarketCrash/Leveraged Fund |
| Contrarian and reversal-oriented investors | 9 | AnchoringEffect/Contrarian Trader, ConfirmationBias/Contrarian Trader, HerdEffect/Contrarian Investor, HerdingInformation/Contrarian, HindsightBias/Contrarian Skeptic, MomentumEffect/Contrarian Trader, OverconfidenceBias/Contrarian Investor, RepresentativenessBias/Contrarian Statistical |
| Macro, currency, sovereign-bond, and carry-trade agents | 8 | AsianFinancialCrisis/Hot Money Funder, CarryTradeUnwind/Carry Trader, CarryTradeUnwind/Funding Currency Buyer, CarryTradeUnwind/Hedged Carry Trader, CurrencyCrisis/Self Fulfilling Trader, CurrencyCrisis/Speculative Attacker, EuropeanDebtCrisis/Core Bond Buyer, EuropeanDebtCrisis/Periphery Bond Seller |
| Regulators, central banks, policy defenders, and rescue/backstop agents | 7 | AsianFinancialCrisis/IMF Rescuer, CurrencyCrisis/Central Bank Defender, EuropeanDebtCrisis/ECB Intervenor, GFC2008/Regulator, LTCMCollapse/Central Bank, SVBBankRun/Regulator, SorosPound/Peg Defender |
| Sentiment, narrative, media, and selective-attention traders | 7 | AssetBubble/Sentiment Trader, AvailabilityBias/Media Influenced Trader, AvailabilityBias/Recent Event Overweighter, ConfirmationBias/Selective Scanner, DotComBubble/New Economy Evangelist, SVBBankRun/Social Media Influencer, SouthSeaBubble/Narrative Believer |
| Overconfidence, hindsight, and representativeness-biased traders | 7 | HindsightBias/Hindsight Overconfident, HindsightBias/Outcome Learner, OverconfidenceBias/Overconfident Trader, OverconfidenceBias/Self Attributor, RepresentativenessBias/Category Overgeneralizer, RepresentativenessBias/Pattern Matcher, ReversalEffect/Overconfident Trader |
| Risk-management, risk-aversion, and portfolio-insurance investors | 6 | BlackMonday1987/Portfolio Insurer, EquityPremium/Risk Averse Saver, EquityPremium/Risk Neutral Investor, HerdEffect/Risk Averse Investor, LTCMCollapse/Risk Manager, MarketCrash/Risk Parity Fund |
| Mental-accounting, house-money, sunk-cost, and opportunity-cost agents | 6 | MentalAccounting/House Money Trader, MentalAccounting/Mental Accountant, MentalAccounting/Sunk Cost Holder, SunkCostFallacy/Commitment Escalator, SunkCostFallacy/Opportunity Cost Trader, SunkCostFallacy/Sunk Cost Holder |
| Informed, insider, block-trade, IPO-flipping, and opportunistic traders | 5 | ArchegosCollapse/Block Trade Buyer, ArchegosCollapse/Information Trader, DotComBubble/IPO Flipper, SorosPound/Opportunistic Trader, SouthSeaBubble/Insider Advantaged |
| Rebalancing, default-following, status-quo, and tax-aware investors | 5 | DispositionEffect/Rag Tax Aware Investor, DispositionEffect/Tax Aware Investor, StatusQuoBias/Active Rebalancer, StatusQuoBias/Default Follower, StatusQuoBias/Inertial Holder |
