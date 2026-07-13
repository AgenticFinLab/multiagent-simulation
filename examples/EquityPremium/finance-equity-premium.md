# EquityPremium — Scenario Target

## §1 Meta

| Field       | Content                                                                                                                   |
|-------------|---------------------------------------------------------------------------------------------------------------------------|
| Name        | EquityPremium                                                                                                             |
| Domain      | finance                                                                                                                   |
| Phenomenon  | Myopic loss aversion causes investors to demand an equity risk premium far exceeding consumption-based model predictions. |
| Pipeline    | masim/skills/polish-simulation-pipeline.md                                                                                |
| Target Spec | masim/skills/define-simulation-scenario-skill.md                                                                          |

## §2 Phenomenon Statement

### §2.1 Trigger

U.S. equities have historically returned approximately 6–8% per year more than Treasury bills. Standard consumption-based asset pricing models with reasonable risk aversion coefficients (gamma 1–10) predict an equity premium of less than 0.35%. This enormous gap between observed and theory-predicted premiums constitutes the equity premium puzzle (Mehra & Prescott, 1985).

### §2.2 Mechanism

The behavioral explanation centers on myopic loss aversion (Benartzi & Thaler, 1995). Investors evaluate portfolios too frequently (myopically), and each evaluation period experiences the full pain of short-horizon volatility. Because losses loom larger than gains (loss aversion coefficient lambda approximately 2.25), myopic investors demand an extraordinary premium to hold equities. Longer evaluation horizons reduce perceived volatility and lower the demanded premium, consistent with professional and institutional investor behavior.

### §2.3 Participants

The causal participants are myopic loss-averse investors, long-horizon investors, risk-neutral investors, conservative investors, and noise traders. Myopic loss-averse and conservative investors suppress stock demand by requiring a high premium for market clearing. Long-horizon and risk-neutral investors provide modest but consistent stock demand at lower premium requirements. Noise traders inject volatility that amplifies perceived equity riskiness for loss-averse investors.

### §2.4 Resolution

The equilibrium equity premium emerges from the tension between myopic loss-averse agents and rational/long-horizon agents. Without myopic agents, the market clears at a low premium; with them dominating, the simulated premium matches historical observations of approximately 6% annualized.

## §3 Research Goals

1. Can heterogeneous investor rules generate a simulated equity premium of 4–7% annualized, matching the historical Mehra-Prescott benchmark?
2. Does removing or reducing the loss-aversion coefficient measurably compress the simulated equity premium?
3. How sensitive is the premium to the evaluation window length (Benartzi-Thaler horizon hypothesis)?
4. Do Rule, LLM, RuleLLM, and Rag variants differ measurably in premium level, allocation patterns, and loss probability?
5. Does increasing noise trader volatility indirectly amplify the equity premium by raising perceived risk for myopic investors?

## §4 Theoretical Anchors

### §4.1 Equity Premium Puzzle

| Field                 | Content                                                                                                                                                          |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation         | Mehra, R., & Prescott, E. C. (1985). The equity premium: A puzzle. *Journal of Monetary Economics*, 15(2), 145-161. https://doi.org/10.1016/0304-3932(85)90061-3 |
| Key mechanism         | Standard expected utility with power utility yields equity premium of 0.35%, far below observed 6.18%.                                                           |
| Key equation          | `E[R_equity] - R_f = gamma * sigma^2_c` where gamma must exceed 30 to match data.                                                                                |
| Motivates agent       | risk-neutral-investor (rational benchmark)                                                                                                                       |
| Parameter implication | `excess_return_multiplier` in [200, 1000] scales rational response to excess return signal.                                                                      |

### §4.2 Myopic Loss Aversion

| Field                 | Content                                                                                                                                                                    |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation         | Benartzi, S., & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. *Quarterly Journal of Economics*, 110(1), 73-92. https://doi.org/10.2307/2118511 |
| Key mechanism         | Loss-averse investors evaluating annually demand ~6% premium; longer horizons reduce demanded premium.                                                                     |
| Key equation          | `perceived_risk = vol * (1 + lambda * loss_prob)`; `target_pct = max(0.1, 0.5 - gamma * perceived_risk)`                                                                   |
| Motivates agent       | myopic-loss-averse-investor                                                                                                                                                |
| Parameter implication | `loss_aversion` in [1.5, 3.0], `evaluation_window` in [3, 20] rounds.                                                                                                      |

### §4.3 Prospect Theory and Loss Aversion

