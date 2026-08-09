# ConfirmationBias

## §1 Meta

| Field       | Content                                                                                                                        |
|-------------|--------------------------------------------------------------------------------------------------------------------------------|
| Name        | ConfirmationBias                                                                                                               |
| Domain      | finance                                                                                                                        |
| Phenomenon  | Investors selectively weight belief-confirming signals and discount contradictory evidence, amplifying directional mispricing. |
| Pipeline    | masim/skills/create-simulation-pipeline.md                                                                                     |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.2)                                                                        |

## §2 Phenomenon Statement

### §2.1 Trigger

The market opens at `initial_price = 100.0` equal to the publicly known
constant fundamental value `F = 100.0`. A single `BeliefAnchor` seeded with
`initial_belief = +1.0` (a bullish "first impression" in the Rabin & Schrag
1999 sense) begins buying and, via the low `λ = 0.02` price impact, produces
a small positive `deviation` in the very first round. That first small
positive deviation is the confirming signal that seeds the phenomenon: it
amplifies BeliefAnchor's belief further, which triggers more buying, which
produces a larger deviation.

### §2.2 Mechanism

Confirmation bias operates through an asymmetric belief-update rule.
BeliefAnchor updates its persistent internal `belief` state as
`belief × (1 + c × |δ|)` when the deviation confirms the belief sign and
`belief × 0.95 + δ × 0.5` when it disconfirms — confirming signals amplify
rapidly (`c = 0.7`) while disconfirming signals decay slowly. SelectiveScanner
reinforces the same channel at the action level: full 600-unit orders on
confirming deviations and half-size 300-unit orders on disconfirming
deviations. Together the two biased agents supply 1100 units of biased
demand per round versus 900 units of stabilising demand from BalancedAnalyst
and ContrarianTrader — the "bias dominance condition" that produces
persistent price deviations that partial rational correction cannot fully
overcome.

### §2.3 Participants

The five participant archetypes are: belief-driven biased demand
(`BeliefAnchor`), position-driven biased demand (`SelectiveScanner`),
Bayesian rational baseline (`BalancedAnalyst`), active bias-fader
(`ContrarianTrader`), and background stochastic flow (`NoiseTrader`).
Together they produce a heterogeneous ecology whose net demand is
persistently biased above `F`.

### §2.4 Resolution

The phenomenon resolves when either (a) sustained disconfirming price
movements accumulate enough decay steps to reduce BeliefAnchor's belief
below the buy trigger `+0.5`, or (b) the finite simulation horizon
(typically 100 rounds) expires. Because the bias dominance condition
holds (1100 > 900) and the decay factor is slow (0.95), full correction
is not the expected end state; the calibrated expected outcome is a
partial correction with `correction_ratio ∈ [0.2, 0.5]` and residual
mispricing.

## §3 Research Goals

1. **Ablation.** Turning off the `BeliefAnchor` (setting `initial_belief = 0`
   and removing the amplification update) is expected to eliminate persistent
   bias and drive `mean_absolute_deviation_pct` below 1 %. Answered via
   `analysis.py: compute_mean_absolute_deviation_pct()` before and after
   ablation.
2. **Parameter sweep.** Varying `confirmation_strength c ∈ {0.3, 0.5, 0.7,
   0.9}` traces the bias-strength-to-persistence curve. Answered via
   `analysis.py: compute_bias_persistence()` across the sweep grid.
3. **Variant comparison.** Do LLM personas without explicit belief-state
   variables spontaneously reproduce the Rule variant's `bias_persistence`
   and positive `return_autocorrelation_ac1`? Answered by comparing `Rule`,
   `LLM`, `RuleLLM`, and `Rag` metric trajectories.

## §4 Theoretical Anchors

### §4.1 Confirmation Bias — Selective Information Processing (Nickerson 1998)

