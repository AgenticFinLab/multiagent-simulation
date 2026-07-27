# StatusQuoBias Scenario Target

## §1 Meta

| Field       | Content                                                                                                                                |
|-------------|----------------------------------------------------------------------------------------------------------------------------------------|
| Name        | StatusQuoBias                                                                                                                          |
| Domain      | finance                                                                                                                                |
| Phenomenon  | Psychological inertia and switching costs suppress portfolio rebalancing, causing persistent mispricing relative to fundamental value. |
| Pipeline    | masim/skills/polish-simulation-pipeline.md                                                                                             |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.2)                                                                                |

## §2 Phenomenon Statement

### §2.1 Trigger

A choice-architecture default or an existing allocation is treated as psychologically privileged, so investors abstain from action unless the valuation signal is unusually large. The archetypal triggers are the experimental status-quo manipulation of Samuelson and Zeckhauser (1988), the 401(k) automatic-enrollment shift of Madrian and Shea (2001), the Swedish Premium Pension default persistence of Cronqvist and Thaler (2004), and the household brokerage inertia documented in Barber and Odean (2000).

### §2.2 Population

Five investor archetypes populate the proxy market: `InertialHolder` (population 3) refuses to change position until deviation exceeds a high switching threshold; `DefaultFollower` (population 3) accepts the passive default allocation until drift is large; `ActiveRebalancer` (population 2) trades on any valuation gap above a rational threshold; `MomentumTrader` (population 2) reinforces visible price trends; `NoiseTrader` (population 2) supplies uninformed background liquidity. A single `Market` coordinator implements the price-formation law.

### §2.3 Amplification

Amplification takes the form of underreaction rather than a bubble spiral: `InertialHolder` and `DefaultFollower` suppress order flow at moderate deviations (`|deviation| ≤ change_threshold` or `|deviation| ≤ active_deviation`), which slows the transmission of valuation news into price. `MomentumTrader` sign-follows deviation once it exceeds `entry_threshold`, temporarily amplifying whichever direction the price has already drifted. `ActiveRebalancer` counter-trades on valuation, and `NoiseTrader` supplies mean-zero background flow.

### §2.4 Collapse / Correction

There is no discrete collapse. Correction is gradual and is driven jointly by (a) the mean-reversion term `γ × (F − P(t))` in the price-formation law and (b) `ActiveRebalancer` buying below fundamental and selling above fundamental once `|deviation| > rebalance_threshold`. In later rounds the biased-agent hold rate and the active-rebalance volume become clearly distinguishable in the standard analysis output (`analysis-bases.md §4 Corrective response`, §4 Stabilization).

## §3 Research Goals

1. Reproduce the status-quo underreaction signature (elevated hold rate among inertial and default agents) with a quantitative acceptance range measurable from the standard investor-order log.
2. Provide a forward-looking rational benchmark (`ActiveRebalancer`) that separates inaction from valuation-driven correction under the same price-formation law.
3. Quantify the underreaction lag (`analysis-bases.md §2.4`) and the biased-vs-rational order-pressure gap under a fixed 200-round experimental horizon.
4. Compare Rule and LLM decision fidelity: verify whether persona-only LLM agents preserve, dampen, or exaggerate the Rule inertia signature.
5. Measure whether retrieved historical evidence (Madrian and Shea 1998–99, Cronqvist and Thaler 2000-cohort, Barber and Odean 1991–96 brokerage panel) shifts inertia and rebalance behavior in the Rag variant, using `rag_stats.json` retrieval coverage as the observable proxy.

## §4 Theoretical Anchors

### §4.1 Status Quo Bias

- Primary citation: Samuelson, W., and Zeckhauser, R. (1988). "Status quo bias in decision making." *Journal of Risk and Uncertainty* 1, 7–59. DOI 10.1007/BF00055564.
- Core mechanism: the current state carries an implicit preference premium; investors act only when the perceived benefit exceeds a psychological switching cost.
- Simulation mapping: `InertialHolder` (`examples/StatusQuoBias/Rule/players.py`) implements `act iff |deviation| > change_threshold`; the sizing formula `Q = max(1, int(base_size × |deviation| / change_threshold × (1 − inertia_strength + 0.1)))` damps the resulting order.

### §4.2 Default Effects

