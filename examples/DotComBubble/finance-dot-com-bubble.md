# DotComBubble — Scenario Target

## §1 Meta

| Field        | Content                                                                        |
|--------------|--------------------------------------------------------------------------------|
| Name         | DotComBubble                                                                   |
| Domain       | finance                                                                        |
| Requested By | a77                                                                            |
| Produced By  | polish-simulation-pipeline.md (reverse-reconstruction from existing artefacts) |
| Created      | 2026-07-13                                                                     |
| Pipeline     | masim/skills/polish-simulation-pipeline.md                                     |
| Target Spec  | masim/skills/define-simulation-scenario-skill.md (v1.0)                        |
| Status       | released                                                                       |

## §2 Phenomenon Statement

### §2.1 Trigger

The phenomenon starts from a technology-sector asset whose price is initially at fundamental value. A narrative about a new technology economy spreads socially and convinces narrative-driven buyers that traditional valuation metrics no longer apply. This trigger is not a fundamental cash-flow shock; it is a coordination shift in which more participants believe that internet adoption justifies ever-higher prices.

### §2.2 Mechanism

The core mechanism is a narrative-driven positive feedback loop: rising price attracts narrative buyers and momentum followers, their demand pushes price farther above fundamental value, and IPO flippers add short-horizon turnover. Limits to arbitrage prevent value investors and short sellers from eliminating the mispricing because synchronization risk makes early correction costly.

### §2.3 Participants

The causal participants are new-economy evangelists, IPO flippers, momentum followers, skeptical value investors, and short sellers. New-economy evangelists and momentum followers supply destabilising demand. IPO flippers add speculative turnover that intensifies the boom but also creates selling pressure near the top. Skeptical value investors and short sellers supply stabilising pressure, but their force is limited by timing failure and squeeze risk.

### §2.4 Resolution

The bubble resolves when narrative demand exhausts and stabilising pressure accumulates. Momentum reversal accelerates the crash. Short sellers profit after the peak but may have suffered losses during the run-up. The end state is convergence toward fundamental value, with recovery time depending on the depth of the crash.

## §3 Research Goals

1. Can heterogeneous investors generate a visible dot-com-style bubble in which peak price exceeds fundamental value by at least 10%?
2. Does removing or weakening narrative demand (NewEconomyEvangelist) measurably reduce bubble amplitude and duration?
3. How sensitive are bubble height and crash severity to the price-impact coefficient and mean-reversion coefficient?
4. Do momentum followers amplify the run-up and crash, measurable via the Momentum Amplification Factor?
5. Do Rule, LLM, RuleLLM, and Rag variants differ measurably in bubble timing, peak ratio, crash severity, and momentum amplification?

## §4 Theoretical Anchors

### §4.1 Narrative Economics and Irrational Exuberance

| Field                 | Content                                                                                                                                                                                                                                            |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation         | Shiller, R. J. (2000). *Irrational Exuberance*. Princeton University Press. https://doi.org/10.1515/9781400865536; Shiller, R. J. (2017). Narrative economics. *American Economic Review*, 107(4), 967-1004. https://doi.org/10.1257/aer.107.4.967 |
| Key mechanism         | A compelling new-economy story relaxes valuation discipline and attracts persistent buying above fundamental value.                                                                                                                                |
| Key equation          | `buy when deviation(t) > -theta_capitulation; deviation(t) = (P(t) - F) / F`                                                                                                                                                                       |
| Motivates agent       | new-economy-evangelist                                                                                                                                                                                                                             |
| Parameter implication | `order_size` in [400, 800], capitulation threshold around -0.20 to -0.30.                                                                                                                                                                          |

### §4.2 IPO Underpricing and Flipping

| Field                 | Content                                                                                                                                                                      |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation         | Ofek, E., & Richardson, M. (2003). DotCom mania: The rise and fall of internet stock prices. *Journal of Finance*, 58(3), 1113-1137. https://doi.org/10.1111/1540-6261.00530 |
| Key mechanism         | Hot IPO markets create first-day demand, rapid turnover, and predictable selling by short-horizon holders.                                                                   |
| Key equation          | `sell when deviation(t) > theta_flip; buy when deviation(t) < 0`                                                                                                             |
| Motivates agent       | ipo-flipper                                                                                                                                                                  |
| Parameter implication | `flip_threshold` in [0.03, 0.10], `order_size` in [500, 900].                                                                                                                |

