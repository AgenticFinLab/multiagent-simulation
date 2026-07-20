# LTCMCollapse - Scenario Target

## §0 Meta CHANGELOG

- 2026-07-20  Target produced by `define-simulation-scenario-skill.md` from the existing LTCMCollapse research, configurations, and four implemented variants; no research question or agent archetype was added.
- 2026-07-20  Polish target-file gate: Case B target produced by the define skill, §11 validation completed with three consecutive PASS runs, then status changed `draft` to `locked`.

## §1 Meta

| Field | Content |
|---|---|
| Name | LTCMCollapse |
| Domain | finance |
| Requested By | Wenyou |
| Produced By | define-simulation-scenario-skill.md v1.2.0 (invoking agent: Codex) |
| Created | 2026-07-20 |
| Pipeline | masim/skills/polish-simulation-pipeline.md |
| Target Spec | masim/skills/define-simulation-scenario-skill.md v1.2.0 |
| Status | locked |

## §2 Phenomenon Statement

### §2.1 Trigger

The August 1998 Russian default and flight to liquidity widen relative-value spreads held by highly leveraged convergence traders. Mark-to-market losses erode their equity while counterparties reassess collateral and funding terms. A small external disturbance therefore pushes a crowded portfolio across funding and risk thresholds.

### §2.2 Mechanism

Leveraged arbitrageurs initially add to apparently attractive convergence positions, but adverse price movement raises margin pressure. Forced deleveraging and common risk limits create sell pressure just as liquidity providers withdraw, so funding liquidity and market liquidity reinforce one another. Lower prices then generate further losses and risk cuts, producing a leverage-liquidity spiral.

### §2.3 Participants

Convergence arbitrageurs hold the long-horizon relative-value thesis, while leverage traders translate equity erosion into forced balance-sheet contraction. Risk managers impose common exposure cuts, and liquidity providers condition their stabilizing capacity on stress. A central-bank coordination proxy represents the official-sector role in organizing a private recapitalization when systemic stress becomes severe.

### §2.4 Resolution

The episode ends when finite positions and cash limit additional forced trading, restoring demand offsets liquidation pressure, and price begins to return toward fundamental value. A sufficiently severe negative deviation may also activate probabilistic emergency support. Resolution is endogenous and contingent, so support is neither automatic nor a hard-coded terminal price path.

## §3 Research Goals

1. Does leveraged convergence trading create a visible price dislocation and drawdown once funding constraints bind?
2. Does ablating leverage traders or risk managers materially reduce peak drawdown and crisis volatility?
3. How do `price_impact`, `leverage_ratio`, and `margin_call_threshold` change cascade onset, maximum deviation, and recovery half-life in parameter sweeps?
4. Does liquidity-provider withdrawal lengthen recovery relative to an otherwise identical run with continuous provision?
5. Do Rule, LLM, and RuleLLM preserve the same leverage-liquidity mechanism while differing in timing or action intensity?

## §4 Theoretical Anchors

### §4.1 Limits to Arbitrage

| Field | Content |
|---|---|
| Full citation | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| Key mechanism (≤30 words) | Interim losses can force professionally managed arbitrage capital to withdraw precisely when mispricing becomes largest. |
| Key equation | Enter when `abs(delta)>entry_spread`; desired exposure is proportional to `cash*leverage*abs(delta)/price`, where `delta=(price-fundamental)/fundamental`. |
| Motivates agent | convergence-arbitrageur |
| Parameter implication | `entry_spread=0.03`, `leverage=15`, and `max_position=5000` create a bounded but fragile convergence position. |

### §4.2 Leverage Cycle and Margin Pressure

| Field | Content |
|---|---|
| Full citation | Geanakoplos, J. (2010). The leverage cycle. *NBER Macroeconomics Annual 2009*, 24, 1-65. https://doi.org/10.1086/648285 |
| Key mechanism (≤30 words) | Falling collateral values tighten feasible leverage and force rapid balance-sheet contraction after tranquil-period expansion. |
| Key equation | A margin breach occurs when `equity < margin_call_threshold*abs(position*price)`; forced quantity is `floor(0.30*abs(position))`. |
| Motivates agent | leverage-trader |
| Parameter implication | `leverage_ratio=25` and `margin_call_threshold=0.04` encode high leverage and a finite equity buffer. |

