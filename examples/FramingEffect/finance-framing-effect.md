# FramingEffect — Scenario Target

## §1 Meta

| Field         | Content                                                |
|---------------|--------------------------------------------------------|
| Name          | FramingEffect                                          |
| Domain        | finance                                                |
| Requested By  | a77                                                    |
| Produced By   | polish-simulation-pipeline.md (reverse-reconstruct)    |
| Created       | 2026-07-17                                             |
| Pipeline      | masim/skills/polish-simulation-pipeline.md             |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.0) |
| Status        | released                                               |

## §2 Phenomenon Statement

### §2.1 Trigger

The phenomenon is triggered when market information conveying the same objective content is presented in two logically equivalent frames — a gain frame ("price up 5% from purchase") and a loss frame ("price still 3% below peak"). Investors who lack the cognitive resources or incentive to convert between frames respond asymmetrically: gain framing induces risk-averse buying, loss framing induces risk-seeking selling. The initial condition is a small deviation from fundamental value that activates framing-sensitive agents before rational arbitrageurs detect mispricing.

### §2.2 Mechanism

The core mechanism is an asymmetric feedback loop driven by Prospect Theory's S-shaped value function: positive deviations trigger the concave (risk-averse) gain domain, leading to trend-reinforcing purchases; negative deviations trigger the convex (risk-seeking) loss domain, leading to panic selling. Because biased agents have lower activation thresholds (2% deviation) and larger position limits (800 shares) than rational counterparties (5% threshold, 500 shares), the net demand imbalance pushes price further from fundamental before stabilising forces intervene.

### §2.3 Participants

Five investor archetypes: GainFrameFollower (gain-frame risk-averse buyer), LossFrameReactor (loss-frame risk-seeking seller), FrameInvariantTrader (rational value contrarian), ArbitrageFramer (mispricing exploiter), and NoiseTrader (random liquidity provider). Biased agents (§4.1, §4.2) are destabilising; rational agents (§4.3, §4.4) are stabilising; the noise trader is neutral.

### §2.4 Resolution

Framing-induced mispricings persist for 5-15 rounds (session-scale) until either: (a) rational agents accumulate sufficient contrarian positions at the 5% threshold, or (b) biased agents exhaust cash/position, reducing their demand contribution. The price then mean-reverts toward fundamental through the γ·(F−P) term. The cycle repeats whenever new deviations cross the 2% activation threshold.

## §3 Research Goals

1. Does framing asymmetry produce systematic price deviations from fundamental value exceeding 3% mean absolute deviation (FDI > 0.03)?
2. Do gain-frame and loss-frame agents amplify price movements beyond what noise alone would produce (FAR ≠ 1.0)?
3. How persistent are framing-induced mispricings before rational correction (5-15 rounds)?
4. Does the Rule variant produce stronger framing distortion than LLM/Rag variants (variant comparison on FDI, FAR)?
5. How sensitive are bubble height and crash severity to λ (price impact) and γ (mean reversion) parameters?

## §4 Theoretical Anchors

### §4.1 Prospect Theory and the Value Function

| Field | Content |
|-------|---------|
| Full citation | Kahneman, D. & Tversky, A. (1979). Prospect Theory: An Analysis of Decision under Risk. *Econometrica*, 47(2), 263-291. https://doi.org/10.2307/1914185 |
| Key mechanism (≤30 words) | Asymmetric value function: gains evaluated with concave risk-averse function, losses with convex risk-seeking function, scaled by loss aversion λ≈2.25. |
| Key equation | `v(x) = x^α if x≥0; v(x) = −λ(−x)^β if x<0` where α,β∈[0.65,0.90], λ∈[1.8,2.5] |
| Motivates agent | gain-frame-follower, loss-frame-reactor |
| Parameter implication | `gain_threshold` 0.02, `framing_scale` 5000, max qty 800; ratio 800/500≈1.6 mirrors λ≈2.25 asymmetry. |

### §4.2 Framing Effects in Information Presentation

| Field | Content |
|-------|---------|
| Full citation | Tversky, A. & Kahneman, D. (1981). The Framing of Decisions and the Psychology of Choice. *Science*, 211(4481), 453-458. https://doi.org/10.1126/science.7455683 |
| Key mechanism (≤30 words) | Logically equivalent choices framed as gains vs. losses elicit systematically different risk preferences — 73% reversal rate. |
| Key equation | `if dev>threshold: perceived_signal="gain"→risk-averse; if dev<-threshold: perceived_signal="loss"→risk-seeking` |
| Motivates agent | gain-frame-follower, loss-frame-reactor |
| Parameter implication | `gain_threshold`=0.02 from Tversky & Kahneman (1981) perceptual threshold for reliable framing reversal. |

### §4.3 Limits to Arbitrage (Framing Persistence)

