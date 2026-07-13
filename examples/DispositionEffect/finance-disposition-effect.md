# DispositionEffect — Scenario Target

## §1 Meta

| Field       | Content                                                     |
|-------------|-------------------------------------------------------------|
| Name        | DispositionEffect                                           |
| Domain      | finance                                                     |
| Produced By | polish-simulation-pipeline.md (reverse-reconstruction seed) |
| Created     | 2026-07-14                                                  |
| Pipeline    | masim/skills/polish-simulation-pipeline.md                  |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.0)     |

## §2 Phenomenon Statement

### §2.1 Trigger

The phenomenon starts from investors who anchor to their original purchase price as a psychological reference point. When the market price rises above cost basis, Prospect Theory's concave value function in the gain domain drives premature profit-taking. When the price falls below cost basis, the convex value function in the loss domain and loss aversion (lambda approx 2.25) discourage selling, creating the disposition effect.

### §2.2 Mechanism

The core mechanism is asymmetric treatment of gains versus losses relative to a reference point. Investors evaluate outcomes through Kahneman and Tversky's (1979) S-shaped value function: risk-averse in gains (sell quickly to lock in profit) and risk-seeking in losses (hold and hope for recovery). Loss aversion amplifies the asymmetry: losses are felt approximately 2.25 times more intensely than equivalent gains, further reducing the willingness to realize losses.

### §2.3 Participants

The causal participants are disposition-biased retail investors (primary behavioral agents), rational expected-utility maximizers (non-behavioral baseline), tax-aware investors (anti-disposition via economic incentive), passive index holders (zero-trading benchmark), and institutional investors (weakened disposition via professional discipline).

### §2.4 Resolution

The simulation resolves when sufficient rounds have elapsed to measure the Proportion of Gains Realized (PGR) and Proportion of Losses Realized (PLR) at statistically meaningful sample sizes. The disposition effect is confirmed when PGR exceeds PLR with a ratio approximating the Odean (1998) benchmark of 1.5. Performance drag is measured as the terminal wealth gap between disposition-biased and rational investors.

## §3 Research Goals

1. Can heterogeneous investor rules reproduce the empirical PGR/PLR ratio of approximately 1.5 matching Odean (1998)?
2. Does the disposition coefficient (DC = PGR - PLR) remain significantly positive across different market volatility regimes?
3. How does the annual performance drag of disposition-biased investors compare to the 3.2-5.7% empirical benchmark?
4. Does tax-loss harvesting produce measurably anti-disposition behavior (PLR > PGR) as predicted by Constantinides (1983)?
5. Do Rule, LLM, RuleLLM, and Rag variants differ measurably in disposition strength, holding period asymmetry, and performance drag?

## §4 Theoretical Anchors

### §4.1 Prospect Theory and Reference Dependence

| Field                      | Content                                                                                                                                                  |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation              | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185 |
| Key mechanism (<=30 words) | Investors evaluate outcomes relative to a reference point with an S-shaped value function: concave for gains, convex for losses, steeper for losses.     |
| Key equation               | `v(x) = x^alpha if x >= 0; -lambda*(-x)^beta if x < 0` with alpha = beta = 0.88, lambda = 2.25.                                                          |
| Motivates agent            | disposition-investor                                                                                                                                     |
| Parameter implication      | `gain_threshold` in [0.02, 0.10], `loss_threshold` in [-0.15, -0.05], `loss_aversion` approx 2.25.                                                       |

### §4.2 Disposition Effect Mechanism

| Field                      | Content                                                                                                                                                                                                              |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation              | Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long: Theory and evidence. *Journal of Finance*, 40(3), 777-790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x |
| Key mechanism (<=30 words) | Four mechanisms drive disposition: loss aversion, mental accounting per position, regret avoidance, and self-control failure.                                                                                        |
| Key equation               | `PGR = RealizedGains / (RealizedGains + PaperGains)`, `PLR = RealizedLosses / (RealizedLosses + PaperLosses)`.                                                                                                       |
| Motivates agent            | disposition-investor, institutional-investor                                                                                                                                                                         |
| Parameter implication      | `sell_fraction_gain` >> `sell_fraction_loss` preserves asymmetry; institutional thresholds are wider and symmetric.                                                                                                  |

### §4.3 Empirical PGR/PLR Evidence

| Field                      | Content                                                                                                                                            |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation              | Odean, T. (1998). Are investors reluctant to realize their losses? *Journal of Finance*, 53(5), 1775-1798. https://doi.org/10.1111/0022-1082.00078 |
| Key mechanism (<=30 words) | 10,000 individual investor accounts show PGR approx 14.8%, PLR approx 9.8%, with December reversal from tax-loss harvesting.                       |
| Key equation               | `PGR/PLR approx 1.51`; `annual_performance_drag approx 3.2%`.                                                                                      |
| Motivates agent            | disposition-investor (calibration target)                                                                                                          |
| Parameter implication      | Calibration: PGR in [0.10, 0.20], PLR in [0.06, 0.12], ratio in [1.4, 1.7].                                                                        |

### §4.4 Tax-Loss Harvesting as Anti-Disposition

