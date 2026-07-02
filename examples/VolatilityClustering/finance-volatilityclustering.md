# VolatilityClustering Scenario Target

## §1 Meta

| Field         | Content                                                                                                                                                                     |
|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name          | VolatilityClustering                                                                                                                                                        |
| Domain        | finance                                                                                                                                                                     |
| Requested By  | Sijia Chen                                                                                                                                                                  |
| Produced By   | define-simulation-scenario-skill.md v1.2.0 (invoking agent: QoderWork)                                                                                                      |
| Created       | 2026-07-02                                                                                                                                                                  |
| Pipeline      | masim/skills/polish-simulation-pipeline.md                                                                                                                                  |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.2)                                                                                                                     |
| Status        | locked                                                                                                                                                                      |
| CHANGELOG     | 2026-07-02  Produced by define-simulation-scenario-skill.md v1.2.0 under polish-simulation-pipeline.md Step 0 Case B (Status: draft). Source of §2–§10 content: existing downstream artefacts under `examples/VolatilityClustering/` (simulation-bases.md, analysis-bases.md, Rule/players.py, configs/VolatilityClustering/Rule/players.yml). / 2026-07-02  Polish target-file gate: structural validation green (10/10 sections, 5 DOIs per §4, 5 stylized facts, 5 agents in §7, 4 variants in §10.1), Status upgraded draft → locked. |

## §2 Phenomenon Statement

### §2.1 Trigger

An initial exogenous noise shock or news event causes a large single-round return in the market. The GARCH volatility process immediately registers the squared return as an innovation, updating conditional variance upward. This elevated variance state propagates into subsequent rounds because GARCH persistence (alpha + beta close to 1.0) ensures that volatility decays slowly rather than reverting instantaneously to the long-run level.

### §2.2 Mechanism

Once volatility rises, trend followers increase position size because their sizing rule scales with the ratio of current volatility to baseline volatility. Larger positions amplify net demand, which via the price-impact coefficient creates larger returns, which feed back into the GARCH variance equation. Noise traders continue to inject random order flow whose absolute magnitude does not change but whose relative impact grows when volatility is already elevated. Slow adapters spread their reaction to the initial shock across multiple rounds because their perceived value updates with a long moving average. The volatility trader explicitly reacts to the high-volatility regime by selling, providing partial dampening. The fundamentalist provides mean-reverting demand on infrequent rounds but does not trade every period, creating gaps in stabilising pressure. The net effect is that periods of high absolute returns cluster together, separated by calm stretches where volatility has decayed toward the GARCH floor.

### §2.3 Participants

Five investor archetypes interact with a GARCH-style market coordinator. One amplifier: a trend follower that increases position size in high-volatility regimes and chases price momentum. One shock generator: a noise trader that produces stochastic order flow. One delayed reactor: a slow adapter whose lagged response extends the effect of each shock across multiple rounds. One volatility-regime trader that sells into high-volatility states and buys into low-volatility states, providing direct feedback from the volatility state to order flow. One stabiliser: a fundamentalist that trades toward the fundamental value anchor on low-frequency rounds.

### §2.4 Resolution

Volatility clustering episodes resolve when the GARCH process mean-reverts conditional variance toward its long-run level (omega / (1 - alpha - beta)), the fundamentalist's stabilising demand offsets trend-follower momentum, and the volatility trader's selling pressure in high-volatility regimes reduces net demand. The system then enters a calm stretch until the next sufficiently large shock re-enters the cycle. Resolution is statistical rather than event-driven: no single catalyst ends the cluster; it decays through the joint effect of mean reversion, stabilising order flow, and lower GARCH innovations during calm rounds.

## §3 Research Goals