| Field | Content |
|-------|---------|
| Full citation | Shleifer, A. & Vishny, R.W. (1997). The Limits of Arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| Key mechanism (≤30 words) | Rational agents cannot fully correct behavioral mispricings due to noise trader risk, capital constraints, and synchronization risk. |
| Key equation | `position_cap_rational / position_cap_biased ≈ 0.62` consistent with Pontiff (2006) 40-60% constraint. |
| Motivates agent | frame-invariant-trader, arbitrage-framer |
| Parameter implication | `rational_threshold`=0.05, max qty 500 (vs 800 for biased), `rational_scale`=3000. |

### §4.4 Noise Trader Risk

| Field | Content |
|-------|---------|
| Full citation | De Long, J.B., Shleifer, A., Summers, L.H. & Waldmann, R.J. (1990). Noise Trader Risk in Financial Markets. *Journal of Political Economy*, 98(4), 703-738. https://doi.org/10.1086/261703 |
| Key mechanism (≤30 words) | Random sentiment traders create persistent mispricing risk that constrains rational arbitrage positions. |
| Key equation | `Var[P(t+1)] = (2γ·ρ_bar²)/(r+μ)²` — noise amplifies price variance beyond fundamental variance. |
| Motivates agent | noise-trader |
| Parameter implication | `trade_probability`=0.3, qty range [100,500]; provides liquidity baseline and occasionally amplifies framing moves. |

### §4.5 Disposition Effect and Reference Dependence

| Field | Content |
|-------|---------|
| Full citation | Odean, T. (1998). Are Investors Reluctant to Realize Their Losses? *Journal of Finance*, 53(5), 1775-1798. https://doi.org/10.1111/0022-1082.00072 |
| Key mechanism (≤30 words) | Retail investors sell winners 50% more often than losers — a market manifestation of framing-induced reference dependence. |
| Key equation | `PGR/PLR ≈ 1.5` (Proportion of Gains Realized / Proportion of Losses Realized) |
| Motivates agent | gain-frame-follower, loss-frame-reactor |
| Parameter implication | Validates the 2:1 asymmetry in biased vs. rational trading capacity; empirical FDI range 0.03-0.10. |

## §5 Stylized Facts

| # | Stylized Fact | Numeric Range | Source | Acceptance Metric |
|---|---|---|---|---|
| F1 | Framing reversals occur in 70-80% of subjects | d=0.38-0.51 effect size | Kuhberger (1998) meta-analysis; Levin et al. (1998) | FDI > 0.03 (framing distorts prices measurably) |
| F2 | Loss aversion coefficient λ≈2.25 | λ∈[1.8, 2.5] | Tversky & Kahneman (1992); 100+ replications | FAR deviates from 1.0 by ≥10% |
| F3 | Professional traders show 30-50% as large framing effects as retail | d_pro/d_retail ∈ [0.30, 0.50] | Haigh & List (2005) | Rational agents correct 40-60% of mispricing within 10 rounds |
| F4 | Mutual fund inflows 2.5x larger under gain framing | flow_gain/flow_neutral ≈ 2.5 | Sirri & Tufano (1998); Barber & Odean (2001) | Gain-frame rounds show higher net demand than loss-frame rounds |
| F5 | Framing-induced mispricings persist 5-15 sessions before correction | mean reversion half-life 5-15 rounds | Summers (1986); LeBaron (2006) ABM calibration | Autocorrelation of deviation > 0.3 at lag 5 |

## §6 Historical / Empirical Anchors

### §6.1 Asian Disease Problem (1981)

| Field | Content |
|-------|---------|
| Event | Laboratory framing experiment: identical problem framed as "save 200" vs. "400 die" |
| Market/Period | Controlled laboratory, 1979-1981; replicated in 1000+ studies |
| Magnitude | 73% preference reversal rate |
| Primary Source | Tversky & Kahneman (1981). *Science*, 211, 453-458. https://doi.org/10.1126/science.7455683 |

### §6.2 Mutual Fund Flow Asymmetry (1980-2005)

| Field | Content |
|-------|---------|
| Event | Gain-framed fund disclosures produce 2.5x larger inflows; loss-framed produce 40% smaller outflows |
| Market/Period | US equity mutual funds, 1980-2005 |
| Magnitude | 2.5x inflow multiplier; 40% outflow reduction |
| Primary Source | Barber & Odean (2001). *QJE*, 116(1), 261-292. https://doi.org/10.1162/003355301556400 |

### §6.3 COVID-19 March 2020 Framing Crash