- Primary citation: Madrian, B. C., and Shea, D. F. (2001). "The power of suggestion: Inertia in 401(k) participation and savings behavior." *Quarterly Journal of Economics* 116(4), 1149–1187. DOI 10.1162/003355301753265543.
- Core mechanism: when a default option exists, inattention and decision costs cause many participants to accept the default passively.
- Simulation mapping: `DefaultFollower` uses `trade iff |deviation| > active_deviation`; the sizing formula `Q = max(1, int(base_size × |deviation| / active_deviation × max(default_weight, 0.1)))` scales the resulting order.

### §4.3 Endowment / Reference Dependence

- Primary citation: Kahneman, D., Knetsch, J. L., and Thaler, R. H. (1991). "Anomalies: The endowment effect, loss aversion, and status quo bias." *Journal of Economic Perspectives* 5(1), 193–206. DOI 10.1257/jep.5.1.193.
- Core mechanism: the current holding is a psychological reference point; changing away from it feels like a loss and is discounted asymmetrically.
- Simulation mapping: encoded implicitly through the high `change_threshold` of `InertialHolder` and the `default_weight` damping of `DefaultFollower`; no separate loss-aversion utility function is required because the effect is folded into the action-threshold form.

### §4.4 Rational Portfolio Rebalancing

- Primary citation: Markowitz, H. (1952). "Portfolio selection." *Journal of Finance* 7(1), 77–91. DOI 10.1111/j.1540-6261.1952.tb01525.x.
- Core mechanism: a mean-variance investor responds directly to valuation and risk signals by moving toward a desired allocation.
- Simulation mapping: `ActiveRebalancer` implements `trade iff |deviation| > rebalance_threshold` with `Q = max(1, int(position_size × |deviation| / rebalance_threshold))`; it is the non-inertial benchmark.

### §4.5 Momentum And Noise Trading

- Primary citations: Jegadeesh, N., and Titman, S. (1993). "Returns to buying winners and selling losers: Implications for stock market efficiency." *Journal of Finance* 48(1), 65–91. DOI 10.1111/j.1540-6261.1993.tb04702.x. Black, F. (1986). "Noise." *Journal of Finance* 41(3), 529–543. DOI 10.1111/j.1540-6261.1986.tb04513.x.
- Core mechanism: intermediate-horizon trend continuation motivates sign-follower demand, while non-informational noise-trader flow provides background liquidity independent of valuation.
- Simulation mapping: `MomentumTrader` sign-follows deviation once `|deviation| > entry_threshold`; `NoiseTrader` samples `Bernoulli(trade_probability)` and, when active, submits a uniform-random `randint(1, noise_size)` order capped by cash/position.

## §5 Stylized Facts

