# MentalAccounting — Simulation Design Basis

## §1 Phenomenon Definition

MentalAccounting models investors who evaluate wealth in separate psychological accounts instead of optimizing total portfolio wealth. The simulation isolates account-local gain/loss framing, the house-money effect, sunk-cost holding, and rational whole-portfolio correction in one market with a constant fundamental value.

This matters in financial markets because the same investor can simultaneously take excess risk in one account, refuse to sell a losing position in another account, and ignore offsetting portfolio gains. The resulting order flow can generate unnecessary turnover, sticky losing inventory, and price pressure that differs from a rational portfolio benchmark.

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

Mental accounting originates in behavioral decision theory as an explanation for why people code, evaluate, and close outcomes in separate accounts. Thaler (1985, 1999) connects this framing to consumer and investor behavior: people do not naturally aggregate all gains and losses into one utility calculation.

The house-money effect extends this account framing to risk taking. Thaler and Johnson (1990) show that prior gains can make later risk feel psychologically cheaper, while prior losses can change subsequent risk appetite.

In investment settings, Barberis and Huang (2001) and Shefrin and Statman (1985) connect account-level evaluation to portfolio segmentation, disposition-like selling, and inefficient holding of losing assets. This scenario maps those mechanisms into heterogeneous trading agents.

#### §1.1.2 Real-World Event Catalogue

| Event | Quantitative Magnitude | Agent Correspondence | Calibration Lesson |
|---|---|---|---|
| Retail brokerage disposition evidence | Odean (1998) documents realized gains being sold more readily than realized losses | MentalAccountant, SunkCostHolder | Account-local reference points create asymmetric selling. |
| House-money laboratory evidence | Thaler & Johnson (1990) report higher risk acceptance after prior gains | HouseMoneyTrader | Gains raise risk multiplier; losses lower it. |
| Narrow framing in individual stocks | Barberis & Huang (2001) links individual-stock accounting to return effects | MentalAccountant, RationalPortfolioManager | Compare segmented decisions against whole-portfolio benchmark. |

#### §1.1.3 Book and Practitioner Literature

| Source | Role |
|---|---|
| Thaler, R. H. (2015). *Misbehaving*. | Practitioner-facing account of mental accounting and house money. |
| Kahneman, D. (2011). *Thinking, Fast and Slow*. | Framing and reference-point interpretation. |
| Shefrin, H. (2000). *Beyond Greed and Fear*. | Behavioral finance framing of investor account segregation. |

## §2 Theoretical Foundation

### §2.1 Mental Accounting

**Citation**: Thaler, R. H. (1999). "Mental Accounting Matters." *Journal of Behavioral Decision Making*, 12(3), 183-206. DOI: 10.1002/(SICI)1099-0771(199909)12:3<183::AID-BDM318>3.0.CO;2-F.

**Mechanism**: Investors encode outcomes in separate accounts and evaluate each account relative to its own reference point. In the simulation, MentalAccountant divides the current position by `num_accounts` and reacts to account-local P&L rather than total portfolio value.

**Mathematical Form**: `pnl = (price - entry_price) / entry_price`; `per_account_position = position / num_accounts`.

**Empirical Evidence**: Odean (1998) and Shefrin & Statman (1985) document asymmetric realization behavior consistent with account-level evaluation.

**Relevance**: Defines `MentalAccountant` in `§4.1`.

### §2.2 House-Money Effect

**Citation**: Thaler, R. H., & Johnson, E. J. (1990). "Gambling with the house money and trying to break even." *Management Science*, 36(6), 643-660. DOI: 10.1287/mnsc.36.6.643.

**Mechanism**: Recent gains are mentally coded as surplus, increasing willingness to take risk; losses reduce risk appetite.

**Mathematical Form**: `risk_factor = gain_risk_multiplier if pnl > 0 else loss_risk_multiplier`.

**Empirical Evidence**: Thaler and Johnson show that prior gains change subsequent risky-choice acceptance.

**Relevance**: Defines `HouseMoneyTrader` in `§4.2`.

### §2.3 Whole-Portfolio Rationality and Narrow Framing

**Citation**: Markowitz, H. (1952). "Portfolio Selection." *Journal of Finance*, 7(1), 77-91. DOI: 10.2307/2975974. Barberis, N., & Huang, M. (2001). "Mental Accounting, Loss Aversion, and Individual Stock Returns." *Journal of Finance*, 56(4), 1247-1292. DOI: 10.1111/0022-1082.00367.

**Mechanism**: Rational portfolio management aggregates positions and trades on total risk-return. Narrow framing evaluates individual positions and can create inefficient order flow.

