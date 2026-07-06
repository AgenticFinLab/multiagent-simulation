# AvailabilityBias — Scenario Target

## §1 Meta

| Field         | Content |
|---------------|---------|
| Name          | AvailabilityBias |
| Domain        | finance |
| Requested By  | User |
| Produced By   | define-simulation-scenario-skill.md v1.0.0 (invoking agent: Codex) |
| Created       | 2026-07-06 |
| Pipeline      | masim/skills/create-simulation-pipeline.md |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.0) |
| Status        | locked |

## §2 Phenomenon Statement

### §2.1 Trigger

A salient market event makes one asset's recent price movement or news narrative unusually easy to recall. The trigger may be a sharp one-round return, a vivid headline, or repeated media coverage that draws investor attention away from base rates. The fundamental value is held constant so the trigger is a perception shock rather than a true cash-flow shock.

### §2.2 Mechanism

Availability-biased traders convert ease of recall into distorted subjective probability. Recent-event overweighting and media amplification raise perceived risk or opportunity, causing biased order flow in the same direction as the salient signal. That order flow moves price away from fundamental value, which can create a new vivid return signal and temporarily reinforce the mispricing loop.

### §2.3 Participants

The causal participants are availability-biased investors, media-influenced traders, rational analysts, fundamental value traders, and uninformed liquidity/noise traders. Biased participants overweight recent and publicized information, while rational participants use objective deviation from fundamental value. Noise traders provide background liquidity and stochastic order flow so the mechanism is not a fully deterministic artifact.

### §2.4 Resolution

The episode ends when salience decays, biased order flow weakens, and stabilizing traders plus mean reversion dominate price formation. Rational analysts and value traders buy undervaluation or sell overvaluation only when the gap is large enough to compensate for risk limits. The expected resolution is partial correction, not instantaneous return to fundamental value.

## §3 Research Goals

1. Measure whether salient recent returns and media-amplified narratives produce a peak price deviation from fundamental value within the calibrated 5%-15% range.
2. Test whether removing the two availability-biased agent types materially reduces biased volume, return autocorrelation, and sustained mispricing.
3. Sweep `recency_weight` and `media_weight` to estimate how subjective probability distortion changes peak deviation and bias persistence.
4. Compare Rule, LLM, RuleLLM, and Rag variants to determine whether language-model reasoning preserves, weakens, or amplifies the same availability-bias mechanism.

## §4 Theoretical Anchors

### §4.1 Availability heuristic

| Field | Content |
|-------|---------|
| Full citation | Tversky, A., & Kahneman, D. (1973). Availability: A heuristic for judging frequency and probability. *Cognitive Psychology*, 5(2), 207-232. https://doi.org/10.1016/0010-0285(73)90033-9 |
| Key mechanism (≤30 words) | Easily recalled recent or vivid events receive excess decision weight relative to objective base rates. |
| Key equation | `perceived_signal = rho * return_pct + (1 - rho) * deviation`, where `rho` is the recency weight. |
| Motivates agent | recent-event-overweighter |
| Parameter implication | `recency_weight` in §9, candidate range 0.50-0.80, default 0.70. |

### §4.2 Ease of retrieval and media salience

| Field | Content |
|-------|---------|
| Full citation | Schwarz, N., Bless, H., Strack, F., Klumpp, G., Rittenauer-Schatka, H., & Simons, A. (1991). Ease of retrieval as information: Another look at the availability heuristic. *Journal of Personality and Social Psychology*, 61(2), 195-202. https://doi.org/10.1037/0022-3514.61.2.195; Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *Journal of Finance*, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x |
| Key mechanism (≤30 words) | Repeated public narratives make a signal feel more probable and important, increasing sentiment-driven order flow. |
| Key equation | `amplified_signal = media_weight * deviation * social_amplification`. |
| Motivates agent | media-influenced-trader |
| Parameter implication | `media_weight` in §9, candidate range 0.60-0.90, default 0.80. |

### §4.3 Memory-based bounded rationality

| Field | Content |
|-------|---------|
| Full citation | Mullainathan, S. (2002). A memory-based model of bounded rationality. *Quarterly Journal of Economics*, 117(3), 735-774. https://doi.org/10.1162/003355302760193887 |
| Key mechanism (≤30 words) | Agents retrieve a biased memory sample, while rational benchmarks use objective weighting rather than recall ease. |
| Key equation | `objective_signal = deviation`; biased alternatives use salience-weighted samples. |
| Motivates agent | systematic-analyst |
| Parameter implication | `evidence_threshold` in §9, candidate range 0.02-0.05, default 0.03. |

### §4.4 Investor sentiment and fundamental correction

| Field | Content |
|-------|---------|
| Full citation | Baker, M., & Wurgler, J. (2007). Investor sentiment in the stock market. *Journal of Economic Perspectives*, 21(2), 129-151. https://doi.org/10.1257/jep.21.2.129; Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| Key mechanism (≤30 words) | Sentiment can move prices away from fundamentals while constrained arbitrage corrects mispricing only gradually. |
| Key equation | `value_demand = sign(F - P) * position_size` when `abs((P - F) / F) > theta_value`. |
| Motivates agent | value-trader |
| Parameter implication | `deviation_threshold` in §9, candidate range 0.03-0.08, default 0.05. |