| Field                     | Content                                                                                                                                                                      |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Nickerson, R. S. (1998). Confirmation bias: A ubiquitous phenomenon in many guises. *Review of General Psychology*, 2(2), 175–220. https://doi.org/10.1037/1089-2680.2.2.175 |
| Key mechanism (≤30 words) | Individuals actively seek confirming evidence, interpret ambiguous evidence as confirming, and discount disconfirming evidence, producing asymmetric belief updating.        |
| Key equation              | Confirming update: `belief(t+1) = belief(t) × (1 + c ×                                                                                                                       |
| Motivates agent           | belief-anchor (§7)                                                                                                                                                           |
| Parameter implication     | `confirmation_strength = 0.7` (§9); `initial_belief = 1.0` (§9); `belief_ceiling = 3.0` (§9).                                                                                |

### §4.2 Biased Assimilation and Attitude Polarization (Lord, Ross & Lepper 1979)

| Field                     | Content                                                                                                                                                                                                                                                                          |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Lord, C. G., Ross, L., & Lepper, M. R. (1979). Biased assimilation and attitude polarization: The effects of prior theories on subsequently considered evidence. *Journal of Personality and Social Psychology*, 37(11), 2098–2109. https://doi.org/10.1037/0022-3514.37.11.2098 |
| Key mechanism (≤30 words) | Investors respond asymmetrically to signals: full-size orders on confirming information, half-size orders on disconfirming information (myside bias).                                                                                                                            |
| Key equation              | `Q_confirming = order_size`; `Q_disconfirming = order_size / 2`; confirming iff `sign(deviation) = sign(current position)`.                                                                                                                                                      |
| Motivates agent           | selective-scanner (§7)                                                                                                                                                                                                                                                           |
| Parameter implication     | `order_size = 600`, `scan_threshold = 0.02` (§9).                                                                                                                                                                                                                                |

### §4.3 Formal Model of Confirmatory Bias (Rabin & Schrag 1999)

| Field                     | Content                                                                                                                                                                             |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Rabin, M., & Schrag, J. L. (1999). First impressions matter: A model of confirmatory bias. *Quarterly Journal of Economics*, 114(1), 37–82. https://doi.org/10.1162/003355399555945 |
| Key mechanism (≤30 words) | With probability q, agents misperceive disconfirming signals as confirming; for high q, beliefs never revise to the truth in finite time.                                           |
| Key equation              | Posterior belief `θ̃(t)` depends on accumulated misperceived signal history; for `q > 0.5` the ratchet effect locks belief in the initial-impression direction.                      |
| Motivates agent           | belief-anchor (§7); rational-baseline foil is balanced-analyst                                                                                                                      |
| Parameter implication     | `confirmation_strength = 0.7` corresponds to high-q regime; predicts low `belief_flip_count` (§9).                                                                                  |

### §4.4 Rational Baseline and Contrarian Correction (Fama 1970; De Bondt & Thaler 1985; Hong & Stein 1999)

| Field                     | Content                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Fama, E. F. (1970). Efficient capital markets: A review of empirical work. *Journal of Finance*, 25(2), 383–417. https://doi.org/10.2307/2325486; De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793–805. https://doi.org/10.2307/2327804; Hong, H., & Stein, J. C. (1999). A unified theory of underreaction, momentum trading, and overreaction in asset markets. *Journal of Finance*, 54(6), 2143–2184. https://doi.org/10.1111/0022-1082.00184 |
| Key mechanism (≤30 words) | Rational Bayesian evaluators trade against fundamental deviations; contrarian traders fade extreme mispricing, but arbitrage capacity is limited.                                                                                                                                                                                                                                                                                                                                                              |
| Key equation              | BalancedAnalyst: trade if `                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Motivates agent           | balanced-analyst (§7); contrarian-trader (§7)                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Parameter implication     | `analysis_threshold = 0.05`, `order_size = 400` (BalancedAnalyst); `contrarian_threshold = 0.05 – 0.10`, `order_size = 500` (ContrarianTrader) (§9).                                                                                                                                                                                                                                                                                                                                                           |

### §4.5 Noise Trading and Market Microstructure (Black 1986)

