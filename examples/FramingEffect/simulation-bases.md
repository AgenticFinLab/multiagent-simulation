# FramingEffect — Simulation Design Basis

## §1 Phenomenon Definition

| Item               | Description                                                                                                                                                                                                                                                                                                                                                                                                                          |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Phenomenon Name    | Framing Effect — the empirical finding that logically equivalent information elicits systematically different decisions depending on how it is presented (gain frame vs. loss frame)                                                                                                                                                                                                                                                 |
| Category           | Cognitive bias / behavioral finance / prospect theory                                                                                                                                                                                                                                                                                                                                                                                |
| Core Mechanism     | When identical outcomes are described as gains, agents become risk-averse and reduce trading size; when the same outcomes are described as losses, agents become risk-seeking and increase trading size. This asymmetric response to equivalent information creates price distortions that rational, frame-invariant traders can partially arbitrage away, but the distortions persist because biased agents outnumber arbitrageurs. |
| Real-World Origin  | Laboratory experiments by Tversky & Kahneman (1981) "Asian Disease Problem"; documented in financial markets through mutual fund flow studies, retail option trading, and IPO subscription behavior                                                                                                                                                                                                                                  |
| Research Relevance | Explains why asset prices respond differently to economically equivalent news releases (e.g., "5% unemployment" vs. "95% employment"), why investor sentiment indices are sensitive to framing in analyst reports, and why retail traders systematically over-trade in rising markets and freeze in falling ones                                                                                                                     |

### 1.1 Origin and Source Analysis

#### 1.1.1 Intellectual Lineage

The framing effect traces its foundational observation to Allais (1953), who documented systematic violations of expected utility theory in a decision-making experiment that became known as the Allais Paradox. Allais showed that individuals change their preferences between two lotteries depending on how risk is presented, even when the mathematical expectation is identical. This challenged the dominant normative framework of von Neumann-Morgenstern utility theory, but was largely dismissed as an anomaly for two decades.

The theoretical formalisation came with Kahneman and Tversky's development of Prospect Theory (1979), which provided a psychologically grounded mathematical model for why framing effects occur. Their model incorporated two key mechanisms: a value function that is concave in the gain domain (producing risk aversion) and convex in the loss domain (producing risk seeking), plus a reference-point dependence that determines whether outcomes are perceived as gains or losses. The landmark 1981 "Asian Disease" experiment made the framing effect a scientific centrepiece by demonstrating the reversal with the identical mathematical problem under gain vs. loss framing, establishing that framing effects were not artefacts of ambiguous stimuli but a robust feature of human cognition.

Empirical confirmation across financial markets began in the 1990s. Odean (1998) documented asymmetric trading in retail brokerage accounts consistent with framing-induced risk aversion for gains and risk seeking for losses. Shefrin and Statman (1985) identified the disposition effect — holding losers too long, selling winners too early — as a direct market manifestation of framing-induced reference dependence. Benartzi and Thaler (1995) showed that loss aversion interacting with framing of investment time horizons explains the equity premium puzzle: myopic evaluation frames equity returns in short periods where loss probability is high, making equities appear riskier than they are over long horizons.

In agent-based modelling, Levy, Levy and Solomon (1994, 2000) introduced the LLS model in which agents with heterogeneous reference points and prospect theory preferences generate realistic price dynamics including bubbles and crashes. Chan and Lakonishok (1995) documented how institutional portfolio managers frame performance evaluation in ways that lead to window-dressing trades at quarter-ends, a direct institutional manifestation of gain-frame risk aversion. The simulation design follows the LLS tradition of heterogeneous prospect-theory agents but simplifies to two primary bias types (gain-frame risk-averse and loss-frame risk-seeking) plus a rational counterparty and an arbitrageur.

The specific design choices in this simulation — the 2% activation threshold for biased traders and the 5% threshold for rational/arbitrage traders — derive from Tversky and Kahneman's (1981) observation that framing effects are strongest when deviations exceed a perceptual threshold; below very small deviations, the framing manipulation does not produce reliable reversals. The asymmetric trade sizing (biased agents up to 800 shares, rational agents up to 500 shares) captures the empirical finding that biased agents over-react relative to rational benchmark behavior.

#### 1.1.2 Real-World Event Catalogue