### §4.5 Noise trader risk

| Field | Content |
|-------|---------|
| Full citation | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| Key mechanism (≤30 words) | Uninformed stochastic order flow creates liquidity and risk that prevents arbitrage from eliminating mispricing instantly. |
| Key equation | `trade ~ Bernoulli(p_trade)`, direction uniformly drawn from buy and sell conditional on activation. |
| Motivates agent | noise-trader |
| Parameter implication | `trade_probability` in §9, candidate range 0.10-0.40, default 0.30. |

## §5 Stylized Facts

| #  | Fact (one sentence) | Quantitative range | Citation | Acceptance metric |
|----|----------------------|--------------------|----------|-------------------|
| F1 | Availability-biased order flow creates bounded price deviation from a constant fundamental value. | 5% <= peak deviation <= 15% | Baker & Wurgler (2007), https://doi.org/10.1257/jep.21.2.129 | `analysis.py: compute_peak_deviation()` in [5, 15] |
| F2 | Mispricing persists for more than one round but decays after biased order flow weakens. | sustained-deviation share >= 10% and <= 40% | Tetlock (2007), https://doi.org/10.1111/j.1540-6261.2007.01232.x | `analysis.py: compute_bias_persistence()` in [0.10, 0.40] |
| F3 | Biased-agent volume exceeds rational volume during availability episodes. | biased/rational intensity ratio 1.0-4.0 | Tversky & Kahneman (1973), https://doi.org/10.1016/0010-0285(73)90033-9 | `analysis.py: compute_bias_magnitude()` in [1.0, 4.0] |
| F4 | Returns show positive autocorrelation during overreaction and weaker or negative autocorrelation during correction. | active-window lag-1 AC1 0.20-0.40 | De Bondt & Thaler (1985), https://doi.org/10.2307/2327804 | `analysis.py: compute_rolling_ac1()` in [0.20, 0.40] during active bias |

## §6 Historical / Empirical Anchors

### §6.1 Post-earnings announcement drift and reversal

| Field | Content |
|-------|---------|
| Name + dates | Post-earnings announcement drift, documented in U.S. equities around quarterly earnings announcements. |
| Trigger | A vivid corporate earnings surprise becomes the most available recent firm-level signal. |
| Quantitative arc | Bernard and Thomas report abnormal drift over roughly 60 trading days after earnings surprises, followed by correction pressure. |
| Agent mapping | recent-event-overweighter maps to investors chasing the surprise, systematic-analyst maps to objective earnings processors, value-trader maps to correction flow, media-influenced-trader maps to publicized surprise narratives, noise-trader maps to uninformed liquidity. |
| Primary source(s) | Bernard, V. L., & Thomas, J. K. (1989). Post-earnings-announcement drift: Delayed price response or risk premium? *Journal of Accounting Research*, 27, 1-36. https://doi.org/10.2307/2491062 |

### §6.2 Media pessimism and short-horizon reversal

| Field | Content |
|-------|---------|
| Name + dates | Wall Street Journal media-pessimism sample, 1984-1999. |
| Trigger | High media pessimism and coverage intensity make negative narratives salient. |
| Quantitative arc | Tetlock finds pessimism predicts downward price pressure followed by short-horizon reversal over days to weeks. |
| Agent mapping | media-influenced-trader maps to narrative-sensitive traders, recent-event-overweighter maps to return salience, systematic-analyst and value-trader map to correction, noise-trader maps to background volume. |
| Primary source(s) | Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *Journal of Finance*, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x |

### §6.3 COVID-19 crash and recovery as salient-news stress case

| Field | Content |
|-------|---------|
| Name + dates | COVID-19 U.S. equity crash and recovery, 2020-02-19 to 2020-08-18. |
| Trigger | Repeated pandemic headlines, extreme recent losses, and uncertainty made negative scenarios highly available. |
| Quantitative arc | The S&P 500 fell about 34% from 2020-02-19 to 2020-03-23 and recovered its prior high by 2020-08-18. |
| Agent mapping | recent-event-overweighter maps to loss-chasing salience, media-influenced-trader maps to headline amplification, systematic-analyst and value-trader map to correction under limits, noise-trader maps to liquidity shocks. |
| Primary source(s) | S&P Dow Jones Indices historical S&P 500 close series; Baker, S. R., Bloom, N., Davis, S. J., Kost, K., Sammon, M., & Viratyosin, T. (2020). The unprecedented stock market reaction to COVID-19. *Review of Asset Pricing Studies*, 10(4), 742-758. https://doi.org/10.1093/rapstu/raaa008 |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart | Theory family (§4 anchor) | Domain role | Primary signals | Intent line | Expected pool match |
|--------------------|------------------------|---------------------------|-------------|-----------------|-------------|---------------------|
| recent-event-overweighter | active retail trader | Behavioral Finance (§4.1) | Destabilising | return_pct, deviation, price | Exists to overweight the latest salient return when forming demand. | examples/AGENT_POOL/finance/recent-event-overweighter.md |
| media-influenced-trader | active retail trader | Behavioral Finance / Media sentiment (§4.2) | Destabilising | deviation, return_pct, price | Exists to convert amplified public narratives into directional order flow. | examples/AGENT_POOL/finance/media-influenced-trader.md |
| systematic-analyst | arbitrageur | Quant / Rational benchmark (§4.3) | Stabilising | price, fundamental, deviation | Exists to trade on objective price-fundamental evidence rather than recall ease. | examples/AGENT_POOL/finance/rational-updater.md |
| value-trader | mutual fund | Fundamental / Value (§4.4) | Stabilising | price, fundamental, deviation | Exists to correct sufficiently large mispricing using a fundamental anchor. | examples/AGENT_POOL/finance/fundamental-analyst.md |
| noise-trader | retail liquidity demander | Behavioral Finance / Noise trading (§4.5) | Context-dependent | price, round, rng_state | Exists to supply bounded uninformed order flow and liquidity shocks. | examples/AGENT_POOL/finance/noise-trader.md |

