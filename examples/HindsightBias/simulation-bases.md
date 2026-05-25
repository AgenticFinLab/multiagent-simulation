# HindsightBias — Simulation Design Basis

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                                                                                                                               |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | Hindsight Bias — the tendency to believe, after learning an outcome, that one had predicted or "knew" it beforehand, leading to overconfident future predictions                                                                                                                                                                                                          |
| Category           | Cognitive bias / behavioral finance / memory distortion                                                                                                                                                                                                                                                                                                                   |
| Core Mechanism     | HindsightOverconfident and OutcomeLearner agents both trade in the direction of the current deviation — interpreting price moves as obvious and predictable in retrospect, leading to overconfident momentum-following that amplifies deviations from fundamental. ProcessEvaluator and ContrarianSkeptic act as rational stabilizers, trading against large mispricings. |
| Real-World Origin  | Documented by Fischhoff (1975) in experimental settings; extended to financial markets through studies of analyst forecast revisions, post-crash attribution narratives, and investor post-hoc rationalization of losses                                                                                                                                                  |
| Research Relevance | Explains over-confidence in trading after apparent patterns; contributes to understanding of bubble formation, under-reaction followed by overreaction, and why investors repeatedly suffer from "it was obvious" reasoning that degrades future calibration                                                                                                              |

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

Hindsight bias was first formally documented by Fischhoff (1975) in a landmark paper titled "Hindsight ≠ Foresight: The Effect of Outcome Knowledge on Judgment Under Uncertainty." In a series of controlled experiments, Fischhoff showed that participants who were told the outcome of an uncertain historical event consistently overestimated the probability they would have assigned to that outcome before knowing it. The effect was robust: even when explicitly instructed to ignore outcome information, subjects could not eliminate hindsight contamination of their prior probability estimates. This work established the cognitive mechanism as a memory distortion — outcome knowledge rewrites the remembered pre-outcome belief.

Fischhoff and Beyth (1975) extended the finding with a prospective design: participants stated their pre-event beliefs in writing, then later recalled those beliefs after learning the outcome. Recalled beliefs systematically shifted toward the actual outcome — demonstrating that hindsight bias affects memory, not just post-hoc reporting. In financial terms, this implies that investors who experience a market gain or loss will misremember their prior confidence levels, leading to systematic overestimation of their own predictive accuracy.

Roese and Vohs (2012) provided the most comprehensive review of four decades of hindsight bias research, organizing the literature into three components: memory distortion (creeping determinism), inevitability judgments ("it had to happen"), and foreseeability judgments ("I knew it would happen"). They documented that all three components increase overconfidence in future predictions — directly mapping to the HindsightOverconfident agent's trade-size amplification in this simulation. Their meta-analysis confirmed the effect is most pronounced for negative financial outcomes, where investors attribute losses to external causes and construct "obvious" narratives.

The connection to financial markets was developed by Daniel, Hirshleifer and Subrahmanyam (1998), who embedded overconfidence — the natural consequence of prolonged hindsight bias — into an asset pricing model. They showed that overconfident investors underreact to public signals (because they discount information that contradicts their self-attributed skill) and overreact to private signals, generating return momentum followed by long-run reversal. This two-stage dynamics (momentum then reversal) is the macrostructure the simulation is designed to capture. The OutcomeLearner (§4.2) embodies the selective attribution mechanism: attributing successful outcomes to skill (positive signal) while discounting failed outcomes as bad luck.

The agent-based modelling literature on hindsight bias is more sparse than for other biases, but Hirshleifer (2001) reviews the full landscape of cognitive biases in financial markets and argues that hindsight bias is the upstream bias for overconfidence — overconfidence is what hindsight bias produces over time. The simulation captures both the first-order effect (hindsight bias itself, causing trend-following) and the downstream consequence (overconfident position sizing via the `hindsight_inflation` and `prediction_overweight` parameters in extras).

#### §1.1.2 Real-World Event Catalogue

