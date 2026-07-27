# SunkCostFallacy Scenario Target

## §1 Meta

| Field       | Content                                                                                                                                        |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | SunkCostFallacy                                                                                                                                |
| Domain      | finance                                                                                                                                        |
| Phenomenon  | Investors irrationally hold or escalate losing positions to justify prior investment, distorting allocation relative to forward-looking value. |
| Pipeline    | masim/skills/polish-simulation-pipeline.md                                                                                                     |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.2)                                                                                        |

## §2 Phenomenon Statement

### §2.1 Trigger

A prior unrecoverable investment cost is treated as psychologically salient and, in a proxy trading environment, distorts current allocation decisions. Losing positions are held or expanded to avoid making the earlier commitment explicit, while forward-looking benchmark agents evaluate only future expected value. The archetypal experimental trigger is the sunk-cost manipulation of Arkes and Blumer (1985); the archetypal field triggers are the multi-year escalation of the Concorde program, the individual-investor averaging-down pattern in Barber and Odean (2000), and the reluctance-to-realize-losses pattern in Odean (1998).

### §2.2 Population

Five investor archetypes populate the proxy market: `SunkCostHolder` (population 3) refuses to sell losing positions; `CommitmentEscalator` (population 3) buys additional exposure after losses to justify prior commitment; `RationalCutter` (population 2) trades on forward-looking valuation; `OpportunityCostTrader` (population 2) reallocates capital when a better alternative use is available; `NoiseTrader` (population 2) provides non-informational baseline liquidity. All five archetypes share a single `Market` coordinator.

### §2.3 Amplification

Amplification is driven jointly by (a) sunk-cost inertia on the sell side — losing-position sell orders are suppressed by `SunkCostHolder`, artificially compressing supply after negative deviation — and (b) escalation of commitment on the buy side — `CommitmentEscalator` adds buy pressure after losses with quantity scaling as `escalation_size × |deviation| / escalation_threshold`. The rational and opportunity-cost agents counter-trade on valuation; the noise trader adds mean-zero background liquidity.

### §2.4 Collapse / Correction

Correction is gradual rather than a discrete collapse. As biased agents deplete cash by averaging down and rational and opportunity-cost agents accumulate corrective order flow, the mean-reversion term `γ × (F − P(t))` and the finite-cash budget constraint combine to pull the price back toward `fundamental_value = 100`. The final divergence phase (`analysis-bases.md §4 Final divergence`) then makes biased-vs-rational order pressure clearly distinguishable rather than producing a sharp crash.

## §3 Research Goals

1. Reproduce the empirically documented sunk-cost signature (sell-side inertia among losing biased agents) and the escalation signature (buy-side amplification after losses) with quantitative acceptance metrics measurable from the standard order log.
2. Provide a forward-looking rational benchmark (RationalCutter + OpportunityCostTrader) that separates commitment-driven order flow from valuation-driven order flow within the same market.
3. Quantify the performance drag (`analysis-bases.md §2.5`) that biased agents suffer relative to the rational benchmark under a fixed price-formation law.
4. Compare Rule and LLM decision-fidelity: verify whether persona-only LLM agents preserve, dampen, or exaggerate the Rule sunk-cost/escalation signatures.
5. Measure whether retrieved historical evidence (Concorde 1960s–70s, retail averaging-down 1991–96, Odean 1987–93 disposition sample) changes escalation and loss-cutting behavior in the Rag variant, using `rag_stats.json` retrieval coverage as the observable proxy.

## §4 Theoretical Anchors

### §4.1 Sunk-Cost Fallacy

- Primary citation: Arkes, H. R., and Blumer, C. (1985). "The psychology of sunk cost." *Organizational Behavior and Human Decision Processes* 35(1), 124–140. DOI 10.1016/0749-5978(85)90049-4.
- Core mechanism: a prior unrecoverable cost is treated as a reason to continue an action even when future expected value does not justify it.
- Simulation mapping: `SunkCostHolder` (`examples/SunkCostFallacy/Rule/players.py`) implements the sell-side inertia — under negative deviation it emits `hold`; under `deviation > hold_threshold` it emits a small reinforcement buy.

### §4.2 Escalation Of Commitment

