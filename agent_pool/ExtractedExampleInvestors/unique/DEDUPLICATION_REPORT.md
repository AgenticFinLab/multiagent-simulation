# Market Deduplication Check Report

The previous catalog was scenario-specific, so repeated market roles appeared many times. This check created a market-level folder and merged similar agents across scenarios.

| Check | Result |
| --- | --- |
| Original profiles | 261 |
| Market archetypes after deduplication | 29 |
| Profiles merged away as duplicates/similar roles | 232 |
| Largest duplicate family | Noise traders and uninformed liquidity participants: 28 profiles |

## Largest Duplicate Families

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

## Notes

- Similarity was semantic rather than exact string matching. For example, `MomentumSpeculator`, `MomentumTrader`, `TrendFollower`, and `MomentumChaser` are merged into one momentum/trend archetype.
- Some scenario-specific institutional roles remain distinct when their financial function is materially different, such as policy backstops, banking-credit actors, and volatility-product managers.
- `EchoChamber` and `RumorSpread` participants are preserved in a non-financial/social-information archetype rather than mixed into ordinary investment roles.