| Field                      | Content                                                                                                                                    |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation              | Constantinides, G. M. (1983). Capital market equilibrium with personal tax. *Econometrica*, 51(3), 611-636. https://doi.org/10.1086/261210 |
| Key mechanism (<=30 words) | Optimal tax policy realizes losses immediately to harvest tax deductions and defers gains to postpone capital gains tax.                   |
| Key equation               | Sell when `gain_loss <= tax_loss_threshold`; hold when `gain_loss >= capital_gains_hold`.                                                  |
| Motivates agent            | tax-aware-investor                                                                                                                         |
| Parameter implication      | `tax_loss_threshold` in [-0.08, -0.03], `capital_gains_hold` in [0.10, 0.25], `tax_harvest_fraction` in [0.3, 0.7].                        |

### §4.5 Institutional Discipline and Weakened Disposition

| Field                      | Content                                                                                                                                                                                                      |
|----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation              | Shapira, Z., & Venezia, I. (2001). Patterns of trading activity of institutional and individual investors. *Journal of Banking and Finance*, 25(8), 1547-1566. https://doi.org/10.1016/S0378-4266(00)00100-2 |
| Key mechanism (<=30 words) | Professional managers exhibit weaker disposition effect due to fiduciary duty, performance evaluation, and systematic risk management.                                                                       |
| Key equation               | Symmetric sell fraction for both gains and losses: `quantity = -position * sell_fraction` at either threshold.                                                                                               |
| Motivates agent            | institutional-investor                                                                                                                                                                                       |
| Parameter implication      | `gain_threshold` in [0.15, 0.30], `loss_threshold` in [-0.20, -0.10], `sell_fraction` in [0.3, 0.5].                                                                                                         |

## §5 Stylized Facts

| #  | Stylized Fact                                   | Numeric Range                | Source                                                     | Acceptance Metric                               |
|----|-------------------------------------------------|------------------------------|------------------------------------------------------------|-------------------------------------------------|
| F1 | PGR exceeds PLR for individual investors        | PGR/PLR in [1.4, 1.7]        | Odean (1998) DOI:10.1111/0022-1082.00078                   | `validate_disposition_effect`                   |
| F2 | Annual performance drag from disposition bias   | 3.2-5.7% drag                | Odean (1998)                                               | `performance_drag_index`                        |
| F3 | December reversal from tax-loss harvesting      | PLR > PGR in December        | Odean (1998); Constantinides (1983)                        | `tax_reversal_index`                            |
| F4 | Institutional investors show weaker disposition | Institutional DC < Retail DC | Shapira & Venezia (2001) DOI:10.1016/S0378-4266(00)00100-2 | `disposition_coefficient` comparison            |
| F5 | Loss aversion coefficient approximately 2.25    | lambda in [2.0, 2.5]         | Kahneman & Tversky (1979) DOI:10.2307/1914185              | `sell_fraction_gain / sell_fraction_loss` ratio |

## §6 Historical / Empirical Anchors

### Odean (1998) US Individual Investors

10,000 discount brokerage accounts (1987-1993). PGR = 14.8%, PLR = 9.8%, PGR/PLR = 1.51. December reversal: PLR temporarily exceeds PGR for tax-loss harvesting. Annual return drag approximately 3.2%.

Source: Odean, T. (1998). DOI: https://doi.org/10.1111/0022-1082.00078

### Grinblatt & Keloharju (2001) Finland

Helsinki Stock Exchange. Disposition effect confirmed cross-culturally: PGR/PLR approximately 1.60. Institutional investors showed weaker effect.

Source: Grinblatt, M. & Keloharju, M. (2001). DOI: https://doi.org/10.1111/0022-1082.00302

### Chen et al. (2007) China

Shanghai and Shenzhen exchanges. PGR/PLR approximately 1.67 -- stronger disposition effect in retail-dominated markets.

Source: Chen, G., Kim, K. A., Nofsinger, J. R., & Rui, O. M. (2007). DOI: https://doi.org/10.1016/j.jbankfin.2006.02.010

## §7 Agent Roster

| # | Agent (kebab)          | Archetype                          | Theory Family                               | Market Role                   | Time Horizon | Risk Tolerance        |
|---|------------------------|------------------------------------|---------------------------------------------|-------------------------------|--------------|-----------------------|
| 1 | disposition-investor   | Disposition-effect investor        | Behavioral Finance / Prospect Theory        | Context-dependent             | medium       | medium (asymmetric)   |
| 2 | rational-investor      | Rational expected-utility investor | Neoclassical Finance                        | Stabilising                   | short-medium | medium                |
| 3 | tax-aware-investor     | Tax-aware investor                 | Tax-Optimal Portfolio Management            | Counter-disposition           | medium-long  | medium                |
| 4 | index-holder           | Passive index holder               | Modern Portfolio Theory / Passive Investing | Neutral                       | very long    | market                |
| 5 | institutional-investor | Institutional investor             | Behavioral Finance (weakened bias)          | Weak-disposition professional | medium       | medium (professional) |

## §8 Environment Specification