- Primary citation: Staw, B. M. (1976). "Knee-deep in the big muddy: A study of escalating commitment to a chosen course of action." *Organizational Behavior and Human Performance* 16(1), 27–44. DOI 10.1016/0030-5073(76)90005-2.
- Core mechanism: decision makers invest additional resources into a failing course of action to justify prior choices.
- Simulation mapping: `CommitmentEscalator` implements `buy` when `deviation < -escalation_threshold` with quantity `escalation_size × |deviation| / escalation_threshold`; a smaller reinforcement buy fires under `deviation > escalation_threshold`.

### §4.3 Mental Accounting

- Primary citation: Thaler, R. H. (1980). "Toward a positive theory of consumer choice." *Journal of Economic Behavior and Organization* 1(1), 39–60. DOI 10.1016/0167-2681(80)90051-7.
- Core mechanism: investors evaluate a position within a separate mental account, so the entry price and the realized-loss framing acquire psychological salience beyond their forward-looking economic content.
- Simulation mapping: the current position is treated as a mental account through the biased agents' asymmetric response to `deviation`; the rational benchmark agents are constructed to be indifferent to entry-cost framing.

### §4.4 Forward-Looking Portfolio Choice

- Primary citation: Odean, T. (1998). "Are investors reluctant to realize their losses?" *Journal of Finance* 53(5), 1775–1798. DOI 10.1111/0022-1082.00072.
- Core mechanism: under expected-utility / portfolio-choice logic, past irreversible costs are irrelevant to current allocation; observed reluctance-to-realize-losses violations identify sunk-cost inertia empirically.
- Simulation mapping: `RationalCutter` implements the forward-looking benchmark — for `abs(deviation) > cut_threshold` it buys undervalued exposure and sells overvalued exposure with quantity `position_size × abs(deviation) / cut_threshold`.

### §4.5 Opportunity Cost And Noise Trading

- Primary citations: Barber, B., and Odean, T. (2000). "Trading is hazardous to your wealth: The common stock investment performance of individual investors." *Journal of Finance* 55(2), 773–806. DOI 10.1111/0022-1082.00226. Black, F. (1986). "Noise." *Journal of Finance* 41(3), 529–543. DOI 10.1111/j.1540-6261.1986.tb04513.x.
- Core mechanism: opportunity-cost reasoning reallocates capital away from underperforming exposures; independently, non-informational noise-trader flow supplies background liquidity that identifies the corrective and biased channels against a common baseline.
- Simulation mapping: `OpportunityCostTrader` mirrors `RationalCutter` at a stricter `realloc_threshold`; `NoiseTrader` samples `Bernoulli(trade_probability)` and, when active, submits a uniform-random quantity capped by cash/position.

## §5 Stylized Facts

| #  | Fact                                                                                                                          | Acceptance range                                                                                                                                                        | Analysis metric                                              |
|----|-------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| F1 | Losing-position holding rate is elevated among sunk-cost / escalator agents relative to rational and opportunity-cost agents. | Biased-group losing-position holding rate ≥ 0.60 across the loss-onset phase; rational-group rate ≤ 0.40 in the same window.                                            | `compute_losing_holding_rate` (analysis-bases.md §2.1).      |
| F2 | Escalation buy volume is materially positive after adverse deviation.                                                         | Aggregate `CommitmentEscalator` buy quantity under `deviation < -escalation_threshold` accounts for ≥ 15% of total buy quantity across the run.                         | `compute_escalation_volume` (analysis-bases.md §2.2).        |
| F3 | Rational-cut order flow is visibly present and directionally correct.                                                         | Under `abs(deviation) > cut_threshold`, `RationalCutter` sells on positive deviation and buys on negative deviation, with total quantity ≥ 30% of biased buy quantity.  | `compute_rational_cut_volume` (analysis-bases.md §2.3).      |
| F4 | Opportunity-cost reallocation is observable.                                                                                  | Total `OpportunityCostTrader` traded quantity under `abs(deviation) > realloc_threshold` accounts for a distinct nonzero share of order flow (≥ 5%).                    | `compute_opportunity_reallocation` (analysis-bases.md §2.4). |
| F5 | Biased agents underperform the rational benchmark on portfolio-value drag.                                                    | End-of-run mean portfolio value of the biased group is strictly below the rational group's mean by an unambiguously positive drag; performance drag metric is positive. | `compute_performance_drag` (analysis-bases.md §2.5).         |

## §6 Historical / Empirical Anchors