| #  | Fact                                                                                                                | Acceptance range                                                                                                                                                                              | Analysis metric                                       |
|----|---------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| F1 | Inertial and default agents hold more often than active-rebalancer and momentum agents after actionable deviations. | Biased-group (`InertialHolder` + `DefaultFollower`) hold rate ≥ 0.60 across the loss/gain-onset phase; rational-group (`ActiveRebalancer` + `MomentumTrader`) rate ≤ 0.30 in the same window. | `compute_inertia_rate` (analysis-bases.md §2.1).      |
| F2 | Active rebalance order flow is visibly present once deviation crosses the rational threshold.                       | Under `                                                                                                                                                                                       | deviation                                             |
| F3 | Price adjustment exhibits an underreaction lag relative to a valuation signal.                                      | Underreaction lag ≥ 3 rounds across the run when averaged over adverse and favourable signal windows.                                                                                         | `compute_underreaction_lag` (analysis-bases.md §2.4). |
| F4 | Momentum flow is observable but bounded.                                                                            | Total `MomentumTrader` absolute quantity accounts for a distinct nonzero share of order flow (≥ 5%) under `                                                                                   | deviation                                             |
| F5 | Price-fundamental deviation remains bounded and finite for the full run.                                            | `max(                                                                                                                                                                                         | deviation                                             |

## §6 Historical / Empirical Anchors

| Case                                             | Time                | Correspondence to model                                                                                                                                                                                                                                                                                                                 |
|--------------------------------------------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 401(k) automatic-enrollment default              | 1998–1999 cohort    | Participation rose from ~49% to ~86% after opt-out default (Madrian and Shea 2001, 10.1162/003355301753265543); maps to `DefaultFollower` holding until `                                                                                                                                                                               |
| Swedish Premium Pension default fund persistence | 2000-cohort         | Majority of later entrants remained in the default allocation (Cronqvist and Thaler 2004, 10.1257/0002828041301633); maps to `DefaultFollower` sustained inaction.                                                                                                                                                                      |
| Household brokerage inertia                      | 1991–1996           | Individual investors underperformed benchmarks by several percentage points annually because of infrequent rebalancing (Barber and Odean 2000, 10.1111/0022-1082.00226); maps to combined `InertialHolder` + `NoiseTrader` order flow.                                                                                                  |
| Defined-contribution contribution inertia        | 1990s–2000s         | Large fraction of participants retained employer defaults for years (Benartzi and Thaler 2007, 10.1257/jep.21.3.81); reinforces the default-adherence structural fact underlying F1.                                                                                                                                                    |
| Intermediate-horizon momentum anomaly            | 1965–1989 US sample | 3-to-12 month winners outperformed losers by ~1%/month (Jegadeesh and Titman 1993, 10.1111/j.1540-6261.1993.tb04702.x); maps to `MomentumTrader` sign-following once `                                                                                                                                                                  |
| Primary sources                                  | —                   | Samuelson and Zeckhauser (1988) 10.1007/BF00055564; Madrian and Shea (2001) 10.1162/003355301753265543; Kahneman, Knetsch, and Thaler (1991) 10.1257/jep.5.1.193; Markowitz (1952) 10.1111/j.1540-6261.1952.tb01525.x; Jegadeesh and Titman (1993) 10.1111/j.1540-6261.1993.tb04702.x; Black (1986) 10.1111/j.1540-6261.1986.tb04513.x. |

## §7 Agent Roster

| Role              | Class Name         | Population | Role Type                | Key Behavior                                                                                                                           | Data Signal        | Time Horizon                                                                                       |
|-------------------|--------------------|-----------:|--------------------------|----------------------------------------------------------------------------------------------------------------------------------------|--------------------|----------------------------------------------------------------------------------------------------|
| Inertial holder   | `InertialHolder`   |          3 | Destabilising (inaction) | On `                                                                                                                                   | deviation          | > change_threshold` buys undervalued / sells overvalued exposure with `Q = max(1, int(base_size ×  |
| Default follower  | `DefaultFollower`  |          3 | Destabilising (inaction) | On `                                                                                                                                   | deviation          | > active_deviation` trades with `Q = max(1, int(base_size ×                                        |
| Active rebalancer | `ActiveRebalancer` |          2 | Stabilising              | On `                                                                                                                                   | deviation          | > rebalance_threshold` buys below and sells above fundamental with `Q = max(1, int(position_size × |
| Momentum trader   | `MomentumTrader`   |          2 | Destabilising (trend)    | On `                                                                                                                                   | deviation          | > entry_threshold` sign-follows deviation with `Q = max(1, int(position_size ×                     |
| Noise trader      | `NoiseTrader`      |          2 | Neutral (liquidity)      | With probability `trade_probability` per round submits a random buy or sell of size `randint(1, noise_size)`; capped by cash/position. | `cash`, `position` | Reacts each round via a fresh Bernoulli draw.                                                      |

Diversity check: two destabilising-through-inaction channels (`InertialHolder`, `DefaultFollower`) plus one destabilising-through-trend channel (`MomentumTrader`), a single stabilising channel (`ActiveRebalancer`), and a neutral liquidity channel (`NoiseTrader`). Theory family §4.1/§4.3 (inertia / endowment) motivates two agents (`InertialHolder`, `DefaultFollower`), consistent with the two-per-family rule; the remaining families are motivated by one agent each.

## §8 Environment Specification

### §8.1 Price Formation

Single-clearing-price rule-based coordinator implemented by `Market` in `examples/StatusQuoBias/Rule/players.py`. The update law is

`P(t+1) = max(0.01, P(t) + price_impact × net_demand + mean_reversion × (fundamental − P(t)) + ε(t))`

with `ε(t) ~ N(0, noise_std)`, `net_demand = total_buy − total_sell` computed from the current round's `{"action", "quantity"}` orders, `fundamental` a constant valuation anchor, and `price_impact`, `mean_reversion`, `noise_std` seeded from `market.extras` in `configs/StatusQuoBias/*/players.yml`. Justification: reduced-form encoding of biased-vs-rational order pressure around a mean-reverting fundamental anchor, faithful to §4.4 Markowitz rebalancing and §4.5 Jegadeesh–Titman / Black.

### §8.2 Information Broadcast

Each round the `Market.decide` step broadcasts a six-field dictionary to every investor: `price` (`P(t)`), `fundamental` (constant `F`), `deviation` (`(price − fundamental) / fundamental`, or zero if `fundamental ≤ 0`), `round` (integer index), `volume` (from `Market.perceive`), and `net_demand` (from `Market.perceive`). No private cost-basis or full order-book fields are broadcast; agents maintain any needed history in their own `custom_state`. Justification: keeps the status-quo / rebalance decision reducible to public `deviation` so that biased and rational channels can be compared on a common observable.

### §8.3 Constraints And Frictions

Short selling: No — sell quantities are capped at current position (`min(quantity, position)`). Cash constraint: Yes — buy quantities are capped at `int(cash / price)`. Margin requirement: No. Circuit breakers: No. Trading hours: No — every round is a full price-formation event. Order type: current-market quantity orders only, tagged with `agent_type` for accounting; `bid_price` is echoed for logging but the clearing law uses the coordinator's running `price`.

### §8.4 Round Structure And Granularity

Each round proceeds in three coordinator steps: (1) `Market.perceive` ingests investor orders from the previous round and stores them; (2) `Market.decide` computes `price`, `deviation`, `volume`, `net_demand`, and broadcasts the market-data dictionary; (3) investors run `perceive → decide → act` and submit `{"action", "bid_price", "quantity", "agent_type", "reasoning"}` orders. One round represents one decision interval at a granularity coarse enough to capture inertia and default persistence rather than intra-day microstructure. A 200-round run notionally spans a multi-quarter horizon over which the underreaction lag and final biased-vs-rational divergence become clearly distinguishable.

## §9 Parameter Seeds

| Parameter                                     | Meaning                                   | Default     | Source                                                                                                 |
|-----------------------------------------------|-------------------------------------------|-------------|--------------------------------------------------------------------------------------------------------|
| `market.extras.initial_price`                 | Initial market price at round 0           | `100.0`     | Source: normalization (simulation-bases.md §6)                                                         |
| `market.extras.fundamental_value`             | Constant forward-looking anchor           | `100.0`     | Source: normalization; equal to `initial_price` so starting deviation is zero (simulation-bases.md §6) |
| `market.extras.price_impact`                  | Net-demand price-impact gain `lambda`     | `0.02`      | simulation-bases.md §3.1; Rule/players.py `Market.decide`                                              |
| `market.extras.mean_reversion`                | Pull-toward-fundamental gain `gamma`      | `0.02`      | simulation-bases.md §3.1                                                                               |
| `market.extras.noise_std`                     | Std-dev of Gaussian price noise `epsilon` | `0.01`      | simulation-bases.md §3.1                                                                               |
| `inertialholder.num_instances`                | Number of InertialHolder agents           | `3`         | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `inertialholder.extras.initial_cash`          | Starting cash per InertialHolder          | `1000000.0` | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `inertialholder.extras.initial_position`      | Starting inventory per InertialHolder     | `500`       | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `inertialholder.extras.change_threshold`      | Status-quo action threshold `             | deviation   | > θ`                                                                                                   |
| `inertialholder.extras.inertia_strength`      | Dampens inertial order size               | `0.90`      | simulation-bases.md §4.1                                                                               |
| `inertialholder.extras.base_size`             | Inertial reinforcement sizing base        | `200`       | simulation-bases.md §4.1                                                                               |
| `defaultfollower.num_instances`               | Number of DefaultFollower agents          | `3`         | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `defaultfollower.extras.initial_cash`         | Starting cash per DefaultFollower         | `800000.0`  | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `defaultfollower.extras.initial_position`     | Starting inventory per DefaultFollower    | `400`       | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `defaultfollower.extras.active_deviation`     | Default-follower action threshold `       | deviation   | > θ`                                                                                                   |
| `defaultfollower.extras.default_weight`       | Scaling of default-driven trade           | `0.50`      | simulation-bases.md §4.2                                                                               |
| `defaultfollower.extras.base_size`            | Default-follower sizing base              | `250`       | simulation-bases.md §4.2                                                                               |
| `activerebalancer.num_instances`              | Number of ActiveRebalancer agents         | `2`         | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `activerebalancer.extras.initial_cash`        | Starting cash per ActiveRebalancer        | `1500000.0` | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `activerebalancer.extras.initial_position`    | Starting inventory per ActiveRebalancer   | `600`       | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `activerebalancer.extras.rebalance_threshold` | Active trading threshold `                | deviation   | > θ`                                                                                                   |
| `activerebalancer.extras.position_size`       | Active sizing base                        | `350`       | simulation-bases.md §4.3                                                                               |
| `momentumtrader.num_instances`                | Number of MomentumTrader agents           | `2`         | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `momentumtrader.extras.initial_cash`          | Starting cash per MomentumTrader          | `1200000.0` | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `momentumtrader.extras.initial_position`      | Starting inventory per MomentumTrader     | `500`       | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `momentumtrader.extras.entry_threshold`       | Momentum activation threshold `           | deviation   | > θ`                                                                                                   |
| `momentumtrader.extras.position_size`         | Momentum sizing base                      | `300`       | simulation-bases.md §4.4                                                                               |
| `noisetrader.num_instances`                   | Number of NoiseTrader agents              | `2`         | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `noisetrader.extras.initial_cash`             | Starting cash per NoiseTrader             | `500000.0`  | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `noisetrader.extras.initial_position`         | Starting inventory per NoiseTrader        | `200`       | configs/StatusQuoBias/Rule/players.yml                                                                 |
| `noisetrader.extras.trade_probability`        | Bernoulli activation probability          | `0.30`      | simulation-bases.md §4.5; Black (1986), 10.1111/j.1540-6261.1986.tb04513.x                             |
| `noisetrader.extras.noise_size`               | Maximum uniform-random noise order size   | `100`       | simulation-bases.md §4.5                                                                               |
| `custom_state_hot_limit` (all agents)         | Hot-tier cache size for `custom_state`    | `3`         | configs/StatusQuoBias/Rule/players.yml (runtime plumbing; not a scenario parameter)                    |

Normalization rows: `initial_price`, `fundamental_value`, and the per-investor `initial_cash` / `initial_position` fields are pure scale parameters set to numeric values that carry no independent empirical content; `initial_price = fundamental_value` guarantees a zero starting deviation.

## §10 Variants And Expected Signatures

### §10.1 Variants To Build

| Variant | Yes/No | Notes                                                                                                                                                                                                                                    |
|---------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Rule    | Yes    | Deterministic baseline; encodes the §4 activation thresholds, quantity rules, and price-formation equation exactly as prescribed by the theoretical anchors and as implemented in `examples/StatusQuoBias/Rule/players.py`.              |
| LLM     | Yes    | Needed to answer §3 research goal 4 (Rule vs LLM decision fidelity); persona-only reasoning replaces the Rule quantity formulas while keeping the canonical order schema (`action`, `bid_price`, `quantity`, `agent_type`, `reasoning`). |
| RuleLLM | Yes    | Exposes the Rule thresholds and quantity formulas as prompt content; isolates the effect of explicit rule guidance on LLM inertia and rebalancing decisions.                                                                             |
| Rag     | Yes    | Needed for §3 goal 5; adds retrieved behavioral-finance evidence (Madrian and Shea 1998–99, Cronqvist and Thaler 2000-cohort, Barber and Odean 1991–96 panel) to the LLM prompt and reports retrieval coverage via `rag_stats.json`.     |

### §10.2 Expected Phenomenon Signature Per Variant

| Variant | Expected signature                                                                                                                                                                                                                                     |
|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Rule    | Reproduces F1–F5 within their acceptance ranges. Biased hold rate ≥ 0.60; active rebalance quantity ≥ 25% of biased quantity; underreaction lag ≥ 3 rounds; momentum share ≥ 5%; deviation bounded.                                                    |
| LLM     | Similar qualitative status-quo anatomy to Rule; magnitudes more variable across runs because persona-conditioned reasoning may partially rationalize away or exaggerate inaction; parse-fallback counts reported in `summary.json` for quality gating. |
| RuleLLM | Should stay closer to the Rule baseline than pure LLM because the Rule thresholds and quantity formulas are exposed to the model as prompt content; residual deviation from Rule captures the effect of persona reasoning at the margins.              |
| Rag     | Retrieved behavioral-finance evidence is expected to increase inertia salience among biased personas and sharpen the biased-vs-rational divergence; retrieval coverage reported in `rag_stats.json` and mirrored into `summary.json`.                  |
