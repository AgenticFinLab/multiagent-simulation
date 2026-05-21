# EquityPremium — Simulation Design Basis

## §1 Phenomenon

**Equity Premium Puzzle** (Mehra & Prescott, 1985): U.S. equities have historically returned approximately 6–8% per year more than Treasury bills, yet standard consumption-based asset pricing models with reasonable risk aversion coefficients (γ ≈ 1–10) predict an equity premium of less than 0.35%. This enormous gap between the observed premium and theory-predicted premium is the "puzzle."

The puzzle resists resolution within classical rational-agent frameworks. The behavioral explanation centers on **myopic loss aversion** (Benartzi & Thaler, 1995): investors evaluate portfolios too frequently (myopically), and each evaluation period experiences the full pain of short-horizon volatility. Because losses loom larger than gains (loss aversion coefficient λ ≈ 2.25), myopic investors demand an extraordinary premium to hold equities. Longer evaluation horizons — looking at 10–20 year windows — reduce perceived volatility and lower the demanded premium, consistent with professional and institutional investor behavior.

**Core stylized facts**:
- U.S. equity premium 1889–1978: ~6.18% annualized (Mehra & Prescott, 1985)
- Required risk aversion to rationalize premium: γ ≈ 30–40 (implausibly high)
- Behavioral explanation: loss aversion λ ≈ 2.25 + 1-year evaluation period explains premium (Benartzi & Thaler, 1995)
- Institutional investors with longer horizons allocate more to equities; retail investors with shorter horizons hold more bonds

## §2 Theory

### Primary: Equity Premium Puzzle (Mehra & Prescott, 1985)

Standard expected utility maximization with power utility and historical consumption data yields an equity premium of only 0.35%, far below the observed 6.18%. Any risk aversion coefficient sufficient to match the premium implies implausible consumption substitution behavior — this is the formal puzzle statement.

Reference: Mehra, R., & Prescott, E. C. (1985). The equity premium: A puzzle. *Journal of Monetary Economics*, 15(2), 145–161. DOI: https://doi.org/10.1016/0304-3932(85)90061-3

### Myopic Loss Aversion (Benartzi & Thaler, 1995)

The behavioral resolution: investors with loss aversion λ ≈ 2.25 who evaluate portfolios annually demand a large premium because short-horizon equity returns look highly risky. As evaluation frequency decreases (longer horizons), the demanded premium falls toward zero. This provides a quantitative explanation for the puzzle without requiring implausible risk aversion.

Reference: Benartzi, S., & Thaler, R. H. (1995). Myopic loss aversion and the equity premium puzzle. *Quarterly Journal of Economics*, 110(1), 73–92. DOI: https://doi.org/10.2307/2118511

### Prospect Theory and Loss Aversion (Kahneman & Tversky, 1979)

The foundational framework for loss aversion. The value function is concave over gains and convex over losses, with losses weighted approximately 2–2.5× more than equivalent gains. For portfolio evaluation, this asymmetry drives excessive risk aversion over short horizons.

Reference: Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263–291. DOI: https://doi.org/10.2307/1914185

### Intertemporal Portfolio Choice and Horizon Effects (Samuelson, 1969)

Under standard utility theory, investment horizon should not affect portfolio choice for i.i.d. returns. Samuelson (1969) establishes the benchmark: rational investors with power utility have constant equity allocation regardless of horizon. This sets the reference point against which behavioral horizon effects are measured.

Reference: Samuelson, P. A. (1969). Lifetime portfolio selection by dynamic stochastic programming. *Review of Economics and Statistics*, 51(3), 239–246. DOI: https://doi.org/10.2307/1926559

### Noise Trading and Return Volatility (Black, 1986)

Uninformed noise traders generate excess volatility above fundamental levels. In the equity premium context, noise trading contributes to the appearance of high equity risk, further amplifying the perceived need for a large premium among loss-averse investors.

Reference: Black, F. (1986). Noise. *Journal of Finance*, 41(3), 528–543. DOI: https://doi.org/10.1111/j.1540-6261.1986.tb04513.x

## §3 Market Design