1. **GARCH persistence and clustering duration.** How does the sum `garch_alpha + garch_beta` affect the average duration of high-volatility episodes? Answered by sweeping persistence across 0.80 to 0.99 and measuring `analysis.py: compute_high_vol_duration()`.
2. **Trend-follower amplification.** Does removing or muting trend followers reduce the amplitude of volatility clusters, and by how much? Answered by an ablation turning off `trend_follower`, measured by `compute_rolling_volatility()` peak comparison.
3. **Noise-trader shock injection.** How does `position_volatility` of the noise trader affect the frequency and severity of volatility spikes? Answered by a sweep on `position_volatility`, measured by `compute_absolute_return_autocorrelation()`.
4. **Rule versus LLM decision fidelity (variant comparison).** Does the LLM variant produce similar volatility clustering patterns to the rule baseline when both face the same GARCH-dynamics market? Answered by comparing `Rule` and `LLM` variants on rolling volatility and autocorrelation metrics.
5. **Slow-adapter persistence contribution.** Does the slow adapter's lagged response extend clustering duration beyond what the GARCH mechanism alone produces? Answered by comparing runs with and without `slow_adapter`, measured by `compute_high_vol_duration()`.

## §4 Theoretical Anchors

### §4.1 Conditional Heteroskedasticity (Engle 1982)

| Field                     | Content                                                                                                                                                                                                                                                                              |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987–1007. https://doi.org/10.2307/1912773                                                                                     |
| Key mechanism (≤30 words) | Conditional variance depends on past squared innovations; large shocks raise future variance, producing volatility clusters rather than constant-variance paths.                                                                                                                      |
| Key equation              | `sigma_t^2 = omega + alpha * epsilon_{t-1}^2 + beta * sigma_{t-1}^2` (GARCH(1,1) form with Bollerslev extension).                                                                                                                                                                   |
| Motivates agent           | Market coordinator (§7); the GARCH state-update law is implemented directly in the coordinator's volatility process.                                                                                                                                                                  |
| Parameter implication     | `garch_omega` = 0.0001, `garch_alpha` = 0.15, `garch_beta` = 0.80; persistence = 0.95, implying slow decay of volatility shocks (see §9).                                                                                                                                           |

### §4.2 Generalized ARCH And Volatility Persistence (Bollerslev 1986)

| Field                     | Content                                                                                                                                                                                                                                                                              |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327. https://doi.org/10.1016/0304-4076(86)90063-1                                                                                                            |
| Key mechanism (≤30 words) | Extends ARCH by adding lagged conditional variance to the variance equation, capturing slow volatility decay and enabling realistic multi-period clustering.                                                                                                                           |
| Key equation              | `sigma_t^2 = omega + alpha_1 * epsilon_{t-1}^2 + beta_1 * sigma_{t-1}^2`; persistence = `alpha_1 + beta_1`.                                                                                                                                                                          |
| Motivates agent           | Market coordinator (§7); the `garch_beta` parameter controls how much of yesterday's variance persists, which is the primary channel producing multi-round clustering.                                                                                                                |
| Parameter implication     | `garch_beta` empirical range 0.70 to 0.90, default 0.80; combined with `garch_alpha` = 0.15 gives persistence 0.95 which matches empirical equity-index estimates (see §9).                                                                                                           |

### §4.3 Heterogeneous Agent Models And Feedback (Brock and Hommes 1998)

| Field                     | Content                                                                                                                                                                                                                                                                              |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Brock, W. A., & Hommes, C. H. (1998). Heterogeneous beliefs and routes to chaos in a simple asset pricing model. *Journal of Economic Dynamics and Control*, 22(8–9), 1235–1274. https://doi.org/10.1016/S0165-1889(98)00011-6                                                       |
| Key mechanism (≤30 words) | Interaction between fundamentalists (stabilising) and chartists (destabilising) produces nonlinear price dynamics and endogenous volatility fluctuations.                                                                                                                             |
| Key equation              | Excess demand: `D_t = n_f * (F - P_t) + n_c * trend_signal_t`, where `n_f`, `n_c` are population fractions.                                                                                                                                                                          |
| Motivates agent           | Fundamentalist (§7) and TrendFollower (§7); the interplay between value-anchoring and momentum-chasing produces endogenous clustering above what GARCH alone generates.                                                                                                               |
| Parameter implication     | `value_sensitivity` = 0.5 for fundamentalist; `trend_threshold` = 0.005 for trend follower; `base_position_size` varies by role (see §9).                                                                                                                                             |