| Event Name                                             | Date(s)                               | Market / Asset                  | Trigger                                                                                                                                    | Magnitude                                                                                               | Duration                                        | Correspondence to Simulation                                                                                                                                                         | Primary Source                                                                                                                                                                                             |
|--------------------------------------------------------|---------------------------------------|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------|-------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1987 Black Monday Post-Hoc Narratives                  | October 19, 1987                      | US equity market (DJIA)         | −22.6% single-day crash; post-crash surveys showed investors believed crash was predictable                                                | DJIA −22.6% in one day; survey: 67% of investors "knew" crash was coming ex-post vs. <5% ex-ante        | 1 day crash; months of post-hoc rationalization | HindsightOverconfident (§4.1) and OutcomeLearner (§4.2) both interpret the post-crash deviation as "obviously" recoverable; ProcessEvaluator (§4.3) resists this narrative           | Shiller, R.J. (1987). "Investor Behavior in the October 1987 Stock Market Crash." *NBER Working Paper* 2446. https://www.nber.org/papers/w2446                                                             |
| Dot-Com Bubble Retrospective Certainty                 | 1995–2000 (bubble); 2000–2002 (crash) | NASDAQ                          | NASDAQ ×6 during bubble; −78% crash; post-2002 surveys: "everyone knew" it was a bubble                                                    | NASDAQ 100: +600% (1995–2000), −78% (2000–2002)                                                         | 7 years bubble, 2 years crash                   | OutcomeLearner (§4.2) attributes bubble gains to skill, not luck; HindsightOverconfident (§4.1) amplifies momentum because it "obviously" continues                                  | Barber, B. & Odean, T. (2002). "Online Investors: Do the Slow Die First?" *Review of Financial Studies*, 15(2), 455–488. https://doi.org/10.1093/rfs/15.2.455                                              |
| 2008 GFC Analyst Forecast Revisions                    | 2007–2009                             | US bank stocks (S&P Financials) | Subprime crisis → bank collapses; analyst target prices slashed 60–80% but analysts claimed they "sensed" the risk earlier                 | Bank of America: −93% peak to trough; analyst target price revision lag 6–12 months behind actual price | 18 months of crisis                             | HindsightOverconfident (§4.1) overestimates how well it predicted the decline; OutcomeLearner (§4.2) misattributes price collapse to bad luck rather than structural risk            | Daniel, K., Hirshleifer, D. & Subrahmanyam, A. (1998). "Investor Psychology and Security Market Under- and Overreactions." *Journal of Finance*, 53(6), 1839–1885. https://doi.org/10.1111/0022-1082.00077 |
| Cryptocurrency Crash Retrospective 2018                | December 2017 – December 2018         | Bitcoin / crypto markets        | Bitcoin −84% from peak; post-crash: overwhelming consensus that "bubble was obvious"                                                       | Bitcoin: $19,783 (Dec 2017) → $3,122 (Dec 2018), −84.2%                                                 | 12 months                                       | OutcomeLearner (§4.2) misattributes $19K peak to skill (overconfident position sizing in next bull phase); HindsightOverconfident (§4.1) amplifies rebounds as "obvious recovery"    | Cong, L.W. et al. (2021). "Tokenomics." *Review of Finance*. https://doi.org/10.1093/rof/rfab038                                                                                                           |
| COVID-19 Market Crash and Recovery — "Obvious Rebound" | March 2020 – August 2020              | S&P 500                         | −34% crash in 33 days; recovery to new highs in 5 months; post-recovery investor surveys showed high "I knew it would recover" attribution | S&P 500: −34% (Feb–March 2020); +51% recovery (March–August 2020)                                       | 5 months recovery                               | HindsightOverconfident (§4.1) and OutcomeLearner (§4.2) both read the rapid recovery as "obviously predictable" — boosting future position sizes and destabilizing the next pullback | Giglio, S., Maggiori, M., Stroebel, J. & Utkus, S. (2021). "Five Facts about Beliefs and Portfolios." *American Economic Review*, 111(5), 1481–1522. https://doi.org/10.1257/aer.20200482                  |

#### §1.1.3 Book and Practitioner Literature

| Title                                                                           | Author(s)      | Year | Publisher                 | Relevance                                                                                                                                                                                                                                                                                                                         |
|---------------------------------------------------------------------------------|----------------|------|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Thinking, Fast and Slow*                                                       | Kahneman, D.   | 2011 | Farrar, Straus and Giroux | Chapter 19 ("The Illusion of Understanding") is the most accessible treatment of hindsight bias; Kahneman connects hindsight bias to overconfidence and the narrative fallacy — the compulsion to construct coherent stories from random events — directly motivating the HindsightOverconfident and OutcomeLearner agent designs |
| *The Halo Effect: And the Eight Other Business Delusions That Deceive Managers* | Rosenzweig, P. | 2007 | Free Press                | Chapter 5 documents systematic hindsight bias in business retrospectives; shows that market analysts attribute outcomes to narratives constructed after the fact; reinforces the OutcomeLearner model of selective attribution and the ContrarianSkeptic model of narrative resistance                                            |

---

## §2 Theoretical Foundation

### Theory 1: Hindsight Bias / Creeping Determinism

#### §T1.1 Citation and Status

- **Primary Citation**: Fischhoff, B. (1975). "Hindsight ≠ Foresight: The Effect of Outcome Knowledge on Judgment Under Uncertainty." *Journal of Experimental Psychology: Human Perception and Performance*, 1(3), 288–299. https://doi.org/10.1037/0096-1523.1.3.288
- **Theory Status**: Foundational — replicated in hundreds of studies across domains; effect size typically d = 0.40–0.60 in meta-analyses
- **Original Context**: Historical judgment tasks; documented memory distortion in recalled prior probability estimates after outcomes were revealed

#### §T1.2 Core Theoretical Mechanism

Hindsight bias — also called the "knew-it-all-along" effect or "creeping determinism" — describes the systematic tendency to perceive past events as more predictable than they were before they occurred. Upon learning an outcome, subjects rewrite their memories of pre-outcome uncertainty: the actual outcome seems obvious in retrospect, and alternative outcomes seem improbable. This cognitive process serves the psychological function of maintaining a coherent self-narrative ("I am a good predictor"), but it systematically inflates estimated prediction accuracy.

The causal chain in financial markets is: (1) Agent experiences a market outcome (price rise or fall) → (2) Agent retrospectively inflates the probability they "should" have assigned to that outcome → (3) Agent updates future confidence upward ("I predicted this correctly") → (4) Agent increases position sizes in the next similar setup → (5) Overconfident position sizes amplify deviations when the agent is correct (momentum) and create catastrophic losses when wrong (crash risk). This is the mechanism encoded in HindsightOverconfident (§4.1) and OutcomeLearner (§4.2).