### §3.1 Price Formation Model

```
P(t+1) = P(t) × (1 + r_stock(t) + α × NetDemand(t))
r_stock(t) = μ_stock + ε(t),   ε(t) ~ N(0, σ_stock)
```

| Symbol  | Meaning                         | Config Key              |
|---------|---------------------------------|-------------------------|
| P(t)    | Stock price at round t          | `initial_stock_price`   |
| μ_stock | Expected stock return per round | `stock_expected_return` |
| σ_stock | Stock return volatility         | `stock_volatility`      |
| α       | Demand impact coefficient       | hardcoded 0.001         |
| r_bond  | Risk-free bond return           | `bond_return`           |

### §3.2 Broadcast Signal

Each round the Market broadcasts:
```json
{
  "stock_price": <float>,
  "prev_stock_price": <float>,
  "stock_return": <float>,
  "bond_return": <float>,
  "round": <int>
}
```

## §4 Investor Taxonomy

### §4.1 MyopicLossAverseInvestor

#### Summary
Evaluates portfolio over a short rolling window, overweighting recent losses. Frequent negative realizations drive extreme equity risk aversion, demanding high premiums before holding stocks.

#### Theoretical and Empirical Foundation
- **Benartzi & Thaler (1995)**: Myopic loss aversion. Investors who evaluate over 1-year horizons and have λ ≈ 2.25 demand ~6% equity premium. DOI: `https://doi.org/10.2307/2118511`
- **Kahneman & Tversky (1979)**: Prospect theory. Loss aversion coefficient λ ≈ 2–2.5 drives asymmetric evaluation. DOI: `https://doi.org/10.2307/1914185`

#### Design Purpose and Activation Scenarios
- **Activates when**: Rolling window loss probability is high (recent negative returns)
- **Role in phenomenon**: Amplifies equity risk premium; primary driver of the puzzle in simulation
- **Interaction effects**: Reduces net stock demand, driving price below fundamental; counterbalanced by LongHorizonInvestor

#### Behavioral Framework

**Information set**: `stock_price`, `stock_history` (rolling `evaluation_window` entries), `stock_return`

**Mechanism narrative**: Computes recent return volatility and loss probability over a short window. Multiplies volatility by a loss-aversion-weighted factor. Sets target stock allocation inversely proportional to perceived risk. Adjusts toward target gradually (30% of gap per round).

**Mathematical model**:
```
returns = [r_t-1, r_t-2, ..., r_t-evaluation_window]
vol = std(returns)
loss_prob = count(r < 0) / evaluation_window
perceived_risk = vol × (1 + loss_aversion × loss_prob)
target_stock_pct = max(0.1, 0.5 - risk_aversion × perceived_risk)
stock_qty = (target_value - current_value) / price × 0.3
```

**Behavioral properties**: Bounded rationality; myopic evaluation horizon; loss aversion (λ > 1)

#### Decision Process Walkthrough

1. Observe `stock_price` and retrieve `stock_history` for last `evaluation_window` rounds
2. Compute `vol` and `loss_prob` from return series
3. Compute `perceived_risk = vol × (1 + loss_aversion × loss_prob)`
4. Compute `target_stock_pct = max(0.1, 0.5 − risk_aversion × perceived_risk)`
5. Submit stock_qty adjustment (clamped to [−10, +10])

#### Worked Numerical Example

Given: price = 105, evaluation_window = 5, recent returns = [−0.02, −0.01, 0.01, −0.02, 0.00]
- vol = 0.013, loss_prob = 0.6
- loss_aversion = 2.25, risk_aversion = 3
- perceived_risk = 0.013 × (1 + 2.25 × 0.6) = 0.031
- target_stock_pct = max(0.1, 0.5 − 3 × 0.031) = 0.407
- stock_qty = (0.407 × portfolio_value − current_stock_value) / 105 × 0.3 → sell signal

#### Academic References
- Benartzi, S., & Thaler, R. H. (1995). *Myopic loss aversion and the equity premium puzzle*. QJE. DOI: https://doi.org/10.2307/2118511

---

### §4.2 LongHorizonInvestor

