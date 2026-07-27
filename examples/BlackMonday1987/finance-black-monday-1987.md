# BlackMonday1987

## §1 Meta

| Field       | Content                                                                                                                              |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------|
| Name        | BlackMonday1987                                                                                                                      |
| Domain      | finance                                                                                                                              |
| Phenomenon  | Portfolio insurance and program trading create a dynamic-hedging feedback loop that amplifies an initial price decline into a crash. |
| Pipeline    | masim/skills/create-simulation-pipeline.md                                                                                           |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.0)                                                                              |

## §2 Phenomenon Statement

### §2.1 Trigger

The scenario begins with a negative index price shock in a market already using portfolio insurance, program trading, and futures-linked execution. The shock pushes price below the first rebalancing thresholds used by mechanical hedging programs. Because the fundamental value is held constant, the initial decline is treated as a market-mechanism stress rather than a cash-flow shock.

### §2.2 Mechanism

The core mechanism is a dynamic-hedging feedback loop. Portfolio insurers sell as prices fall, program traders add threshold-based sell orders, and index arbitrageurs transmit futures-market pressure into the cash index. Their combined order imbalance depresses price further, causing more mechanical selling, wider liquidity stress, and temporary breakdown of price discovery.

### §2.3 Participants

The causally relevant participants are portfolio insurers, index arbitrageurs, program/feedback traders, value investors, and noise traders. Portfolio insurers and program traders provide the mechanical sell pressure, index arbitrageurs transmit cross-market stress, value investors provide delayed stabilizing demand, and noise traders supply background order flow. The market coordinator aggregates the orders and updates the index price.

### §2.4 Resolution

The crash stops when automated sellers exhaust inventory, price falls far enough to activate value-investor demand, and mean reversion becomes large relative to remaining sell pressure. The resolution is partial stabilization after a large drawdown, not a smooth return to fair value. No circuit breaker is included because the historical 1987 event occurred before modern U.S. market-wide circuit breakers.

## §3 Research Goals

1. Measure whether portfolio insurance plus program trading can generate a Black Monday-sized drawdown of roughly 15%-35%.
2. Test by ablation whether removing portfolio insurers or program traders materially reduces crash depth, crash velocity, and sell-volume concentration.
3. Sweep `hedge_ratio`, `feedback_strength`, and `price_impact` to estimate when dynamic hedging becomes self-reinforcing.
4. Compare Rule, LLM, RuleLLM, and Rag variants to see whether model-based reasoning changes crash timing, drawdown, and stabilizing value demand.

## §4 Theoretical Anchors

### §4.1 Portfolio insurance and dynamic hedging

| Field                     | Content                                                                                                                                            |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Leland, H. E. (1980). Who should buy portfolio insurance? *Journal of Finance*, 35(2), 581-594. https://doi.org/10.1111/j.1540-6261.1980.tb02190.x |
| Key mechanism (≤30 words) | Dynamic hedgers sell falling markets to reduce equity exposure, creating endogenous positive feedback when many agents rebalance together.         |
| Key equation              | `sell_qty = hedge_ratio * abs(deviation) * position` when `deviation < -rebalance_threshold`.                                                      |
| Motivates agent           | portfolio-insurer                                                                                                                                  |
| Parameter implication     | `rebalance_threshold` 0.02-0.05 and `hedge_ratio` 0.30-0.70 in §9.                                                                                 |

### §4.2 Index futures arbitrage transmission

| Field                     | Content                                                                                                                                                                                              |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Stoll, H. R., & Whaley, R. E. (1990). The dynamics of stock index and stock index futures returns. *Journal of Financial and Quantitative Analysis*, 25(4), 441-468. https://doi.org/10.2307/2331010 |
| Key mechanism (≤30 words) | Futures-market pressure can lead cash-market returns when arbitrage desks sell spot baskets against discounted futures.                                                                              |
| Key equation              | `Q_arb = base_size` when `abs(deviation) > arb_threshold`, direction set by spot/fair-value gap.                                                                                                     |
| Motivates agent           | index-arbitrageur                                                                                                                                                                                    |
| Parameter implication     | `arb_threshold` 0.005-0.03 and `base_size` 40-120 in §9.                                                                                                                                             |

### §4.3 Positive feedback trading

| Field                     | Content                                                                                                                                                                                                                                          |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Positive feedback investment strategies and destabilizing rational speculation. *Journal of Finance*, 45(2), 379-395. https://doi.org/10.1111/j.1540-6261.1990.tb03695.x |
| Key mechanism (≤30 words) | Traders who sell after price declines can make rational speculation destabilizing when feedback demand is large enough.                                                                                                                          |
| Key equation              | `Q_program = base_size * (1 + feedback_strength * abs(deviation) * 10)`.                                                                                                                                                                         |
| Motivates agent           | program-trader                                                                                                                                                                                                                                   |
| Parameter implication     | `trigger_threshold` 0.005-0.03 and `feedback_strength` 0.8-1.5 in §9.                                                                                                                                                                            |