| Field                     | Content                                                                                                                                        |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529–543. https://doi.org/10.2307/2328481                                                 |
| Key mechanism (≤30 words) | Noise traders provide liquidity and stochasticity; their random flow prevents perfectly deterministic price paths and adds realistic variance. |
| Key equation              | With probability `p_NT`, `Q_noise ~ Uniform(min_order, max_order)` with random sign.                                                           |
| Motivates agent           | noise-trader (§7)                                                                                                                              |
| Parameter implication     | `trade_probability = 0.30`, `min_order = 10.0`, `max_order = 50.0` (§9).                                                                       |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                                                                   | Quantitative range           | Citation                                                     | Acceptance metric                                                 |
|----|-----------------------------------------------------------------------------------------------------------------------|------------------------------|--------------------------------------------------------------|-------------------------------------------------------------------|
| F1 | The Rule variant exhibits a peak bias amplitude between 2 % and 8 % of fundamental value.                             | `2 % ≤ bias_amplitude ≤ 8 %` | Nickerson (1998) 10.1037/1089-2680.2.2.175                   | `analysis.py: compute_bias_amplitude_pct()` ∈ [2.0, 8.0]          |
| F2 | Deviation persistence exceeds 30 rounds in a 100-round simulation at `confirmation_strength = 0.7`.                   | `bias_persistence ≥ 30`      | Rabin & Schrag (1999) 10.1162/003355399555945                | `analysis.py: compute_bias_persistence()` ≥ 30                    |
| F3 | Time-averaged absolute price deviation is between 1 % and 5 % of fundamental value.                                   | `1 % ≤ MAD ≤ 5 %`            | Nickerson (1998); Summers (1986) 10.2307/2328487             | `analysis.py: compute_mean_absolute_deviation_pct()` ∈ [1.0, 5.0] |
| F4 | BeliefAnchor's persistent belief sign flips at most twice across the simulation run under high confirmation strength. | `belief_flip_count ≤ 2`      | Lord, Ross & Lepper (1979) 10.1037/0022-3514.37.11.2098      | `analysis.py: compute_belief_flip_count()` ≤ 2                    |
| F5 | Return autocorrelation AC(1) is positive (momentum fingerprint) when the bias dominance condition holds.              | `AC(1) ∈ [0.05, 0.25]`       | Jegadeesh & Titman (1993) 10.1111/j.1540-6261.1993.tb04702.x | `analysis.py: compute_return_autocorrelation_ac1()` > 0           |

## §6 Historical / Empirical Anchors

### §6.1 Analyst Forecast Clustering (Hong & Kubik 2003)

| Field             | Content                                                                                                                                                                                                                                                                                       |
|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Analyst Forecast Clustering and Career Concerns; US equity analysts, 1985 – 2000.                                                                                                                                                                                                             |
| Trigger           | Sell-side analysts observe consensus forecasts and their own career incentives; herding pressure amplifies the prior consensus direction.                                                                                                                                                     |
| Quantitative arc  | Analyst consensus deviates from realised earnings by 10 – 20 % in the direction of the prior consensus; contrarian analysts are 60 % more likely to be dismissed.                                                                                                                             |
| Agent mapping     | Career-concerned analysts → BeliefAnchor (compound bullish belief through confirming interpretations); selective-scanning analysts → SelectiveScanner (cite only supporting reports); unbiased analysts → BalancedAnalyst; contrarian analysts → ContrarianTrader; retail flow → NoiseTrader. |
| Primary source(s) | Hong, H., & Kubik, J. D. (2003). Analyzing the analysts: Career concerns and biased earnings forecasts. *Journal of Finance*, 58(1), 313–351. https://doi.org/10.1111/1540-6261.00526                                                                                                         |

### §6.2 Dotcom Bubble Believers and Debunkers (1998 – 2001)

| Field             | Content                                                                                                                                                                                                                                                     |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Dotcom Bubble Confirmation Bias in Analyst Coverage; 1998 – 2001.                                                                                                                                                                                           |
| Trigger           | Rising tech valuations reward bullish analyst calls; a first-impression "new economy" narrative anchors bullish belief across the analyst community.                                                                                                        |
| Quantitative arc  | NASDAQ Composite rose 400 % between 1995 – 2000 peak; bullish tech analysts (Blodget, Meeker) maintained buy ratings even as fundamentals deteriorated in 2000; the bubble persisted ≈ 2.5 years before final correction.                                   |
| Agent mapping     | Committed technology bulls → BeliefAnchor (belief compounding under high-q regime); analysts reading only bullish research → SelectiveScanner; value investors like Buffett → BalancedAnalyst + ContrarianTrader; retail narrative followers → NoiseTrader. |
| Primary source(s) | Ofek, E., & Richardson, M. (2003). DotCom mania: The rise and fall of internet stock prices. *Journal of Finance*, 58(3), 1113–1137. https://doi.org/10.1111/1540-6261.00522                                                                                |

### §6.3 US Housing Bubble (2004 – 2007)