#### Summary
Maintains a target stock allocation based on a long-horizon strategy, adjusting slowly toward the target. Long evaluation windows reduce perceived volatility, enabling higher equity allocation.

#### Theoretical and Empirical Foundation
- **Samuelson (1969)**: Intertemporal portfolio choice. Constant equity allocation is optimal for i.i.d. returns and power utility. DOI: `https://doi.org/10.2307/1926559`
- **Benartzi & Thaler (1995)**: Long evaluation horizon reduces perceived risk, lowering demanded premium. DOI: `https://doi.org/10.2307/2118511`

#### Design Purpose and Activation Scenarios
- **Activates when**: Always active; gradually rebalances toward `target_stock_pct`
- **Role in phenomenon**: Provides stabilizing equity demand; counteracts MyopicLossAverseInvestor's sell pressure
- **Interaction effects**: Supports stock price; reduces equity premium in aggregate

#### Behavioral Framework

**Information set**: `stock_price` only (no rolling evaluation)

**Mechanism narrative**: Computes the gap between current and target stock allocation, adjusts by 20% of the gap per round. Insensitive to short-term losses — embodies the long-horizon rational benchmark.

**Mathematical model**:
```
target_value = target_stock_pct × portfolio_value
stock_qty = (target_value - current_stock_value) / price × 0.2
stock_qty clamped to [-15, +15]
```

**Behavioral properties**: Rational target allocation; slow rebalancing; horizon insensitivity

#### Decision Process Walkthrough

1. Observe `stock_price` from market broadcast
2. Compute portfolio_value = cash + stock × price
3. Compute gap between target and current stock value
4. Submit 20% of gap as stock_qty order

#### Worked Numerical Example

Given: price = 102, cash = 10000, stock = 50, target_stock_pct = 0.60
- portfolio_value = 10000 + 50 × 102 = 15100
- target_value = 0.60 × 15100 = 9060
- current_value = 50 × 102 = 5100
- stock_qty = (9060 − 5100) / 102 × 0.2 ≈ 7.8 → buy 7.8 units

#### Academic References
- Samuelson, P. A. (1969). *Lifetime portfolio selection by dynamic stochastic programming*. ReStat. DOI: https://doi.org/10.2307/1926559

---

### §4.3 RiskNeutralInvestor

#### Summary
Trades on the excess return signal between stocks and bonds. Represents the standard expected-utility benchmark that the equity premium puzzle challenges.

#### Theoretical and Empirical Foundation
- **Mehra & Prescott (1985)**: Risk-neutral benchmark where excess return fully explains allocation. DOI: `https://doi.org/10.1016/0304-3932(85)90061-3`
- **Lucas (1978)**: Asset pricing under rational expectations. DOI: `https://doi.org/10.2307/1913837`

#### Design Purpose and Activation Scenarios
- **Activates when**: `excess_return = stock_return - bond_return` ≠ 0
- **Role in phenomenon**: Provides rational benchmark; its modest allocation reveals why the puzzle exists
- **Interaction effects**: Partial counterforce to myopic loss-averse selling

#### Behavioral Framework

**Information set**: `stock_return`, `bond_return`

**Mechanism narrative**: Computes excess return and scales it by a multiplier. Trades proportionally to the signal without loss aversion adjustment.

**Mathematical model**:
```
excess_return = stock_return - bond_return
stock_qty = excess_return × excess_return_multiplier
stock_qty clamped to [-20, +20]
```

**Behavioral properties**: Fully rational; no loss aversion; ignores short-term volatility

#### Decision Process Walkthrough

1. Observe `stock_return` and `bond_return`
2. Compute excess_return
3. Submit stock_qty = excess_return × multiplier

#### Worked Numerical Example

Given: stock_return = 0.008, bond_return = 0.002, multiplier = 500
- excess_return = 0.006
- stock_qty = 0.006 × 500 = 3.0 → buy 3 units

#### Academic References
- Mehra, R., & Prescott, E. C. (1985). *The equity premium: A puzzle*. JME. DOI: https://doi.org/10.1016/0304-3932(85)90061-3