| Field                 | Content                                                                                                                                                  |
|-----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation         | Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-291. https://doi.org/10.2307/1914185 |
| Key mechanism         | Value function concave over gains, convex over losses; losses weighted ~2.25x more than equivalent gains.                                                |
| Key equation          | `v(x) = x^alpha for x >= 0; -lambda * (-x)^beta for x < 0` with lambda ~ 2.25                                                                            |
| Motivates agent       | conservative-investor                                                                                                                                    |
| Parameter implication | `target_stock_pct` in [0.15, 0.35] reflects persistent bond preference from loss aversion.                                                               |

### §4.4 Intertemporal Portfolio Choice

| Field                 | Content                                                                                                                                                                        |
|-----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation         | Samuelson, P. A. (1969). Lifetime portfolio selection by dynamic stochastic programming. *Review of Economics and Statistics*, 51(3), 239-246. https://doi.org/10.2307/1926559 |
| Key mechanism         | Under i.i.d. returns and power utility, optimal equity allocation is horizon-independent (benchmark).                                                                          |
| Key equation          | `target_allocation = constant` regardless of investment horizon for i.i.d. returns.                                                                                            |
| Motivates agent       | long-horizon-investor                                                                                                                                                          |
| Parameter implication | `target_stock_pct` in [0.50, 0.80] for long-horizon rational benchmark.                                                                                                        |

### §4.5 Noise Trading and Excess Volatility

| Field                 | Content                                                                                                           |
|-----------------------|-------------------------------------------------------------------------------------------------------------------|
| Full citation         | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 528-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x |
| Key mechanism         | Uninformed noise traders generate excess volatility above fundamental levels, amplifying perceived equity risk.   |
| Key equation          | `stock_qty ~ N(0, noise_std)` — zero-mean random demand.                                                          |
| Motivates agent       | noise-trader                                                                                                      |
| Parameter implication | `noise_std` in [2.0, 12.0] controls excess volatility contribution.                                               |

## §5 Stylized Facts

| #  | Fact                                                                               | Numeric range                           | Acceptance metric                              | Primary source                                            |
|----|------------------------------------------------------------------------------------|-----------------------------------------|------------------------------------------------|-----------------------------------------------------------|
| F1 | U.S. equity premium 1889-1978 averaged ~6.18% annualized                           | 4-8%                                    | `simulated_equity_premium` in [0.04, 0.08]     | Mehra & Prescott (1985) DOI: 10.1016/0304-3932(85)90061-3 |
| F2 | Loss-averse investors with 1-year evaluation are indifferent at historical premium | lambda ~ 2.25, window ~ 12              | `loss_probability_index` in [0.40, 0.55]       | Benartzi & Thaler (1995) DOI: 10.2307/2118511             |
| F3 | Longer evaluation horizons reduce demanded equity premium                          | Positive correlation horizon-allocation | `evaluation_frequency_sensitivity` > 0.5       | Benartzi & Thaler (1995) DOI: 10.2307/2118511             |
| F4 | Institutional investors allocate more to equities than retail                      | 60% vs 30% typical                      | `equity_allocation_deviation` shows separation | Samuelson (1969) DOI: 10.2307/1926559                     |
| F5 | Noise trading creates excess volatility above fundamental                          | Stock vol 15-20% vs bond ~0             | `stock_return_volatility_ratio` > 3            | Black (1986) DOI: 10.1111/j.1540-6261.1986.tb04513.x      |

## §6 Historical / Empirical Anchors

### §6.1 Mehra-Prescott Dataset (1889-1978)

U.S. equity premium averaged 6.18% vs. bond return of 0.80%. Required risk aversion gamma > 30 under standard consumption-based models. Primary source: Mehra & Prescott (1985), DOI: 10.1016/0304-3932(85)90061-3.

### §6.2 Benartzi-Thaler Calibration (1926-1990)

Using CRSP data, Benartzi & Thaler showed that loss-averse investors with lambda = 2.25 and 1-year evaluation horizon are indifferent between stocks and bonds at the historical premium. Primary source: Benartzi & Thaler (1995), DOI: 10.2307/2118511.

### §6.3 Post-War Premium Persistence (1946-2000)

The equity premium has persisted at 5-8% across multiple sub-periods and international markets, suggesting it is not a statistical artifact of the pre-war sample. Primary source: Mehra (2003), DOI: 10.3386/w9525.

## §7 Agent Roster