The key distinction between hindsight bias and other overconfidence biases is its *retrospective* nature: hindsight bias is specifically about distorted memory of pre-outcome beliefs, not about intrinsic overconfidence in ability. However, Roese and Vohs (2012) document that repeated hindsight bias episodes generate stable overconfidence — the steady-state consequence is indistinguishable from the overconfidence modeled in Daniel et al. (1998). For simulation purposes, the two biased agents embody this accumulated effect.

The limits of hindsight bias correction are documented by Fischhoff (1977): even when subjects are told about hindsight bias and explicitly instructed to correct for it, they under-correct significantly. This is analogous to ContrarianSkeptic (§4.4) behavior — even an agent who is skeptical of post-hoc narratives cannot fully neutralize hindsight-inflated momentum.

#### §T1.3 Mathematical Formulation

**Hindsight bias belief inflation model (Roese & Vohs, 2012)**:
```
P_hindsight(outcome) = P_true(outcome) + δ × I(outcome occurred)

where:
  P_true(outcome) = genuine ex-ante probability
  δ = hindsight inflation factor ∈ [0.15, 0.40] (meta-analytic range)
  I(outcome occurred) = 1 if outcome is realized, 0 otherwise
```

| Symbol                  | Definition                                       | Calibrated Value           | Source                                          |
|-------------------------|--------------------------------------------------|----------------------------|-------------------------------------------------|
| δ                       | Hindsight inflation factor                       | 0.15–0.40                  | Roese & Vohs (2012) meta-analysis               |
| `hindsight_inflation`   | Simulation extras parameter                      | 1.0 (base), 1.5 (inflated) | §6 parameter table                              |
| `prediction_overweight` | Confidence multiplier for HindsightOverconfident | 1.0–2.0                    | Daniel et al. (1998) overconfidence calibration |

In simulation encoding:
```
qty = min(800, int(abs(deviation) * 5000 * hindsight_inflation * prediction_overweight))
```
Both HindsightOverconfident and OutcomeLearner use abs(deviation) × 5000 as baseline — the extras parameters allow calibration of the inflation multiplier.

#### §T1.4 Empirical Evidence

| Study                    | Context                          | Finding                                                                        | Relevance to Simulation                                                         |
|--------------------------|----------------------------------|--------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| Fischhoff (1975)         | Historical judgment tasks        | 67% of subjects overestimated ex-ante probability of realized outcome          | Directly validates HindsightOverconfident (§4.1) over-confidence magnitude      |
| Fischhoff & Beyth (1975) | US-China Nixon visit predictions | Recalled pre-visit beliefs shifted toward actual outcome; effect size d ≈ 0.50 | Validates OutcomeLearner (§4.2) selective memory of successes                   |
| Roese & Vohs (2012)      | Meta-analysis, 800+ studies      | d = 0.42 mean effect size; strongest for negative financial outcomes           | Calibrates activation threshold and trade sizing parameters                     |
| Daniel et al. (1998)     | US equity return predictability  | Overconfidence produces momentum followed by reversal                          | Validates phase structure: hindsight-induced momentum, then rational correction |
| Barber & Odean (2002)    | Online retail investors          | Active traders underperform by 6.5%/year; overconfidence strongest post-win    | Validates WDI prediction: overconfident agents lose wealth to rational agents   |

#### §T1.5 Relevance to Simulation

Theory 1 is the primary mechanism encoded by HindsightOverconfident (§4.1) and OutcomeLearner (§4.2). ProcessEvaluator (§4.3) and ContrarianSkeptic (§4.4) represent the population of agents who resist hindsight narrative construction by focusing on process quality and narrative skepticism respectively.

---

### Theory 2: Outcome Bias and Selective Attribution

#### §T2.1 Citation and Status

- **Primary Citation**: Fischhoff, B. & Beyth, R. (1975). "'I Knew It Would Happen': Remembered Probabilities of Once-Future Things." *Organizational Behavior and Human Performance*, 13(1), 1–16. https://doi.org/10.1016/0030-5073(75)90002-1
- **Theory Status**: Well-established — outcome bias is a component of hindsight bias; documented across financial and professional judgment contexts
- **Original Context**: Prospective study of probability judgments for Nixon visit outcomes

#### §T2.2 Core Theoretical Mechanism

Outcome bias is the specific component of hindsight bias that concerns evaluation of decisions: when evaluating whether a decision was good, people overweight the actual outcome and underweight the decision process quality. A good process that produces a bad outcome is rated worse than a bad process that produces a good outcome. In financial markets, this generates selective attribution: investors attribute gains to skill (process was good) and losses to bad luck (process was fine, outcome was unlucky). OutcomeLearner (§4.2) implements this directly through the `success_attribution` and `failure_discount` extras parameters, which modulate how strongly good and bad outcomes affect future confidence.

The market dynamics generated by selective attribution are: (1) After a period of gains, biased investors believe their process was validated → increase position sizes → amplify further gains → momentum; (2) After losses, biased investors blame external factors → do not update down → maintain large positions → amplify further losses before eventual capitulation. This asymmetric response generates the non-linear volatility dynamics observed in the simulation: price deviations grow more slowly initially but self-reinforce once established.