---

### §4.4 ConservativeInvestor

#### Summary
Prefers bond allocation; adjusts toward a low equity target very slowly. Embodies the prospect-theory-driven bond preference that amplifies the equity premium puzzle.

#### Theoretical and Empirical Foundation
- **Kahneman & Tversky (1979)**: Prospect theory; loss aversion drives persistent bond preference. DOI: `https://doi.org/10.2307/1914185`
- **Benartzi & Thaler (1995)**: Conservative investors demand high premium before entering equities. DOI: `https://doi.org/10.2307/2118511`

#### Design Purpose and Activation Scenarios
- **Activates when**: Always active; allocates minimally to stocks
- **Role in phenomenon**: Represents the majority of retail investors who demand the high premium; key source of the puzzle
- **Interaction effects**: Persistent sell/hold pressure on equities; reinforces MyopicLossAverseInvestor's direction

#### Behavioral Framework

**Information set**: `stock_price`

**Mechanism narrative**: Targets a low stock allocation (e.g., 20–30%), adjusts slowly (10% of gap per round). Conservative rebalancing means stock allocation rarely reaches target.

**Mathematical model**:
```
target_value = target_stock_pct × portfolio_value
stock_qty = (target_value - current_stock_value) / price × 0.1
stock_qty clamped to [-5, +5]
```

**Behavioral properties**: Loss aversion; strong status quo bias; slow adjustment

#### Decision Process Walkthrough

1. Observe `stock_price`
2. Compute target vs. current stock value
3. Adjust 10% of gap per round (clamped ±5)

#### Worked Numerical Example

Given: price = 100, cash = 15000, stock = 20, target_stock_pct = 0.25
- portfolio_value = 15000 + 20 × 100 = 17000
- target_value = 0.25 × 17000 = 4250; current_value = 2000
- stock_qty = (4250 − 2000) / 100 × 0.1 = 2.25 → buy 2.25 units

#### Academic References
- Kahneman, D., & Tversky, A. (1979). *Prospect theory*. Econometrica. DOI: https://doi.org/10.2307/1914185

---

### §4.5 NoiseTrader

#### Summary
Trades randomly with Gaussian noise centered at zero. Provides excess volatility and background liquidity without directional information.

#### Theoretical and Empirical Foundation
- **Black (1986)**: Noise traders create excess volatility, masking fundamental information. DOI: `https://doi.org/10.1111/j.1540-6261.1986.tb04513.x`
- **De Long et al. (1990)**: Noise trader risk affects arbitrageur willingness to correct mispricings. DOI: `https://doi.org/10.1086/261703`

#### Design Purpose and Activation Scenarios
- **Activates when**: Every round; `stock_qty ~ N(0, noise_std)`
- **Role in phenomenon**: Adds volatility that amplifies perceived equity risk for loss-averse investors
- **Interaction effects**: Increases short-horizon volatility experienced by MyopicLossAverseInvestor; indirectly amplifies the premium

#### Behavioral Framework

**Information set**: `stock_price` (used only for portfolio constraint)

**Mechanism narrative**: Draws a Gaussian random stock quantity each round. Independent of any fundamental or momentum signal.

**Mathematical model**:
```
stock_qty ~ N(0, noise_std)
stock_qty clamped to [-10, +10]
```

**Behavioral properties**: Zero information; random walk; uncorrelated with fundamentals

#### Decision Process Walkthrough

1. Draw `stock_qty = random.gauss(0, noise_std)`
2. Clamp to [−10, +10]
3. Execute trade if portfolio constraints allow

#### Worked Numerical Example

Given: noise_std = 3
- stock_qty = gauss(0, 3) → e.g., −1.7 → sell 1.7 units

#### Academic References
- Black, F. (1986). *Noise*. Journal of Finance. DOI: https://doi.org/10.1111/j.1540-6261.1986.tb04513.x

---

## §5 Agent Diversity