### §4.3 Momentum Trading

| Field                 | Content                                                                                                                                                                                                            |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation         | Jegadeesh, N., & Titman, S. (1993). Returns to buying winners and selling losers: Implications for stock market efficiency. *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x |
| Key mechanism         | Recent price increases attract trend-following demand; recent decreases attract selling.                                                                                                                           |
| Key equation          | `momentum(t) = (P(t) - P(t-1)) / P(t-1); buy when momentum > theta; sell when momentum < -theta`                                                                                                                   |
| Motivates agent       | momentum-follower                                                                                                                                                                                                  |
| Parameter implication | `momentum_threshold` in [0.01, 0.05], `order_size` in [300, 700].                                                                                                                                                  |

### §4.4 Value Investing and Fundamental Anchoring

| Field                 | Content                                                                                    |
|-----------------------|--------------------------------------------------------------------------------------------|
| Full citation         | Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.                          |
| Key mechanism         | Value investors buy below intrinsic value and sell above it, providing a valuation anchor. |
| Key equation          | `buy when deviation < theta_buy; sell when deviation > theta_sell`                         |
| Motivates agent       | skeptical-value-investor                                                                   |
| Parameter implication | `value_buy_threshold` in [-0.15, -0.05], `value_sell_threshold` in [0.15, 0.30].           |

### §4.5 Limits to Arbitrage and Synchronization Risk

| Field                 | Content                                                                                                                               |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| Full citation         | Abreu, D., & Brunnermeier, M. K. (2003). Bubbles and crashes. *Econometrica*, 71(1), 173-204. https://doi.org/10.1111/1468-0262.00401 |
| Key mechanism         | Short sellers who know a bubble exists can still lose money if they attack too early due to coordination failure.                     |
| Key equation          | `short when deviation > theta_short; cover when deviation < theta_cover`                                                              |
| Motivates agent       | short-seller                                                                                                                          |
| Parameter implication | `short_threshold` in [0.10, 0.25], `cover_threshold` in [-0.10, 0.00].                                                                |

## §5 Stylized Facts

| #  | Fact                                                                               | Source                                 | Acceptance Metric                               |
|----|------------------------------------------------------------------------------------|----------------------------------------|-------------------------------------------------|
| F1 | NASDAQ rose from ~750 to ~5,048 (1995-2000), a multi-hundred-percent overvaluation | Shiller (2000); NASDAQ historical data | `bubble_amplitude_index` > 0.10                 |
| F2 | The bubble persisted for several years before crashing                             | Abreu & Brunnermeier (2003)            | `bubble_duration` > 15 rounds                   |
| F3 | Post-peak decline was roughly 78%                                                  | Ofek & Richardson (2003)               | `crash_severity` in [0.30, 0.80]                |
| F4 | Momentum and trend-following amplified the run-up                                  | Jegadeesh & Titman (1993)              | `momentum_amplification_factor` in [0.20, 0.50] |
| F5 | Value investors and short sellers were correct but early                           | Abreu & Brunnermeier (2003)            | `short_seller_resistance` > 0                   |

## §6 Historical / Empirical Anchors

### §6.1 NASDAQ Dot-Com Bubble (1995-2002)

The NASDAQ Composite rose from roughly 750 in 1995 to 5,048 in March 2000, then declined roughly 78% by October 2002. This is the primary calibration anchor for bubble amplitude and crash severity.

### §6.2 Internet IPO Market (1999)

Dot-com IPO first-day returns were often extreme (VA Linux rose roughly 698% on its first day). This anchors the IPO flipper's behavior and order size.

### §6.3 Short-Seller and Value-Investor Timing Failure

Julian Robertson's Tiger Management suffered underperformance before the crash despite identifying overvaluation. This anchors the stabiliser timing-failure dynamic.

## §7 Agent Roster