| Case                               | Time               | Correspondence to model                                                                                                                                                                                                       |
|------------------------------------|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Concorde project escalation        | 1960s–1970s        | Multi-year public re-investment after adverse commercial signals maps to `CommitmentEscalator` reinvesting under `deviation < -escalation_threshold`.                                                                         |
| NBA-draft playing-time escalation  | 1980s–1990s sample | Prior-investment salience preserving allocation maps to `SunkCostHolder` withholding sell orders on losing positions.                                                                                                         |
| Retail averaging-down              | 1991–1996          | Discount-brokerage retail investors adding to losing positions maps directly to `CommitmentEscalator` buy pressure under negative deviation (Barber and Odean 2000).                                                          |
| Odean brokerage disposition sample | 1987–1993          | Documented reluctance to realize losses in individual accounts maps to `SunkCostHolder` avoiding sell orders on losing positions.                                                                                             |
| Corporate project continuation     | 1970s–1990s        | Continued capital expenditure after negative feedback in experimental and field studies maps to `CommitmentEscalator` averaging down after unfavorable deviation.                                                             |
| Primary sources                    | —                  | Arkes and Blumer (1985) 10.1016/0749-5978(85)90049-4; Staw (1976) 10.1016/0030-5073(76)90005-2; Staw and Hoang (1995) 10.2307/2393785; Barber and Odean (2000) 10.1111/0022-1082.00226; Odean (1998) 10.1111/0022-1082.00072. |

## §7 Agent Roster

| Role                    | Class Name              | Population | Role Type               | Key Behavior                                                                                                                                                                                 | Data Signal                              | Time Horizon                                  |
|-------------------------|-------------------------|-----------:|-------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------|-----------------------------------------------|
| Sunk-cost holder        | `SunkCostHolder`        |          3 | Destabilising (holding) | Emits `hold` on losing positions; on `deviation > hold_threshold` emits a small reinforcement buy of `max(1, int(base_size × deviation / hold_threshold))` capped by cash.                   | `deviation`, `price`, `cash`             | Reacts to current-round deviation only.       |
| Commitment escalator    | `CommitmentEscalator`   |          3 | Destabilising           | On `deviation < -escalation_threshold`, buys `max(1, int(escalation_size × abs(deviation) / escalation_threshold))` capped by cash; on `deviation > escalation_threshold` buys half as much. | `deviation`, `price`, `cash`             | Reacts to current-round deviation only.       |
| Rational cutter         | `RationalCutter`        |          2 | Stabilising             | On `abs(deviation) > cut_threshold`, buys undervalued exposure and sells overvalued exposure with quantity `max(1, int(position_size × abs(deviation) / cut_threshold))`.                    | `deviation`, `price`, `cash`, `position` | Reacts to current-round deviation only.       |
| Opportunity-cost trader | `OpportunityCostTrader` |          2 | Stabilising             | Same directional rule as `RationalCutter` at the stricter `realloc_threshold` — reallocates when a better alternative use is likely.                                                         | `deviation`, `price`, `cash`, `position` | Reacts to current-round deviation only.       |
| Noise trader            | `NoiseTrader`           |          2 | Neutral (liquidity)     | With probability `trade_probability` per round submits a uniform-random buy or sell of size `randint(1, noise_size)` capped by cash / position.                                              | `cash`, `position`                       | Reacts each round via a fresh Bernoulli draw. |

Diversity check: two destabilising channels (`SunkCostHolder` sell-side inertia, `CommitmentEscalator` buy-side escalation) and two stabilising channels (`RationalCutter` valuation, `OpportunityCostTrader` reallocation) are both present; `NoiseTrader` supplies a fifth mean-zero channel. Theory family §4.4 (forward-looking benchmark) motivates two agents (`RationalCutter`, `OpportunityCostTrader`), consistent with the two-per-family rule.

## §8 Environment Specification

### §8.1 Price Formation

Single-clearing-price rule-based coordinator implemented by `Market` in `examples/SunkCostFallacy/Rule/players.py`. The update law is

`P(t+1) = max(0.01, P(t) + price_impact × net_demand + mean_reversion × (fundamental − P(t)) + ε(t))`

where `ε(t) ~ N(0, noise_std)`, `net_demand = total_buy − total_sell` computed from the current round's `{"action", "quantity"}` orders, `fundamental` is the constant valuation anchor, and `price_impact`, `mean_reversion`, and `noise_std` are seeded from `market.extras` in `configs/SunkCostFallacy/*/players.yml`. Justification: §4.1–§4.4 as a reduced-form encoding of biased-vs-rational order pressure with a mean-reverting fundamental anchor.

### §8.2 Information Broadcast

