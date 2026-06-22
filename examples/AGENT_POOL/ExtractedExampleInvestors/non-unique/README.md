# Investment Agent Catalog

This folder was generated from the current repository by scanning `configs/*/*/players.yml` and `examples/*/*/players.py`.

- Agent profiles: 261
- Scenarios covered: 45
- Scope: configured non-coordinator agents with `role: player`.
- Grouping rule: `scenario + class name after removing LLM/RuleLLM/RagLLM prefix`, so Rule, LLM, RuleLLM, and Rag variants are merged where they share an archetype.
- Note: `EchoChamber` and `RumorSpread` are social-propagation scenarios, so their participants are marked as non-financial/social rather than ordinary investment agents.

## Scenario Counts

| Scenario | Agent profiles |
| --- | --- |
| AnchoringEffect | 9 |
| ArchegosCollapse | 5 |
| AsianFinancialCrisis | 5 |
| AssetBubble | 10 |
| AvailabilityBias | 5 |
| BlackMonday1987 | 5 |
| CarryTradeUnwind | 5 |
| ConfirmationBias | 5 |
| CreditCycle | 5 |
| CurrencyCrisis | 5 |
| DispositionEffect | 12 |
| DotComBubble | 5 |
| EchoChamber | 6 |
| EndowmentEffect | 5 |
| EquityPremium | 10 |
| EuropeanDebtCrisis | 5 |
| FlashCrash | 7 |
| FlashCrash2010 | 5 |
| FramingEffect | 5 |
| GFC2008 | 5 |
| GamblerFallacy | 5 |
| GameStopShortSqueeze | 5 |
| HerdEffect | 5 |
| HerdingInformation | 5 |
| HindsightBias | 5 |
| LTCMCollapse | 5 |
| LUNACollapse | 5 |
| LiquidityDryup | 9 |
| LossAversion | 5 |
| MarketCrash | 7 |
| MentalAccounting | 5 |
| MomentumEffect | 8 |
| OverconfidenceBias | 5 |
| RepresentativenessBias | 5 |
| ReversalEffect | 7 |
| RumorSpread | 5 |
| SVBBankRun | 5 |
| ShortSqueeze | 6 |
| SorosPound | 5 |
| SouthSeaBubble | 5 |
| StatusQuoBias | 5 |
| SunkCostFallacy | 5 |
| TulipMania | 5 |
| VolatilityClustering | 5 |
| Volmageddon | 5 |

## Agent Index