| # | Agent (kebab)            | Theory Family              | Market Role               | Time Horizon | Risk Tolerance | Primary Signals            |
|---|--------------------------|----------------------------|---------------------------|--------------|----------------|----------------------------|
| 1 | new-economy-evangelist   | Narrative Economics (§4.1) | destabilising             | medium       | high           | deviation                  |
| 2 | ipo-flipper              | IPO Underpricing (§4.2)    | mixed                     | short        | medium         | deviation                  |
| 3 | momentum-follower        | Momentum Trading (§4.3)    | destabilising             | short        | high           | momentum (1-period return) |
| 4 | skeptical-value-investor | Value Investing (§4.4)     | stabilising               | long         | low            | deviation                  |
| 5 | short-seller             | Limits to Arbitrage (§4.5) | stabilising (constrained) | medium       | high           | deviation                  |

## §8 Environment Specification

### §8.1 Price Formation

Single-asset market with normalized price. Price update formula:
```
P(t+1) = max(P(t) + lambda * D(t) + gamma * (F - P(t)) + epsilon(t), 0.01)
D(t) = buy_volume(t) - sell_volume(t)
epsilon(t) ~ N(0, sigma^2)
```

### §8.2 Information Broadcast

Market broadcasts: `price`, `fundamental`, `deviation`, `round`. All agents observe the same broadcast each round.

### §8.3 Constraints and Frictions

- Cash constraint: cannot buy more than affordable.
- Inventory constraint: cannot sell more than held.
- No explicit short-selling cost (short sellers use standard sell mechanics).
- Positive price floor at 0.01.

### §8.4 Round Granularity

Each round represents one trading period. Full experiments use 200 rounds. Each round: Market receives orders -> updates price -> broadcasts state -> investors observe and decide -> emit orders for next round.

## §9 Parameter Seeds

| #  | Parameter            | Baseline | Belongs to               | Empirical Range | Source                      |
|----|----------------------|----------|--------------------------|-----------------|-----------------------------|
| 1  | initial_price        | 100.0    | environment              | normalization   | normalization               |
| 2  | fundamental_value    | 100.0    | environment              | normalization   | normalization               |
| 3  | price_impact         | 0.01     | environment              | [0.005, 0.05]   | simulation-bases.md §3      |
| 4  | mean_reversion       | 0.005    | environment              | [0.001, 0.01]   | simulation-bases.md §3      |
| 5  | noise_std            | 1.0      | environment              | [0.5, 2.0]      | simulation-bases.md §3      |
| 6  | order_size           | 600      | new-economy-evangelist   | [400, 800]      | simulation-bases.md §6      |
| 7  | order_size           | 700      | ipo-flipper              | [500, 900]      | simulation-bases.md §6      |
| 8  | flip_threshold       | 0.05     | ipo-flipper              | [0.03, 0.10]    | Ofek & Richardson (2003)    |
| 9  | order_size           | 500      | momentum-follower        | [300, 700]      | simulation-bases.md §6      |
| 10 | momentum_threshold   | 0.02     | momentum-follower        | [0.01, 0.05]    | Jegadeesh & Titman (1993)   |
| 11 | order_size           | 400      | skeptical-value-investor | [200, 600]      | simulation-bases.md §6      |
| 12 | value_buy_threshold  | -0.10    | skeptical-value-investor | [-0.15, -0.05]  | Graham (1949)               |
| 13 | value_sell_threshold | 0.20     | skeptical-value-investor | [0.15, 0.30]    | Graham (1949)               |
| 14 | order_size           | 400      | short-seller             | [200, 600]      | simulation-bases.md §6      |
| 15 | short_threshold      | 0.15     | short-seller             | [0.10, 0.25]    | Abreu & Brunnermeier (2003) |
| 16 | cover_threshold      | -0.05    | short-seller             | [-0.10, 0.00]   | Abreu & Brunnermeier (2003) |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Decision Mechanism                                        |
|---------|--------|-----------------------------------------------------------|
| Rule    | Yes    | Deterministic thresholds from §4                          |
| LLM     | Yes    | Persona-only language reasoning                           |
| RuleLLM | Yes    | Persona plus explicit threshold rules                     |
| Rag     | Yes    | RuleLLM-style reasoning with retrieved historical context |

### §10.2 Pass / Fail Criteria

| # | Criterion          | Metric | Threshold       |
|---|--------------------|--------|-----------------|
| 1 | Bubble forms       | BAI    | > 0.10          |
| 2 | Bubble persists    | BD     | > 15 rounds     |
| 3 | Crash occurs       | CS     | in [0.30, 0.80] |
| 4 | Momentum amplifies | MAF    | in [0.20, 0.50] |