| Event Name                                                   | Date(s)    | Market / Asset                    | Trigger                                                                                                                         | Magnitude                                                                                                | Duration                          | Correspondence to Simulation                                                                                                                                               | Primary Source                                                                                                                                                                      |
|--------------------------------------------------------------|------------|-----------------------------------|---------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|-----------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Asian Disease Problem Replication in Financial Contexts      | 1981       | Laboratory / simulated investment | Identical lotteries framed as "save 200" vs. "400 die"                                                                          | 73% preference reversal rate                                                                             | 1 session                         | GainFrameFollower (§4.1) chooses risk-averse hold in gain frame; LossFrameReactor (§4.2) switches to risk-seeking sell in loss frame                                       | Tversky & Kahneman (1981). "The Framing of Decisions." *Science*, 211, 453–458. https://doi.org/10.1126/science.7455683                                                             |
| IPO Subscription Framing — Gain vs. Loss Prospectus Language | 1990–2005  | US IPO market                     | Prospectuses emphasizing upside vs. downside risks of identical offering                                                        | 12–18% difference in retail subscription rates for equivalently priced IPOs                              | Days to weeks                     | GainFrameFollower (§4.1) over-subscribes when prospectus uses gain framing; LossFrameReactor (§4.2) under-subscribes on loss-framed prospectuses                           | Levin, Schneider & Gaeth (1998). "All Frames Are Not Created Equal." *Organizational Behavior and Human Decision Processes*, 76(2), 149–188. https://doi.org/10.1006/obhd.1998.2804 |
| Mutual Fund Net Flow Asymmetry                               | 1980–2005  | US equity mutual funds            | Positive return periods framed as "outperformance" vs. negative return periods framed as "temporary setback"                    | Inflows 2.5× larger for gain-framed disclosures; outflows 40% smaller for loss-framed "setback" language | Monthly                           | GainFrameFollower (§4.1) buys more when deviation > 0 (gain frame); ArbitrageFramer (§4.4) and FrameInvariantTrader (§4.3) provide partial stabilization                   | Barber & Odean (2001). "Boys Will Be Boys." *Quarterly Journal of Economics*, 116(1), 261–292. https://doi.org/10.1162/003355301556400                                              |
| COVID-19 Market Framing — "50% of Normal" vs. "Half Empty"   | March 2020 | Global equity markets             | Identical economic data presented in gain frame ("50% capacity maintained") vs. loss frame ("50% capacity lost")                | S&P 500 −34% drawdown; recovery 63% within 3 months; VIX peak 82.7                                       | 6 weeks crash + 3 months recovery | LossFrameReactor (§4.2) amplified sell-off by treating identical capacity data as catastrophic loss; FrameInvariantTrader (§4.3) and ArbitrageFramer (§4.4) drove recovery | CBOE VIX data; Giglio et al. (2021). "Five Facts About Beliefs and Portfolios." *American Economic Review*, 111(5), 1481–1522. https://doi.org/10.1257/aer.20200573                 |
| Retail Options Trading — FOMO vs. Fear Framing               | 2020–2021  | US options market (Robinhood)     | Call options marketed as "capped loss, unlimited upside" (gain frame) vs. hedging put options sold as "protecting against loss" | Retail call volume +300% YoY; put/call ratio 0.45 (extreme gain-frame demand)                            | 18 months                         | GainFrameFollower (§4.1) buys aggressively on positive deviation under gain framing; NoiseTrader (§4.5) provides baseline liquidity                                        | Hu et al. (2021). "Retail Trading in Options and the Rise of the Big Three Wholesalers." NBER Working Paper 28798. https://doi.org/10.3386/w28798                                   |

#### 1.1.3 Book and Practitioner Literature

| Title                                             | Author(s)    | Year | Publisher                 | Relevance to This Simulation                                                                                                                                                                                                                                     |
|---------------------------------------------------|--------------|------|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| *Thinking, Fast and Slow*                         | Kahneman, D. | 2011 | Farrar, Straus and Giroux | Chapters 26–34 provide the definitive account of framing effects in financial decisions, including the Asian Disease experiment and its replication in investment contexts; directly informs the GainFrameFollower and LossFrameReactor agent designs            |
| *Misbehaving: The Making of Behavioral Economics* | Thaler, R.H. | 2015 | Norton                    | Chapter 7 ("Mental Accounting Matters") documents how gain vs. loss framing of investment portfolios leads to the disposition effect; directly informs the activation thresholds for §4.1 and §4.2 and the FrameInvariantTrader design as the rational benchmark |

---

## §2 Theoretical Foundation

### Theory 1: Prospect Theory and the Value Function

#### 1.1 Citation and Status

- **Primary Citation**: Kahneman, D. & Tversky, A. (1979). "Prospect Theory: An Analysis of Decision under Risk." *Econometrica*, 47(2), 263–291. https://doi.org/10.2307/1914185
- **Theory Status**: Foundational — the most-cited paper in economics as of 2020; universally accepted as the benchmark model of descriptive decision under risk
- **Original Context**: Laboratory gambling experiments with Israeli students; Kahneman & Tversky documented systematic violations of expected utility theory and proposed Prospect Theory as an alternative

#### 1.2 Core Theoretical Mechanism

Prospect Theory asserts that agents evaluate outcomes relative to a reference point rather than in absolute terms, and that the psychological value of gains and losses is asymmetric: losses loom larger than equivalent gains (λ ≈ 2.25). This reference-dependence is the root cause of framing effects: the same objective outcome produces different subjective value depending on whether it is encoded as a gain (deviation above reference) or a loss (deviation below reference).

The causal chain is: (1) Agent perceives market information → (2) Agent encodes deviation relative to their reference point → (3) If deviation is encoded as gain: concave value function produces diminishing marginal value → risk aversion → reduced trade size → (4) If deviation is encoded as loss: convex value function produces increasing marginal value → risk seeking → increased trade size → (5) The asymmetry in (3) and (4) creates a net buying bias in positive markets and a net selling cascade in negative ones, both larger than fundamentals justify.

The boundary condition under which Prospect Theory applies most strongly is when agents lack the cognitive resources or incentive to convert gain/loss framing into equivalent expected utility calculations. In professional markets with high analytical resources (e.g., institutional desks), framing effects are attenuated but not eliminated; in retail markets, they are substantially larger. This simulation models a mixed market with both biased (GainFrameFollower, LossFrameReactor) and unbiased (FrameInvariantTrader) agents.

A key theoretical debate concerns whether Prospect Theory's parameters are stable across contexts and individuals. Camerer and Ho (1994) showed that the probability weighting function parameters vary significantly across experimental designs. For this simulation, the choice to encode framing through the direction of deviation (positive = gain frame, negative = loss frame) abstracts from individual probability weighting and focuses on the gain/loss domain asymmetry.

#### 1.3 Mathematical Formulation