The rational counterpart — ProcessEvaluator (§4.3) — evaluates decisions by process quality regardless of outcome, correcting mispricings at |deviation| > 0.05 without regard to whether recent price history makes the correction "obvious" or "surprising."

#### §T2.3 Mathematical Formulation

**Selective attribution update rule (Daniel et al., 1998 formalization)**:
```
Confidence(t+1) = Confidence(t) + α × I(success) − β × I(failure)

where:
  α = success attribution weight = success_attribution ∈ [1.0, 2.5]
  β = failure discount weight = failure_discount ∈ [0.1, 0.5]  (β << α for biased agents)
  I(success) = 1 if recent position was profitable
```

| Symbol                | Definition                      | Calibrated Value      | Source                                      |
|-----------------------|---------------------------------|-----------------------|---------------------------------------------|
| α                     | Success attribution weight      | 1.0 (base)            | Barber & Odean (2000)                       |
| β                     | Failure discount weight         | Typically 0.2–0.4 × α | Odean (1998) disposition effect calibration |
| `success_attribution` | OutcomeLearner extras parameter | 1.0 (base)            | §6 parameter table                          |
| `failure_discount`    | OutcomeLearner extras parameter | 1.0 (base)            | §6 parameter table                          |

#### §T2.4 Empirical Evidence

| Study                             | Context                   | Finding                                                            | Relevance                                                      |
|-----------------------------------|---------------------------|--------------------------------------------------------------------|----------------------------------------------------------------|
| Baron & Hershey (1988). *JEP:HPP* | Professional judgment     | Decision quality ratings inflated 40% when outcomes were favorable | Validates OutcomeLearner success_attribution mechanism         |
| Odean (1998). *JF* 53(5)          | US retail brokerage       | Investors hold losses 2× longer than gains (disposition effect)    | Validates asymmetric β << α calibration                        |
| Barber & Odean (2000). *JF* 55(2) | US retail trading 1991–96 | Most active traders underperform by 6.5%/year                      | Validates WDI: OutcomeLearner wealth decreases over simulation |

#### §T2.5 Relevance to Simulation

Theory 2 is the mechanism specifically encoded by OutcomeLearner (§4.2). The `success_attribution` and `failure_discount` parameters allow calibration of the asymmetry; in the base parameterization (both = 1.0), OutcomeLearner behaves identically to HindsightOverconfident, confirming that both biases produce trend-following behavior as the first-order market effect.

---

### Theory 3: Limits to Arbitrage Against Narrative Consensus

#### §T3.1 Citation and Status

- **Primary Citation**: Shleifer, A. & Vishny, R.W. (1997). "The Limits of Arbitrage." *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- **Theory Status**: Canonical — establishes why rational agents cannot fully arbitrage away behavioral biases
- **Original Context**: Asset pricing theory; professional arbitrage with capital constraints

#### §T3.2 Core Theoretical Mechanism

Even when ProcessEvaluator (§4.3) and ContrarianSkeptic (§4.4) correctly identify hindsight-inflated mispricings, they face capital constraints that limit their corrective impact. In this simulation, rational agents are capped at 500 shares vs. 800 for biased agents (a 62.5% capacity ratio, within the Pontiff (2006) empirical range of 40–60% for constrained arbitrage). Noise trader risk from NoiseTrader (§4.5) further prevents rational agents from bringing price immediately to fundamental. The result is partial and delayed correction — consistent with the Daniel et al. (1998) two-stage dynamics: momentum phase (bias dominates) followed by eventual reversal phase (rational correction prevails as momentum exhausts itself).

#### §T3.3 Mathematical Formulation

The rational agent corrective capacity ratio is:
```
Capacity ratio = max_qty_rational / max_qty_biased = 500 / 800 = 0.625

Expected partial correction within 5 rounds (RCE) ≈ 0.35–0.65
(from Pontiff (2006): arbitrage capital ≈ 50% of theoretical maximum)
```

#### §T3.4 Empirical Evidence

| Study                       | Context             | Finding                                                                   | Relevance                                                            |
|-----------------------------|---------------------|---------------------------------------------------------------------------|----------------------------------------------------------------------|
| Pontiff (2006). *JFE* 80(2) | US equity anomalies | Arbitrage capital ≈ 50% of theoretical maximum due to capital constraints | Predicts RCE ≈ 0.40–0.65                                             |
| Shleifer & Vishny (1997)    | Asset pricing       | Noise trader risk prevents rational correction of large mispricings       | Validates ProcessEvaluator/ContrarianSkeptic partial correction only |

#### §T3.5 Relevance to Simulation

Theory 3 explains why even with two rational stabilizing agents (§4.3, §4.4) the simulation produces persistent mispricings — the capacity asymmetry is intentional and calibrated to match empirical arbitrage limits.

---

## §3 Market Design

| Component         | Design Choice                                                  | Justification                                           |
|-------------------|----------------------------------------------------------------|---------------------------------------------------------|
| Price formation   | P(t+1) = P(t) + λ × D(t) + γ × (F − P(t)) + ε(t)               | Standard Walrasian ABM market (Farmer & Foley, 2009)    |
| Fundamental value | Constant F                                                     | Isolates hindsight bias as the sole source of deviation |
| Market broadcast  | `{type, price, fundamental, deviation, round}`                 | Provides all signals needed for hindsight-based trading |
| Order format      | buy / sell / hold with `bid_price`, `quantity`, `reasoning`, `agent_type`, and `strategy` | Canonical auditable order flow |
| Agent capacity    | Biased agents: max 800 shares; rational agents: max 500 shares | Implements limits to arbitrage (Theory 3)               |

