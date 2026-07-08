# OverconfidenceBias — Scenario Target

## §1 Meta

| Field         | Content                                                                |
|---------------|------------------------------------------------------------------------|
| Name          | OverconfidenceBias                                                     |
| Domain        | finance                                                                |
| Requested By  | Zihan                                                                  |
| Produced By   | define-simulation-scenario-skill.md v1.2.0 (invoking agent: Claude Code) |
| Created       | 2026-07-07                                                             |
| Pipeline      | masim/skills/polish-simulation-pipeline.md                             |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.2)                |
| Status        | draft                                                                  |

| CHANGELOG | |
|---|---|
| 2026-07-07 | Polish Step 0: target file produced from `simulation-bases.md` and `analysis-bases.md` downstream artefacts via define-skill end-to-end invocation (Case B, pre-filled from existing). |

## §2 Phenomenon Statement

### §2.1 Trigger
The scenario begins with a stable fundamental anchor and a small price deviation from that anchor. Overconfident agents observe the deviation and treat it as a meaningful private signal rather than noise, inflating the perceived signal precision. A small initial return — positive or negative — crosses an activation threshold that triggers a trade far larger than a well-calibrated investor would submit.

### §2.2 Mechanism
Overconfident agents overestimate the precision of their private signals and trade more aggressively than fundamentals warrant. Self-attributing agents compound the effect: after favorable outcomes, they credit skill and increase conviction; after unfavorable outcomes, they discount luck and maintain confidence. This creates a positive-feedback loop where biased demand pushes prices away from fundamental value, which in turn generates momentum that reinforces overconfident interpretation. Calibrated and contrarian agents provide offsetting discipline, but their corrective action is gradual. Noise traders add background liquidity and prevent a mechanically deterministic path.

### §2.3 Participants
The core participant classes are overconfident signal-inflating traders, self-attributing confidence-reinforcing traders, well-calibrated benchmark traders, contrarian mean-reversion traders, and background noise traders. Overconfident traders drive excess volume and directional order flow. Self-attributors amplify conviction after favorable outcomes. Calibrated traders provide the rational-valuation benchmark. Contrarian traders fade bias-driven deviations. Noise traders supply uninformed background flow.

### §2.4 Resolution
The bias-driven deviation weakens when sufficiently large mispricing attracts contrarian and calibrated offsetting flow that exceeds overconfident demand. Self-attributing agents may eventually face unfavorable outcomes that erode their inflated confidence, reducing their order sizes. The price reverts toward fundamental value as stabilising order flow dominates, though reversion may be gradual if self-attribution delays confidence decay.

## §3 Research Goals

1. **Excess turnover.** Can the simulation generate overconfident-agent turnover that is measurably higher than calibrated-agent turnover, consistent with Barber and Odean (2001) evidence of 45%+ excess trading?
2. **Volatility signature.** Does overconfident order flow produce price volatility exceeding the level explainable by fundamental drift and noise alone?
3. **Self-attribution dynamics.** Does the self-attributing agent increase position size after favorable outcomes and maintain confidence after unfavorable ones, producing asymmetric conviction adjustment?
4. **Ablation.** If the overconfident trader is removed, does excess turnover and volatility fall relative to the full model?
5. **Parameter sweep and variant comparison.** How does the precision-overestimate parameter change turnover and volatility, and how do LLM-driven agents differ from the deterministic Rule baseline in confidence calibration?

## §4 Theoretical Anchors

### §4.1 Overconfidence and Biased Self-Attribution

| Field                     | Content |
|---------------------------|---------|
| Full citation             | Daniel, K., Hirshleifer, D., & Subrahmanyam, A. (1998). Investor psychology and security market under- and overreactions. *Journal of Finance*, 53(6), 1839-1885. https://doi.org/10.1111/0022-1082.00077 |
| Key mechanism (≤30 words) | Investors overestimate private signal precision and attribute favourable outcomes to skill while discounting unfavourable outcomes as noise. |
| Key equation              | Perceived signal: `s_hat = precision_overestimate * deviation`; self-attribution multiplier `m_conf > 1` after favourable outcomes, `m_conf = 1` after unfavourable. |
| Motivates agent           | overconfident-trader (§7), self-attributor (§7) |
| Parameter implication     | precision_overestimate range 1.2 to 3.0, default 2.0; confidence_multiplier range 1.1 to 2.0, default 1.5. |