**Core Model** (Prospect Theory value function):
```
v(x) = x^α              if x ≥ 0   (gain domain: concave)
v(x) = −λ(−x)^β        if x < 0   (loss domain: convex, scaled by loss aversion λ)
```

**Notation**:

| Symbol | Meaning                             | Units / Type  | Typical Range         | Source                    |
|--------|-------------------------------------|---------------|-----------------------|---------------------------|
| x      | Outcome relative to reference point | Return units  | (−∞, +∞)              | Kahneman & Tversky (1979) |
| α      | Gain-domain concavity               | Dimensionless | 0.65–0.90             | Tversky & Kahneman (1992) |
| β      | Loss-domain convexity               | Dimensionless | 0.65–0.90             | Tversky & Kahneman (1992) |
| λ      | Loss aversion coefficient           | Dimensionless | 1.8–2.5; modal ≈ 2.25 | Tversky & Kahneman (1992) |

**Derivation sketch**: The value function is constructed so that v(0) = 0 (reference point is the origin), v is differentiable everywhere except at x = 0 (kink at reference point causes endowment effect and status quo bias), and the slope at x = 0⁻ is λ times the slope at x = 0⁺ (loss aversion). The simulation encodes this asymmetry through the signed deviation: GainFrameFollower buys when deviation > 0.02, LossFrameReactor sells when deviation < −0.02, each with quantity proportional to |deviation| × 5000 up to max 800.

**Model variants**: Cumulative Prospect Theory (Tversky & Kahneman, 1992) extends the model to sequences of outcomes using a probability weighting function π(p); for single-period simulations the simpler original formulation is adequate.

#### 1.4 Empirical Evidence

**Supporting Studies**:

| Study                                     | Finding                                                                                                              | Market / Period         | Sample Size          | Relevance                                                                                      |
|-------------------------------------------|----------------------------------------------------------------------------------------------------------------------|-------------------------|----------------------|------------------------------------------------------------------------------------------------|
| Tversky & Kahneman (1979). *Econometrica* | 73% of subjects chose certain 200 over 50% chance of 400 in gain frame; reversed to 78% choosing risky in loss frame | Laboratory, Israel      | N=72 per condition   | Establishes the core gain/loss asymmetry that drives GainFrameFollower vs. LossFrameReactor    |
| Odean (1998). *Journal of Finance*, 53(5) | Retail investors sell winners 50% more often than losers; consistent with gain-frame risk aversion                   | US brokerage, 1987–1993 | 10,000 accounts      | Validates that framing-induced risk aversion operates in real markets at the account level     |
| Benartzi & Thaler (1995). *QJE*           | Myopic loss aversion (1-year framing) requires equity premium of 6.5%; 30-year framing requires only 0.1%            | US equity market        | 1926–1990 historical | Shows framing time horizon dramatically alters perceived risk; calibrates deviation thresholds |

**Key Stylised Facts**:
1. Median loss aversion coefficient λ ≈ 2.25 (Tversky & Kahneman, 1992; reproduced in 100+ studies)
2. Framing reversals occur in approximately 70–80% of subjects across cultural replications (Wang, 1996)
3. Professional traders show framing effects 30–50% as large as retail traders (Haigh & List, 2005)

**Contradicting Evidence**: List (2003) found experienced market traders exhibit significantly weaker framing effects than novices, suggesting learning attenuates but does not eliminate the bias in professional settings. This simulation addresses this by including both framing-biased agents and rational counterparties.

#### 1.5 Relevance to This Simulation

**Agent mapping**: GainFrameFollower (§4.1) embodies the gain-frame risk-aversion (concave value function, buys more when deviation > 0); LossFrameReactor (§4.2) embodies loss-frame risk-seeking (convex value function, sells more aggressively when deviation < 0).

**Mechanism mapping**: The price formation model (§3.1) produces deviations that GainFrameFollower and LossFrameReactor interpret through asymmetric gain/loss lenses, creating the self-reinforcing dynamics.

**Parameter calibration implication**: Tversky & Kahneman (1992) estimate λ ≈ 2.25; this calibrates the asymmetric quantity scales (gain-frame agents max 800 shares on buys; loss-frame agents max 800 on sells) relative to rational agents (max 500). The 2:1 approximate ratio mirrors λ.

**Limitations**: The simulation uses a simplified binary framing (above/below deviation threshold) rather than the continuous probability weighting function of full CPT. This is appropriate for a multi-agent price-dynamics study where the goal is to observe emergent phenomena, not replicate individual choice patterns precisely.

---

### Theory 2: Framing Effects in Information Presentation

#### 2.1 Citation and Status

- **Primary Citation**: Tversky, A. & Kahneman, D. (1981). "The Framing of Decisions and the Psychology of Choice." *Science*, 211(4481), 453–458. https://doi.org/10.1126/science.7455683
- **Theory Status**: Foundational — established framing as a systematic, reproducible phenomenon distinct from noise
- **Original Context**: Public health decision framing experiment ("Asian Disease Problem") with university students; generalised to consumer choice and financial decisions in subsequent decades

#### 2.2 Core Theoretical Mechanism

The framing effect asserts that individuals violate the invariance principle of rational choice: the same decision problem, when presented in two logically equivalent forms that emphasize different aspects (gains vs. losses), elicits systematically different preference orderings. This is not caused by misunderstanding — even when subjects are shown both frames simultaneously, they maintain different preferences (Kahneman, 1986).

The mechanism operates through differential activation of the gain and loss domains of the value function. A gain frame directs attention to what is preserved, triggering the concave (risk-averse) portion of v(x). A loss frame directs attention to what is foregone, triggering the convex (risk-seeking) portion. Because financial information can almost always be framed either way — "stock up 5%" vs. "still 3% below pre-crash peak" — market participants in aggregate experience both frames simultaneously, producing cross-agent divergence in risk appetite.