---

## §4 Investor Taxonomy

### §4.1 HindsightOverconfident

**Summary**: Implements Fischhoff (1975) hindsight bias — the agent interprets price moves as "obviously" predictable in retrospect, amplifying momentum by buying when deviation > 0.02 and selling when deviation < −0.02.

**Theoretical and Empirical Basis**: Fischhoff, B. (1975). "Hindsight ≠ Foresight." *JEP:HPP*, 1(3), 288–299. `doi:10.1037/0096-1523.1.3.288`; Daniel, Hirshleifer & Subrahmanyam (1998). `doi:10.1111/0022-1082.00077`

**Design Purpose**: Encode the "knew-it-all-along" effect in position sizing — each perceived success inflates confidence via `hindsight_inflation` and `prediction_overweight`, creating a momentum amplifier that drives price away from fundamental.

**Behavioral Framework**:

| Decision Variable   | Logic                                                             | Formula                                                                        |
|---------------------|-------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Activation          | Trades when deviation large enough to trigger hindsight certainty | `abs(deviation) > 0.02`                                                        |
| Direction           | Follows deviation direction (momentum-following)                  | buy if dev > 0; sell if dev < 0                                                |
| Quantity            | Scaled by deviation magnitude × inflation parameters              | `min(800, int(abs(dev) × 5000 × hindsight_inflation × prediction_overweight))` |
| Cash constraint     | Cannot buy more than cash allows                                  | `buy_qty = min(qty, int(cash / price))`                                        |
| Position constraint | Cannot sell more than held                                        | `sell_qty = min(qty, max(position, 0))`                                        |

**Decision Process**:
1. Receive market broadcast: `{price, fundamental, deviation, round}`
2. Check `abs(deviation) > 0.02` — if not, hold
3. If deviation > 0: bias triggers "this move was obvious" → buy order
4. If deviation < 0: bias triggers "this decline was obvious" → sell order
5. Quantity = `min(800, int(abs(dev) × 5000 × hindsight_inflation × prediction_overweight))`

**Worked Example**: fundamental = 100, price = 103.5, deviation = +0.035, hindsight_inflation = 1.2, prediction_overweight = 1.0 → qty = min(800, int(0.035 × 5000 × 1.2 × 1.0)) = min(800, 210) = 210 shares buy order.

**Academic References**: `simulation-bases.md §2 Theory 1`; `doi:10.1037/0096-1523.1.3.288`; `doi:10.1111/0022-1082.00077`

### §4.2 OutcomeLearner

**Summary**: Implements Fischhoff & Beyth (1975) outcome bias and Odean (1998) selective attribution — the agent attributes gains to skill and losses to bad luck, producing asymmetric momentum that is stronger in bull phases.

**Theoretical and Empirical Basis**: Fischhoff & Beyth (1975). "'I Knew It Would Happen'." *OBHP*, 13(1), 1–16. `doi:10.1016/0030-5073(75)90002-1`; Odean (1998). `doi:10.1111/0022-1082.00259`

**Design Purpose**: Encode selective attribution — `success_attribution` scales up confidence after gains, `failure_discount` reduces the downward update after losses, creating an asymmetric confidence trajectory that generates bull-phase momentum dominance (OBI > 1.0).

**Behavioral Framework**:

| Decision Variable   | Logic                                                    | Formula                                                                   |
|---------------------|----------------------------------------------------------|---------------------------------------------------------------------------|
| Activation          | Trades when deviation crosses threshold                  | `abs(deviation) > 0.02`                                                   |
| Direction           | Follows deviation (same as HindsightOverconfident)       | buy if dev > 0; sell if dev < 0                                           |
| Quantity            | Scaled by deviation magnitude and attribution parameters | `min(800, int(abs(dev) × 5000 × success_attribution × failure_discount))` |
| Cash constraint     | Cannot exceed available cash                             | `buy_qty = min(qty, int(cash / price))`                                   |
| Position constraint | Cannot sell beyond held shares                           | `sell_qty = min(qty, max(position, 0))`                                   |

**Decision Process**:
1. Receive market broadcast: `{price, fundamental, deviation, round}`
2. Check `abs(deviation) > 0.02` — if not, hold
3. If deviation > 0: success attribution active → buy with amplified confidence
4. If deviation < 0: failure discount reduces downward update → still sells but with smaller position
5. Quantity = `min(800, int(abs(dev) × 5000 × success_attribution × failure_discount))`

**Worked Example**: fundamental = 100, price = 103.5, deviation = +0.035, success_attribution = 1.5, failure_discount = 0.5 → qty = min(800, int(0.035 × 5000 × 1.5)) = min(800, 262) = 262 shares buy order. (In loss round: qty = min(800, int(0.035 × 5000 × 0.5)) = min(800, 87) = 87 shares sell order.)

**Academic References**: `simulation-bases.md §2 Theory 2`; `doi:10.1016/0030-5073(75)90002-1`; Barber & Odean (2000) `doi:10.1111/0022-1082.00226`