| Field             | Content                                                                                                                                                                                                                                                      |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | US Housing Bubble; 2004 – 2007.                                                                                                                                                                                                                              |
| Trigger           | A sustained bullish first impression across market participants (economists, rating agencies, investment banks, retail buyers) becomes self-confirming as price appreciation continues.                                                                      |
| Quantitative arc  | Case-Shiller Composite-20 Home Price Index rose ≈ 90 % nominal between 2000 – 2006 peak; contrarian warnings (Shiller 2005) were consistently discounted; correction (2007 – 2012) lagged the peak by roughly 12 months.                                     |
| Agent mapping     | Bullish population → BeliefAnchor (near-universal high `initial_belief`); rating agencies citing only supporting models → SelectiveScanner; skeptics like Shiller → BalancedAnalyst + ContrarianTrader; retail speculators → NoiseTrader.                    |
| Primary source(s) | Case, K. E., & Shiller, R. J. (2003). Is there a bubble in the housing market? *Brookings Papers on Economic Activity*, 2003(2), 299–342. https://doi.org/10.1353/eca.2004.0004; Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press. |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart          | Theory family (§4 anchor)    | Domain role   | Primary signals               | Intent line                                                                                                            | Expected pool match                              |
|--------------------|---------------------------------|------------------------------|---------------|-------------------------------|------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------|
| belief-anchor      | Career-concerned analyst / bull | Confirmatory Bias (§4.1)     | Destabilising | price, fundamental, deviation | "Exists to compound a persistent belief state under confirming signals and generate sustained one-directional demand." | masim/agents/defines/finance/belief-anchor.md     |
| selective-scanner  | Selectively-sourcing analyst    | Biased Assimilation (§4.2)   | Destabilising | price, fundamental, deviation | "Exists to place full-size orders on confirming signals and half-size orders on disconfirming signals."                | masim/agents/defines/finance/selective-scanner.md |
| balanced-analyst   | Unbiased Bayesian evaluator     | Rational Baseline (§4.4)     | Stabilising   | price, fundamental, deviation | "Exists to close large deviations between price and observable fundamental via symmetric two-sided trading."           | masim/agents/defines/finance/balanced-analyst.md  |
| contrarian-trader  | Short-horizon reversal desk     | Contrarian Correction (§4.4) | Stabilising   | price, fundamental, deviation | "Exists to fade sustained overshoots by trading opposite to the sign of `deviation` above the activation threshold."   | masim/agents/defines/finance/contrarian-trader.md |
| noise-trader       | Retail background flow          | Noise (§4.5)                 | Context-dep.  | price (random draw)           | "Exists to inject small random background order flow around the price with a fixed per-round trade probability."       | masim/agents/defines/finance/noise-trader.md      |

Diversity: 2 stabilising, 2 destabilising, 1 context-dependent; theory
families do not repeat more than twice across agents (Rational Baseline and
Contrarian Correction share the §4.4 anchor); every agent's primary signals
appear in the §8.2 broadcast list.

## §8 Environment Specification

### §8.1 Price Formation

Single-asset, single-venue, quote-driven equity-style market with the
`Kyle (1985)`-style linear impact model:

```
P(t+1) = P(t) + λ · D(t) + γ · [F − P(t)] + ε(t)
```

`λ = 0.02` (price impact), `γ = 0.02` (mean reversion), `F = 100.0`
(constant fundamental), `ε(t) ~ N(0, 0.02²)`. Rationale: `λ = 0.02` is
slightly higher than the AvailabilityBias baseline (0.01) to make
confirmation-bias-driven sustained accumulation observable within a
100-round simulation; `γ = 0.02` creates the fundamental tension that the
bias dominance condition (1100 > 900 units) is designed to slightly
overcome; `F` is constant to isolate perceptual bias from fundamental
information asymmetry.

### §8.2 Information Broadcast

Each round, the market broadcasts `{price, fundamental, deviation, round}`
to all investors. `fundamental` is deliberately visible to isolate
confirmation bias as a cognitive rather than informational failure
(Nickerson 1998). Crucially, the `deviation` signal is identical for all
agents — confirmation bias is NOT about different agents receiving
different information; it is about the same signal being processed
asymmetrically by biased vs. rational agents.

### §8.3 Constraints and Frictions

| Item              | Yes/No  | Rationale                                                               |
|-------------------|---------|-------------------------------------------------------------------------|
| Short-selling     | Bounded | Sells limited to current position (no naked shorts).                    |
| Margin / leverage | No      | Focuses attention on cognitive bias, not funding-liquidity spirals.     |
| Circuit breakers  | No      | Not needed at `λ = 0.02`.                                               |
| Bid-ask spread    | No      | Continuous quote-driven price; frictionless per §3 abstraction.         |
| Transaction cost  | No      | Same rationale.                                                         |
| Price floor       | Yes     | `max(price, 0.01)` prevents numerical collapse under pathological runs. |