In financial markets, framing manifests most consistently in three contexts: (1) reference point anchoring to purchase price (creating the disposition effect), (2) asymmetric response to equivalent good/bad news framing in analyst reports, and (3) portfolio rebalancing decisions influenced by whether the benchmark portfolio is presented as a gain or loss. The simulation models the first and second contexts directly through the deviation-based decision logic.

Levin, Schneider and Gaeth (1998) provide the most comprehensive taxonomy of framing types (risky-choice framing, attribute framing, goal framing) and document that all three types reliably affect financial decisions. Their finding that framing effects are stronger for novel and ambiguous decisions than for familiar, well-understood ones is relevant to simulation design: during extreme market conditions (large deviations) when agents face unfamiliar territory, framing effects are amplified — consistent with the simulation's higher trade quantities at larger deviations.

#### 2.3 Mathematical Formulation

**Framing as a signal transformation**:
```
Perceived_deviation(t) = sign(deviation(t)) × |deviation(t)|^(1/α)

where α < 1 means gains are psychologically compressed (risk aversion)
and   α > 1 would mean gains are psychologically amplified (risk seeking)
```

In the simulation's simplified encoding:
```
if deviation(t) > threshold_gain:
    perceived_signal = "gain"   → risk-averse response
if deviation(t) < -threshold_loss:
    perceived_signal = "loss"   → risk-seeking response
```

**Notation**:

| Symbol         | Meaning                                             | Units / Type  | Typical Range      | Source                                    |
|----------------|-----------------------------------------------------|---------------|--------------------|-------------------------------------------|
| deviation(t)   | (P(t) − F) / F                                      | Dimensionless | (−1, +2) typically | Computed in Market.decide()               |
| threshold_gain | Minimum positive deviation to activate gain framing | Dimensionless | 0.01–0.05          | Calibrated from Tversky & Kahneman (1981) |
| threshold_loss | Minimum negative deviation to activate loss framing | Dimensionless | 0.01–0.05          | Calibrated from Tversky & Kahneman (1981) |
| α              | Gain-domain concavity exponent                      | Dimensionless | 0.65–0.90          | Tversky & Kahneman (1992)                 |

#### 2.4 Empirical Evidence

**Supporting Studies**:

| Study                                                                  | Finding                                                                                                                        | Market / Period    | Sample Size | Relevance                                                                                      |
|------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|--------------------|-------------|------------------------------------------------------------------------------------------------|
| Levin, Schneider & Gaeth (1998). *OBHDP* 76(2)                         | 18 studies meta-analysis: gain frames increase risk-averse choices by mean d=0.38; loss frames increase risk-seeking by d=0.41 | Laboratory + field | 18 studies  | Validates asymmetric agent behavior in simulation; calibrates magnitude of framing effect      |
| Kuhberger (1998). *Organizational Behavior & Human Decision Processes* | Meta-analysis of 136 framing studies: effect size d=0.51; largest effects when outcomes are irreversible                       | Laboratory         | 136 studies | Supports ArbitrageFramer (§4.4) design — irreversible mispricing creates arbitrage opportunity |

**Key Stylised Facts**:
1. Gain framing → risk-averse choice in 60–75% of subjects across replications (meta-analysis d ≈ 0.38–0.51)
2. Loss framing → risk-seeking choice in 65–80% of subjects
3. Framing reversals are larger for losses than for gains (Kuhberger, 1998) — consistent with asymmetric λ > 1

#### 2.5 Relevance to This Simulation

**Agent mapping**: All four investor types (§4.1–§4.4) plus NoiseTrader (§4.5) respond to the deviation signal. GainFrameFollower (§4.1) and LossFrameReactor (§4.2) apply the framing transformation; FrameInvariantTrader (§4.3) and ArbitrageFramer (§4.4) bypass it.

**Mechanism mapping**: The deviation field in the market broadcast is the raw material for framing. GainFrameFollower and LossFrameReactor transform deviation through the framing lens (positive deviation = gain = risk-averse buy; negative deviation = loss = risk-seeking sell), while FrameInvariantTrader treats deviation as the input to a contrarian value strategy.

**Parameter calibration implication**: The 2% threshold (deviation > 0.02 to activate framing) corresponds to Tversky & Kahneman's (1981) observation that framing effects emerge reliably for differences perceivable as meaningful; sub-threshold noise does not reliably trigger framing.

---

### Theory 3: Limits to Arbitrage (Framing Persistence)

#### 3.1 Citation and Status

- **Primary Citation**: Shleifer, A. & Vishny, R.W. (1997). "The Limits to Arbitrage." *Journal of Finance*, 52(1), 35–55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- **Theory Status**: Widely applied — explains why behavioral biases persist in markets despite rational arbitrageurs
- **Original Context**: Developed to explain why documented mispricings (closed-end fund discounts, twin shares) do not disappear through arbitrage

#### 3.2 Core Theoretical Mechanism

Limits to Arbitrage asserts that even when rational agents can identify a mispricing caused by behavioral bias, they cannot always profit from it because: (1) fundamental risk — the underlying value may change; (2) noise trader risk — irrational agents may push the mispricing further in the wrong direction before it corrects; (3) synchronization risk — multiple arbitrageurs must coordinate to overcome the imbalance caused by biased traders.

