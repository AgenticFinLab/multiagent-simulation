# Rational, Bayesian, calibrated, skeptical, and systematic analysts

## Merge Rationale

This file is a deduplicated market-level archetype. Scenario-specific agents are grouped here when their financial role, decision target, and theoretical mechanism are materially similar, even if the original class names differ.

## Summary

| Field | Content |
| --- | --- |
| Archetype | Rational, Bayesian, calibrated, skeptical, and systematic analysts |
| Merged profiles | 17 |
| Scenarios | AnchoringEffect, AvailabilityBias, ConfirmationBias, DispositionEffect, EndowmentEffect, EquityPremium, FramingEffect, GamblerFallacy, HerdingInformation, HindsightBias, LossAversion, MentalAccounting, OverconfidenceBias, RepresentativenessBias, SouthSeaBubble, SunkCostFallacy |
| Observed names | Balanced Analyst, Bayesian Updater, Calibrated Trader, Frame Invariant Trader, Independent Assessor, Independent Thinker, New Buyer, Process Evaluator, Rag Rational Investor, Rational Cutter, Rational Investor, Rational Optimizer, Rational Portfolio Manager, Rational Trader, Rational Updater, Skeptical Analyst, Systematic Analyst |

## Consolidated Definition and Goals

- **AnchoringEffect / Rational Updater**: RationalUpdater represents the Muth-rational agent who acts optimally on all available information -- the theoretical benchmark that every other agent in this simulation deviates from. It uses the true fundamental deviation directly, with no anchoring adjustment, and trades immediately when price differs from fundamental by more than 2%. RationalUpdater is the corrective force that prevents the anchoring-induced mispricing from growing without limit and provides the "rational expectations" baseline against which the bias magnitude of other agents can be measured.
- **AvailabilityBias / Systematic Analyst**: The SystematicAnalyst is the rational benchmark -- an institutional investor who processes all available information using objective, evidence-based methods without availability bias. Unlike RecentEventOverweighter (who overweights recent returns) and MediaInfluencedTrader (who overweights media-amplified signals), the SystematicAnalyst responds only to the objective fundamental deviation: the actual gap between price and intrinsic value. This investor represents the Bayesian ideal of flat-weighted information processing, where no event is given disproportionate cognitive salience. The SystematicAnalyst's behavior defines the counterfactual: what prices would look like if availability bias did not exist.
- **ConfirmationBias / Balanced Analyst**: The BalancedAnalyst is the rational benchmark -- a fundamental analyst who evaluates all market information objectively, without prior beliefs or position bias. Unlike BeliefAnchor (who amplifies confirming signals) or SelectiveScanner (who responds asymmetrically based on position), the BalancedAnalyst applies the same evidence standard to bullish and bearish signals. It buys when prices are genuinely below fundamental (deviation < -5%) and sells when genuinely above (deviation > +5%), serving as the primary mean-reversion force that limits how far confirmation bias can push prices from intrinsic value.
- **DispositionEffect / Rag Rational Investor**: RAG-enhanced rational investor.
- **DispositionEffect / Rational Investor**: `RationalInvestor` is the expected-utility benchmark. It ignores purchase-price anchoring and rebalances toward a target equity allocation.
- **EndowmentEffect / New Buyer**: A new entrant who evaluates assets purely at market value with no ownership bias, representing the rational WTP side of the endowment gap. Provides corrective buying when prices are below or at fundamental.
- **EquityPremium / Rational Optimizer**: LLM-driven rational optimizer -- expected utility maximizer modeling benchmark behavior. Theory: simulation-bases.md Section 4.5.
- **FramingEffect / Frame Invariant Trader**: **Summary**: The FrameInvariantTrader represents professional fund managers or quant traders who evaluate information by substance rather than framing. They trade contrariwise to framing-biased agents: buying when price is below fundamental (stabilizing) and selling when above (stabilizing). They represent the rational counterparty that partially constrains framing-induced mispricings. Their larger activation threshold (5% vs. 2% for biased agents) reflects the higher evidence bar rational traders require before committing capital.
- **GamblerFallacy / Independent Assessor**: **Summary**: Represents quantitative traders or statistically trained investors who correctly treat each price change as independent (no streak fallacy). They trade contrarian to the current deviation -- buying when price is below fundamental (deviation < -0.05) and selling when above (deviation > 0.05). Their 5% threshold and 500-share cap reflect both a higher evidence bar for independent-evidence reasoning and the limits to arbitrage constraints.
- **HerdingInformation / Independent Thinker**: **Summary**: Implements rational Bayesian updating with correct private signal processing. Contrarian -- buys when cascade overvalues, sells when undervalues. Represents the arbitrage force against cascade inefficiency.
- **HindsightBias / Process Evaluator**: **Summary**: Implements Roese & Vohs (2012) process-oriented rationality -- the agent evaluates decisions on process quality independent of outcome narratives, acting as a contrarian stabilizer at larger deviations (|deviation| > 0.05).
- **LossAversion / Rational Trader**: **Summary**: Expected-utility maximiser that corrects mispricings when deviation exceeds 3%. Provides a rational-agent baseline against which loss-aversion wealth penalties are benchmarked. Capacity capped at 500 shares to reflect practical limits to arbitrage.
- **MentalAccounting / Rational Portfolio Manager**: 1. **Summary**: Uses whole-portfolio valuation and serves as the rational benchmark. It trades against price-fundamental deviations. 2. **Theoretical and Empirical Foundation**: Markowitz (1952) provides whole-portfolio optimization; Barberis & Huang (2001) motivates contrast with narrow framing. 3. **Design Purpose and Activation Scenarios**: Activates when absolute deviation exceeds the configured rational threshold. 4. **Behavioral Framework**: Uses `risk_aversion`, `base_size`, `quantity_scale`, and `deviation_threshold`. 5. **Decision Process Walkthrough**: Buy undervaluation, sell overvaluation, size by deviation and risk aversion. 6. **Worked Numerical Example**: With `deviation=-4%`, `risk_aversion=0.7`, `quantity_scale=3000`, raw quantity is 84 before caps. 7. **Academic References**: Markowitz (1952); Barberis & Huang (2001).
- **OverconfidenceBias / Calibrated Trader**: 1. **Summary**: CalibratedTrader estimates signal precision correctly and trades only when the deviation is meaningful. It is the rational benchmark. 2. **Theoretical and Empirical Foundation**: Grossman and Stiglitz (1980, DOI `10.2307/1805228`) motivate disciplined information-based trading. 3. **Design Purpose and Activation Scenarios**: Activates only when `abs(deviation) > trade_threshold`. 4. **Behavioral Framework**: Trades in the value direction: buy undervaluation and sell overvaluation. Quantity scales with `signal_precision`. 5. **Decision Process Walkthrough**: Compare price to fundamental, verify the threshold, compute bounded size, and emit a stabilizing order. 6. **Worked Numerical Example**: If price is 4% below fundamental and threshold is 3%, it buys a bounded quantity proportional to signal precision. 7. **Academic References**: Grossman and Stiglitz (1980), Odean (1998).
- **RepresentativenessBias / Bayesian Updater**: **Summary**: A stabilizing benchmark that combines prior/base-rate information with observed evidence. It corrects overreaction when price deviates materially from fundamental value.
- **SouthSeaBubble / Skeptical Analyst**: **Summary**: A fundamental analyst focused on cash-flow plausibility rather than promotional hype. **Theoretical and Empirical Basis**: Fundamental valuation and skeptical analysis of unrealistic monopoly claims. **Design Purpose**: Provide stabilizing sell pressure against overpricing. **Behavioral Framework**: Activates when `abs(deviation) > 0.05` and sizes `min(500, int(abs(deviation) * 3000))`. **Decision Process**: Buy if price is below fundamental; sell if price is above fundamental; otherwise hold. **Worked Numerical Example**: At 10% overpricing, raw sell quantity is 300. **Academic References**: Fundamental valuation literature and Dale's South Sea Bubble analysis.
- **SunkCostFallacy / Rational Cutter**: This investor represents forward-looking agents who ignore past costs and act on valuation.