**Note**: §4.1 and §4.2 share the same directional rule, but branch-current defaults differentiate their scale: §4.1 uses `hindsight_inflation = 1.5`, while §4.2 uses `success_attribution = 1.3` for positive deviations and `failure_discount = 1.0` for negative deviations.

### §4.3 ProcessEvaluator

**Summary**: Implements Roese & Vohs (2012) process-oriented rationality — the agent evaluates decisions on process quality independent of outcome narratives, acting as a contrarian stabilizer at larger deviations (|deviation| > 0.05).

**Theoretical and Empirical Basis**: Roese, N.J. & Vohs, K.D. (2012). "Hindsight Bias." *Perspectives on Psychological Science*, 7(5), 411–426. `doi:10.1177/1745691612454303`; Shleifer & Vishny (1997). `doi:10.1111/j.1540-6261.1997.tb03807.x`

**Design Purpose**: Encode the rational baseline that focuses on process rather than outcome — when deviation exceeds 0.05, the agent concludes the process-based analysis indicates mispricing regardless of whether the narrative makes the move seem "obvious", acting as a contrarian correction force.

**Behavioral Framework**:

| Decision Variable | Logic                                                               | Formula                                                            |
|-------------------|---------------------------------------------------------------------|--------------------------------------------------------------------|
| Activation        | Higher threshold than biased agents — requires large mispricing     | `abs(deviation) > 0.05`                                            |
| Direction         | Contrarian — trades against deviation                               | buy if dev < −0.05; sell if dev > 0.05                             |
| Quantity          | Scaled by deviation magnitude and process/outcome weight parameters | `min(500, int(abs(dev) × 3000 × process_weight × outcome_weight))` |
| Cash constraint   | Cannot exceed available cash                                        | `buy_qty = min(qty, int(cash / price))`                            |

**Decision Process**:
1. Receive market broadcast: `{price, fundamental, deviation, round}`
2. Check `abs(deviation) > 0.05` — if not, hold
3. If deviation > 0.05: price above fundamental → sell order (correcting overpricing)
4. If deviation < −0.05: price below fundamental → buy order (correcting underpricing)
5. Quantity = `min(500, int(abs(dev) × 3000 × process_weight × outcome_weight))`

**Worked Example**: fundamental = 100, price = 106, deviation = +0.06, process_weight = 1.0, outcome_weight = 1.0 → qty = min(500, int(0.06 × 3000 × 1.0)) = min(500, 180) = 180 shares sell order.

**Academic References**: `simulation-bases.md §2 Theory 3`; `doi:10.1177/1745691612454303`; Pontiff (2006) `doi:10.1016/j.jfineco.2005.09.001`

### §4.4 ContrarianSkeptic

**Summary**: Implements Roese & Vohs (2012) narrative skepticism — the agent resists post-hoc consensus narratives and trades against deviations with a higher threshold, acting as a second rational stabilizer at |deviation| > 0.05.

**Theoretical and Empirical Basis**: Roese, N.J. & Vohs, K.D. (2012). *Perspectives on Psychological Science*, 7(5), 411–426. `doi:10.1177/1745691612454303`; De Bondt & Thaler (1985). `doi:10.1111/j.1540-6261.1985.tb05004.x`

**Design Purpose**: Encode skepticism of "obvious in hindsight" narratives — the agent refuses to be swept into consensus momentum and instead acts on the fundamental signal alone, providing a second correction force alongside ProcessEvaluator.

**Behavioral Framework**:

| Decision Variable  | Logic                                                  | Formula                                                             |
|--------------------|--------------------------------------------------------|---------------------------------------------------------------------|
| Activation         | Same threshold as ProcessEvaluator                     | `abs(deviation) > 0.05`                                             |
| Direction          | Contrarian — trades against deviation                  | buy if dev < −0.05; sell if dev > 0.05                              |
| Quantity           | Scaled by deviation and skepticism parameter | `min(max_order, int(abs(dev) × quantity_scale × skepticism_level))` |

**Decision Process**:
1. Receive market broadcast: `{price, fundamental, deviation, round}`
2. Check `abs(deviation) > 0.05` — if not, hold
3. If deviation > 0.05: narrative skeptic concludes "this isn't as obvious as market thinks" → sell order
4. If deviation < −0.05: similarly → buy order
5. Quantity = `min(max_order, int(abs(dev) × quantity_scale × skepticism_level))`

**Worked Example**: fundamental = 100, price = 107, deviation = +0.07, skepticism_level = 0.6, quantity_scale = 3000, max_order = 500 → qty = min(500, int(0.07 × 3000 × 0.6)) = 126 shares sell order.

**Academic References**: `simulation-bases.md §2 Theory 3`; `doi:10.1177/1745691612454303`; Shleifer & Vishny (1997) `doi:10.1111/j.1540-6261.1997.tb03807.x`

### §4.5 NoiseTrader

**Summary**: Implements Black (1986) uninformed noise trading — the agent trades randomly with no fundamental signal, providing baseline liquidity and ensuring non-trivial price volatility even in the absence of bias agents.

**Theoretical and Empirical Basis**: Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529–543. `doi:10.1111/j.1540-6261.1986.tb04513.x`

**Design Purpose**: Provide stochastic baseline trading that prevents trivially clean price series; the random trades occasionally push prices across bias agent thresholds (0.02, 0.05), creating natural variation in bias onset timing across seeds.