### §4.4 Time-Series Momentum And Volatility Scaling (Moskowitz, Ooi, and Pedersen 2012)

| Field                     | Content                                                                                                                                                                                                                                                                              |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228–250. https://doi.org/10.1016/j.jfineco.2011.11.003                                                                                                      |
| Key mechanism (≤30 words) | Past returns predict future returns across asset classes; practitioners scale momentum positions by inverse volatility, creating feedback from volatility state to order size.                                                                                                          |
| Key equation              | `position_t = sign(r_{lookback}) * (sigma_target / sigma_t) * base_size`; in our variant, high vol increases rather than decreases position size via `volatility_sensitivity`.                                                                                                         |
| Motivates agent           | TrendFollower (§7); the volatility-scaling mechanism means trend followers amplify returns more in turbulent regimes, a direct channel for extending volatility clusters.                                                                                                              |
| Parameter implication     | `volatility_sensitivity` = 0.8, `baseline_volatility` = 1.0, `lookback_window` = 3 (see §9). Empirical evidence supports short lookback windows for intraday/daily momentum.                                                                                                          |

### §4.5 Noise Trader Risk (De Long et al. 1990)

| Field                     | Content                                                                                                                                                                                                                                                                              |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703–738. https://doi.org/10.1086/261703                                                                                       |
| Key mechanism (≤30 words) | Noise traders create unpredictable demand shocks that generate risk for arbitrageurs and inject variance into the price process independent of fundamental information.                                                                                                                |
| Key equation              | `order_t = N(0, position_volatility) + mean_reversion * (-position_t)`.                                                                                                                                                                                                               |
| Motivates agent           | NoiseTrader (§7); stochastic order flow provides the exogenous innovation that feeds the GARCH squared-return term even in the absence of fundamental news.                                                                                                                           |
| Parameter implication     | `position_volatility` = 15.0, `mean_reversion_speed` = 0.1 (see §9). Position mean-reversion prevents inventory divergence without eliminating shock generation.                                                                                                                      |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                                                               | Quantitative range                                                        | Citation                                                                                              | Acceptance metric                                                          |
|----|-------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| F1 | Absolute-return autocorrelation at lag 1 is significantly positive, indicating volatility persistence.            | 0.10 ≤ abs_return_autocorrelation(lag=1) ≤ 0.60                          | Engle (1982, 10.2307/1912773); Bollerslev (1986, 10.1016/0304-4076(86)90063-1)                        | `analysis.py: compute_absolute_return_autocorrelation(lag=1)` ∈ [0.10, 0.60] |
| F2 | High-volatility episodes last at least 5 rounds on average before mean-reverting to within the floor threshold.  | 5 ≤ mean(high_vol_duration) ≤ 50                                          | Cont (2001, Quantitative Finance, 10.1088/1469-7688/1/2/304); Mandelbrot (1963)                       | `analysis.py: compute_high_vol_duration()` mean ∈ [5, 50]                   |
| F3 | Trend-follower order volume is positively correlated with current volatility regime.                              | corr(trend_vol, market_vol) ≥ 0.30                                        | Moskowitz, Ooi, and Pedersen (2012, 10.1016/j.jfineco.2011.11.003)                                    | `analysis.py: compute_trend_amplification_share()` correlation ≥ 0.30       |
| F4 | Removing trend followers reduces peak rolling volatility by at least 20 %.                                        | peak_full − peak_no_trend ≥ 0.20 × peak_full                             | Brock and Hommes (1998, 10.1016/S0165-1889(98)00011-6)                                               | `analysis.py: ablation_peak_volatility_delta()` ≥ 0.20                      |
| F5 | The volatility trader generates measurable stabilisation pressure during high-vol episodes.                        | vol_trader_sell_volume > 0 in at least 30 % of high-vol rounds            | Volatility timing literature; Moreira and Muir (2017, 10.1111/jofi.12575)                             | `analysis.py: compute_stabilization_pressure()` ≥ 0.30                      |