| Scenario | Agent | Category | Mechanisms | File |
| --- | --- | --- | --- | --- |
| AnchoringEffect | Anchored Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [AnchoringEffect__AnchoredTrader.md](AnchoringEffect__AnchoredTrader.md) |
| AnchoringEffect | Contrarian Trader | Financial/investment | Rule | [AnchoringEffect__ContrarianTrader.md](AnchoringEffect__ContrarianTrader.md) |
| AnchoringEffect | Disposition Trader | Financial/investment | Rule | [AnchoringEffect__DispositionTrader.md](AnchoringEffect__DispositionTrader.md) |
| AnchoringEffect | Fundamental Analyst | Financial/investment | Rule | [AnchoringEffect__FundamentalAnalyst.md](AnchoringEffect__FundamentalAnalyst.md) |
| AnchoringEffect | Historical Anchor | Financial/investment | Rule, LLM, RuleLLM, Rag | [AnchoringEffect__HistoricalAnchor.md](AnchoringEffect__HistoricalAnchor.md) |
| AnchoringEffect | Liquidity Provider | Financial/investment | Rule | [AnchoringEffect__LiquidityProvider.md](AnchoringEffect__LiquidityProvider.md) |
| AnchoringEffect | Momentum Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [AnchoringEffect__MomentumTrader.md](AnchoringEffect__MomentumTrader.md) |
| AnchoringEffect | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [AnchoringEffect__NoiseTrader.md](AnchoringEffect__NoiseTrader.md) |
| AnchoringEffect | Rational Updater | Financial/investment | Rule, LLM, RuleLLM, Rag | [AnchoringEffect__RationalUpdater.md](AnchoringEffect__RationalUpdater.md) |
| ArchegosCollapse | Block Trade Buyer | Financial/investment | Rule, LLM, RuleLLM, Rag | [ArchegosCollapse__BlockTradeBuyer.md](ArchegosCollapse__BlockTradeBuyer.md) |
| ArchegosCollapse | Concentrated Fund | Financial/investment | Rule, LLM, RuleLLM, Rag | [ArchegosCollapse__ConcentratedFund.md](ArchegosCollapse__ConcentratedFund.md) |
| ArchegosCollapse | Information Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [ArchegosCollapse__InformationTrader.md](ArchegosCollapse__InformationTrader.md) |
| ArchegosCollapse | Prime Broker 1 | Financial/investment | Rule, LLM, RuleLLM, Rag | [ArchegosCollapse__PrimeBroker1.md](ArchegosCollapse__PrimeBroker1.md) |
| ArchegosCollapse | Prime Broker 2 | Financial/investment | Rule, LLM, RuleLLM, Rag | [ArchegosCollapse__PrimeBroker2.md](ArchegosCollapse__PrimeBroker2.md) |
| AsianFinancialCrisis | Contagion Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [AsianFinancialCrisis__ContagionTrader.md](AsianFinancialCrisis__ContagionTrader.md) |
| AsianFinancialCrisis | Hot Money Funder | Financial/investment | Rule, LLM, RuleLLM, Rag | [AsianFinancialCrisis__HotMoneyFunder.md](AsianFinancialCrisis__HotMoneyFunder.md) |
| AsianFinancialCrisis | IMF Rescuer | Financial/investment | Rule, LLM, RuleLLM, Rag | [AsianFinancialCrisis__IMFRescuer.md](AsianFinancialCrisis__IMFRescuer.md) |
| AsianFinancialCrisis | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [AsianFinancialCrisis__NoiseTrader.md](AsianFinancialCrisis__NoiseTrader.md) |
| AsianFinancialCrisis | Value Contrarian | Financial/investment | Rule, LLM, RuleLLM, Rag | [AsianFinancialCrisis__ValueContrarian.md](AsianFinancialCrisis__ValueContrarian.md) |
| AssetBubble | Conservative Holder | Financial/investment | Rule, LLM, RuleLLM, Rag | [AssetBubble__ConservativeHolder.md](AssetBubble__ConservativeHolder.md) |
| AssetBubble | Fundamental Investor | Financial/investment | Rule | [AssetBubble__FundamentalInvestor.md](AssetBubble__FundamentalInvestor.md) |
| AssetBubble | Greater Fool Speculator | Financial/investment | LLM | [AssetBubble__GreaterFoolSpeculator.md](AssetBubble__GreaterFoolSpeculator.md) |
| AssetBubble | Leveraged Buyer | Financial/investment | Rule, RuleLLM, Rag | [AssetBubble__LeveragedBuyer.md](AssetBubble__LeveragedBuyer.md) |
| AssetBubble | Leveraged Speculator | Financial/investment | LLM | [AssetBubble__LeveragedSpeculator.md](AssetBubble__LeveragedSpeculator.md) |
| AssetBubble | Momentum Speculator | Financial/investment | Rule, RuleLLM, Rag | [AssetBubble__MomentumSpeculator.md](AssetBubble__MomentumSpeculator.md) |
| AssetBubble | Noise Trader | Financial/investment | Rule, RuleLLM, Rag | [AssetBubble__NoiseTrader.md](AssetBubble__NoiseTrader.md) |
| AssetBubble | Rational Arbitrageur | Financial/investment | Rule, LLM, RuleLLM, Rag | [AssetBubble__RationalArbitrageur.md](AssetBubble__RationalArbitrageur.md) |
| AssetBubble | Sentiment Trader | Financial/investment | LLM | [AssetBubble__SentimentTrader.md](AssetBubble__SentimentTrader.md) |
| AssetBubble | Value Investor | Financial/investment | LLM, RuleLLM, Rag | [AssetBubble__ValueInvestor.md](AssetBubble__ValueInvestor.md) |
| AvailabilityBias | Media Influenced Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [AvailabilityBias__MediaInfluencedTrader.md](AvailabilityBias__MediaInfluencedTrader.md) |
| AvailabilityBias | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [AvailabilityBias__NoiseTrader.md](AvailabilityBias__NoiseTrader.md) |
| AvailabilityBias | Recent Event Overweighter | Financial/investment | Rule, LLM, RuleLLM, Rag | [AvailabilityBias__RecentEventOverweighter.md](AvailabilityBias__RecentEventOverweighter.md) |
| AvailabilityBias | Systematic Analyst | Financial/investment | Rule, LLM, RuleLLM, Rag | [AvailabilityBias__SystematicAnalyst.md](AvailabilityBias__SystematicAnalyst.md) |
| AvailabilityBias | Value Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [AvailabilityBias__ValueTrader.md](AvailabilityBias__ValueTrader.md) |
| BlackMonday1987 | Index Arbitrageur | Financial/investment | Rule, LLM, RuleLLM, Rag | [BlackMonday1987__IndexArbitrageur.md](BlackMonday1987__IndexArbitrageur.md) |
| BlackMonday1987 | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [BlackMonday1987__NoiseTrader.md](BlackMonday1987__NoiseTrader.md) |
| BlackMonday1987 | Portfolio Insurer | Financial/investment | Rule, LLM, RuleLLM, Rag | [BlackMonday1987__PortfolioInsurer.md](BlackMonday1987__PortfolioInsurer.md) |
| BlackMonday1987 | Program Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [BlackMonday1987__ProgramTrader.md](BlackMonday1987__ProgramTrader.md) |
| BlackMonday1987 | Value Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [BlackMonday1987__ValueInvestor.md](BlackMonday1987__ValueInvestor.md) |
| CarryTradeUnwind | Carry Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [CarryTradeUnwind__CarryTrader.md](CarryTradeUnwind__CarryTrader.md) |
| CarryTradeUnwind | Funding Currency Buyer | Financial/investment | Rule, LLM, RuleLLM, Rag | [CarryTradeUnwind__FundingCurrencyBuyer.md](CarryTradeUnwind__FundingCurrencyBuyer.md) |
| CarryTradeUnwind | Hedged Carry Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [CarryTradeUnwind__HedgedCarryTrader.md](CarryTradeUnwind__HedgedCarryTrader.md) |
| CarryTradeUnwind | Leveraged Carry Fund | Financial/investment | Rule, LLM, RuleLLM, Rag | [CarryTradeUnwind__LeveragedCarryFund.md](CarryTradeUnwind__LeveragedCarryFund.md) |
| CarryTradeUnwind | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [CarryTradeUnwind__NoiseTrader.md](CarryTradeUnwind__NoiseTrader.md) |
| ConfirmationBias | Balanced Analyst | Financial/investment | Rule, LLM, RuleLLM, Rag | [ConfirmationBias__BalancedAnalyst.md](ConfirmationBias__BalancedAnalyst.md) |
| ConfirmationBias | Belief Anchor | Financial/investment | Rule, LLM, RuleLLM, Rag | [ConfirmationBias__BeliefAnchor.md](ConfirmationBias__BeliefAnchor.md) |
| ConfirmationBias | Contrarian Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [ConfirmationBias__ContrarianTrader.md](ConfirmationBias__ContrarianTrader.md) |
| ConfirmationBias | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [ConfirmationBias__NoiseTrader.md](ConfirmationBias__NoiseTrader.md) |
| ConfirmationBias | Selective Scanner | Financial/investment | Rule, LLM, RuleLLM, Rag | [ConfirmationBias__SelectiveScanner.md](ConfirmationBias__SelectiveScanner.md) |
| CreditCycle | Counter Cyclical Lender | Financial/investment | Rule, LLM, RuleLLM, Rag | [CreditCycle__CounterCyclicalLender.md](CreditCycle__CounterCyclicalLender.md) |
| CreditCycle | Minsky Borrower | Financial/investment | Rule, LLM, RuleLLM, Rag | [CreditCycle__MinskyBorrower.md](CreditCycle__MinskyBorrower.md) |
| CreditCycle | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [CreditCycle__NoiseTrader.md](CreditCycle__NoiseTrader.md) |
| CreditCycle | Pro Cyclical Lender | Financial/investment | Rule, LLM, RuleLLM, Rag | [CreditCycle__ProCyclicalLender.md](CreditCycle__ProCyclicalLender.md) |
| CreditCycle | Value Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [CreditCycle__ValueInvestor.md](CreditCycle__ValueInvestor.md) |
| CurrencyCrisis | Central Bank Defender | Financial/investment | Rule, LLM, RuleLLM, Rag | [CurrencyCrisis__CentralBankDefender.md](CurrencyCrisis__CentralBankDefender.md) |
| CurrencyCrisis | Fundamental Hedger | Financial/investment | Rule, LLM, RuleLLM, Rag | [CurrencyCrisis__FundamentalHedger.md](CurrencyCrisis__FundamentalHedger.md) |
| CurrencyCrisis | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [CurrencyCrisis__NoiseTrader.md](CurrencyCrisis__NoiseTrader.md) |
| CurrencyCrisis | Self Fulfilling Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [CurrencyCrisis__SelfFulfillingTrader.md](CurrencyCrisis__SelfFulfillingTrader.md) |
| CurrencyCrisis | Speculative Attacker | Financial/investment | Rule, LLM, RuleLLM, Rag | [CurrencyCrisis__SpeculativeAttacker.md](CurrencyCrisis__SpeculativeAttacker.md) |
| DispositionEffect | Disposition Biased | Financial/investment | LLM, RuleLLM | [DispositionEffect__DispositionBiased.md](DispositionEffect__DispositionBiased.md) |
| DispositionEffect | Disposition Investor | Financial/investment | Rule | [DispositionEffect__DispositionInvestor.md](DispositionEffect__DispositionInvestor.md) |
| DispositionEffect | Index Holder | Financial/investment | Rule | [DispositionEffect__IndexHolder.md](DispositionEffect__IndexHolder.md) |
| DispositionEffect | Institutional Investor | Financial/investment | Rule, LLM, RuleLLM | [DispositionEffect__InstitutionalInvestor.md](DispositionEffect__InstitutionalInvestor.md) |
| DispositionEffect | Loss Averse | Financial/investment | LLM, RuleLLM | [DispositionEffect__LossAverse.md](DispositionEffect__LossAverse.md) |
| DispositionEffect | Rag Disposition Investor | Financial/investment | Rag | [DispositionEffect__RagDispositionInvestor.md](DispositionEffect__RagDispositionInvestor.md) |
| DispositionEffect | Rag Institutional Investor | Financial/investment | Rag | [DispositionEffect__RagInstitutionalInvestor.md](DispositionEffect__RagInstitutionalInvestor.md) |
| DispositionEffect | Rag Loss Averse | Financial/investment | Rag | [DispositionEffect__RagLossAverse.md](DispositionEffect__RagLossAverse.md) |
| DispositionEffect | Rag Rational Investor | Financial/investment | Rag | [DispositionEffect__RagRationalInvestor.md](DispositionEffect__RagRationalInvestor.md) |
| DispositionEffect | Rag Tax Aware Investor | Financial/investment | Rag | [DispositionEffect__RagTaxAwareInvestor.md](DispositionEffect__RagTaxAwareInvestor.md) |
| DispositionEffect | Rational Investor | Financial/investment | Rule, LLM, RuleLLM | [DispositionEffect__RationalInvestor.md](DispositionEffect__RationalInvestor.md) |
| DispositionEffect | Tax Aware Investor | Financial/investment | Rule, LLM, RuleLLM | [DispositionEffect__TaxAwareInvestor.md](DispositionEffect__TaxAwareInvestor.md) |
| DotComBubble | IPO Flipper | Financial/investment | Rule, LLM, RuleLLM, Rag | [DotComBubble__IPOFlipper.md](DotComBubble__IPOFlipper.md) |
| DotComBubble | Momentum Follower | Financial/investment | Rule, LLM, RuleLLM, Rag | [DotComBubble__MomentumFollower.md](DotComBubble__MomentumFollower.md) |
| DotComBubble | New Economy Evangelist | Financial/investment | Rule, LLM, RuleLLM, Rag | [DotComBubble__NewEconomyEvangelist.md](DotComBubble__NewEconomyEvangelist.md) |
| DotComBubble | Short Seller | Financial/investment | Rule, LLM, RuleLLM, Rag | [DotComBubble__ShortSeller.md](DotComBubble__ShortSeller.md) |
| DotComBubble | Skeptical Value Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [DotComBubble__SkepticalValueInvestor.md](DotComBubble__SkepticalValueInvestor.md) |
| EchoChamber | Bridge Builder | Non-financial/social | Rule, LLM, RuleLLM, Rag | [EchoChamber__BridgeBuilder.md](EchoChamber__BridgeBuilder.md) |
| EchoChamber | Conformist | Non-financial/social | Rule, LLM, RuleLLM, Rag | [EchoChamber__Conformist.md](EchoChamber__Conformist.md) |
| EchoChamber | Critical Thinker | Non-financial/social | Rule, LLM, RuleLLM, Rag | [EchoChamber__CriticalThinker.md](EchoChamber__CriticalThinker.md) |
| EchoChamber | Ideologue | Non-financial/social | Rule, LLM, RuleLLM, Rag | [EchoChamber__Ideologue.md](EchoChamber__Ideologue.md) |
| EchoChamber | Passive Bystander | Non-financial/social | LLM | [EchoChamber__PassiveBystander.md](EchoChamber__PassiveBystander.md) |
| EchoChamber | Passive Follower | Non-financial/social | Rule, RuleLLM, Rag | [EchoChamber__PassiveFollower.md](EchoChamber__PassiveFollower.md) |
| EndowmentEffect | Endowed Holder | Financial/investment | Rule, LLM, RuleLLM, Rag | [EndowmentEffect__EndowedHolder.md](EndowmentEffect__EndowedHolder.md) |
| EndowmentEffect | New Buyer | Financial/investment | Rule, LLM, RuleLLM, Rag | [EndowmentEffect__NewBuyer.md](EndowmentEffect__NewBuyer.md) |
| EndowmentEffect | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [EndowmentEffect__NoiseTrader.md](EndowmentEffect__NoiseTrader.md) |
| EndowmentEffect | Rational Arbitrageur | Financial/investment | Rule, LLM, RuleLLM, Rag | [EndowmentEffect__RationalArbitrageur.md](EndowmentEffect__RationalArbitrageur.md) |
| EndowmentEffect | Status Quo Seller | Financial/investment | Rule, LLM, RuleLLM, Rag | [EndowmentEffect__StatusQuoSeller.md](EndowmentEffect__StatusQuoSeller.md) |
| EquityPremium | Conservative Investor | Financial/investment | Rule | [EquityPremium__ConservativeInvestor.md](EquityPremium__ConservativeInvestor.md) |
| EquityPremium | Institutional Investor | Financial/investment | LLM, RuleLLM, Rag | [EquityPremium__InstitutionalInvestor.md](EquityPremium__InstitutionalInvestor.md) |
| EquityPremium | Long Horizon Investor | Financial/investment | Rule | [EquityPremium__LongHorizonInvestor.md](EquityPremium__LongHorizonInvestor.md) |
| EquityPremium | Long Term Investor | Financial/investment | LLM, RuleLLM, Rag | [EquityPremium__LongTermInvestor.md](EquityPremium__LongTermInvestor.md) |
| EquityPremium | Myopic Loss Averse | Financial/investment | LLM, RuleLLM, Rag | [EquityPremium__MyopicLossAverse.md](EquityPremium__MyopicLossAverse.md) |
| EquityPremium | Myopic Loss Averse Investor | Financial/investment | Rule | [EquityPremium__MyopicLossAverseInvestor.md](EquityPremium__MyopicLossAverseInvestor.md) |
| EquityPremium | Noise Trader | Financial/investment | Rule | [EquityPremium__NoiseTrader.md](EquityPremium__NoiseTrader.md) |
| EquityPremium | Rational Optimizer | Financial/investment | LLM, RuleLLM, Rag | [EquityPremium__RationalOptimizer.md](EquityPremium__RationalOptimizer.md) |
| EquityPremium | Risk Averse Saver | Financial/investment | LLM, RuleLLM, Rag | [EquityPremium__RiskAverseSaver.md](EquityPremium__RiskAverseSaver.md) |
| EquityPremium | Risk Neutral Investor | Financial/investment | Rule | [EquityPremium__RiskNeutralInvestor.md](EquityPremium__RiskNeutralInvestor.md) |
| EuropeanDebtCrisis | Core Bond Buyer | Financial/investment | Rule, LLM, RuleLLM, Rag | [EuropeanDebtCrisis__CoreBondBuyer.md](EuropeanDebtCrisis__CoreBondBuyer.md) |
| EuropeanDebtCrisis | Creditor Panicker | Financial/investment | Rule, LLM, RuleLLM, Rag | [EuropeanDebtCrisis__CreditorPanicker.md](EuropeanDebtCrisis__CreditorPanicker.md) |
| EuropeanDebtCrisis | ECB Intervenor | Financial/investment | Rule, LLM, RuleLLM, Rag | [EuropeanDebtCrisis__ECBIntervenor.md](EuropeanDebtCrisis__ECBIntervenor.md) |
| EuropeanDebtCrisis | Hedged Fund | Financial/investment | Rule, LLM, RuleLLM, Rag | [EuropeanDebtCrisis__HedgedFund.md](EuropeanDebtCrisis__HedgedFund.md) |
| EuropeanDebtCrisis | Periphery Bond Seller | Financial/investment | Rule, LLM, RuleLLM, Rag | [EuropeanDebtCrisis__PeripheryBondSeller.md](EuropeanDebtCrisis__PeripheryBondSeller.md) |
| FlashCrash | Algorithmic Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [FlashCrash__AlgorithmicTrader.md](FlashCrash__AlgorithmicTrader.md) |
| FlashCrash | Flash Market Maker | Financial/investment | LLM | [FlashCrash__FlashMarketMaker.md](FlashCrash__FlashMarketMaker.md) |
| FlashCrash | Fundamental Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [FlashCrash__FundamentalTrader.md](FlashCrash__FundamentalTrader.md) |
| FlashCrash | High Frequency Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [FlashCrash__HighFrequencyTrader.md](FlashCrash__HighFrequencyTrader.md) |
| FlashCrash | Market Maker | Financial/investment | Rule, RuleLLM, Rag | [FlashCrash__MarketMaker.md](FlashCrash__MarketMaker.md) |
| FlashCrash | Retail Trader | Financial/investment | Rule | [FlashCrash__RetailTrader.md](FlashCrash__RetailTrader.md) |
| FlashCrash | Stop Loss Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [FlashCrash__StopLossTrader.md](FlashCrash__StopLossTrader.md) |
| FlashCrash2010 | Fundamental Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [FlashCrash2010__FundamentalTrader.md](FlashCrash2010__FundamentalTrader.md) |
| FlashCrash2010 | HFT Market Maker | Financial/investment | Rule, LLM, RuleLLM, Rag | [FlashCrash2010__HFTMarketMaker.md](FlashCrash2010__HFTMarketMaker.md) |
| FlashCrash2010 | Momentum Chaser | Financial/investment | Rule, LLM, RuleLLM, Rag | [FlashCrash2010__MomentumChaser.md](FlashCrash2010__MomentumChaser.md) |
| FlashCrash2010 | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [FlashCrash2010__NoiseTrader.md](FlashCrash2010__NoiseTrader.md) |
| FlashCrash2010 | Stop Loss Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [FlashCrash2010__StopLossTrader.md](FlashCrash2010__StopLossTrader.md) |
| FramingEffect | Arbitrage Framer | Financial/investment | Rule, LLM, RuleLLM, Rag | [FramingEffect__ArbitrageFramer.md](FramingEffect__ArbitrageFramer.md) |
| FramingEffect | Frame Invariant Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [FramingEffect__FrameInvariantTrader.md](FramingEffect__FrameInvariantTrader.md) |
| FramingEffect | Gain Frame Follower | Financial/investment | Rule, LLM, RuleLLM, Rag | [FramingEffect__GainFrameFollower.md](FramingEffect__GainFrameFollower.md) |
| FramingEffect | Loss Frame Reactor | Financial/investment | Rule, LLM, RuleLLM, Rag | [FramingEffect__LossFrameReactor.md](FramingEffect__LossFrameReactor.md) |
| FramingEffect | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [FramingEffect__NoiseTrader.md](FramingEffect__NoiseTrader.md) |
| GFC2008 | Distressed Buyer | Financial/investment | Rule, LLM, RuleLLM, Rag | [GFC2008__DistressedBuyer.md](GFC2008__DistressedBuyer.md) |
| GFC2008 | Leveraged Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [GFC2008__LeveragedInvestor.md](GFC2008__LeveragedInvestor.md) |
| GFC2008 | MBS Originator | Financial/investment | Rule, LLM, RuleLLM, Rag | [GFC2008__MBSOriginator.md](GFC2008__MBSOriginator.md) |
| GFC2008 | Rating Agency | Financial/investment | Rule, LLM, RuleLLM, Rag | [GFC2008__RatingAgency.md](GFC2008__RatingAgency.md) |
| GFC2008 | Regulator | Financial/investment | Rule, LLM, RuleLLM, Rag | [GFC2008__Regulator.md](GFC2008__Regulator.md) |
| GamblerFallacy | Arbitrageur | Financial/investment | Rule, LLM, RuleLLM, Rag | [GamblerFallacy__Arbitrageur.md](GamblerFallacy__Arbitrageur.md) |
| GamblerFallacy | Hot Hand Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [GamblerFallacy__HotHandTrader.md](GamblerFallacy__HotHandTrader.md) |
| GamblerFallacy | Independent Assessor | Financial/investment | Rule, LLM, RuleLLM, Rag | [GamblerFallacy__IndependentAssessor.md](GamblerFallacy__IndependentAssessor.md) |
| GamblerFallacy | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [GamblerFallacy__NoiseTrader.md](GamblerFallacy__NoiseTrader.md) |
| GamblerFallacy | Streak Reversal Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [GamblerFallacy__StreakReversalTrader.md](GamblerFallacy__StreakReversalTrader.md) |
| GameStopShortSqueeze | Institutional Value | Financial/investment | Rule, LLM, RuleLLM, Rag | [GameStopShortSqueeze__InstitutionalValue.md](GameStopShortSqueeze__InstitutionalValue.md) |
| GameStopShortSqueeze | Market Maker Gamma | Financial/investment | Rule, LLM, RuleLLM, Rag | [GameStopShortSqueeze__MarketMakerGamma.md](GameStopShortSqueeze__MarketMakerGamma.md) |
| GameStopShortSqueeze | Momentum Retail | Financial/investment | Rule, LLM, RuleLLM, Rag | [GameStopShortSqueeze__MomentumRetail.md](GameStopShortSqueeze__MomentumRetail.md) |
| GameStopShortSqueeze | Retail Coordinated | Financial/investment | Rule, LLM, RuleLLM, Rag | [GameStopShortSqueeze__RetailCoordinated.md](GameStopShortSqueeze__RetailCoordinated.md) |
| GameStopShortSqueeze | Short Seller HF | Financial/investment | Rule, LLM, RuleLLM, Rag | [GameStopShortSqueeze__ShortSellerHF.md](GameStopShortSqueeze__ShortSellerHF.md) |
| HerdEffect | Aggressive Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [HerdEffect__AggressiveInvestor.md](HerdEffect__AggressiveInvestor.md) |
| HerdEffect | Contrarian Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [HerdEffect__ContrarianInvestor.md](HerdEffect__ContrarianInvestor.md) |
| HerdEffect | Momentum Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [HerdEffect__MomentumInvestor.md](HerdEffect__MomentumInvestor.md) |
| HerdEffect | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [HerdEffect__NoiseTrader.md](HerdEffect__NoiseTrader.md) |
| HerdEffect | Risk Averse Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [HerdEffect__RiskAverseInvestor.md](HerdEffect__RiskAverseInvestor.md) |
| HerdingInformation | Cascade Follower | Financial/investment | Rule, LLM, RuleLLM, Rag | [HerdingInformation__CascadeFollower.md](HerdingInformation__CascadeFollower.md) |
| HerdingInformation | Contrarian | Financial/investment | Rule, LLM, RuleLLM, Rag | [HerdingInformation__Contrarian.md](HerdingInformation__Contrarian.md) |
| HerdingInformation | Independent Thinker | Financial/investment | Rule, LLM, RuleLLM, Rag | [HerdingInformation__IndependentThinker.md](HerdingInformation__IndependentThinker.md) |
| HerdingInformation | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [HerdingInformation__NoiseTrader.md](HerdingInformation__NoiseTrader.md) |
| HerdingInformation | Reputation Herder | Financial/investment | Rule, LLM, RuleLLM, Rag | [HerdingInformation__ReputationHerder.md](HerdingInformation__ReputationHerder.md) |
| HindsightBias | Contrarian Skeptic | Financial/investment | Rule, LLM, RuleLLM, Rag | [HindsightBias__ContrarianSkeptic.md](HindsightBias__ContrarianSkeptic.md) |
| HindsightBias | Hindsight Overconfident | Financial/investment | Rule, LLM, RuleLLM, Rag | [HindsightBias__HindsightOverconfident.md](HindsightBias__HindsightOverconfident.md) |
| HindsightBias | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [HindsightBias__NoiseTrader.md](HindsightBias__NoiseTrader.md) |
| HindsightBias | Outcome Learner | Financial/investment | Rule, LLM, RuleLLM, Rag | [HindsightBias__OutcomeLearner.md](HindsightBias__OutcomeLearner.md) |
| HindsightBias | Process Evaluator | Financial/investment | Rule, LLM, RuleLLM, Rag | [HindsightBias__ProcessEvaluator.md](HindsightBias__ProcessEvaluator.md) |
| LTCMCollapse | Central Bank | Financial/investment | Rule, LLM, RuleLLM, Rag | [LTCMCollapse__CentralBank.md](LTCMCollapse__CentralBank.md) |
| LTCMCollapse | Convergence Arbitrageur | Financial/investment | Rule, LLM, RuleLLM, Rag | [LTCMCollapse__ConvergenceArbitrageur.md](LTCMCollapse__ConvergenceArbitrageur.md) |
| LTCMCollapse | Leverage Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [LTCMCollapse__LeverageTrader.md](LTCMCollapse__LeverageTrader.md) |
| LTCMCollapse | Liquidity Provider | Financial/investment | Rule, LLM, RuleLLM, Rag | [LTCMCollapse__LiquidityProvider.md](LTCMCollapse__LiquidityProvider.md) |
| LTCMCollapse | Risk Manager | Financial/investment | Rule, LLM, RuleLLM, Rag | [LTCMCollapse__RiskManager.md](LTCMCollapse__RiskManager.md) |
| LUNACollapse | Anchor Depositor | Financial/investment | Rule, LLM, RuleLLM, Rag | [LUNACollapse__AnchorDepositor.md](LUNACollapse__AnchorDepositor.md) |
| LUNACollapse | Arbitrageur | Financial/investment | Rule, LLM, RuleLLM, Rag | [LUNACollapse__Arbitrageur.md](LUNACollapse__Arbitrageur.md) |
| LUNACollapse | De Fi Lender | Financial/investment | Rule, LLM, RuleLLM, Rag | [LUNACollapse__DeFiLender.md](LUNACollapse__DeFiLender.md) |
| LUNACollapse | Stablecoin Holder | Financial/investment | Rule, LLM, RuleLLM, Rag | [LUNACollapse__StablecoinHolder.md](LUNACollapse__StablecoinHolder.md) |
| LUNACollapse | Value Buyer | Financial/investment | Rule, LLM, RuleLLM, Rag | [LUNACollapse__ValueBuyer.md](LUNACollapse__ValueBuyer.md) |
| LiquidityDryup | Arbitrageur | Financial/investment | LLM, RuleLLM, Rag | [LiquidityDryup__Arbitrageur.md](LiquidityDryup__Arbitrageur.md) |
| LiquidityDryup | Forced Seller | Financial/investment | LLM, RuleLLM, Rag | [LiquidityDryup__ForcedSeller.md](LiquidityDryup__ForcedSeller.md) |
| LiquidityDryup | Liquidity Demander | Financial/investment | LLM, RuleLLM, Rag | [LiquidityDryup__LiquidityDemander.md](LiquidityDryup__LiquidityDemander.md) |
| LiquidityDryup | Liquidity Seeker | Financial/investment | Rule | [LiquidityDryup__LiquiditySeeker.md](LiquidityDryup__LiquiditySeeker.md) |
| LiquidityDryup | Market Maker | Financial/investment | Rule, LLM, RuleLLM, Rag | [LiquidityDryup__MarketMaker.md](LiquidityDryup__MarketMaker.md) |
| LiquidityDryup | Momentum Trader | Financial/investment | Rule | [LiquidityDryup__MomentumTrader.md](LiquidityDryup__MomentumTrader.md) |
| LiquidityDryup | Noise Trader | Financial/investment | Rule | [LiquidityDryup__NoiseTrader.md](LiquidityDryup__NoiseTrader.md) |
| LiquidityDryup | Value Investor | Financial/investment | LLM, RuleLLM, Rag | [LiquidityDryup__ValueInvestor.md](LiquidityDryup__ValueInvestor.md) |
| LiquidityDryup | Value Trader | Financial/investment | Rule | [LiquidityDryup__ValueTrader.md](LiquidityDryup__ValueTrader.md) |
| LossAversion | Break Even Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [LossAversion__BreakEvenTrader.md](LossAversion__BreakEvenTrader.md) |
| LossAversion | Loss Averse Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [LossAversion__LossAverseInvestor.md](LossAversion__LossAverseInvestor.md) |
| LossAversion | Market Maker | Financial/investment | Rule, LLM, RuleLLM, Rag | [LossAversion__MarketMaker.md](LossAversion__MarketMaker.md) |
| LossAversion | Momentum Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [LossAversion__MomentumTrader.md](LossAversion__MomentumTrader.md) |
| LossAversion | Rational Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [LossAversion__RationalTrader.md](LossAversion__RationalTrader.md) |
| MarketCrash | Bottom Fisher | Financial/investment | Rule, LLM, RuleLLM, Rag | [MarketCrash__BottomFisher.md](MarketCrash__BottomFisher.md) |
| MarketCrash | Leveraged Fund | Financial/investment | LLM, RuleLLM, Rag | [MarketCrash__LeveragedFund.md](MarketCrash__LeveragedFund.md) |
| MarketCrash | Leveraged Hedge Fund | Financial/investment | Rule | [MarketCrash__LeveragedHedgeFund.md](MarketCrash__LeveragedHedgeFund.md) |
| MarketCrash | Market Maker | Financial/investment | Rule, LLM, RuleLLM, Rag | [MarketCrash__MarketMaker.md](MarketCrash__MarketMaker.md) |
| MarketCrash | Panic Seller | Financial/investment | Rule, LLM, RuleLLM, Rag | [MarketCrash__PanicSeller.md](MarketCrash__PanicSeller.md) |
| MarketCrash | Passive Investor | Financial/investment | Rule | [MarketCrash__PassiveInvestor.md](MarketCrash__PassiveInvestor.md) |
| MarketCrash | Risk Parity Fund | Financial/investment | Rule, LLM, RuleLLM, Rag | [MarketCrash__RiskParityFund.md](MarketCrash__RiskParityFund.md) |
| MentalAccounting | House Money Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [MentalAccounting__HouseMoneyTrader.md](MentalAccounting__HouseMoneyTrader.md) |
| MentalAccounting | Mental Accountant | Financial/investment | Rule, LLM, RuleLLM, Rag | [MentalAccounting__MentalAccountant.md](MentalAccounting__MentalAccountant.md) |
| MentalAccounting | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [MentalAccounting__NoiseTrader.md](MentalAccounting__NoiseTrader.md) |
| MentalAccounting | Rational Portfolio Manager | Financial/investment | Rule, LLM, RuleLLM, Rag | [MentalAccounting__RationalPortfolioManager.md](MentalAccounting__RationalPortfolioManager.md) |
| MentalAccounting | Sunk Cost Holder | Financial/investment | Rule, LLM, RuleLLM, Rag | [MentalAccounting__SunkCostHolder.md](MentalAccounting__SunkCostHolder.md) |
| MomentumEffect | Contrarian Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [MomentumEffect__ContrarianTrader.md](MomentumEffect__ContrarianTrader.md) |
| MomentumEffect | Fundamental Anchor | Financial/investment | LLM, RuleLLM, Rag | [MomentumEffect__FundamentalAnchor.md](MomentumEffect__FundamentalAnchor.md) |
| MomentumEffect | Fundamental Trader | Financial/investment | Rule | [MomentumEffect__FundamentalTrader.md](MomentumEffect__FundamentalTrader.md) |
| MomentumEffect | Index Fund | Financial/investment | Rule | [MomentumEffect__IndexFund.md](MomentumEffect__IndexFund.md) |
| MomentumEffect | Market Maker | Financial/investment | Rule | [MomentumEffect__MarketMaker.md](MomentumEffect__MarketMaker.md) |
| MomentumEffect | Momentum Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [MomentumEffect__MomentumTrader.md](MomentumEffect__MomentumTrader.md) |
| MomentumEffect | Technical Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [MomentumEffect__TechnicalTrader.md](MomentumEffect__TechnicalTrader.md) |
| MomentumEffect | Trend Follower | Financial/investment | LLM, RuleLLM, Rag | [MomentumEffect__TrendFollower.md](MomentumEffect__TrendFollower.md) |
| OverconfidenceBias | Calibrated Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [OverconfidenceBias__CalibratedTrader.md](OverconfidenceBias__CalibratedTrader.md) |
| OverconfidenceBias | Contrarian Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [OverconfidenceBias__ContrarianInvestor.md](OverconfidenceBias__ContrarianInvestor.md) |
| OverconfidenceBias | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [OverconfidenceBias__NoiseTrader.md](OverconfidenceBias__NoiseTrader.md) |
| OverconfidenceBias | Overconfident Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [OverconfidenceBias__OverconfidentTrader.md](OverconfidenceBias__OverconfidentTrader.md) |
| OverconfidenceBias | Self Attributor | Financial/investment | Rule, LLM, RuleLLM, Rag | [OverconfidenceBias__SelfAttributor.md](OverconfidenceBias__SelfAttributor.md) |
| RepresentativenessBias | Bayesian Updater | Financial/investment | Rule, LLM, RuleLLM, Rag | [RepresentativenessBias__BayesianUpdater.md](RepresentativenessBias__BayesianUpdater.md) |
| RepresentativenessBias | Category Overgeneralizer | Financial/investment | Rule, LLM, RuleLLM, Rag | [RepresentativenessBias__CategoryOvergeneralizer.md](RepresentativenessBias__CategoryOvergeneralizer.md) |
| RepresentativenessBias | Contrarian Statistical | Financial/investment | Rule, LLM, RuleLLM, Rag | [RepresentativenessBias__ContrarianStatistical.md](RepresentativenessBias__ContrarianStatistical.md) |
| RepresentativenessBias | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [RepresentativenessBias__NoiseTrader.md](RepresentativenessBias__NoiseTrader.md) |
| RepresentativenessBias | Pattern Matcher | Financial/investment | Rule, LLM, RuleLLM, Rag | [RepresentativenessBias__PatternMatcher.md](RepresentativenessBias__PatternMatcher.md) |
| ReversalEffect | Contrarian Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [ReversalEffect__ContrarianInvestor.md](ReversalEffect__ContrarianInvestor.md) |
| ReversalEffect | Index Tracker | Financial/investment | Rule | [ReversalEffect__IndexTracker.md](ReversalEffect__IndexTracker.md) |
| ReversalEffect | Momentum Chaser | Financial/investment | LLM, RuleLLM, Rag | [ReversalEffect__MomentumChaser.md](ReversalEffect__MomentumChaser.md) |
| ReversalEffect | Momentum Investor | Financial/investment | Rule | [ReversalEffect__MomentumInvestor.md](ReversalEffect__MomentumInvestor.md) |
| ReversalEffect | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [ReversalEffect__NoiseTrader.md](ReversalEffect__NoiseTrader.md) |
| ReversalEffect | Overconfident Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [ReversalEffect__OverconfidentTrader.md](ReversalEffect__OverconfidentTrader.md) |
| ReversalEffect | Value Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [ReversalEffect__ValueInvestor.md](ReversalEffect__ValueInvestor.md) |
| RumorSpread | Distorting Relayer | Non-financial/social | Rule, LLM, RuleLLM, Rag | [RumorSpread__DistortingRelayer.md](RumorSpread__DistortingRelayer.md) |
| RumorSpread | Fact Checker | Non-financial/social | Rule, LLM, RuleLLM, Rag | [RumorSpread__FactChecker.md](RumorSpread__FactChecker.md) |
| RumorSpread | Gullible Spreader | Non-financial/social | Rule, LLM, RuleLLM, Rag | [RumorSpread__GullibleSpreader.md](RumorSpread__GullibleSpreader.md) |
| RumorSpread | Skeptical Evaluator | Non-financial/social | Rule, LLM, RuleLLM, Rag | [RumorSpread__SkepticalEvaluator.md](RumorSpread__SkepticalEvaluator.md) |
| RumorSpread | Uninformed Bystander | Non-financial/social | Rule, LLM, RuleLLM, Rag | [RumorSpread__UninformedBystander.md](RumorSpread__UninformedBystander.md) |
| SVBBankRun | Bank Manager | Financial/investment | Rule, LLM, RuleLLM, Rag | [SVBBankRun__BankManager.md](SVBBankRun__BankManager.md) |
| SVBBankRun | Bond Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [SVBBankRun__BondTrader.md](SVBBankRun__BondTrader.md) |
| SVBBankRun | Depositor | Financial/investment | Rule, LLM, RuleLLM, Rag | [SVBBankRun__Depositor.md](SVBBankRun__Depositor.md) |
| SVBBankRun | Regulator | Financial/investment | Rule, LLM, RuleLLM, Rag | [SVBBankRun__Regulator.md](SVBBankRun__Regulator.md) |
| SVBBankRun | Social Media Influencer | Financial/investment | Rule, LLM, RuleLLM, Rag | [SVBBankRun__SocialMediaInfluencer.md](SVBBankRun__SocialMediaInfluencer.md) |
| ShortSqueeze | Institutional Holder | Financial/investment | Rule, LLM, RuleLLM, Rag | [ShortSqueeze__InstitutionalHolder.md](ShortSqueeze__InstitutionalHolder.md) |
| ShortSqueeze | Momentum Buyer | Financial/investment | Rule, LLM, RuleLLM, Rag | [ShortSqueeze__MomentumBuyer.md](ShortSqueeze__MomentumBuyer.md) |
| ShortSqueeze | Retail Coordinator | Financial/investment | LLM, RuleLLM, Rag | [ShortSqueeze__RetailCoordinator.md](ShortSqueeze__RetailCoordinator.md) |
| ShortSqueeze | Retail Trader | Financial/investment | Rule | [ShortSqueeze__RetailTrader.md](ShortSqueeze__RetailTrader.md) |
| ShortSqueeze | Short Seller | Financial/investment | Rule, LLM, RuleLLM, Rag | [ShortSqueeze__ShortSeller.md](ShortSqueeze__ShortSeller.md) |
| ShortSqueeze | Value Investor | Financial/investment | Rule, LLM, RuleLLM, Rag | [ShortSqueeze__ValueInvestor.md](ShortSqueeze__ValueInvestor.md) |
| SorosPound | Convergence Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [SorosPound__ConvergenceTrader.md](SorosPound__ConvergenceTrader.md) |
| SorosPound | Macro Hedge Fund | Financial/investment | Rule, LLM, RuleLLM, Rag | [SorosPound__MacroHedgeFund.md](SorosPound__MacroHedgeFund.md) |
| SorosPound | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [SorosPound__NoiseTrader.md](SorosPound__NoiseTrader.md) |
| SorosPound | Opportunistic Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [SorosPound__OpportunisticTrader.md](SorosPound__OpportunisticTrader.md) |
| SorosPound | Peg Defender | Financial/investment | Rule, LLM, RuleLLM, Rag | [SorosPound__PegDefender.md](SorosPound__PegDefender.md) |
| SouthSeaBubble | Arbitrageur | Financial/investment | Rule, LLM, RuleLLM, Rag | [SouthSeaBubble__Arbitrageur.md](SouthSeaBubble__Arbitrageur.md) |
| SouthSeaBubble | Insider Advantaged | Financial/investment | Rule, LLM, RuleLLM, Rag | [SouthSeaBubble__InsiderAdvantaged.md](SouthSeaBubble__InsiderAdvantaged.md) |
| SouthSeaBubble | Narrative Believer | Financial/investment | Rule, LLM, RuleLLM, Rag | [SouthSeaBubble__NarrativeBeliever.md](SouthSeaBubble__NarrativeBeliever.md) |
| SouthSeaBubble | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [SouthSeaBubble__NoiseTrader.md](SouthSeaBubble__NoiseTrader.md) |
| SouthSeaBubble | Skeptical Analyst | Financial/investment | Rule, LLM, RuleLLM, Rag | [SouthSeaBubble__SkepticalAnalyst.md](SouthSeaBubble__SkepticalAnalyst.md) |
| StatusQuoBias | Active Rebalancer | Financial/investment | Rule, LLM, RuleLLM, Rag | [StatusQuoBias__ActiveRebalancer.md](StatusQuoBias__ActiveRebalancer.md) |
| StatusQuoBias | Default Follower | Financial/investment | Rule, LLM, RuleLLM, Rag | [StatusQuoBias__DefaultFollower.md](StatusQuoBias__DefaultFollower.md) |
| StatusQuoBias | Inertial Holder | Financial/investment | Rule, LLM, RuleLLM, Rag | [StatusQuoBias__InertialHolder.md](StatusQuoBias__InertialHolder.md) |
| StatusQuoBias | Momentum Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [StatusQuoBias__MomentumTrader.md](StatusQuoBias__MomentumTrader.md) |
| StatusQuoBias | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [StatusQuoBias__NoiseTrader.md](StatusQuoBias__NoiseTrader.md) |
| SunkCostFallacy | Commitment Escalator | Financial/investment | Rule, LLM, RuleLLM, Rag | [SunkCostFallacy__CommitmentEscalator.md](SunkCostFallacy__CommitmentEscalator.md) |
| SunkCostFallacy | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [SunkCostFallacy__NoiseTrader.md](SunkCostFallacy__NoiseTrader.md) |
| SunkCostFallacy | Opportunity Cost Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [SunkCostFallacy__OpportunityCostTrader.md](SunkCostFallacy__OpportunityCostTrader.md) |
| SunkCostFallacy | Rational Cutter | Financial/investment | Rule, LLM, RuleLLM, Rag | [SunkCostFallacy__RationalCutter.md](SunkCostFallacy__RationalCutter.md) |
| SunkCostFallacy | Sunk Cost Holder | Financial/investment | Rule, LLM, RuleLLM, Rag | [SunkCostFallacy__SunkCostHolder.md](SunkCostFallacy__SunkCostHolder.md) |
| TulipMania | Early Exit Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [TulipMania__EarlyExitTrader.md](TulipMania__EarlyExitTrader.md) |
| TulipMania | Intrinsic Value Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [TulipMania__IntrinsicValueTrader.md](TulipMania__IntrinsicValueTrader.md) |
| TulipMania | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [TulipMania__NoiseTrader.md](TulipMania__NoiseTrader.md) |
| TulipMania | Social Proof Follower | Financial/investment | Rule, LLM, RuleLLM, Rag | [TulipMania__SocialProofFollower.md](TulipMania__SocialProofFollower.md) |
| TulipMania | Trend Chaser | Financial/investment | Rule, LLM, RuleLLM, Rag | [TulipMania__TrendChaser.md](TulipMania__TrendChaser.md) |
| VolatilityClustering | Fundamentalist | Financial/investment | Rule, LLM, RuleLLM, Rag | [VolatilityClustering__Fundamentalist.md](VolatilityClustering__Fundamentalist.md) |
| VolatilityClustering | Noise Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [VolatilityClustering__NoiseTrader.md](VolatilityClustering__NoiseTrader.md) |
| VolatilityClustering | Slow Adapter | Financial/investment | Rule, LLM, RuleLLM, Rag | [VolatilityClustering__SlowAdapter.md](VolatilityClustering__SlowAdapter.md) |
| VolatilityClustering | Trend Follower | Financial/investment | Rule, LLM, RuleLLM, Rag | [VolatilityClustering__TrendFollower.md](VolatilityClustering__TrendFollower.md) |
| VolatilityClustering | Volatility Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [VolatilityClustering__VolatilityTrader.md](VolatilityClustering__VolatilityTrader.md) |
| Volmageddon | Equity Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [Volmageddon__EquityTrader.md](Volmageddon__EquityTrader.md) |
| Volmageddon | Long Vol Hedger | Financial/investment | Rule, LLM, RuleLLM, Rag | [Volmageddon__LongVolHedger.md](Volmageddon__LongVolHedger.md) |
| Volmageddon | Short Vol Trader | Financial/investment | Rule, LLM, RuleLLM, Rag | [Volmageddon__ShortVolTrader.md](Volmageddon__ShortVolTrader.md) |
| Volmageddon | Vol Arbitrageur | Financial/investment | Rule, LLM, RuleLLM, Rag | [Volmageddon__VolArbitrageur.md](Volmageddon__VolArbitrageur.md) |
| Volmageddon | Vol ETN Manager | Financial/investment | Rule, LLM, RuleLLM, Rag | [Volmageddon__VolETNManager.md](Volmageddon__VolETNManager.md) |