### §4.4 Limits to arbitrage and value floors

| Field                     | Content                                                                                                                                               |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x |
| Key mechanism (≤30 words) | Correct beliefs do not eliminate mispricing instantly because stabilizing capital is limited and risky during crashes.                                |
| Key equation              | `value_buy = base_size` when `price < fundamental * (1 - value_discount)`.                                                                            |
| Motivates agent           | value-investor                                                                                                                                        |
| Parameter implication     | `value_discount` 0.10-0.30 and `base_size` 20-80 in §9.                                                                                               |

### §4.5 Noise and microstructure stress

| Field                     | Content                                                                                                                                                                                                                                           |
|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x; Kyle, A. S. (1985). Continuous auctions and insider trading. *Econometrica*, 53(6), 1315-1335. https://doi.org/10.2307/1913210 |
| Key mechanism (≤30 words) | Uninformed order flow and price impact create background volatility and make liquidity provision costly under imbalance.                                                                                                                          |
| Key equation              | `trade ~ Bernoulli(trade_probability)` with bounded random order quantity.                                                                                                                                                                        |
| Motivates agent           | noise-trader                                                                                                                                                                                                                                      |
| Parameter implication     | `trade_probability` 0.03-0.10 and `price_impact` 0.03-0.08 in §9.                                                                                                                                                                                 |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                                  | Quantitative range             | Citation                                                                            | Acceptance metric                                         |
|----|--------------------------------------------------------------------------------------|--------------------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------|
| F1 | The simulated index experiences a crash-scale drawdown.                              | 15% <= max drawdown <= 35%     | Brady Commission (1988), Report of the Presidential Task Force on Market Mechanisms | `analysis.py: _compute_max_drawdown()` in [15, 35]        |
| F2 | The crash is fast, with peak per-round decline in the cascade phase.                 | crash velocity >= 2% per round | Brady Commission (1988) intraday timeline                                           | `analysis.py: _compute_crash_velocity()` >= 2             |
| F3 | Portfolio insurers and program traders dominate sell-side volume during the cascade. | combined sell volume >= 50%    | Brady Commission (1988)                                                             | `analysis.py: agent_vwap` sell attribution >= 0.50        |
| F4 | Feedback dynamics produce positive return autocorrelation during the crash phase.    | AC1 0.30-0.60                  | Lo & MacKinlay (1988), https://doi.org/10.1093/rfs/1.1.41                           | `analysis.py: _compute_autocorrelation()` in [0.30, 0.60] |

## §6 Historical / Empirical Anchors

### §6.1 Black Monday 1987

| Field             | Content                                                                                                                                                                                                                                                        |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Black Monday 1987, 1987-10-19.                                                                                                                                                                                                                                 |
| Trigger           | Prior-week selling, portfolio insurance rebalancing, futures-market pressure, and liquidity stress interacted after the market opened.                                                                                                                         |
| Quantitative arc  | The Dow Jones Industrial Average fell 22.6% in one day; S&P 500 futures and cash markets experienced large lead-lag dislocations and severe order imbalance.                                                                                                   |
| Agent mapping     | portfolio-insurer maps to dynamic hedging sellers; index-arbitrageur maps to futures-cash transmission desks; program-trader maps to automated feedback selling; value-investor maps to delayed contrarian demand; noise-trader maps to background order flow. |
| Primary source(s) | Presidential Task Force on Market Mechanisms. (1988). *Report of the Presidential Task Force on Market Mechanisms*. U.S. Government Printing Office.                                                                                                           |

### §6.2 Futures-cash lead-lag during crash stress

| Field             | Content                                                                                                                                                     |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | S&P 500 futures and cash-market lead-lag around the 1987 crash.                                                                                             |
| Trigger           | Futures selling by hedgers pushed derivatives below fair value, inducing cash-market basket selling by arbitrageurs.                                        |
| Quantitative arc  | Stoll and Whaley document futures leading cash returns by minutes and occasionally longer during stressed intervals.                                        |
| Agent mapping     | index-arbitrageur maps directly to the futures-cash transmission channel; portfolio-insurer and program-trader create the initiating futures/cash pressure. |
| Primary source(s) | Stoll & Whaley (1990), https://doi.org/10.2307/2331010                                                                                                      |

## §7 Agent Roster