### §4.2 Overconfidence and Trading Volume

| Field                     | Content |
|---------------------------|---------|
| Full citation             | Odean, T. (1998). Volume, volatility, price, and profit when all traders are above average. *Journal of Finance*, 53(6), 1887-1934. https://doi.org/10.1111/0022-1082.00078 |
| Key mechanism (≤30 words) | When traders believe their signals are above average, trading volume and volatility increase even without superior information. |
| Key equation              | Trade probability increases with overconfidence; expected volume E[V] = f(precision_overestimate) is monotonically increasing. |
| Motivates agent           | overconfident-trader (§7) |
| Parameter implication     | base_position_size range 5 to 30, default 15; max_position range 30 to 100, default 60. |

### §4.3 Trading Is Hazardous to Your Wealth (Empirical Household Evidence)

| Field                     | Content |
|---------------------------|---------|
| Full citation             | Barber, B. M., & Odean, T. (2001). Boys will be boys: Gender, overconfidence, and common stock investment. *Quarterly Journal of Economics*, 116(1), 261-292. https://doi.org/10.1162/003355301556400 |
| Key mechanism (≤30 words) | Groups expected to be more overconfident trade 45% more and earn lower net returns after costs, confirming excess-trading prediction. |
| Key equation              | Excess turnover = (turnover_overconfident - turnover_calibrated) / turnover_calibrated; expect ≥ 0.45 in active phases. |
| Motivates agent           | calibrated-trader (§7) as benchmark; overconfident-trader (§7) as test agent |
| Parameter implication     | calibrated_trade_frequency range 3 to 10 rounds, default 5; overconfident activation threshold ≤ 0.01. |

### §4.4 Overreaction and Long-Horizon Reversal

| Field                     | Content |
|---------------------------|---------|
| Full citation             | De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x |
| Key mechanism (≤30 words) | Bias-driven price moves eventually reverse as calibrated and contrarian participants exploit mispricing once deviation is large enough. |
| Key equation              | Contrarian trade when abs(deviation) > reversion_threshold; quantity scales with deviation magnitude. |
| Motivates agent           | contrarian-investor (§7) |
| Parameter implication     | reversion_threshold range 0.03 to 0.10, default 0.06. |

## §5 Stylized Facts

| #  | Fact (one sentence) | Quantitative range | Citation | Acceptance metric |
|----|----------------------|--------------------|----------|-------------------|
| F1 | Overconfident agent turnover exceeds calibrated-agent turnover by at least 40% during active phases. | excess_turnover >= 0.40 | Barber & Odean (2001), https://doi.org/10.1162/003355301556400 | `analysis.py: _compute_excess_turnover()` >= 0.40 |
| F2 | Price deviation from fundamental exceeds the noise-only baseline level during overconfidence-driven episodes. | max_deviation > 2 * sigma_noise | Daniel, Hirshleifer & Subrahmanyam (1998), https://doi.org/10.1111/0022-1082.00077 | `analysis.py: _compute_max_deviation()` > 2 * sigma |
| F3 | Self-attributing agent position size increases after favourable outcomes relative to after unfavourable outcomes. | avg_position_gain_rounds / avg_position_loss_rounds > 1.2 | Daniel, Hirshleifer & Subrahmanyam (1998), https://doi.org/10.1111/0022-1082.00077 | `analysis.py: _self_attribution_ratio()` > 1.2 |
| F4 | Trading volume during overconfidence-driven phases exceeds volume during stable phases. | volume_active / volume_stable > 1.5 | Odean (1998), https://doi.org/10.1111/0022-1082.00078 | `analysis.py: _volume_ratio_active_stable()` > 1.5 |
| F5 | Contrarian offset flow increases as absolute deviation from fundamental grows. | contrarian_volume_share rising with abs(deviation) | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x | `analysis.py: contrarian_vs_deviation_correlation()` > 0 |

## §6 Historical / Empirical Anchors

### §6.1 Barber-Odean Household Trading Study (1991-1996)

