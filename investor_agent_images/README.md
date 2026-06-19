# Investor Agent Images

This folder maps each deduplicated investor-agent archetype to one stable, unique avatar image for interface display.

## Files

- `png/`: PNG avatar files, one per deduplicated agent type. Use these as the default interface images.
- `avatars/`: original SVG avatar files, kept as scalable source assets.
- `agent_avatar_map.csv`: tabular mapping for spreadsheet or simple loader use.
- `agent_avatar_map.json`: structured mapping for application code.
- `README.md`: visual preview table.

## Usage Contract

- Use `agent_type` as the stable lookup key.
- Use `image_path` for the default PNG path relative to this folder.
- Use `svg_image_path` if a scalable SVG source is preferred.
- The source profile points back to `agent_pool/ExtractedExampleInvestors/unique/`.

## Avatar Map

| Agent type | Display name | PNG avatar | Source profile |
| --- | --- | --- | --- |
| `AlgorithmicHighFrequencyTrader` | Algorithmic HFT | ![Algorithmic HFT investor avatar](png/AlgorithmicHighFrequencyTrader.png) | [AlgorithmicHighFrequencyTrader.md](../agent_pool/ExtractedExampleInvestors/unique/AlgorithmicHighFrequencyTrader.md) |
| `AnchoringBiasInvestor` | Anchoring Bias | ![Anchoring Bias investor avatar](png/AnchoringBiasInvestor.png) | [AnchoringBiasInvestor.md](../agent_pool/ExtractedExampleInvestors/unique/AnchoringBiasInvestor.md) |
| `Arbitrageur` | Arbitrageur | ![Arbitrageur investor avatar](png/Arbitrageur.png) | [Arbitrageur.md](../agent_pool/ExtractedExampleInvestors/unique/Arbitrageur.md) |
| `BankingCreditAgent` | Banking Credit | ![Banking Credit investor avatar](png/BankingCreditAgent.png) | [BankingCreditAgent.md](../agent_pool/ExtractedExampleInvestors/unique/BankingCreditAgent.md) |
| `ContrarianReversalInvestor` | Contrarian Reversal | ![Contrarian Reversal investor avatar](png/ContrarianReversalInvestor.png) | [ContrarianReversalInvestor.md](../agent_pool/ExtractedExampleInvestors/unique/ContrarianReversalInvestor.md) |
| `CryptoDeFiAgent` | Crypto DeFi | ![Crypto DeFi investor avatar](png/CryptoDeFiAgent.png) | [CryptoDeFiAgent.md](../agent_pool/ExtractedExampleInvestors/unique/CryptoDeFiAgent.md) |
| `FramingEffectTrader` | Framing Effect | ![Framing Effect investor avatar](png/FramingEffectTrader.png) | [FramingEffectTrader.md](../agent_pool/ExtractedExampleInvestors/unique/FramingEffectTrader.md) |
| `HerdingCascadeAgent` | Herding Cascade | ![Herding Cascade investor avatar](png/HerdingCascadeAgent.png) | [HerdingCascadeAgent.md](../agent_pool/ExtractedExampleInvestors/unique/HerdingCascadeAgent.md) |
| `InformedOpportunisticTrader` | Informed Opportunistic | ![Informed Opportunistic investor avatar](png/InformedOpportunisticTrader.png) | [InformedOpportunisticTrader.md](../agent_pool/ExtractedExampleInvestors/unique/InformedOpportunisticTrader.md) |
| `LeveragedFundInvestor` | Leveraged Fund | ![Leveraged Fund investor avatar](png/LeveragedFundInvestor.png) | [LeveragedFundInvestor.md](../agent_pool/ExtractedExampleInvestors/unique/LeveragedFundInvestor.md) |
| `LossAversionDispositionInvestor` | Loss Aversion | ![Loss Aversion investor avatar](png/LossAversionDispositionInvestor.png) | [LossAversionDispositionInvestor.md](../agent_pool/ExtractedExampleInvestors/unique/LossAversionDispositionInvestor.md) |
| `MacroCurrencySovereignTrader` | Macro Currency | ![Macro Currency investor avatar](png/MacroCurrencySovereignTrader.png) | [MacroCurrencySovereignTrader.md](../agent_pool/ExtractedExampleInvestors/unique/MacroCurrencySovereignTrader.md) |
| `MarketMakerLiquidityAgent` | Market Maker Liquidity | ![Market Maker Liquidity investor avatar](png/MarketMakerLiquidityAgent.png) | [MarketMakerLiquidityAgent.md](../agent_pool/ExtractedExampleInvestors/unique/MarketMakerLiquidityAgent.md) |
| `MentalAccountingSunkCostTrader` | Mental Accounting | ![Mental Accounting investor avatar](png/MentalAccountingSunkCostTrader.png) | [MentalAccountingSunkCostTrader.md](../agent_pool/ExtractedExampleInvestors/unique/MentalAccountingSunkCostTrader.md) |
| `MomentumTrendTrader` | Momentum Trend | ![Momentum Trend investor avatar](png/MomentumTrendTrader.png) | [MomentumTrendTrader.md](../agent_pool/ExtractedExampleInvestors/unique/MomentumTrendTrader.md) |
| `NoiseTrader` | Noise Trader | ![Noise Trader investor avatar](png/NoiseTrader.png) | [NoiseTrader.md](../agent_pool/ExtractedExampleInvestors/unique/NoiseTrader.md) |
| `OverconfidenceAndRepresentativenessTrader` | Overconfidence | ![Overconfidence investor avatar](png/OverconfidenceAndRepresentativenessTrader.png) | [OverconfidenceAndRepresentativenessTrader.md](../agent_pool/ExtractedExampleInvestors/unique/OverconfidenceAndRepresentativenessTrader.md) |
| `PanicForcedSeller` | Panic Forced Seller | ![Panic Forced Seller investor avatar](png/PanicForcedSeller.png) | [PanicForcedSeller.md](../agent_pool/ExtractedExampleInvestors/unique/PanicForcedSeller.md) |
| `PassiveInstitutionalLongHorizonInvestor` | Passive Institutional | ![Passive Institutional investor avatar](png/PassiveInstitutionalLongHorizonInvestor.png) | [PassiveInstitutionalLongHorizonInvestor.md](../agent_pool/ExtractedExampleInvestors/unique/PassiveInstitutionalLongHorizonInvestor.md) |
| `PolicyBackstopAgent` | Policy Backstop | ![Policy Backstop investor avatar](png/PolicyBackstopAgent.png) | [PolicyBackstopAgent.md](../agent_pool/ExtractedExampleInvestors/unique/PolicyBackstopAgent.md) |
| `RationalAnalystInvestor` | Rational Analyst | ![Rational Analyst investor avatar](png/RationalAnalystInvestor.png) | [RationalAnalystInvestor.md](../agent_pool/ExtractedExampleInvestors/unique/RationalAnalystInvestor.md) |
| `RebalancingStatusQuoInvestor` | Rebalancing Status Quo | ![Rebalancing Status Quo investor avatar](png/RebalancingStatusQuoInvestor.png) | [RebalancingStatusQuoInvestor.md](../agent_pool/ExtractedExampleInvestors/unique/RebalancingStatusQuoInvestor.md) |
| `RetailCoordinatedTrader` | Retail Coordinated | ![Retail Coordinated investor avatar](png/RetailCoordinatedTrader.png) | [RetailCoordinatedTrader.md](../agent_pool/ExtractedExampleInvestors/unique/RetailCoordinatedTrader.md) |
| `RiskManagementInvestor` | Risk Management | ![Risk Management investor avatar](png/RiskManagementInvestor.png) | [RiskManagementInvestor.md](../agent_pool/ExtractedExampleInvestors/unique/RiskManagementInvestor.md) |
| `SentimentNarrativeTrader` | Sentiment Narrative | ![Sentiment Narrative investor avatar](png/SentimentNarrativeTrader.png) | [SentimentNarrativeTrader.md](../agent_pool/ExtractedExampleInvestors/unique/SentimentNarrativeTrader.md) |
| `ShortSellerAndShortVolTrader` | Short Seller Short Vol | ![Short Seller Short Vol investor avatar](png/ShortSellerAndShortVolTrader.png) | [ShortSellerAndShortVolTrader.md](../agent_pool/ExtractedExampleInvestors/unique/ShortSellerAndShortVolTrader.md) |
| `SocialInformationAgents` | Social Information | ![Social Information investor avatar](png/SocialInformationAgents.png) | [SocialInformationAgents.md](../agent_pool/ExtractedExampleInvestors/unique/SocialInformationAgents.md) |
| `ValueFundamentalInvestor` | Value Fundamental | ![Value Fundamental investor avatar](png/ValueFundamentalInvestor.png) | [ValueFundamentalInvestor.md](../agent_pool/ExtractedExampleInvestors/unique/ValueFundamentalInvestor.md) |
| `VolatilityProductTrader` | Volatility Product | ![Volatility Product investor avatar](png/VolatilityProductTrader.png) | [VolatilityProductTrader.md](../agent_pool/ExtractedExampleInvestors/unique/VolatilityProductTrader.md) |