**Mathematical Form**: `qty = min(base_size, abs(deviation) * risk_aversion * quantity_scale)`.

**Empirical Evidence**: Barberis and Huang show that individual-stock accounting can affect prices; Markowitz provides the rational benchmark.

**Relevance**: Defines `RationalPortfolioManager` in `§4.3`.

### §2.4 Sunk-Cost Holding and Noise Trading

**Citation**: Arkes, H. R., & Blumer, C. (1985). "The psychology of sunk cost." *Organizational Behavior and Human Decision Processes*, 35(1), 124-140. DOI: 10.1016/0749-5978(85)90049-4. Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529-543. DOI: 10.1111/j.1540-6261.1986.tb04513.x.

**Mechanism**: Prior investment makes losing positions hard to abandon; noise traders provide background liquidity unrelated to fundamentals.

**Mathematical Form**: SunkCostHolder sells only after large gains; NoiseTrader trades randomly with configured probability and size.

**Empirical Evidence**: Arkes and Blumer document sunk-cost persistence; Black formalizes noise as unavoidable non-informational trading.

**Relevance**: Defines `SunkCostHolder` in `§4.4` and `NoiseTrader` in `§4.5`.

## §3 Market Design

The market uses the shared single-asset price rule:

`P(t+1) = max(0.01, P(t) + lambda * net_demand + gamma * (F - P(t)) + epsilon_t)`

| Parameter | Value | Role |
|---|---:|---|
| `initial_price` | 100.0 | starting price |
| `fundamental_value` | 100.0 | constant rational anchor |
| `price_impact` | 0.02 | order-flow impact |
| `mean_reversion` | 0.01 | weak fundamental pull |
| `noise_std` | 0.012 | small exogenous noise |

The market broadcasts `price`, `fundamental`, `deviation`, `net_demand`, `volume`, and `round`. Investors return canonical orders with `action`, `bid_price`, `quantity`, `reasoning`, `agent_type`, and `strategy`.

## §4 Investor Taxonomy

### §4.1 MentalAccountant

1. **Summary**: Segregates current holdings into separate mental accounts and evaluates each account relative to entry price. This creates local realization behavior that can diverge from total-portfolio optimization.
2. **Theoretical and Empirical Foundation**: Thaler (1999) explains account coding; Odean (1998) and Shefrin & Statman (1985) document account-level realization patterns.
3. **Design Purpose and Activation Scenarios**: Activates when account-level P&L crosses gain or loss thresholds.
4. **Behavioral Framework**: Uses `num_accounts`, `loss_aversion_per_account`, current `position`, and `entry_price`.
5. **Decision Process Walkthrough**: Compute account P&L; sell 70% of one account after gains above 5%; reluctantly sell 20% of one account after loss threshold; otherwise hold.
6. **Worked Numerical Example**: With `position=600`, `num_accounts=3`, and `pnl=+8%`, per-account position is 200 and sell quantity is 140.
7. **Academic References**: Thaler (1985, 1999); Odean (1998); Shefrin & Statman (1985).

### §4.2 HouseMoneyTrader

1. **Summary**: Takes more risk after gains and less after losses. This creates outcome-dependent order size.
2. **Theoretical and Empirical Foundation**: Thaler & Johnson (1990) document increased risk acceptance after prior gains.
3. **Design Purpose and Activation Scenarios**: Activates when price deviation exceeds the configured threshold and risk appetite depends on current P&L.
4. **Behavioral Framework**: Uses `gain_risk_multiplier`, `loss_risk_multiplier`, `base_size`, and `deviation_threshold`.
5. **Decision Process Walkthrough**: Compute P&L; choose risk factor; buy undervaluation or sell overvaluation when deviation is large enough.
6. **Worked Numerical Example**: With `base_size=400`, `pnl>0`, and `gain_risk_multiplier=2.0`, candidate size is 800 before cash/inventory constraints.
7. **Academic References**: Thaler & Johnson (1990); Barberis & Huang (2001).

### §4.3 RationalPortfolioManager

1. **Summary**: Uses whole-portfolio valuation and serves as the rational benchmark. It trades against price-fundamental deviations.
2. **Theoretical and Empirical Foundation**: Markowitz (1952) provides whole-portfolio optimization; Barberis & Huang (2001) motivates contrast with narrow framing.
3. **Design Purpose and Activation Scenarios**: Activates when absolute deviation exceeds the configured rational threshold.
4. **Behavioral Framework**: Uses `risk_aversion`, `base_size`, `quantity_scale`, and `deviation_threshold`.
5. **Decision Process Walkthrough**: Buy undervaluation, sell overvaluation, size by deviation and risk aversion.
6. **Worked Numerical Example**: With `deviation=-4%`, `risk_aversion=0.7`, `quantity_scale=3000`, raw quantity is 84 before caps.
7. **Academic References**: Markowitz (1952); Barberis & Huang (2001).