**Behavioral Framework**:

| Decision Variable | Logic                    | Formula                                         |
|-------------------|--------------------------|-------------------------------------------------|
| Activity          | Trades on a random basis | `if random.random() < trade_probability: trade` |
| Direction         | Uniformly random         | 50% buy, 50% sell                               |
| Quantity          | Random within config range | `random.randint(min_order, max_order)` shares |

**Decision Process**:
1. Receive market broadcast: `{price, fundamental, deviation, round}`
2. Draw uniform random number; if < `trade_probability` (default 0.30): execute trade
3. Draw uniform random direction: buy or sell
4. Draw random quantity from `[min_order, max_order]`

**Worked Example**: trade_probability = 0.30 → 30% chance of trading each round. If trading: 50% buy 100–500 shares, 50% sell 100–500 shares. Expected net contribution to NetDemand: 0.

**Academic References**: Black (1986) `doi:10.1111/j.1540-6261.1986.tb04513.x`; De Long et al. (1990) `doi:10.1086/261703`

---

## §5 Agent Diversity Rationale

| Agent Pair              | Diversity Purpose                                                                                                                                                                             |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| §4.1 vs. §4.2           | Both destabilizing, but distinct theoretical mechanisms: §4.1 is memory distortion; §4.2 is selective attribution. Default behavior is identical; differentiation requires extras calibration |
| §4.3 vs. §4.4           | Both stabilizing contrarians, but from different perspectives: §4.3 focuses on decision process quality; §4.4 focuses on narrative skepticism                                                 |
| §4.1/§4.2 vs. §4.3/§4.4 | Core destabilizing vs. stabilizing tension; capacity asymmetry (800 vs. 500) reflects empirical limits to arbitrage                                                                           |
| §4.5 (NoiseTrader)      | Baseline noise floor; prevents trivially clean price series; ensures non-zero GFI even without fallacy agents                                                                                 |

---

## §6 Parameter Reference Table

| Parameter             | Agent         | Default | Calibrated Range | Source                               |
|-----------------------|---------------|---------|------------------|--------------------------------------|
| initial_price         | Market        | 100.0   | 50–200           | Standard ABM initialization          |
| fundamental_value     | Market        | 100.0   | 80–120           | Stable fundamental assumption        |
| price_impact (λ)      | Market        | 0.03    | 0.01–0.10        | Config path: `market.config.extras.price_impact`; Farmer & Foley (2009) |
| mean_reversion (γ)    | Market        | 0.01    | 0.01–0.10        | Config path: `market.config.extras.mean_reversion`; mean-reversion ABM literature |
| noise_std             | Market        | 0.015   | 0.005–0.05       | Config path: `market.config.extras.noise_std`; Black (1986) noise calibration |
| initial_cash          | Investors     | 500,000–2,000,000 | Fixed | Config path: each investor `config.extras.initial_cash`; capacity normalization |
| initial_position      | Investors     | 0–500   | Fixed            | Config path: each investor `config.extras.initial_position` |
| activation_threshold  | §4.1/§4.2     | 0.02    | 0.01–0.05        | Config path: biased investor `activation_threshold`; Roese & Vohs (2012) |
| quantity_scale        | §4.1/§4.2     | 5000    | 3000–8000        | Config path: biased investor `quantity_scale`; calibrated order sensitivity |
| max_order             | §4.1/§4.2     | 800     | 500–1000         | Config path: biased investor `max_order`; limits-to-arbitrage capacity asymmetry |
| hindsight_inflation   | §4.1          | 1.5     | 1.0–2.0          | Roese & Vohs (2012) δ ≈ 0.15–0.40    |
| prediction_overweight | §4.1          | 1.0     | 1.0–2.0          | Daniel et al. (1998) overconfidence  |
| success_attribution   | §4.2          | 1.3     | 1.0–2.5          | Barber & Odean (2000)                |
| failure_discount      | §4.2          | 1.0     | 0.2–1.0          | Odean (1998) disposition effect      |
| activation_threshold  | §4.3/§4.4     | 0.05    | 0.03–0.10        | Config path: rational investor `activation_threshold`; Shleifer & Vishny (1997) |
| quantity_scale        | §4.3/§4.4     | 3000    | 2000–5000        | Config path: rational investor `quantity_scale`; calibrated correction capacity |
| max_order             | §4.3/§4.4/§4.5 | 500    | 300–800          | Config path: rational/noise `max_order`; capacity asymmetry |
| process_weight        | §4.3          | 0.8     | 0.5–2.0          | Roese & Vohs (2012) process focus    |
| outcome_weight        | §4.3          | 1.0     | 0.5–2.0          | Rational baseline                    |
| skepticism_level      | §4.4          | 0.6     | 0.5–3.0          | Narrative skepticism scaling         |
| trade_probability     | §4.5          | 0.30    | 0.10–0.50        | Black (1986) noise trader literature |
| min_order             | §4.5          | 100     | 50–200           | Config path: `noisetrader.config.extras.min_order`; baseline liquidity floor |

---

## §7 Round Structure