## §6 Historical / Empirical Anchors

### §6.1 Equity Index Volatility Clustering Episodes

| Field             | Content                                                                                                                                                                                                                                                                              |
|-------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Multiple equity-index stress periods (e.g., 2008 Financial Crisis, 2010 Flash Crash, 2020 COVID-19 Crash)                                                                                                                                                                           |
| Trigger           | Macro news, earnings surprise, or exogenous liquidity shock causes a single large-magnitude return that initiates a regime shift from low to high conditional variance.                                                                                                               |
| Quantitative arc  | Daily absolute returns cluster: autocorrelation of absolute returns at lag 1 typically 0.20–0.40 for equity indices (Cont, 2001); VIX term structure inverts during clusters; rolling 20-day realised volatility can sustain 2–5× its calm-period level for weeks before mean-reverting. |
| Agent mapping     | `trend_follower` maps to CTA/managed-futures trend strategies that scale by volatility; `noise_trader` maps to retail flow and uninformed institutional rebalancing; `fundamentalist` maps to value/contrarian funds with slow re-entry; `slow_adapter` maps to pension/insurance mandates with quarterly rebalancing; `volatility_trader` maps to volatility-targeting mandates and risk-parity strategies. |
| Primary source(s) | Cont, R. (2001). Empirical properties of asset returns: stylized facts and statistical issues. *Quantitative Finance*, 1(2), 223–236. https://doi.org/10.1088/1469-7688/1/2/304; Mandelbrot, B. (1963). The variation of certain speculative prices. *Journal of Business*, 36(4), 394–419; Engle, R. F. (1982), https://doi.org/10.2307/1912773 |

## §7 Agent Roster

| Agent name (kebab)    | Real-world counterpart                       | Theory family (§4 anchor)                          | Domain role      | Primary signals                          | Intent line                                                                                  | Expected pool match          |
|-----------------------|----------------------------------------------|----------------------------------------------------|------------------|------------------------------------------|----------------------------------------------------------------------------------------------|------------------------------|
| fundamentalist        | value/contrarian fund                        | Heterogeneous Agent Feedback (§4.3)                | Stabilising      | price, fundamental                       | Exists to damp excessive deviation by trading toward fundamental value at low frequency.     | (new)                        |
| trend-follower        | CTA / managed-futures trend strategy         | Time-Series Momentum (§4.4)                        | Destabilising    | price, price_history, volatility         | Exists to amplify shocks by chasing trends with volatility-scaled position sizing.            | (new)                        |
| noise-trader          | retail flow / uninformed institutional order | Noise Trader Risk (§4.5)                           | Shock generator  | none (stochastic)                        | Exists to inject exogenous order-flow shocks that feed the GARCH variance process.            | (new)                        |
| slow-adapter          | pension/insurance mandate (quarterly)        | Heterogeneous Agent Feedback (§4.3)                | Persistence      | price, fundamental, moving_average       | Exists to spread the effect of each shock across multiple rounds through delayed updating.    | (new)                        |
| volatility-trader     | volatility-targeting / risk-parity strategy  | Conditional Heteroskedasticity (§4.1, §4.2)        | Stabilising      | volatility, vol_moving_average           | Exists to sell in high-vol regimes and buy in low-vol regimes, providing direct vol feedback. | (new)                        |

Diversity check: at least one Stabilising (`fundamentalist`, `volatility-trader`) and one Destabilising (`trend-follower`) role are present; one Shock generator (`noise-trader`) and one Persistence agent (`slow-adapter`). Theory family §4.3 motivates two agents (`fundamentalist`, `slow-adapter`), consistent with the two-per-family rule.

## §8 Environment Specification

### §8.1 Price Formation

Single-clearing-price rule-based coordinator built around a GARCH(1,1)-augmented price formation equation:

`P(t+1) = P(t) + price_impact * NetDemand + mean_reversion * (F - P(t)) + sigma(t) * epsilon`

`sigma(t)^2 = garch_omega + garch_alpha * r(t-1)^2 + garch_beta * sigma(t-1)^2`