| Field             | Content |
|-------------------|---------|
| Name + dates      | Barber and Odean household brokerage sample, 1991-1996. |
| Trigger           | Large discount-brokerage dataset of 35,000+ households permitted direct measurement of turnover, returns, and demographic correlates. |
| Quantitative arc  | Men traded approximately 45% more than women and earned annual net returns roughly 1.4 percentage points lower after costs; turnover was the primary mechanism, not stock selection. |
| Agent mapping     | `overconfident-trader` maps to high-turnover male investors in the sample; `calibrated-trader` maps to the low-turnover female-investor benchmark; `noise-trader` maps to uninformed background trading. |
| Primary source(s) | Barber & Odean (2001), https://doi.org/10.1162/003355301556400 |

### §6.2 Late-1990s Retail Internet-Stock Trading

| Field             | Content |
|-------------------|---------|
| Name + dates      | Retail internet-stock trading wave, 1998-2000. |
| Trigger           | Widespread internet access and discount brokerage enabled unprecedented retail participation in technology stocks during the dot-com era. |
| Quantitative arc  | NASDAQ rose approximately 86% in 1999 and fell approximately 78% from its March 2000 peak to its October 2002 trough. High retail confidence and frequent trading amplified the initial rise and subsequent crash. |
| Agent mapping     | `overconfident-trader` maps to retail day-traders chasing technology momentum; `self-attributor` maps to traders who credited skill for dot-com gains; `contrarian-investor` maps to hedge funds that shorted the overvaluation. |
| Primary source(s) | Shiller (2000), *Irrational Exuberance*; Daniel, Hirshleifer & Subrahmanyam (1998), https://doi.org/10.1111/0022-1082.00077 |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart | Theory family (§4 anchor) | Domain role | Primary signals | Intent line | Expected pool match |
|--------------------|------------------------|---------------------------|-------------|-----------------|-------------|---------------------|
| overconfident-trader | overconfident retail investor or active day-trader | Overconfidence (§4.1) and Trading Volume (§4.2) | Destabilising | price, deviation, return | "Exists to trade more aggressively than warranted by inflating perceived signal precision." | (none — likely new) |
| self-attributor | self-attributing active fund manager or biased retail trader | Biased Self-Attribution (§4.1) | Destabilising | price, return, position | "Exists to amplify conviction after favourable outcomes while discounting unfavourable ones as luck." | (none — likely new) |
| calibrated-trader | well-calibrated professional investor or institutional benchmark | Overconfidence (§4.1) benchmark and Barber-Odean empirical (§4.3) | Stabilising | price, fundamental, deviation | "Exists to trade at a calibrated frequency with unbiased signal response, serving as the rationality benchmark." | examples/AGENT_POOL/finance/rational-updater.md |
| contrarian-investor | contrarian hedge fund or mean-reversion strategist | Overreaction (§4.4) | Stabilising | price, deviation | "Exists to fade bias-driven price moves when deviation from fundamental exceeds a threshold." | examples/AGENT_POOL/finance/contrarian-trader.md |
| noise-trader | uninformed retail liquidity provider | Noise Trading (§4.5 context) | Context-dependent | price, cash, position | "Exists to add background liquidity and non-informational volatility that prevents a mechanically deterministic path." | examples/AGENT_POOL/finance/noise-trader.md |

Diversity notes: the roster includes two destabilising agents (overconfident-trader, self-attributor), two stabilising agents (calibrated-trader, contrarian-investor), and one context-dependent liquidity provider (noise-trader). Theory families span overconfidence, biased self-attribution, empirical household evidence, overreaction/reversal, and noise trading. Signal diversity includes price, deviation, return, fundamental, position, and cash channels.

## §8 Environment Specification

### §8.1 Price Formation

Single price-impact plus mean-reversion market with stable fundamental anchor:

`P(t+1) = max(P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t), 1.0)`, where `D(t)` is aggregate buy quantity minus sell quantity, `F` is constant fundamental value, `lambda` is price impact, `gamma` is mean reversion, and `epsilon(t)` is Gaussian noise with standard deviation `sigma`. The fundamental value is held constant to isolate overconfidence-driven deviations from drift-driven effects. Moderate price impact ensures that overconfident order flow produces visible price moves; moderate mean reversion provides the stabilizing anchor.

### §8.2 Information Broadcast