### §8.4 Round Granularity

One round represents one analyst forecast-revision opportunity (roughly
one trading day for equity analysts). Motivated by Hong & Kubik (2003)
career-concern cadence rescaled to daily rounds; 100 rounds ≈ one quarter,
which is the empirical horizon over which analyst forecast bias is
measured to persist.

## §9 Parameter Seeds

| Parameter                         | Symbol | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation                                                                                       |
|-----------------------------------|--------|----------------------------------|-----------------|-------------------|-------------------------------------------------------------------------------------------------------|
| `initial_price`                   | P0     | environment (§8.1)               | 100.0           | 100.0             | Source: normalization                                                                                 |
| `fundamental_value`               | F      | environment (§8.1)               | 100.0           | 100.0             | Source: normalization                                                                                 |
| `price_impact`                    | λ      | environment (§8.1)               | 0.005 – 0.05    | 0.02              | Hong & Stein (1999) 10.1111/0022-1082.00184                                                           |
| `mean_reversion`                  | γ      | environment (§8.1)               | 0.005 – 0.05    | 0.02              | Fama (1970) 10.2307/2325486                                                                           |
| `noise_std`                       | σ      | environment (§8.1)               | 0.01 – 0.05     | 0.02              | Standard calibration; consistent with AvailabilityBias family                                         |
| `confirmation_strength`           | c      | belief-anchor (§7)               | 0.3 – 0.9       | 0.7               | Nickerson (1998) 10.1037/1089-2680.2.2.175; Rabin & Schrag (1999) 10.1162/003355399555945 upper-range |
| `initial_belief`                  | b0     | belief-anchor (§7)               | -1.0 – 1.0      | 1.0               | Rabin & Schrag (1999) first-impression prior                                                          |
| `belief_ceiling`                  | b_max  | belief-anchor (§7)               | 3.0             | 3.0               | Source: normalization (numerical stability guard)                                                     |
| `order_size` (BeliefAnchor)       | q_BA   | belief-anchor (§7)               | 400 – 700       | 500               | Bias dominance condition; consistent with sibling scenarios                                           |
| `order_size` (SelectiveScanner)   | q_SS   | selective-scanner (§7)           | 500 – 800       | 600               | Lord et al. (1979) 2:1 confirming:disconfirming ratio                                                 |
| `scan_threshold`                  | τ_SS   | selective-scanner (§7)           | 0.01 – 0.05     | 0.02              | Klayman (1995) selective-search calibration                                                           |
| `analysis_threshold`              | τ_BAn  | balanced-analyst (§7)            | 0.03 – 0.10     | 0.05              | Fama (1970); De Bondt & Thaler (1985) 10.2307/2327804                                                 |
| `contrarian_threshold`            | τ_CT   | contrarian-trader (§7)           | 0.05 – 0.15     | 0.05 – 0.10       | Hong & Stein (1999)                                                                                   |
| `trade_probability` (NoiseTrader) | p_NT   | noise-trader (§7)                | 0.10 – 0.50     | 0.30              | Black (1986) 10.2307/2328481                                                                          |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤ 1 sentence)                                                                                                |
|---------|--------|-------------------------------------------------------------------------------------------------------------------------|
| Rule    | Yes    | Required deterministic baseline for the §5 stylized-fact benchmark and F4 belief-flip metric.                           |
| LLM     | Yes    | Answers research goal 3 (do LLM personas spontaneously maintain a persistent belief state?).                            |
| RuleLLM | Yes    | Answers research goal 3 hybrid: dual-section prompt embeds Rule quantitative belief update inside LLM persona.          |
| Rag     | Yes    | Answers research goal 3 with retrieval-augmented awareness: does citing confirmation-bias literature moderate the bias? |

### §10.2 Pass / Fail Criteria

| Criterion                                                            | Status when satisfied |
|----------------------------------------------------------------------|-----------------------|
| All §5 stylized facts reproduced within their ranges (Rule variant)  | green                 |
| Every §3 research question answerable from `analysis.py`             | green                 |
| Ablating BeliefAnchor produces measurable MAD reduction (≥ 60 %)     | green                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green                 |