### §4.4 SunkCostHolder

1. **Summary**: Holds losing positions because past investment remains psychologically salient. It sells only after sufficiently large gains.
2. **Theoretical and Empirical Foundation**: Arkes & Blumer (1985) document sunk-cost persistence.
3. **Design Purpose and Activation Scenarios**: Creates sticky losing inventory and delayed selling.
4. **Behavioral Framework**: Uses `sunk_cost_weight`, entry price, current price, and position.
5. **Decision Process Walkthrough**: Compute P&L; sell a configured fraction only after gains exceed 10%; otherwise hold.
6. **Worked Numerical Example**: With `position=500`, `sunk_cost_weight=0.6`, and `pnl=+12%`, sell quantity is 300.
7. **Academic References**: Arkes & Blumer (1985); Shefrin & Statman (1985).

### §4.5 NoiseTrader

1. **Summary**: Provides random non-informational order flow and background liquidity.
2. **Theoretical and Empirical Foundation**: Black (1986) formalizes noise trading.
3. **Design Purpose and Activation Scenarios**: Adds stochastic trading not tied to mental accounting signals.
4. **Behavioral Framework**: Uses `trade_probability` and `noise_size`.
5. **Decision Process Walkthrough**: With configured probability, choose buy or sell and draw a bounded size.
6. **Worked Numerical Example**: With `trade_probability=0.3` and `noise_size=150`, roughly 30% of rounds generate a 1-150 share random order before constraints.
7. **Academic References**: Black (1986).

## §5 Agent Diversity

The population combines segmented-account bias, outcome-dependent risk appetite, rational portfolio correction, sunk-cost inertia, and noise liquidity. This mix allows the simulation to separate mental-accounting order flow from rational value correction.

## §6 Parameter Table

| Parameter | Value | Used By | Justification |
|---|---:|---|---|
| `num_accounts` | 3 | MentalAccountant | Multiple psychological accounts. |
| `loss_aversion_per_account` | 2.25 | MentalAccountant | Losses receive larger subjective weight. |
| `gain_risk_multiplier` | 2.0 | HouseMoneyTrader | Gains increase risk appetite. |
| `loss_risk_multiplier` | 0.5 | HouseMoneyTrader | Losses reduce risk appetite. |
| `deviation_threshold` | 0.02 | HouseMoneyTrader, RationalPortfolioManager | Minimum actionable mispricing. |
| `risk_aversion` | 0.7 | RationalPortfolioManager | Moderates rational sizing. |
| `quantity_scale` | 3000 | RationalPortfolioManager | Converts deviation to shares. |
| `sunk_cost_weight` | 0.6 | SunkCostHolder | Fraction sold after large gains. |
| `trade_probability` | 0.3 | NoiseTrader | Background activity rate. |
| `noise_size` | 150 | NoiseTrader | Random order cap. |

## §7 Round Structure

Each round: market clears previous orders, updates price, broadcasts state, investors update account-level state, investors decide one order, and the order is routed back to the market for the next round.

## §8 Historical Cases

| Case | Event Profile | Quantitative Evidence | Agent Mapping | Calibration Lesson |
|---|---|---|---|---|
| Retail disposition evidence | Individual investors realize gains more readily than losses | Odean (1998) reports significant sell-winner/hold-loser asymmetry | MentalAccountant, SunkCostHolder | Account reference points drive order flow. |
| House-money experiments | Prior gains change subsequent risk choice | Thaler & Johnson (1990) show gain-conditioned risk seeking | HouseMoneyTrader | Gain/loss multipliers should be asymmetric. |
| Narrow-framing asset pricing | Individual stock accounting affects demand | Barberis & Huang (2001) model individual-stock mental accounts | MentalAccountant, RationalPortfolioManager | Need rational benchmark for comparison. |

## §9 Variant Comparison

| Variant | Decision Mechanism | Expected Effect |
|---|---|---|
| Rule | deterministic account formulas | calibrated baseline |
| LLM | persona-only account reasoning | stochastic mental-accounting expression |
| RuleLLM | persona plus explicit decision rules | closer to Rule with textual reasoning |
| Rag | RuleLLM plus retrieved behavioral-finance context | knowledge may clarify or dampen bias |