| Field | Type | Definition | Rationale |
|-------|------|------------|-----------|
| `price` | float | Current market price. | Primary state signal for all agents. |
| `fundamental` | float | Constant fundamental value. | Required for deviation calculation and value anchoring. |
| `deviation` | float | `(price - fundamental) / fundamental`. | Primary signal for overconfidence interpretation and contrarian response. |
| `return` | float | `(price - prev_price) / prev_price`. | Required for self-attribution dynamics (favourable vs unfavourable outcomes). |
| `volume` | float | Total trading volume proxy. | Supports excess-turnover diagnostics. |
| `round` | int | Current round number. | Supports phase tracking. |

### §8.3 Constraints and Frictions

| Item | Yes / No | Rationale |
|------|----------|-----------|
| Short-selling allowed | Yes | Required for contrarian-investor to fade overvalued prices. |
| Margin and leverage | No | Baseline uses cash-constrained positions; overconfidence amplifies via aggressiveness, not explicit leverage. |
| Price floor | Yes | Prevents non-positive prices; floor at 1.0. |
| Transaction costs | No | Baseline abstracts from explicit costs; excess-turnover metric captures the volume differential directly. |

### §8.4 Round Granularity

Each round approximates a short trading interval — roughly one trading day. A 200-round run covers initial confidence buildup, overconfident activation, self-attribution amplification, contrarian offset, and stabilization or reversal phases. Smoke tests may use fewer rounds.

## §9 Parameter Seeds

| Parameter | Symbol | Belongs to (agent / environment) | Empirical range | Candidate default | Source citation |
|-----------|--------|-----------------------------------|-----------------|-------------------|-----------------|
| initial price | P(0) | environment (§8.1) | normalised | 100.0 | Source: normalization |
| fundamental value | F | environment (§8.1) | normalised | 100.0 | Source: normalization |
| price impact | lambda | environment (§8.1) | 0.03 to 0.12 | 0.06 | Daniel, Hirshleifer & Subrahmanyam (1998), https://doi.org/10.1111/0022-1082.00077 |
| mean reversion | gamma | environment (§8.1) | 0.005 to 0.03 | 0.01 | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x |
| noise standard deviation | sigma | environment (§8.1) | 0.10 to 0.50 | 0.25 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| precision overestimate | k_prec | overconfident-trader (§7) | 1.2 to 3.0 | 2.0 | Daniel, Hirshleifer & Subrahmanyam (1998), https://doi.org/10.1111/0022-1082.00077 |
| confidence multiplier | m_conf | self-attributor (§7) | 1.1 to 2.0 | 1.5 | Daniel, Hirshleifer & Subrahmanyam (1998), https://doi.org/10.1111/0022-1082.00077 |
| overconfident max position | Q_max_oc | overconfident-trader (§7) | 30 to 100 | 60.0 | Odean (1998), https://doi.org/10.1111/0022-1082.00078 |
| calibrated trade frequency | f_cal | calibrated-trader (§7) | 3 to 10 rounds | 5 | Barber & Odean (2001), https://doi.org/10.1162/003355301556400 |
| contrarian reversion threshold | theta_rev | contrarian-investor (§7) | 0.03 to 0.10 | 0.06 | De Bondt & Thaler (1985), https://doi.org/10.1111/j.1540-6261.1985.tb05004.x |
| noise trade probability | p_noise | noise-trader (§7) | 0.10 to 0.50 | 0.30 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |

Normalization cap: 2 of 11 rows are pure-scale normalization, at the §11 cap boundary (18.2%). Merged: initial_price and fundamental_value jointly normalised to 100.0.

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale |
|---------|--------|-----------|
| Rule | Yes | Deterministic baseline for excess turnover, volatility signature, and self-attribution dynamics. |
| LLM | Yes | Tests whether persona-driven overconfidence reasoning amplifies or moderates trading aggression relative to the Rule baseline. |
| RuleLLM | Yes | Tests whether explicit overconfidence rules inside LLM reasoning preserve bias strength while allowing judgmental conviction expression. |
| Rag | Yes | Tests whether retrieved behavioural-finance literature changes agent confidence calibration or self-attribution patterns. |

### §10.2 Pass / Fail Criteria

| Criterion | Status when satisfied |
|-----------|-----------------------|
| The deterministic variant initializes agents, runs from repository root, writes records, and completes without uncaught exceptions. | green |
| At least one overconfidence mechanism activates: excess turnover, volatility elevation, or asymmetric self-attribution. | green |
| Analysis can load generated records and compute the core metrics from §5. | green |
| All four variants declared Yes in §10.1 build and produce all required output artefacts. | green |