| Step | Agent                                                                                    | Action                                                | Output                |
|------|------------------------------------------------------------------------------------------|-------------------------------------------------------|-----------------------|
| 1    | HindsightOverconfident, OutcomeLearner, ProcessEvaluator, ContrarianSkeptic, NoiseTrader | `perceive()`: read market broadcast; initialize state | Updated custom_state  |
| 2    | All investors                                                                            | `decide()`: compute buy/sell/hold + quantity          | Decision dict         |
| 3    | All investors                                                                            | `act()`: send order to Market                         | Order message         |
| 4    | Market                                                                                   | `perceive()`: aggregate all orders; compute new price | —                     |
| 5    | Market                                                                                   | `decide()`: return price + fundamental + deviation    | Market result dict    |
| 6    | Market                                                                                   | `act()`: broadcast market update to all investors     | Market update message |

---

## §8 Historical Case Studies

### Case 1: 1987 Black Monday — The "Obvious" Crash Narrative

| Attribute          | Detail                                                                                                                                                                                |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Event              | DJIA −22.6% on October 19, 1987 — largest single-day percentage decline in US history                                                                                                 |
| Mechanism          | Post-crash surveys (Shiller, 1987) showed 67% of investors believed the crash was predictable or had sensed it beforehand, despite <5% having predicted it in writing pre-crash       |
| Magnitude          | DJIA −508 points (−22.6%) in one trading session; VIX equivalent estimated at 150+                                                                                                    |
| Duration           | Single-day crash; post-hoc narrative construction lasted months                                                                                                                       |
| Agents Modeled     | HindsightOverconfident (§4.1): "I saw this coming" → increased confidence in next prediction; OutcomeLearner (§4.2): attributed pre-crash selling to skill, held losses as "bad luck" |
| Rational Response  | ProcessEvaluator (§4.3) and ContrarianSkeptic (§4.4) would have focused on fundamental deviation rather than narrative                                                                |
| Simulation Mapping | The crash created a strong negative deviation; biased agents interpret this as "obvious" on the following round; both sell aggressively amplifying the downward momentum              |

### Case 2: Dot-Com Bubble — Skill Attribution and Crash Denial

| Attribute          | Detail                                                                                                                                                                                                |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Event              | NASDAQ ×6 (1995–2000) followed by −78% crash (2000–2002)                                                                                                                                              |
| Mechanism          | During the bubble, investors attributed gains to their own prescience about internet's future — outcome bias. Post-crash, narrative shifted to "everyone knew it was a bubble" — hindsight bias       |
| Magnitude          | NASDAQ 100: +600% (1995–2000); −78% (2000–2002); median internet stock −90%+                                                                                                                          |
| Duration           | 5 years bubble; 2 years crash                                                                                                                                                                         |
| Agents Modeled     | OutcomeLearner (§4.2): bubble gains → inflated success_attribution → overconfident position sizing into continued upward deviation; crash → failure_discount reduces position reduction speed         |
| Rational Response  | ProcessEvaluator (§4.3): would have sold at +5% deviation threshold; ContrarianSkeptic (§4.4): would have resisted "internet is different" narrative                                                  |
| Simulation Mapping | Sustained positive deviation → §4.1 and §4.2 keep buying; §4.3 and §4.4 partially correct but are overwhelmed (500 vs. 800 share cap); eventual deviation collapse triggers large rational correction |

### Case 3: COVID-19 Recovery — "Obvious Rebound" Overconfidence

| Attribute          | Detail                                                                                                                                                                                                               |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Event              | S&P 500 −34% (Feb–March 2020); full recovery within 5 months (August 2020)                                                                                                                                           |
| Mechanism          | Post-recovery surveys showed high "I knew it would recover quickly" attribution despite overwhelming bearish consensus at the March 2020 trough                                                                      |
| Magnitude          | S&P 500: 3,386 (Feb 19, 2020) → 2,237 (March 23, 2020) → 3,508 (August 18, 2020)                                                                                                                                     |
| Duration           | 33-day crash; 149-day recovery                                                                                                                                                                                       |
| Agents Modeled     | HindsightOverconfident (§4.1): post-recovery → increased confidence → amplified position sizes in next volatility episode; OutcomeLearner (§4.2): attributes recovery profits to skill                               |
| Rational Response  | ProcessEvaluator (§4.3) and ContrarianSkeptic (§4.4) both would have bought at the trough deviation (-34% = strong buy signal) correctly                                                                             |
| Simulation Mapping | The rapid recovery creates a positive deviation signal; §4.1 and §4.2 interpret it as "obviously predictable continuation"; increase trade sizes; §4.3/§4.4 partially correct; VAF rises during rapid-recovery phase |

---

## §9 Variant Comparison

| Variant | Investor Logic                                 | Key Difference from Rule                              | Expected Outcome                                            |
|---------|------------------------------------------------|-------------------------------------------------------|-------------------------------------------------------------|
| Rule    | Config-driven deviation thresholds             | Baseline                                              | Strongest hindsight momentum                                |
| LLM     | LLM prompt with hindsight/outcome bias persona | Language model may partially recognize hindsight trap | Reduced momentum; higher ACI                                |
| RuleLLM | Rule logic + LLM narrative generation          | Rule logic dominates; LLM adds context                | Near-Rule behavior                                          |
| Rag     | LLM + retrieval of behavioral finance papers   | Retrieves Fischhoff (1975), Daniel et al. (1998)      | Most moderate; may self-correct after retrieving literature |