| Agent                    | Kebab name                  | Theory family | Market role   | Time horizon      | Risk tolerance | Primary signals                          |
|--------------------------|-----------------------------|---------------|---------------|-------------------|----------------|------------------------------------------|
| MyopicLossAverseInvestor | myopic-loss-averse-investor | behavioral    | destabilising | short (5 rounds)  | low            | stock_price, stock_history, stock_return |
| LongHorizonInvestor      | long-horizon-investor       | rational      | stabilising   | long (50+ rounds) | moderate-high  | stock_price                              |
| RiskNeutralInvestor      | risk-neutral-investor       | rational      | stabilising   | medium            | moderate       | stock_return, bond_return                |
| ConservativeInvestor     | conservative-investor       | behavioral    | destabilising | medium            | very low       | stock_price                              |
| NoiseTrader              | noise-trader                | noise         | neutral       | none              | n/a            | stock_price (constraint only)            |

## §8 Environment Specification

### §8.1 Price Formation

Two-asset market: stock (risky) and bond (risk-free). Price evolves as:
```
P(t+1) = P(t) * (1 + mu_stock + 0.001 * NetDemand(t) + epsilon(t))
epsilon(t) ~ N(0, sigma_stock)
```

### §8.2 Information Broadcast

Each round the Market broadcasts:
`{stock_price, prev_stock_price, stock_return, bond_return, round}`

### §8.3 Constraints and Frictions

- No short selling (stock quantity >= 0)
- Cash constraint (cannot spend more than available cash)
- Price floor at 1.0

### §8.4 Round Granularity

Each round represents approximately one trading day. Market broadcasts first, then investors perceive and decide simultaneously.

## §9 Parameter Seeds

| Parameter                | Belongs to                  | Type  | Default   | Empirical range   | Source citation                                      |
|--------------------------|-----------------------------|-------|-----------|-------------------|------------------------------------------------------|
| stock_expected_return    | Market                      | float | 0.000238  | [0.0001, 0.0004]  | ~6% annual / 252 days (Mehra & Prescott 1985)        |
| bond_return              | Market                      | float | 0.0000397 | [0.00002, 0.0001] | ~1% annual / 252 days                                |
| stock_volatility         | Market                      | float | 0.00945   | [0.005, 0.015]    | ~15% annual / sqrt(252)                              |
| initial_stock_price      | Market                      | float | 100.0     | [50, 200]         | Source: normalization                                |
| loss_aversion            | myopic-loss-averse-investor | float | 2.25      | [1.5, 3.0]        | Benartzi & Thaler (1995) DOI: 10.2307/2118511        |
| evaluation_window        | myopic-loss-averse-investor | int   | 5         | [3, 20]           | Benartzi & Thaler (1995) DOI: 10.2307/2118511        |
| risk_aversion            | myopic-loss-averse-investor | float | 2.0       | [1.0, 5.0]        | Standard CRRA range                                  |
| target_stock_pct         | long-horizon-investor       | float | 0.60      | [0.50, 0.80]      | Samuelson (1969) DOI: 10.2307/1926559                |
| target_stock_pct         | conservative-investor       | float | 0.20      | [0.15, 0.35]      | Kahneman & Tversky (1979) DOI: 10.2307/1914185       |
| excess_return_multiplier | risk-neutral-investor       | float | 500       | [200, 1000]       | Calibration to match rational benchmark allocation   |
| noise_std                | noise-trader                | float | 8.0       | [2.0, 12.0]       | Black (1986) DOI: 10.1111/j.1540-6261.1986.tb04513.x |
| initial_cash             | All investors               | float | 10000.0   | [5000, 50000]     | Source: normalization                                |
| initial_stock            | All investors               | float | 0.0       | [0, 100]          | Source: normalization                                |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Notes                                                  |
|---------|--------|--------------------------------------------------------|
| Rule    | Yes    | Deterministic baseline; pure formula-driven allocation |
| LLM     | Yes    | LLM persona per investor type; free-form reasoning     |
| RuleLLM | Yes    | Embedded rules + LLM reasoning within bounds           |
| Rag     | Yes    | RAG-retrieved evidence augments LLM allocation         |

### §10.2 Pass / Fail Criteria

1. Rule variant produces simulated equity premium in [0.04, 0.08] annualized over 200 rounds.
2. MyopicLossAverseInvestor shows persistent under-allocation (EAD > 0.15) relative to neutral benchmark.
3. LongHorizonInvestor maintains higher equity allocation than MyopicLossAverseInvestor across all variants.
4. All four variants complete without uncaught exceptions in both 5-round smoke and full 200-round runs.