### §4.3 Procyclical Risk Management

| Field | Content |
|---|---|
| Full citation | Jorion, P. (2000). Risk management lessons from Long-Term Capital Management. *European Financial Management*, 6(3), 277-300. https://doi.org/10.1111/1468-036X.00125 |
| Key mechanism (≤30 words) | Normal-period risk estimates understate stress correlation and liquidity, making simultaneous exposure cuts individually prudent but systemically amplifying. |
| Key equation | Cut half the position when `abs(delta)>3*var_limit`; the direct stress diagnostic is `var_trigger`. |
| Motivates agent | risk-manager |
| Parameter implication | `var_limit=0.05` and `var_trigger=0.06` separate ordinary fluctuation from institutional stress. |

### §4.4 Funding and Market Liquidity Spiral

| Field | Content |
|---|---|
| Full citation | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098 |
| Key mechanism (≤30 words) | Funding constraints reduce liquidity supply; lower market liquidity raises price impact and tightens funding constraints further. |
| Key equation | Provide countercyclical orders inside the stress boundary and withdraw as stress rises, subject to `abs(position)<inventory_limit`. |
| Motivates agent | liquidity-provider |
| Parameter implication | `inventory_limit=2000` and `stress_exit=0.40` bound the capacity and probability of liquidity withdrawal. |

### §4.5 Crisis Coordination and Liquidity Backstop

| Field | Content |
|---|---|
| Full citation | President's Working Group on Financial Markets. (1999). *Hedge Funds, Leverage, and the Lessons of Long-Term Capital Management*. https://www.govinfo.gov/app/details/GOVPUB-PR-PURL-LPS77446 |
| Key mechanism (≤30 words) | Coordinated recapitalization can arrest disorderly liquidation when concentrated counterparty exposures threaten market functioning. |
| Key equation | Intervene when `delta < -intervention_threshold` and a Bernoulli draw with probability `rescue_probability` succeeds. |
| Motivates agent | central-bank |
| Parameter implication | `intervention_threshold=0.10`, `rescue_probability=0.50`, and a bounded intervention size represent contingent coordination. |

## §5 Stylized Facts

| # | Fact | Quantitative range | Citation | Acceptance metric |
|---|---|---|---|---|
| F1 | Stress produces a visible deviation from fundamental value without numerical collapse. | `5% <= max_abs_deviation_pct <= 60%` | Shleifer & Vishny (1997) and scenario calibration | `calculate_ltcm_metrics(): max_abs_deviation_pct` |
| F2 | Leveraged deleveraging produces a material but finite drawdown. | `5% <= max_drawdown_pct <= 60%` | Geanakoplos (2010) and PWG (1999) | `calculate_ltcm_metrics(): max_drawdown_pct` |
| F3 | Crisis volatility exceeds calm-market noise. | `1% <= return_volatility_pct <= 12%` | Jorion (2000) and scenario calibration | `calculate_ltcm_metrics(): return_volatility_pct` |
| F4 | Endogenous liquidity withdrawal makes the dislocation persistent. | `mean_abs_deviation_pct > 0` and finite `recovery_half_life` when a trough occurs | Brunnermeier & Pedersen (2009) | `calculate_ltcm_metrics(): mean_abs_deviation_pct, recovery_half_life` |
| F5 | The trajectory remains finite and does not finish beyond its worst observed stress. | `final_abs_deviation_pct <= max_abs_deviation_pct` and `min_price > 0` | PWG (1999) mechanism and positive-price invariant | `calculate_ltcm_metrics(): final_abs_deviation_pct, min_price` |

## §6 Historical / Empirical Anchors

### §6.1 Long-Term Capital Management Crisis, August-September 1998