Each round the `Market.decide` step broadcasts a dictionary with four fields to every investor: `price` (current `P(t)`), `fundamental` (constant anchor `F`), `deviation` (`(price − fundamental) / fundamental`, or zero if `fundamental ≤ 0`), and `round` (integer index). No private cost-basis, order-book, or history fields are broadcast; agents maintain any needed history in their own `custom_state`. Justification: keeps the sunk-cost / opportunity-cost decision reducible to public `deviation` so that biased and rational channels can be compared on a common observable.

### §8.3 Constraints And Frictions

Short selling: No — sell quantities are capped at current position (`min(quantity, position)`). Cash constraint: Yes — buy quantities are capped at `int(cash / price)`. Margin requirement: No. Circuit breakers: No. Trading hours: No — every round is a full price-formation event. Order type: current-market quantity orders only, tagged with `agent_type` for accounting; `bid_price` is echoed for logging but the clearing law uses the coordinator's running `price`.

### §8.4 Round Structure And Granularity

Each round proceeds in three coordinator steps: (1) `Market.perceive` ingests investor orders from the previous round and applies the price-update law; (2) `Market.decide` computes `deviation` and broadcasts the market-data dictionary; (3) investors run `perceive → decide → act` and submit fresh `{"action", "bid_price", "quantity", "agent_type", "reasoning"}` orders. One round represents one decision interval at a granularity coarse enough to capture aggregated commitment and reallocation flows rather than intra-day microstructure. A 200-round run notionally spans a multi-quarter horizon over which the sunk-cost / opportunity-cost divergence in `analysis-bases.md §4 Final divergence` becomes clearly distinguishable.

## §9 Parameter Seeds

| Parameter                                         | Meaning                                             | Default     | Source                                                                                                 |
|---------------------------------------------------|-----------------------------------------------------|-------------|--------------------------------------------------------------------------------------------------------|
| `market.extras.initial_price`                     | Initial market price at round 0                     | `100.0`     | Source: normalization (simulation-bases.md §6)                                                         |
| `market.extras.fundamental_value`                 | Constant forward-looking anchor                     | `100.0`     | Source: normalization; equal to `initial_price` so starting deviation is zero (simulation-bases.md §6) |
| `market.extras.price_impact`                      | Net-demand price-impact gain `lambda`               | `0.02`      | simulation-bases.md §3.1; Rule/players.py `Market.perceive`                                            |
| `market.extras.mean_reversion`                    | Pull-toward-fundamental gain `gamma`                | `0.015`     | simulation-bases.md §3.1                                                                               |
| `market.extras.noise_std`                         | Std-dev of Gaussian price noise `epsilon`           | `0.01`      | simulation-bases.md §3.1                                                                               |
| `sunkcostholder.num_instances`                    | Number of SunkCostHolder agents                     | `3`         | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `sunkcostholder.extras.initial_cash`              | Starting cash per SunkCostHolder                    | `1000000.0` | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `sunkcostholder.extras.initial_position`          | Starting inventory per SunkCostHolder               | `500`       | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `sunkcostholder.extras.hold_threshold`            | Positive reinforcement gate `deviation > θ`         | `0.1`       | simulation-bases.md §4.1; Arkes and Blumer (1985), 10.1016/0749-5978(85)90049-4                        |
| `sunkcostholder.extras.base_size`                 | Sunk-cost reinforcement sizing base                 | `200`       | simulation-bases.md §4.1                                                                               |
| `commitmentescalator.num_instances`               | Number of CommitmentEscalator agents                | `3`         | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `commitmentescalator.extras.initial_cash`         | Starting cash per CommitmentEscalator               | `1200000.0` | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `commitmentescalator.extras.initial_position`     | Starting inventory per CommitmentEscalator          | `400`       | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `commitmentescalator.extras.escalation_threshold` | Loss threshold for averaging-down `                 | deviation   | > θ`                                                                                                   |
| `commitmentescalator.extras.escalation_size`      | Escalation sizing base                              | `400`       | simulation-bases.md §4.2                                                                               |
| `rationalcutter.num_instances`                    | Number of RationalCutter agents                     | `2`         | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `rationalcutter.extras.initial_cash`              | Starting cash per RationalCutter                    | `1500000.0` | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `rationalcutter.extras.initial_position`          | Starting inventory per RationalCutter               | `600`       | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `rationalcutter.extras.cut_threshold`             | Forward-looking valuation gate `abs(deviation) > θ` | `0.05`      | simulation-bases.md §4.3; Odean (1998), 10.1111/0022-1082.00072                                        |
| `rationalcutter.extras.position_size`             | Rational sizing base                                | `350`       | simulation-bases.md §4.3                                                                               |
| `opportunitycosttrader.num_instances`             | Number of OpportunityCostTrader agents              | `2`         | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `opportunitycosttrader.extras.initial_cash`       | Starting cash per OpportunityCostTrader             | `1300000.0` | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `opportunitycosttrader.extras.initial_position`   | Starting inventory per OpportunityCostTrader        | `500`       | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `opportunitycosttrader.extras.realloc_threshold`  | Opportunity-cost gate `abs(deviation) > θ`          | `0.08`      | simulation-bases.md §4.4; Barber and Odean (2000), 10.1111/0022-1082.00226                             |
| `opportunitycosttrader.extras.position_size`      | Opportunity-cost sizing base                        | `300`       | simulation-bases.md §4.4                                                                               |
| `noisetrader.num_instances`                       | Number of NoiseTrader agents                        | `2`         | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `noisetrader.extras.initial_cash`                 | Starting cash per NoiseTrader                       | `500000.0`  | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `noisetrader.extras.initial_position`             | Starting inventory per NoiseTrader                  | `200`       | configs/SunkCostFallacy/Rule/players.yml                                                               |
| `noisetrader.extras.trade_probability`            | Bernoulli activation probability                    | `0.3`       | simulation-bases.md §4.5; Black (1986), 10.1111/j.1540-6261.1986.tb04513.x                             |
| `noisetrader.extras.noise_size`                   | Maximum uniform-random noise order size             | `100`       | simulation-bases.md §4.5                                                                               |
| `custom_state_hot_limit` (all investors)          | Hot-tier cache size for `custom_state`              | `3`         | configs/SunkCostFallacy/Rule/players.yml (runtime plumbing; not a scenario parameter)                  |