| Agent name (kebab) | Real-world counterpart   | Theory family (§4 anchor)                | Domain role       | Primary signals               | Intent line                                                                | Expected pool match                                |
|--------------------|--------------------------|------------------------------------------|-------------------|-------------------------------|----------------------------------------------------------------------------|----------------------------------------------------|
| portfolio-insurer  | mutual fund / pension    | Liquidity / Funding (§4.1)               | Destabilising     | price, fundamental, deviation | Exists to reduce equity exposure mechanically as the index falls.          | examples/AGENT_POOL/finance/portfolio-insurer.md   |
| index-arbitrageur  | proprietary trading desk | Microstructure (§4.2)                    | Context-dependent | price, fundamental, deviation | Exists to transmit futures-cash dislocations into spot index order flow.   | examples/AGENT_POOL/finance/index-arbitrageur.md   |
| program-trader     | quant fund / CTA         | Behavioral Finance (§4.3)                | Destabilising     | price, deviation, round       | Exists to amplify downward moves through threshold-based feedback selling. | examples/AGENT_POOL/finance/program-trader.md      |
| value-investor     | mutual fund / pension    | Fundamental / Value (§4.4)               | Stabilising       | price, fundamental, deviation | Exists to supply contrarian demand after a sufficiently deep discount.     | examples/AGENT_POOL/finance/fundamental-analyst.md |
| noise-trader       | retail investor          | Noise / Liquidity-providing noise (§4.5) | Context-dependent | price, round, rng_state       | Exists to provide stochastic background order flow.                        | examples/AGENT_POOL/finance/noise-trader.md        |

## §8 Environment Specification

### §8.1 Price Formation

The environment is a single-price index market. Price follows `P(t+1) = P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t)`, where `D(t)` is buy quantity minus sell quantity. The high price-impact coefficient represents stressed 1987 intraday liquidity and delayed specialist absorption.

### §8.2 Information Broadcast

Each round broadcasts `price`, `fundamental`, `deviation`, and `round`. These are sufficient for the level-triggered portfolio insurance, index arbitrage, program trading, value-investing, and noise-trading mechanisms already implemented in the scenario. No `prev_price` signal is required because the core triggers are level/deviation based rather than return based.

### §8.3 Constraints and Frictions

No market-wide circuit breaker is modeled. Agents are constrained by cash, inventory, base order size, and maximum realizable quantity. The market applies a positive price floor and constant fundamental value so the crash comes from order-flow feedback rather than deteriorating fundamentals.

### §8.4 Round Granularity

One round represents an intraday trading interval in which program trades can be submitted, orders are aggregated, and the index price updates. The 200-round default config supports pre-crash stability, feedback onset, cascade escalation, floor formation, and recovery phases. Historical timing is calibrated against the 1987 single-session crash and Stoll-Whaley intraday lead-lag evidence.

## §9 Parameter Seeds

| Parameter                 | Symbol       | Belongs to (agent / environment) | Empirical range       | Candidate default | Source citation                                                                                    |
|---------------------------|--------------|----------------------------------|-----------------------|-------------------|----------------------------------------------------------------------------------------------------|
| rebalance threshold       | `theta_pi`   | portfolio-insurer (§7)           | 0.02-0.05             | 0.02              | Leland (1980), https://doi.org/10.1111/j.1540-6261.1980.tb02190.x; Brady Commission (1988)         |
| hedge ratio               | `h`          | portfolio-insurer (§7)           | 0.30-0.70             | 0.50              | Brady Commission (1988)                                                                            |
| arbitrage threshold       | `theta_arb`  | index-arbitrageur (§7)           | 0.005-0.03            | 0.01              | Stoll & Whaley (1990), https://doi.org/10.2307/2331010                                             |
| program trigger threshold | `theta_prog` | program-trader (§7)              | 0.005-0.03            | 0.01              | Brady Commission (1988); De Long et al. (1990), https://doi.org/10.1111/j.1540-6261.1990.tb03695.x |
| feedback strength         | `phi`        | program-trader (§7)              | 0.80-1.50             | 1.20              | De Long et al. (1990), https://doi.org/10.1111/j.1540-6261.1990.tb03695.x                          |
| value discount            | `m`          | value-investor (§7)              | 0.10-0.30             | 0.15              | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                       |
| trade probability         | `p_n`        | noise-trader (§7)                | 0.03-0.10             | 0.05              | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                                   |
| price impact              | `lambda`     | environment (§8.1)               | 0.03-0.08             | 0.05              | Kyle (1985), https://doi.org/10.2307/1913210; Brady Commission (1988)                              |
| mean reversion            | `gamma`      | environment (§8.1)               | 0.005-0.02            | 0.01              | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                       |
| fundamental value         | `F`          | environment (§8.1)               | Source: normalization | 250.0             | Source: normalization                                                                              |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤1 sentence)                                                                        |
|---------|--------|------------------------------------------------------------------------------------------------|
| Rule    | Yes    | Required deterministic baseline for the crash feedback mechanism.                              |
| LLM     | Yes    | Tests whether persona-only decision making delays or amplifies crash behavior.                 |
| RuleLLM | Yes    | Tests whether explicit rule prompts preserve the deterministic mechanism with model reasoning. |
| Rag     | Yes    | Tests whether retrieved 1987 crash context changes agent behavior.                             |

### §10.2 Pass / Fail Criteria

| Criterion                                                            | Status when satisfied |
|----------------------------------------------------------------------|-----------------------|
| All §5 stylized facts reproduced within their ranges                 | green                 |
| Every §3 research question answerable from analysis                  | green                 |
| Ablating any §7 agent produces a measurable change                   | green                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green                 |