where `P(t)` is the asset price, `F` is fundamental value, `NetDemand` is sum of buy quantities minus sell quantities, `sigma(t)` is the conditional standard deviation bounded by `[min_volatility, max_volatility]`, `r(t-1)` is the previous-round return, and `epsilon ~ N(0,1)` is a standard normal draw. The coordinator clamps `P(t+1)` at a strictly positive floor `1.0` to preserve divisibility.

For RuleLLM and Rag variants, a liquidity-sensitive extension replaces the constant `price_impact` with `base_price_impact * liquidity_factor`, where `liquidity_factor` increases when effective depth (sum of `provides_liquidity` orders) falls below `low_liquidity_threshold`. This extension preserves the same GARCH volatility dynamics but allows price impact to be state-dependent.

### §8.2 Information Broadcast

Each round the coordinator broadcasts to every investor: `price` (current `P(t)`), `prev_price` (`P(t-1)`), `return` (percentage change), `volatility` (current `sigma(t)`), `prev_volatility` (`sigma(t-1)`), `volume` (total traded), `net_demand`, `round` (integer index), and `fundamental` (constant anchor `F`). Agents needing longer history maintain their own state buffers.

### §8.3 Constraints and Frictions

Short selling: Yes, implicitly permitted (negative quantity orders accepted). Margin requirements: No explicit margin; position mean-reversion in NoiseTrader and cash limits provide soft constraints. Circuit breakers: No; the simulation allows unconstrained volatility swings within GARCH bounds. Trading hours: No; every round is a full price-formation event.

### §8.4 Round Granularity

One round represents one intraday trading interval at a granularity sufficient to capture the feedback between heterogeneous investors and the GARCH volatility process. A 200-round run corresponds notionally to roughly 10–40 trading days, which is the typical duration of an observed volatility clustering episode transitioning from calm to stress and back.

## §9 Parameter Seeds