Normalization rows: `initial_price`, `fundamental_value`, and the per-investor `initial_cash` / `initial_position` fields are pure scale parameters set to numeric values that carry no independent empirical content; `initial_price = fundamental_value` guarantees a zero starting deviation.

## §10 Variants And Expected Signatures

### §10.1 Variants To Build

| Variant | Yes/No | Notes                                                                                                                                                                                                                                    |
|---------|--------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Rule    | Yes    | Deterministic baseline; encodes the §4 activation thresholds, quantity rules, and price-formation equation exactly as prescribed by the theoretical anchors and as implemented in `examples/SunkCostFallacy/Rule/players.py`.            |
| LLM     | Yes    | Needed to answer §3 research goal 4 (Rule vs LLM decision fidelity); persona-only reasoning replaces the Rule quantity formulas while keeping the canonical order schema (`action`, `bid_price`, `quantity`, `agent_type`, `reasoning`). |
| RuleLLM | Yes    | Exposes the Rule thresholds and quantity formulas as prompt content; isolates the effect of explicit rule guidance on LLM escalation and cutting decisions.                                                                              |
| Rag     | Yes    | Needed for §3 goal 5; adds retrieved behavioral evidence (Concorde escalation, retail averaging-down, Odean disposition sample) to the LLM prompt and reports retrieval coverage via `rag_stats.json`.                                   |

### §10.2 Expected Phenomenon Signature Per Variant

| Variant | Expected signature                                                                                                                                                                                                                                                      |
|---------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Rule    | Reproduces F1–F5 within their acceptance ranges. Biased losing-position holding rate ≥ 0.60; escalation buy share ≥ 15% of total buy quantity; rational-cut order flow ≥ 30% of biased buy quantity; opportunity reallocation ≥ 5%; performance drag strictly positive. |
| LLM     | Similar qualitative sunk-cost anatomy to Rule; magnitudes more variable across runs because persona-conditioned reasoning may partially rationalize away or exaggerate holding and averaging-down; parse-fallback counts reported in `summary.json` for quality gating. |
| RuleLLM | Should stay closer to the Rule baseline than pure LLM because the Rule thresholds and quantity formulas are exposed to the model as prompt content; residual deviation from Rule captures the effect of persona reasoning at the margins.                               |
| Rag     | Retrieved behavioral evidence (Concorde, retail averaging-down, Odean disposition) is expected to increase escalation salience and may sharpen the biased-vs-rational split; retrieval coverage reported in `rag_stats.json` and mirrored into `summary.json`.          |