## Consolidated Financial Theory

- Theoretical basis: simulation-bases.md Section 2.4 (Muth, 1961 -- Rational Expectations).
- Decision rule (simulation-bases.md Section 4.3 -- Rule-Based Behavior):
- LLM-driven rational updater -- Bayesian, no anchoring bias (benchmark). Theory: simulation-bases.md Section 4.3 -- RationalUpdater.
- RuleLLM rational updater -- Bayesian, no anchoring bias (benchmark). Theory: simulation-bases.md Section 4.3 -- RationalUpdater.
- RAG-augmented rational updater -- Bayesian, no anchoring bias (benchmark). Theory: simulation-bases.md Section 4.3 -- RationalUpdater.
- Theory: simulation-bases.md Section 4.3 -- SystematicAnalyst
- Theoretical basis: Mullainathan (2002) -- Bayesian rational processing; absence of bias.
- LLM-driven systematic analyst -- objective information weighting (benchmark). Theory: simulation-bases.md Section 4.3.
- RuleLLM systematic analyst -- objective information weighting (benchmark). Theory: simulation-bases.md Section 4.3.
- RAG-augmented systematic analyst -- objective information weighting. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.3 -- BalancedAnalyst
- Theoretical basis: Bayesian rational updating; processes signals without cognitive
- LLM-driven balanced analyst -- Bayesian rational updater, no cognitive bias. Theory: simulation-bases.md Section 4.3.
- RuleLLM-driven balanced analyst -- Bayesian rational updater, no cognitive bias. Theory: simulation-bases.md Section 4.3.
- RAG-augmented balanced analyst -- Bayesian rational updater, no cognitive bias. Theory: simulation-bases.md Section 4.3.
- Theory: simulation-bases.md Section 4.2 -- RationalInvestor
- Theoretical basis: Expected Utility Theory; RAG retrieves rational portfolio management research.
- NOT affected by sunk costs or reference points.
- Theoretical basis: Expected Utility Theory (von Neumann & Morgenstern, 1944); ignores purchase price.
- LLM-driven rational investor -- trades on fundamentals, ignores reference point. Theory: simulation-bases.md Section 4.2.
- Hybrid rule+LLM rational investor -- rebalancing rules embedded, no reference point. Theory: simulation-bases.md Section 4.2.
- Theory: simulation-bases.md Section 4.4 -- NewBuyer
- Theoretical basis: Kahneman et al. (1990) -- buyers unaffected by endowment effect;
- LLM-driven unbiased new buyer -- evaluates assets at market price, no ownership distortion. Theory: simulation-bases.md Section 4.4.
- RuleLLM unbiased new buyer -- fundamental evaluation rules, no ownership bias. Theory: simulation-bases.md Section 4.4.
- RAG-augmented new buyer -- unbiased fundamental evaluation with buyer behavior literature. Theory: simulation-bases.md Section 4.4.