| Field | Content |
|---|---|
| Name + dates | Long-Term Capital Management crisis, 1998-08-17 to 1998-09-23 |
| Trigger | Russia's default and ruble devaluation accelerated a global flight to liquidity and widened crowded relative-value spreads. |
| Quantitative arc | LTCM entered 1998 with about $4.8 billion of capital and more than $125 billion in borrowed funds; a private consortium supplied $3.625 billion in September. |
| Agent mapping | Relative-value positions map to convergence-arbitrageur; balance-sheet contraction to leverage-trader; institutional limits to risk-manager; dealers to liquidity-provider; New York Fed-facilitated coordination to central-bank. |
| Primary source(s) | President's Working Group on Financial Markets (1999), https://www.govinfo.gov/app/details/GOVPUB-PR-PURL-LPS77446; Edwards, F. R. (1999), https://doi.org/10.1257/jep.13.2.189 |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart | Theory family (§4 anchor) | Domain role | Primary signals | Intent line | Expected pool match |
|---|---|---|---|---|---|---|
| convergence-arbitrageur | leveraged relative-value hedge fund | Limits to Arbitrage (§4.1) | Context-dependent | price, fundamental, deviation | Exists to trade expected convergence while exposing funding fragility. | examples/AGENT_POOL/finance/convergence-arbitrageur.md |
| leverage-trader | balance-sheet-constrained leveraged fund | Leverage Cycle (§4.2) | Destabilising | price, deviation, equity | Exists to convert margin pressure into forced deleveraging. | examples/AGENT_POOL/finance/leverage-trader.md |
| risk-manager | institutional risk-control desk | Procyclical Risk Management (§4.3) | Context-dependent | price, deviation, position | Exists to reduce individual exposure at the risk of synchronized selling. | examples/AGENT_POOL/finance/risk-manager.md |
| liquidity-provider | inventory-constrained dealer | Funding and Market Liquidity (§4.4) | Stabilising | price, deviation, position | Exists to supply ordinary liquidity and withdraw when funding stress binds. | examples/AGENT_POOL/finance/liquidity-provider.md |
| central-bank | official-sector crisis coordinator | Crisis Coordination (§4.5) | Stabilising | price, deviation, round | Exists to provide contingent support during systemic stress. | examples/AGENT_POOL/finance/central-bank.md |

## §8 Environment Specification

### §8.1 Price Formation

The market is a single-clearing-price environment with linear order impact: `P(t+1)=max(price_floor,P(t)+lambda*D(t)+gamma*(F-P(t))+epsilon(t)+F*shock_return(t))`. Here `D(t)` is net feasible order demand, `F` is the fixed public fundamental, and `epsilon(t)` is seeded Gaussian noise. The specification isolates the leverage-liquidity mechanism rather than reconstructing LTCM's multi-asset portfolio.

### §8.2 Information Broadcast

Every round broadcasts `price`, `fundamental`, `deviation`, and `round`; portfolio agents additionally observe their own `cash`, `position`, and derived equity. Price and fundamental identify relative-value stress, deviation drives common thresholds, and round supports records and controlled shocks.

### §8.3 Constraints and Frictions

Orders are clipped by available cash and inventory, market price has a strictly positive floor, and positions are bounded by archetype-specific limits. Short selling is not required for the core crisis path, margin and VaR constraints are active, and no circuit breaker is imposed. Liquidity withdrawal and probabilistic crisis coordination are the principal endogenous frictions.

### §8.4 Round Granularity

One round represents one stress-market clearing interval: prior orders update price, the market broadcasts state, agents decide, feasible orders update portfolios, and records persist. The formal baseline contains 200 rounds. This is a mechanism-time scale rather than a literal calendar-day mapping.

## §9 Parameter Seeds