| Field | Content |
|-------|---------|
| Event | Identical pandemic data framed as "50% maintained" vs. "50% lost" by different media |
| Market/Period | S&P 500, Feb-Apr 2020 |
| Magnitude | -34% drawdown in 33 days; 63% recovery in 3 months; VIX peak 82.7 |
| Primary Source | Giglio et al. (2021). *AER*, 111(5), 1481-1522. https://doi.org/10.1257/aer.20200573 |

## §7 Agent Roster

| # | Agent (kebab) | Theory Family | Market Role | Time Horizon | Risk Tolerance | Primary Signals |
|---|---|---|---|---|---|---|
| 1 | gain-frame-follower | Prospect Theory (§4.1, §4.2) | Destabilising | Immediate (every round) | Risk-averse in gains | deviation, price |
| 2 | loss-frame-reactor | Prospect Theory (§4.1, §4.2) | Destabilising | Immediate (every round) | Risk-seeking in losses | deviation, price |
| 3 | frame-invariant-trader | Limits to Arbitrage (§4.3) | Stabilising | Medium (5% threshold) | Moderate | deviation, fundamental |
| 4 | arbitrage-framer | Limits to Arbitrage (§4.3) | Stabilising | Medium (5% threshold) | Moderate | deviation, fundamental |
| 5 | noise-trader | Noise Trader Risk (§4.4) | Neutral | Random (30% participation) | Indifferent | price (random) |

## §8 Environment Specification

### §8.1 Price Formation

Formula: `P(t+1) = P(t) + λ·D(t) + γ·[F−P(t)] + ε(t)` where D(t) = net demand, F = fundamental value, ε~N(0,σ²).

### §8.2 Information Broadcast

Each round the Market broadcasts `{price, fundamental, deviation, round}` to all investors. `deviation = (price−fundamental)/fundamental` is the framing signal.

### §8.3 Constraints and Frictions

- Biased agents: 2% activation threshold, 800-share cap, framing_scale=5000
- Rational agents: 5% activation threshold, 500-share cap, rational_scale=3000
- NoiseTrader: 30% participation probability, 100-500 shares random

### §8.4 Round Granularity

Each round represents one trading session (1 day). The framing bias is refreshed each round when new price information is broadcast. Standard run: 200 rounds.

## §9 Parameter Seeds

| # | Parameter | Value | Empirical Range | Belongs to | Source Citation |
|---|---|---|---|---|---|
| 1 | initial_price | 100.0 | 1-10000 | Environment | Normalization |
| 2 | fundamental_value | 100.0 | Same as P(0) | Environment | Normalization |
| 3 | price_impact (λ) | 0.001 | 0.0001-0.01 | Environment | LeBaron (2006) ABM calibration |
| 4 | mean_reversion (γ) | 0.05 | 0.01-0.15 | Environment | Summers (1986) variance bounds |
| 5 | noise_std (σ) | 0.5 | 0.1-2.0 | Environment | Shiller (1981) excess volatility |
| 6 | initial_cash | 100000.0 | — | All agents | Normalization |
| 7 | initial_position | 1000 | 500-5000 | All agents | Normalization |
| 8 | gain_threshold | 0.02 | 0.01-0.05 | gain-frame-follower, loss-frame-reactor | Tversky & Kahneman (1981) |
| 9 | framing_scale | 5000 | 3000-8000 | gain-frame-follower, loss-frame-reactor | Calibrated for realistic volumes |
| 10 | rational_threshold | 0.05 | 0.03-0.10 | frame-invariant-trader, arbitrage-framer | Shleifer & Vishny (1997) |
| 11 | rational_scale | 3000 | 2000-5000 | frame-invariant-trader, arbitrage-framer | Limits to arbitrage calibration |
| 12 | trade_probability | 0.3 | 0.1-0.5 | noise-trader | Black (1986) noise trader model |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale |
|---------|--------|-----------|
| Rule | Yes | Deterministic baseline; finance-domain requires Rule for calibration |
| LLM | Yes | Persona-driven framing susceptibility comparison |
| RuleLLM | Yes | Rule-anchored LLM hybrid for constrained reasoning |
| Rag | Yes | Retrieval-augmented for historical framing context |

### §10.2 Pass / Fail Criteria

| # | Criterion | Metric | Threshold | Rationale |
|---|---|---|---|---|
| 1 | Framing produces measurable distortion | FDI | > 0.03 | LeBaron (2006): calibrated ABMs produce 3-12% mean deviation |
| 2 | Gain/loss asymmetry is non-trivial | FAR | ∉ [0.9, 1.1] | Tversky & Kahneman (1992): λ≈2.25 implies measurable asymmetry |
| 3 | Rational correction is bounded | RCE | 0.4-0.8 | Pontiff (2006): arbitrage corrects 40-60% of mispricing |
| 4 | Framing persists across rounds | Autocorr(dev, lag=5) | > 0.3 | Summers (1986): mean reversion half-life 5-15 rounds |