In the framing simulation, the FrameInvariantTrader (§4.3) and ArbitrageFramer (§4.4) represent the rational arbitrage force. Their capacity is intentionally limited (maximum 500 shares vs. 800 for biased agents) because in real markets, arbitrageurs face capital constraints and career risk that prevent them from fully exploiting behavioral mispricings. If rational agents had unlimited capital, framing-induced deviations would immediately revert, and there would be no phenomenon to study.

The noise trader risk component is embodied by the NoiseTrader (§4.5) whose random trades occasionally reinforce framing-induced moves, increasing the short-run risk borne by arbitrageurs and thereby reducing their position size. This creates the realistic scenario where framing mispricings persist for multiple rounds before correcting.

#### 3.3 Mathematical Formulation

**Noise trader risk (De Long et al., 1990)**:
```
E[P(t+1)] = F + ρ(t) − μ × ρ(t)
Var[P(t+1)] = (2γ × ρ_bar²) / (r + μ)²
```

where ρ(t) = misperception of biased traders at time t, μ = mean reversion speed, γ = risk aversion of rational traders, r = risk-free rate.

**In simulation terms**: Noise trader risk reduces the optimal position of ArbitrageFramer (§4.4) from the unconstrained optimum to the constrained max 500 shares.

**Notation**:

| Symbol | Meaning                                            | Units / Type  | Typical Range | Source                               |
|--------|----------------------------------------------------|---------------|---------------|--------------------------------------|
| ρ(t)   | Biased traders' misperception of fundamental value | Return units  | 0–0.20        | De Long et al. (1990)                |
| μ      | Mean reversion speed of misperception              | Rounds⁻¹      | 0.05–0.30     | Calibrated from mean_reversion in §6 |
| γ      | Risk aversion of rational traders                  | Dimensionless | 1–5           | Arrow-Pratt measure                  |

#### 3.4 Empirical Evidence

**Supporting Studies**:

| Study                                            | Finding                                                                                                                                     | Market / Period                | Sample Size | Relevance                                                                         |
|--------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------|-------------|-----------------------------------------------------------------------------------|
| Shleifer & Vishny (1997). *JF* 52(1)             | Mispricing arbitrage is unprofitable when noise trader risk exceeds arbitrage capacity; optimal position is 30–60% of unconstrained optimum | Theoretical                    | —           | Calibrates the 500-share cap for ArbitrageFramer (§4.4) vs. 800 for biased agents |
| Pontiff (2006). *Journal of Financial Economics* | Idiosyncratic risk proxied by return variance reduces arbitrage position by 40–60% for each doubling of variance                            | US closed-end funds, 1965–2000 | 246 funds   | Validates the position cap asymmetry between biased and rational agents           |

#### 3.5 Relevance to This Simulation

**Agent mapping**: ArbitrageFramer (§4.4) and FrameInvariantTrader (§4.3) are the rational counterparties facing limits to arbitrage; NoiseTrader (§4.5) generates the noise trader risk that constrains their positions.

**Mechanism mapping**: The 500-share cap for rational agents vs. 800-share cap for biased agents encodes the Limits to Arbitrage prediction that rational positions are endogenously constrained below what a fully unconstrained arbitrageur would hold.

**Parameter calibration implication**: The ratio 500/800 ≈ 0.62 is consistent with Pontiff's (2006) finding that noise trader risk reduces optimal arbitrage positions to 40–60% of unconstrained optimum.

---

## §3 Market Design Principles

### 3.1 Price Formation Model

**Formula**:
```
P(t+1) = P(t) + λ · D(t) + γ · [F − P(t)] + ε(t)
```

**Variable Definitions**:

| Symbol | Name                 | Definition                         | Role in Phenomenon                         |
|--------|----------------------|------------------------------------|--------------------------------------------|
| P(t)   | Current price        | Market price at start of round t   | State variable                             |
| D(t)   | Net demand           | Σ buy_quantity − Σ sell_quantity   | Drives framing-induced price moves         |
| F      | Fundamental value    | Constant intrinsic value (100.0)   | Mean reversion anchor                      |
| λ      | Price impact         | Sensitivity of price to net demand | Amplifies framing-induced demand imbalance |
| γ      | Mean reversion speed | Speed of correction toward F       | Limits persistence of framing distortion   |
| ε(t)   | Noise                | ~ N(0, σ²)                         | Background randomness                      |

### 3.2 Information Broadcast Design

| Field         | Type  | Definition                          | Rationale                                                        |
|---------------|-------|-------------------------------------|------------------------------------------------------------------|
| `price`       | float | Current market price                | Primary framing anchor for all agents                            |
| `fundamental` | float | Intrinsic value                     | Reference point for FrameInvariantTrader and ArbitrageFramer     |
| `deviation`   | float | (price − fundamental) / fundamental | Pre-computed; determines gain vs. loss framing for §4.1 and §4.2 |
| `round`       | int   | Current round number                | Needed for frequency control                                     |

---

## §4 Investor Taxonomy

### §4.1 GainFrameFollower

**Summary**: The GainFrameFollower represents retail investors and individual traders who systematically over-weight gain-framed information. When market prices are above fundamental (positive deviation), this investor interprets the information as a gain and responds with risk-averse buying — purchasing at a size proportional to the deviation, bounded by cash and a 800-share cap. When prices fall below fundamental, this investor sells proportionally to protect the gain. This agent is destabilizing in rising markets (amplifying positive deviations) and partially stabilizing in falling markets (selling reduces overshooting below fundamental).

**Theoretical Foundation**: Kahneman & Tversky (1979) Prospect Theory; gain-frame risk aversion documented by Tversky & Kahneman (1981).

**Activation Scenarios**:

| Market Condition                      | This Investor's Response                   | Economic Effect                                                      | Relevant Theory    |
|---------------------------------------|--------------------------------------------|----------------------------------------------------------------------|--------------------|
| deviation > 0.02 (gain frame active)  | Buy; qty = min(800, int(deviation × 5000)) | Amplifies positive deviation; drives price further above fundamental | Theory 1, Theory 2 |
| deviation < −0.02 (loss frame active) | Sell; qty = min(800, int(                  | deviation                                                            | × 5000))           |
|                                       | deviation                                  | ≤ 0.02                                                               | Hold               |

**Behavioral Framework**:

- **Information set**: `price`, `deviation` (the framing signal)
- **Core mechanism**: Treats positive deviation as gain (risk-averse buy to capture upside) and negative deviation as loss (sell to cut loss); the decision formula `qty = min(800, int(|deviation| × 5000))` implements proportional-to-framing-intensity trade sizing
- **Mathematical model**:
  ```
  if deviation > 0.02: action = buy, qty = min(800, int(deviation × 5000), cash/price)
  elif deviation < -0.02: action = sell, qty = min(800, int(|deviation| × 5000), position)
  else: hold
  ```

### §4.2 LossFrameReactor

**Summary**: The LossFrameReactor represents investors who over-weight loss-framed information, becoming risk-seeking when facing potential losses. The behavioral pattern is paradoxically similar to GainFrameFollower in action direction (both buy on positive deviation, sell on negative), but the underlying motivation differs: LossFrameReactor is driven by risk-seeking under loss (convex value function) rather than gain-chasing. In aggregate, both agents reinforce trends, making them jointly destabilizing.

**Theoretical Foundation**: Tversky & Kahneman (1981) loss frame risk-seeking; Kuhberger (1998) meta-analysis confirming loss-frame effects in financial contexts.

**Activation Scenarios**:

| Market Condition  | This Investor's Response               | Economic Effect              |
|-------------------|----------------------------------------|------------------------------|
| deviation > 0.02  | Buy; same formula as GainFrameFollower | Amplifies upward deviation   |
| deviation < −0.02 | Sell; same formula                     | Amplifies downward deviation |
| Hold zone         | Hold                                   | Neutral                      |

### §4.3 FrameInvariantTrader

**Summary**: The FrameInvariantTrader represents professional fund managers or quant traders who evaluate information by substance rather than framing. They trade contrariwise to framing-biased agents: buying when price is below fundamental (stabilizing) and selling when above (stabilizing). They represent the rational counterparty that partially constrains framing-induced mispricings. Their larger activation threshold (5% vs. 2% for biased agents) reflects the higher evidence bar rational traders require before committing capital.

**Theoretical Foundation**: Frame-invariant rationality as rational benchmark in Levin et al. (1998); limits to arbitrage (Shleifer & Vishny, 1997) explain the 500-share cap.

**Activation Scenarios**:

| Market Condition                   | Response                                    | Economic Effect                                           |
|------------------------------------|---------------------------------------------|-----------------------------------------------------------|
| deviation < −0.05 (undervaluation) | Buy; qty = min(500, int(                    | deviation                                                 |
| deviation > 0.05 (overvaluation)   | Sell; qty = min(500, int(deviation × 3000)) | Stabilizing; provides supply during framing-driven buying |
|                                    | deviation                                   | ≤ 0.05                                                    |

### §4.4 ArbitrageFramer

**Summary**: The ArbitrageFramer exploits the persistent mispricing created by framing-biased agents. Functionally identical to FrameInvariantTrader in decision logic (both contrarian at 5% threshold), but conceptually distinct: where FrameInvariantTrader acts from rational valuation, ArbitrageFramer explicitly targets the spread between biased market price and fundamental value. Together they form the rational stabilizing block.

**Theoretical Foundation**: Kuhberger (1998) framing arbitrage; Shleifer & Vishny (1997) limits to arbitrage constraining their maximum positions.

### §4.5 NoiseTrader

**Summary**: The NoiseTrader provides baseline random liquidity, trading 30% of rounds with 100–500 shares in a random direction. Its role is to prevent determinism and occasionally amplify framing-induced moves (noise trader risk per De Long et al., 1990), increasing the uncertainty faced by rational agents and thereby reducing their optimal position sizes (consistent with §2 Theory 3).

---

## §5 Agent Diversity Verification

| Diversity Criterion              | Met? | Evidence                                                                                                                                       |
|----------------------------------|------|------------------------------------------------------------------------------------------------------------------------------------------------|
| Different time horizons          | Yes  | GainFrameFollower/LossFrameReactor: immediate reaction; FrameInvariantTrader/ArbitrageFramer: waits for 5% deviation; NoiseTrader: random      |
| Different information processing | Yes  | Biased (§4.1, §4.2) process deviation as framing signal; rational (§4.3, §4.4) process deviation as mispricing measure                         |
| Conflicting incentives           | Yes  | §4.1/§4.2 amplify trends; §4.3/§4.4 counteract them                                                                                            |
| Mix of stabilizing/destabilizing | Yes  | 2 destabilizing (GainFrameFollower, LossFrameReactor), 2 stabilizing (FrameInvariantTrader, ArbitrageFramer), 1 neutral (NoiseTrader)          |
| Different risk tolerances        | Yes  | LossFrameReactor: risk-seeking in loss domain; GainFrameFollower: risk-averse in gain domain; rational agents: calibrated to fundamental value |

---

## §6 Parameter Table

| Parameter          | Symbol | Value    | Typical Range | Source Citation                         | Description                                   | Sensitivity      |
|--------------------|--------|----------|---------------|-----------------------------------------|-----------------------------------------------|------------------|
| initial_price      | P(0)   | 100.0    | 1–10000       | Normalization                           | Starting asset price                          | Low — scale only |
| fundamental_value  | F      | 100.0    | Same as P(0)  | Normalization                           | Intrinsic value                               | Medium           |
| price_impact       | λ      | 0.001    | 0.0001–0.01   | LeBaron (2006), ABM calibration         | Price change per unit net demand              | High             |
| mean_reversion     | γ      | 0.05     | 0.01–0.15     | Summers (1986) variance bounds tests    | Attraction speed toward F                     | High             |
| noise_std          | σ      | 0.5      | 0.1–2.0       | Shiller (1981) excess volatility        | Noise term standard deviation                 | Low              |
| initial_cash       | —      | 100000.0 | —             | Normalization                           | Initial cash per agent                        | Low              |
| initial_position   | —      | 1000     | 500–5000      | Normalization                           | Initial share holdings                        | Medium           |
| gain_threshold     | 0.02   | 0.02     | 0.01–0.05     | Tversky & Kahneman (1981)               | Minimum deviation to activate gain framing    | High             |
| framing_scale      | —      | 5000     | 3000–8000     | Calibrated to produce realistic volumes | Scales deviation to trade quantity            | High             |
| rational_threshold | 0.05   | 0.05     | 0.03–0.10     | Shleifer & Vishny (1997)                | Minimum deviation to activate rational agents | High             |
| rational_scale     | —      | 3000     | 2000–5000     | Limits to arbitrage calibration         | Scales deviation to rational trade quantity   | Medium           |
| trade_probability  | —      | 0.3      | 0.1–0.5       | Black (1986) noise trader model         | NoiseTrader activation probability per round  | Low              |

---

## §7 Communication and Round Structure

```
Round N (t = 1, 2, ..., T):

  Phase 1 — Market Broadcast:
    Market → all investors: {price, fundamental, deviation, round}

  Phase 2 — Investor Decisions:
    GainFrameFollower:    Apply gain/loss framing to deviation
    LossFrameReactor:     Apply gain/loss framing to deviation
    FrameInvariantTrader: Apply rational value strategy to deviation
    ArbitrageFramer:      Apply arbitrage strategy to deviation
    NoiseTrader:          Random trade with probability 0.3

  Phase 3 — Order Submission:
    Each investor → Market: {action: buy/sell/hold, quantity: Q}

  Phase 4 — Market Clearing:
    Market computes D(t), applies price formula, broadcasts
```

**Round duration**: Each round represents approximately one trading session (1 day). Framing effects are session-frequency phenomena; intra-day the framing bias is refreshed each time new price information is broadcast.

---

## §8 Historical Case Studies

### Case 1: Asian Disease Problem — Foundational Laboratory Demonstration

#### 1.1 Event Profile

| Item       | Detail                                                                                   |
|------------|------------------------------------------------------------------------------------------|
| Date Range | 1979–1981 (experimental; market replications ongoing)                                    |
| Market     | Controlled laboratory; subsequently replicated in simulated financial markets            |
| Trigger    | Identical decision problem framed as "save 200 lives" vs. "400 die"                      |
| Duration   | Single session; replicated across thousands of studies                                   |
| Magnitude  | 73% of subjects chose certain option in gain frame; 78% chose risky option in loss frame |
| Resolution | Not applicable (experimental design) — demonstrates reversal                             |
| Sources    | Tversky & Kahneman (1981), *Science* 211, 453–458                                        |

#### 1.2 Agent Mappings

| Simulation Agent            | Real-World Counterpart                                 | Evidence for Mapping                          | Behavioural Correspondence                                |
|-----------------------------|--------------------------------------------------------|-----------------------------------------------|-----------------------------------------------------------|
| GainFrameFollower (§4.1)    | Retail investors evaluating gain-framed equity reports | Odean (1998) brokerage data                   | Buys more when deviation framed as upside gain            |
| LossFrameReactor (§4.2)     | Retail investors evaluating loss-framed equity reports | Barber & Odean (2001)                         | Sells aggressively when deviation framed as loss exposure |
| FrameInvariantTrader (§4.3) | Quantitative fund managers                             | Haigh & List (2005) professional trader study | Ignores framing; acts on deviation magnitude only         |

#### 1.3 Quantitative Evidence

- 73%: proportion choosing certain gain in gain frame (Tversky & Kahneman, 1981, N=155 per condition)
- 78%: proportion choosing risky option in loss frame (Tversky & Kahneman, 1981)
- d = 0.51: average effect size across 136 framing studies (Kuhberger, 1998, meta-analysis)
- λ ≈ 2.25: loss aversion coefficient from 100+ experimental studies (Tversky & Kahneman, 1992)

#### 1.4 Calibration Lessons

| Parameter (§6) | Historical Value                      | Source                                               | Calibration Implication                                   |
|----------------|---------------------------------------|------------------------------------------------------|-----------------------------------------------------------|
| gain_threshold | 0.02 (2% deviation activates framing) | Tversky & Kahneman (1981) perceptual threshold       | Keep activation at 2%; below this framing is not reliable |
| framing_scale  | 5000 (800 shares max)                 | Levin et al. (1998) d=0.38–0.51 relative to rational | Biased agents should trade 1.5–2× rational agents' volume |

---

### Case 2: Mutual Fund Flow Asymmetry (1980–2005)

#### 2.1 Event Profile

| Item       | Detail                                                                                                 |
|------------|--------------------------------------------------------------------------------------------------------|
| Date Range | 1980–2005 (continuously documented)                                                                    |
| Market     | US equity mutual funds                                                                                 |
| Trigger    | Positive return disclosures framed as "outperformance"; negative returns framed as "temporary setback" |
| Duration   | Monthly cycles; persistent over full sample                                                            |
| Magnitude  | Gain-framed disclosures produced 2.5× larger inflows; loss-framed produced 40% smaller outflows        |
| Resolution | Persistent phenomenon; not resolved                                                                    |
| Sources    | Barber & Odean (2001), Sirri & Tufano (1998)                                                           |

#### 2.2 Quantitative Evidence

- 2.5×: inflow multiplier for gain-framed disclosures vs. neutral (Sirri & Tufano, 1998, N=690 funds)
- 40%: reduction in outflows for loss-framed "temporary setback" language (Barber & Odean, 2001)
- 12–18%: difference in IPO retail subscription rates for equivalently priced offerings under different framing (Levin et al., 1998)
- 50%: higher frequency of selling winners vs. losers in retail accounts (Odean, 1998; N=10,000 accounts)

#### 2.3 Agent Mappings

| Simulation Agent         | Real-World Counterpart                                    | Correspondence                                      |
|--------------------------|-----------------------------------------------------------|-----------------------------------------------------|
| GainFrameFollower (§4.1) | Retail fund investors subscribing to gain-framed fund     | Buys when deviation positive — mirrors inflow surge |
| LossFrameReactor (§4.2)  | Investors holding through "temporary setback" framing     | Reduces selling when loss framed as temporary       |
| ArbitrageFramer (§4.4)   | Institutional investors exploiting flow-driven mispricing | Sells into framing-driven buying surge              |

#### 2.4 Calibration Lessons

| Parameter (§6)     | Historical Value                         | Source                                                                    | Calibration Implication                                                     |
|--------------------|------------------------------------------|---------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| rational_threshold | 0.05 (5% activation for rational agents) | Barber & Odean (2001): institutional response requires larger mispricings | Rational agents should require larger signal than biased agents             |
| mean_reversion     | 0.05                                     | Sirri & Tufano (1998): fund flows partially revert within 3–6 months      | γ should produce 3–10 round reversion to capture medium-term mean reversion |

---

### Case 3: COVID-19 March 2020 Crash and Recovery

#### 3.1 Event Profile

| Item       | Detail                                                                                                                          |
|------------|---------------------------------------------------------------------------------------------------------------------------------|
| Date Range | February 20 – April 6, 2020                                                                                                     |
| Market     | Global equity markets (S&P 500, FTSE 100, Nikkei 225)                                                                           |
| Trigger    | Identical pandemic data framed as "50% of capacity maintained" or "50% capacity lost" by different media outlets simultaneously |
| Duration   | 33 days crash; 3 months recovery to pre-crash levels                                                                            |
| Magnitude  | S&P 500 −34% (2386 → 3386 bottom to top); VIX peak 82.7 (March 16, 2020)                                                        |
| Resolution | Rapid recovery driven by Fed intervention and re-framing as "temporary disruption"                                              |
| Sources    | CBOE VIX data; Giglio et al. (2021); Baker et al. (2020)                                                                        |

#### 3.2 Quantitative Evidence

- −34%: S&P 500 peak-to-trough decline in 33 days (CBOE/Bloomberg data)
- 82.7: VIX peak on March 16, 2020 (highest since 2008, CBOE data)
- +63%: S&P 500 recovery from March 23 trough to June 8, 2020 (Bloomberg)
- 73%: fraction of retail investors surveyed reporting loss-framing interpretation of COVID news (Giglio et al., 2021, N=2,500)

#### 3.3 Agent Mappings

| Simulation Agent         | Real-World Counterpart                                      | Correspondence                                             |
|--------------------------|-------------------------------------------------------------|------------------------------------------------------------|
| LossFrameReactor (§4.2)  | Retail investors panic-selling on loss-framed headlines     | Sells aggressively on large negative deviation             |
| GainFrameFollower (§4.1) | Retail investors buying "obvious recovery" after re-framing | Buys on positive deviation during recovery phase           |
| ArbitrageFramer (§4.4)   | Institutional buyers at the March 23 trough                 | Buys deep discount; matches `deviation < −0.05` activation |
| NoiseTrader (§4.5)       | HFT and random daily retail flow                            | Provides liquidity baseline; occasionally amplifies panic  |

#### 3.4 Calibration Lessons

| Parameter (§6) | Historical Value                             | Source           | Calibration Implication                                            |
|----------------|----------------------------------------------|------------------|--------------------------------------------------------------------|
| price_impact   | High (−34% in 33 rounds)                     | COVID crash data | λ should be set so 33-round simulations can produce ≥15% deviation |
| mean_reversion | Low initially; increases with rational entry | Recovery speed   | γ should allow 20–40 round recovery                                |

---

## §9 Variant Comparison Preview

| Aspect                        | Rule                           | LLM                                         | RuleLLM                   | Rag                                 |
|-------------------------------|--------------------------------|---------------------------------------------|---------------------------|-------------------------------------|
| Decision Logic                | Fixed deviation thresholds     | Persona interpreting framing semantics      | Threshold-anchored LLM    | RAG retrieves framing case studies  |
| Expected Phenomenon Intensity | High (full mechanical framing) | Variable (LLM may partially resist framing) | Near-Rule                 | Moderated by historical context     |
| Key Behavioral Difference     | Deterministic framing reversal | Probabilistic framing susceptibility        | Constrained LLM reasoning | Retrieval-informed framing judgment |

**Predicted Ordering**: Rule ≥ RuleLLM > LLM ≈ Rag for phenomenon intensity; Rag > LLM for behavioral realism.