| Parameter              | Symbol              | Belongs to (agent / environment) | Empirical range         | Candidate default | Source citation                                                                              |
|------------------------|---------------------|----------------------------------|-------------------------|-------------------|----------------------------------------------------------------------------------------------|
| initial price          | P0                  | environment (§8.1)               | Source: normalization   | 100.0             | Source: normalization                                                                         |
| fundamental value      | F                   | environment (§8.1)               | Source: normalization   | 100.0             | Source: normalization                                                                         |
| price impact           | lambda              | environment (§8.1)               | 0.02 to 0.10            | 0.05              | Brock and Hommes (1998), 10.1016/S0165-1889(98)00011-6                                       |
| mean reversion         | gamma               | environment (§8.1)               | 0.01 to 0.05            | 0.02              | Brock and Hommes (1998), 10.1016/S0165-1889(98)00011-6                                       |
| GARCH omega            | omega               | environment (§8.1)               | 0.00005 to 0.001        | 0.0001            | Engle (1982), 10.2307/1912773                                                                 |
| GARCH alpha            | alpha               | environment (§8.1)               | 0.05 to 0.25            | 0.15              | Engle (1982), 10.2307/1912773; Bollerslev (1986), 10.1016/0304-4076(86)90063-1               |
| GARCH beta             | beta                | environment (§8.1)               | 0.70 to 0.90            | 0.80              | Bollerslev (1986), 10.1016/0304-4076(86)90063-1                                              |
| min volatility         | sigma_min           | environment (§8.1)               | 0.1 to 1.0              | 0.5               | Numerical stability bound                                                                     |
| max volatility         | sigma_max           | environment (§8.1)               | 5.0 to 20.0             | 10.0              | Numerical stability bound                                                                     |
| trade frequency        | f_trade             | fundamentalist (§7)              | 2 to 5                  | 3                 | Brock and Hommes (1998), 10.1016/S0165-1889(98)00011-6                                       |
| value sensitivity      | s_val               | fundamentalist (§7)              | 0.2 to 1.0              | 0.5               | Brock and Hommes (1998), 10.1016/S0165-1889(98)00011-6                                       |
| value noise std        | sigma_val           | fundamentalist (§7)              | 1.0 to 5.0              | 2.0               | Estimation noise; prevents perfect information                                                |
| lookback window (TF)   | w_trend             | trend-follower (§7)              | 2 to 10                 | 3                 | Moskowitz, Ooi, and Pedersen (2012), 10.1016/j.jfineco.2011.11.003                           |
| trend threshold        | theta_trend         | trend-follower (§7)              | 0.001 to 0.02           | 0.005             | Moskowitz, Ooi, and Pedersen (2012), 10.1016/j.jfineco.2011.11.003                           |
| volatility sensitivity | s_vol               | trend-follower (§7)              | 0.3 to 1.5              | 0.8               | Moskowitz, Ooi, and Pedersen (2012), 10.1016/j.jfineco.2011.11.003                           |
| baseline volatility    | sigma_base          | trend-follower (§7)              | 0.5 to 2.0              | 1.0               | Calibration reference for vol ratio                                                           |
| position volatility    | sigma_noise         | noise-trader (§7)                | 5.0 to 30.0             | 15.0              | De Long et al. (1990), 10.1086/261703                                                         |
| mean reversion speed   | rho_noise           | noise-trader (§7)                | 0.05 to 0.20            | 0.1               | De Long et al. (1990), 10.1086/261703                                                         |
| lookback window (SA)   | w_slow              | slow-adapter (§7)                | 5 to 20                 | 10                | Brock and Hommes (1998), 10.1016/S0165-1889(98)00011-6                                       |
| update weight          | alpha_slow          | slow-adapter (§7)                | 0.05 to 0.30            | 0.1               | Adaptive expectations literature                                                              |
| vol lookback           | w_vol               | volatility-trader (§7)           | 3 to 10                 | 5                 | Engle (1982), 10.2307/1912773                                                                 |
| high vol threshold     | theta_high          | volatility-trader (§7)           | 1.2 to 2.0              | 1.5               | Volatility timing evidence; Moreira and Muir (2017), 10.1111/jofi.12575                      |
| low vol threshold      | theta_low           | volatility-trader (§7)           | 0.5 to 0.9              | 0.7               | Volatility timing evidence; Moreira and Muir (2017), 10.1111/jofi.12575                      |
| base position size     | Q_base              | all investors (§7)               | 10 to 50                | varies by agent   | Calibrated to produce meaningful net demand relative to price_impact                          |
| initial cash           | C0                  | all investors (§7)               | Source: normalization   | 10000.0           | Source: normalization                                                                         |
| initial position       | X0                  | all investors (§7)               | Source: normalization   | 0.0               | Source: normalization                                                                         |

Three rows (`initial price`, `fundamental value`, `initial cash`, `initial position`) are marked `Source: normalization`; these are pure scale parameters that carry no independent empirical content. The two price/value rows are set equal so initial deviation is zero; cash/position are shared defaults for all investors.

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant   | Build? | Rationale (≤1 sentence)                                                                                                                                       |
|-----------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Rule      | Yes    | Required deterministic baseline; encodes GARCH dynamics and formulaic investor rules exactly as prescribed by the theoretical anchors.                         |
| LLM       | Yes    | Needed to answer §3 research goal 4 (Rule versus LLM decision fidelity), which requires a persona-conditioned counterpart to the rule baseline.               |
| RuleLLM   | Yes    | Needed to isolate the effect of prompt-embedded rules versus persona-only reasoning, with added liquidity-aware pricing for sensitivity checks.                |
| Rag       | Yes    | Needed to test whether retrieved volatility-regime knowledge changes investor sizing or timing, extending §3 goal 4.                                           |

### §10.2 Pass / Fail Criteria

| Criterion                                                                | Status when satisfied |
|--------------------------------------------------------------------------|-----------------------|
| All §5 stylized facts F1 through F5 reproduced within their ranges       | green                 |
| Every §3 research question answerable from analysis outputs              | green                 |
| Ablating any §7 agent produces a measurable change in the trajectory     | green                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions     | green                 |