| Parameter | Symbol | Belongs to | Empirical / calibration range | Candidate default | Source citation |
|---|---|---|---|---|---|
| `initial_price`, `fundamental_value` | `P0,F` | §8.1 environment | positive normalized index | `100.0, 100.0` | normalization |
| `price_impact` | `lambda` | §8.1 environment | positive stress-impact scale | `0.03` | Brunnermeier & Pedersen (2009), scenario calibration |
| `mean_reversion` | `gamma` | §8.1 environment | `[0,1]` | `0.01` | Shleifer & Vishny (1997), scenario calibration |
| `noise_std` | `sigma` | §8.1 environment | `[0,0.05]` normalized | `0.015` | controlled trigger calibration |
| `entry_spread`, `leverage`, `max_position` | `theta_e,L,Qmax` | convergence-arbitrageur | positive; leverage below reported LTCM balance-sheet scale | `0.03, 15, 5000` | Shleifer & Vishny (1997); PWG (1999) |
| `leverage_ratio`, `margin_call_threshold` | `L_m,theta_m` | leverage-trader | high leverage; trigger in `(0,1)` | `25, 0.04` | Geanakoplos (2010); PWG (1999) |
| `var_trigger`, `var_limit` | `theta_v,V` | risk-manager | stress fractions in `(0,1)` | `0.06, 0.05` | Jorion (2000) |
| `inventory_limit`, `stress_exit` | `Imax,s` | liquidity-provider | positive inventory; probability/intensity in `[0,1]` | `2000, 0.40` | Brunnermeier & Pedersen (2009) |
| `intervention_threshold`, `rescue_probability` | `theta_i,p_i` | central-bank | stress fraction in `(0,1)`; probability in `[0,1]` | `0.10, 0.50` | PWG (1999), scenario calibration |
| `trade_probability`, `noise_size` | `p_b,Q_b` | central-bank | probability in `[0,1]`; non-negative quantity | `0.30, 150` | bounded background-activity calibration |
| `base_size` | `Q0` | all trading agents | positive bounded order quantity | `300-500` | scenario order-scale calibration |
| `initial_cash`, `initial_position` | `C0,H0` | all trading agents | non-negative feasible endowment | role-specific | scenario balance-sheet calibration |
| `random_seed`, `price_floor` | `seed,Pmin` | §8.1 environment | non-negative integer; strictly positive | `20260720, 0.01` | reproducibility and numerical invariant |
| `shock_schedule` | `S(t)` | §8.1 environment | bounded signed round-to-return map | calibrated during Step 4 | controlled identification stimulus |
| `temperature`, `max_tokens` | `T,M` | model-driven variants | `T in [0,2]`, `M>0` | role-specific, `600` | bounded model sampling configuration |
| `chunk_size`, `chunk_overlap`, `top_k` | `c,o,k` | retrieval variant | positive integers with `o<c` | `512, 64, 5` | retrieval calibration |
| `custom_state_hot_limit` | `h` | §8 environment and agents | positive integer | `3` | bounded runtime-history window |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Canonical identity prefix | Rationale |
|---|---|---|---|
| Rule | Yes | `rule_` | Required deterministic calibration and causal baseline. |
| LLM | Yes | `llm_` | Tests persona-driven decisions under the common market contract. |
| RuleLLM | Yes | `rulellm_` | Tests rule-bounded language-model reasoning against Rule. |
| Rag | Yes | `ragllm_` | Preserves the existing retrieval-grounded variant for static conformance; formal Rag simulation is outside the current run scope. |

### §10.2 Pass / Fail Criteria

1. All five roster archetypes resolve bidirectionally across `simulation-bases.md`, pool profiles/icons, configurations, and implementation classes in every built variant.
2. The Rule variant reproduces all five §5 criteria in a complete 200-round run with finite positive prices and machine-readable analysis output.
3. Ablating leverage-trader or risk-manager and sweeping `price_impact`, `leverage_ratio`, or `margin_call_threshold` are explicit reproducible configuration changes.
4. Rule, LLM, and RuleLLM pass configuration, import, setup, and bounded smoke checks; Rag passes static configuration/import checks but is not formally simulated in this run.
5. Every §3 research question is traceable to a metric, ablation, sweep, or cross-variant comparison.
6. No built variant raises an uncaught exception in the capability-appropriate validation scope declared above.