The five investors produce the equity premium puzzle through divergent allocation strategies:
- **MyopicLossAverseInvestor** and **ConservativeInvestor** suppress stock demand, requiring a high premium for market clearing
- **LongHorizonInvestor** and **RiskNeutralInvestor** provide modest but consistent stock demand at lower premium requirements
- **NoiseTrader** injects volatility that amplifies the perceived riskiness of equities for loss-averse investors

The aggregate demanded premium emerges from the tension between myopic loss-averse agents and rational/long-horizon agents. Without myopic agents, the market clears at a low premium; with them dominating, the simulated premium matches historical observations.

## §6 Parameter Table

| Parameter                  | Investor                 | Type  | Description                                      |
|----------------------------|--------------------------|-------|--------------------------------------------------|
| `loss_aversion`            | MyopicLossAverseInvestor | float | Loss aversion coefficient λ (default ≈ 2.25)     |
| `evaluation_window`        | MyopicLossAverseInvestor | int   | Rolling window for return evaluation (default 5) |
| `risk_aversion`            | MyopicLossAverseInvestor | float | Risk aversion scaling in target allocation       |
| `target_stock_pct`         | LongHorizonInvestor      | float | Target equity allocation (default ≈ 0.60)        |
| `excess_return_multiplier` | RiskNeutralInvestor      | float | Scales excess return to stock quantity           |
| `target_stock_pct`         | ConservativeInvestor     | float | Low equity target (default ≈ 0.25)               |
| `noise_std`                | NoiseTrader              | float | Standard deviation of Gaussian noise trades      |
| `initial_cash`             | All investors            | float | Starting cash balance                            |
| `initial_stock`            | All investors            | int   | Starting stock holdings                          |
| `stock_expected_return`    | Market                   | float | Expected stock return per round                  |
| `bond_return`              | Market                   | float | Risk-free bond return per round                  |
| `stock_volatility`         | Market                   | float | Stock return volatility (σ)                      |
| `initial_stock_price`      | Market                   | float | Starting stock price                             |

## §7 Round Structure

1. **Market perceive**: Collects all investor stock_qty orders from inbounds
2. **Market decide**: Computes `net_stock_demand`; adds random return `r_stock`; sets new price; broadcasts `market_data`
3. **Investor perceive**: Each investor receives `market_data`; updates `stock_history`
4. **Investor decide**: Each investor computes target allocation; submits `stock_qty` order

## §8 Historical Cases

### Mehra-Prescott Dataset (1889–1978)
U.S. equity premium averaged 6.18% vs. bond return of 0.80%, a premium of 5.38 percentage points. Mehra & Prescott showed this required γ > 30 under standard theory. The simulation replicates this aggregate pattern through the heterogeneous investor mix.

### Benartzi-Thaler Calibration (1995)
Using CRSP data 1926–1990, Benartzi & Thaler showed that loss-averse investors with a 1-year evaluation horizon are indifferent between stocks and bonds at the historical premium, providing a behavioral explanation. The simulation's MyopicLossAverseInvestor uses this exact calibration (λ ≈ 2.25, 1-year window).

## §9 Variant Comparison

| Aspect                | Rule                                      | LLM                             | RuleLLM                                    | Rag                                     |
|-----------------------|-------------------------------------------|---------------------------------|--------------------------------------------|-----------------------------------------|
| Decision mechanism    | Threshold formulas (target allocation)    | LLM persona per investor type   | Embedded allocation rules + LLM            | RAG-retrieved evidence + LLM            |
| Equity premium source | Hard-coded loss_aversion × perceived_risk | LLM reasons about risk aversion | Rules set floor; LLM adjusts within bounds | Retrieved literature informs allocation |
| Stochasticity         | Only noise_std randomness                 | Full LLM stochasticity          | Threshold-bounded LLM variance             | RAG retrieval variance                  |
| Realism               | Mechanistic but calibrated                | Nuanced but inconsistent        | Balanced control and flexibility           | Knowledge-grounded                      |
| `stock_qty`           | Deterministic formula output              | LLM allocation decision         | Rule-anchored LLM allocation decision      | RAG-augmented allocation decision       |
| `reasoning`           | Not applicable                            | LLM rationale                   | RuleLLM rationale                          | RAG-grounded rationale                  |