## Merged Scenario Agents

| Scenario | Original agent | Original profile |
| --- | --- | --- |
| AnchoringEffect | Rational Updater | [AnchoringEffect__RationalUpdater.md](../AnchoringEffect__RationalUpdater.md) |
| AvailabilityBias | Systematic Analyst | [AvailabilityBias__SystematicAnalyst.md](../AvailabilityBias__SystematicAnalyst.md) |
| ConfirmationBias | Balanced Analyst | [ConfirmationBias__BalancedAnalyst.md](../ConfirmationBias__BalancedAnalyst.md) |
| DispositionEffect | Rag Rational Investor | [DispositionEffect__RagRationalInvestor.md](../DispositionEffect__RagRationalInvestor.md) |
| DispositionEffect | Rational Investor | [DispositionEffect__RationalInvestor.md](../DispositionEffect__RationalInvestor.md) |
| EndowmentEffect | New Buyer | [EndowmentEffect__NewBuyer.md](../EndowmentEffect__NewBuyer.md) |
| EquityPremium | Rational Optimizer | [EquityPremium__RationalOptimizer.md](../EquityPremium__RationalOptimizer.md) |
| FramingEffect | Frame Invariant Trader | [FramingEffect__FrameInvariantTrader.md](../FramingEffect__FrameInvariantTrader.md) |
| GamblerFallacy | Independent Assessor | [GamblerFallacy__IndependentAssessor.md](../GamblerFallacy__IndependentAssessor.md) |
| HerdingInformation | Independent Thinker | [HerdingInformation__IndependentThinker.md](../HerdingInformation__IndependentThinker.md) |
| HindsightBias | Process Evaluator | [HindsightBias__ProcessEvaluator.md](../HindsightBias__ProcessEvaluator.md) |
| LossAversion | Rational Trader | [LossAversion__RationalTrader.md](../LossAversion__RationalTrader.md) |
| MentalAccounting | Rational Portfolio Manager | [MentalAccounting__RationalPortfolioManager.md](../MentalAccounting__RationalPortfolioManager.md) |
| OverconfidenceBias | Calibrated Trader | [OverconfidenceBias__CalibratedTrader.md](../OverconfidenceBias__CalibratedTrader.md) |
| RepresentativenessBias | Bayesian Updater | [RepresentativenessBias__BayesianUpdater.md](../RepresentativenessBias__BayesianUpdater.md) |
| SouthSeaBubble | Skeptical Analyst | [SouthSeaBubble__SkepticalAnalyst.md](../SouthSeaBubble__SkepticalAnalyst.md) |
| SunkCostFallacy | Rational Cutter | [SunkCostFallacy__RationalCutter.md](../SunkCostFallacy__RationalCutter.md) |