## §8 Environment Specification

### §8.1 Price Formation

The environment is a dealer-style single-price market with price update `P(t+1) = P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t)`. Net demand `D(t)` aggregates buy minus sell quantity from all traders. Price impact and mean reversion isolate temporary mispricing from permanent fundamental news.

### §8.2 Information Broadcast

Each round broadcasts `price`, `prev_price`, `fundamental`, `deviation`, `return_pct`, `volume`, and `round`. `price`, `fundamental`, and `deviation` support rational correction and media-salience amplification; `return_pct` supports the recent-event availability channel; `volume` and `round` support analysis and phase interpretation.

### §8.3 Constraints and Frictions

Short selling is represented only through inventory-constrained sell orders in the current implementation, so agents cannot silently create unlimited short exposure. Agents have cash, position, maximum order, and activation thresholds. The environment applies a positive price floor and bounded Gaussian noise.

### §8.4 Round Granularity

One round represents one trading interval in which public price and narrative information are refreshed. The calibration is intentionally abstract, allowing the same mechanism to cover daily earnings-news salience and shorter media-driven attention episodes. Historical anchor §6.2 justifies interpreting multiple rounds as a days-to-weeks media correction window.

## §9 Parameter Seeds

| Parameter | Symbol | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation |
|-----------|--------|----------------------------------|-----------------|-------------------|-----------------|
| recency weight | `rho` | recent-event-overweighter (§7) | 0.50-0.80 | 0.70 | Tversky & Kahneman (1973), https://doi.org/10.1016/0010-0285(73)90033-9 |
| salience threshold | `theta_s` | recent-event-overweighter (§7) | 0.01-0.04 | 0.02 | De Bondt & Thaler (1985), https://doi.org/10.2307/2327804 |
| media weight | `mu_m` | media-influenced-trader (§7) | 0.60-0.90 | 0.80 | Tetlock (2007), https://doi.org/10.1111/j.1540-6261.2007.01232.x |
| social amplification | `a_m` | media-influenced-trader (§7) | 1.00-2.00 | 1.50 | Schwarz et al. (1991), https://doi.org/10.1037/0022-3514.61.2.195 |
| evidence threshold | `theta_e` | systematic-analyst (§7) | 0.02-0.05 | 0.03 | Mullainathan (2002), https://doi.org/10.1162/003355302760193887 |
| value deviation threshold | `theta_v` | value-trader (§7) | 0.03-0.08 | 0.05 | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| trade probability | `p_n` | noise-trader (§7) | 0.10-0.40 | 0.30 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| price impact | `lambda` | environment (§8.1) | 0.01-0.05 | 0.02 | Hasbrouck, J. (1991). Measuring the information content of stock trades. *Journal of Finance*, 46(1), 179-207. https://doi.org/10.1111/j.1540-6261.1991.tb03749.x |
| mean reversion | `gamma` | environment (§8.1) | 0.01-0.05 | 0.03 | Baker & Wurgler (2007), https://doi.org/10.1257/jep.21.2.129 |
| initial price and fundamental | `P0`, `F` | environment (§8.1) | Source: normalization | 100.0 | Source: normalization |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤1 sentence) |
|---------|--------|--------------------------|
| Rule | Yes | Required deterministic baseline for the availability-bias mechanism. |
| LLM | Yes | Tests whether persona-only reasoning reproduces or dilutes the bias in research goal 4. |
| RuleLLM | Yes | Tests whether explicit rule anchoring preserves the deterministic mechanism with model reasoning. |
| Rag | Yes | Tests whether retrieved behavioral-finance context changes availability-biased decisions. |

### §10.2 Pass / Fail Criteria

| Criterion | Status when satisfied |
|-----------|-----------------------|
| All §5 stylized facts reproduced within their ranges | green |
| Every §3 research question answerable from analysis | green |
| Ablating any §7 agent produces a measurable change | green |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green |