### §8.1 Price Formation

```
P(t+1) = P(t) + lambda * NetDemand(t) + gamma * [F(t) - P(t)] + epsilon(t) + N(t)
```

Where: lambda = 0.08 (price impact), gamma = 0.05 (mean reversion), F(t) = 100.0 (fundamental value), epsilon ~ N(0, sigma^2) with sigma = 0.6, N(t) = news shock with probability 0.15 and magnitude ~ Uniform(-4, 4).

### §8.2 Information Broadcast

Each round the market broadcasts: `{price, prev_price, return, return_pct, volume, net_demand, news_shock, round}`.

### §8.3 Constraints and Frictions

- Minimum price floor: 1.0
- Position limits per investor type (max_position from config)
- Cash constraint: buy orders limited by available cash
- Minimum trade quantity: 0.5 shares

### §8.4 Round Granularity

Six-phase round loop: (1) Market.perceive collects orders, (2) Market.decide computes price dynamics, (3) Market.act broadcasts market data, (4) Investor.perceive updates state, (5) Investor.decide applies type-specific logic, (6) Investor.act executes trade.

## §9 Parameter Seeds

| #  | Parameter                      | Default | Belongs to                             | Empirical Range | Source                    |
|----|--------------------------------|---------|----------------------------------------|-----------------|---------------------------|
| 1  | initial_price                  | 100.0   | environment                            | normalization   | normalization             |
| 2  | fundamental_value              | 100.0   | environment                            | normalization   | normalization             |
| 3  | price_impact                   | 0.08    | environment                            | [0.05, 0.15]    | calibration               |
| 4  | mean_reversion                 | 0.05    | environment                            | [0.02, 0.10]    | calibration               |
| 5  | noise_std                      | 0.6     | environment                            | [0.3, 1.0]      | calibration               |
| 6  | news_probability               | 0.15    | environment                            | [0.05, 0.30]    | calibration               |
| 7  | news_impact_range              | 4.0     | environment                            | [2.0, 8.0]      | calibration               |
| 8  | gain_threshold (disposition)   | 0.03    | disposition-investor                   | [0.02, 0.10]    | Odean (1998)              |
| 9  | loss_threshold (disposition)   | -0.10   | disposition-investor                   | [-0.15, -0.05]  | Kahneman & Tversky (1979) |
| 10 | loss_aversion                  | 2.25    | disposition-investor                   | [2.0, 2.5]      | Kahneman & Tversky (1979) |
| 11 | sell_fraction_gain             | 0.50    | disposition-investor                   | [0.3, 0.7]      | calibration               |
| 12 | sell_fraction_loss             | 0.15    | disposition-investor                   | [0.05, 0.25]    | calibration               |
| 13 | target_allocation              | 0.50    | rational-investor                      | [0.3, 0.7]      | portfolio theory          |
| 14 | rebalance_threshold            | 0.10    | rational-investor                      | [0.05, 0.15]    | calibration               |
| 15 | tax_loss_threshold             | -0.05   | tax-aware-investor                     | [-0.08, -0.03]  | Constantinides (1983)     |
| 16 | capital_gains_hold             | 0.20    | tax-aware-investor                     | [0.10, 0.25]    | Constantinides (1983)     |
| 17 | tax_harvest_fraction           | 0.50    | tax-aware-investor                     | [0.3, 0.7]      | calibration               |
| 18 | gain_threshold (institutional) | 0.25    | institutional-investor                 | [0.15, 0.30]    | Shapira & Venezia (2001)  |
| 19 | loss_threshold (institutional) | -0.15   | institutional-investor                 | [-0.20, -0.10]  | Shapira & Venezia (2001)  |
| 20 | sell_fraction (institutional)  | 0.40    | institutional-investor                 | [0.3, 0.5]      | calibration               |
| 21 | initial_purchase_price         | 100.0   | all investors                          | normalization   | normalization             |
| 22 | initial_cash                   | 10000.0 | all investors                          | normalization   | normalization             |
| 23 | initial_position               | 30.0    | disposition/rational/tax/institutional | [20, 50]        | calibration               |
| 24 | initial_position (index)       | 50.0    | index-holder                           | [30, 100]       | calibration               |

## §10 Variants and Validation

### §10.1 Variants to Build

| Variant | Build? | Rationale                                                     |
|---------|--------|---------------------------------------------------------------|
| Rule    | Yes    | Deterministic baseline; required for finance-domain scenarios |
| LLM     | Yes    | LLM persona-driven disposition behavior                       |
| RuleLLM | Yes    | Hybrid: embedded quantitative rules + LLM reasoning           |
| Rag     | Yes    | RAG-augmented with prospect theory literature retrieval       |

### §10.2 Pass / Fail Criteria

1. Rule variant PGR/PLR ratio in [1.2, 2.0] (centered on Odean 1998 benchmark of 1.5).
2. DispositionInvestor terminal wealth < RationalInvestor terminal wealth (performance drag > 0).
3. TaxAwareInvestor PLR > DispositionInvestor PLR (anti-disposition confirmed).
4. All four variants complete 200 rounds without uncaught exceptions.
