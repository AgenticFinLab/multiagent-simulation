# AnchoringEffect / Fundamental Analyst

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AnchoringEffect |
| Agent type | Fundamental Analyst |
| Canonical class | `FundamentalAnalyst` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

FundamentalAnalyst represents the institutional investor who knows the true fundamental value exists but incorporates it only gradually -- modelling the conservatism bias documented by Barberis, Shleifer & Vishny (1998). Unlike RationalUpdater (who uses F directly with no delay), FundamentalAnalyst maintains a `belief` that exponentially smooths toward F at rate lambda_b = 0.05 per round. This means it takes approximately 40-60 rounds for FundamentalAnalyst's belief to converge within 90% of the true fundamental. The result is a gradually strengthening correction force that is weak early in the simulation (when anchoring dominates) but increasingly effective in later rounds -- modelling how institutional research slowly incorporates new information.

## Financial Theory / Theoretical Basis

### Rule / `FundamentalAnalyst`
- Theoretical basis: Barberis, Shleifer & Vishny (1998); Shleifer & Vishny (1997).

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `25.0` | Rule |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `100.0` | Rule |
| learning_rate | Rule: `0.05` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | fundamental_analyst | Fundamental Analyst | `FundamentalAnalyst` | 1 | `examples/AnchoringEffect/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.8 FundamentalAnalyst

#### 4.8.1  Summary

FundamentalAnalyst represents the institutional investor who knows the true fundamental value exists but incorporates it only gradually -- modelling the conservatism bias documented by Barberis, Shleifer & Vishny (1998). Unlike RationalUpdater (who uses F directly with no delay), FundamentalAnalyst maintains a `belief` that exponentially smooths toward F at rate lambda_b = 0.05 per round. This means it takes approximately 40-60 rounds for FundamentalAnalyst's belief to converge within 90% of the true fundamental. The result is a gradually strengthening correction force that is weak early in the simulation (when anchoring dominates) but increasingly effective in later rounds -- modelling how institutional research slowly incorporates new information.

#### 4.8.2  Theoretical and Empirical Foundation

**Conservatism Bias and Slow Belief Updating**:
- Theory / Study: Conservatism and Underreaction in Investor Beliefs
- Citation: Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0
- Core Insight: Investors update beliefs too slowly in response to new information (conservatism), especially when the information is statistical or abstract. This leads to systematic underreaction to earnings surprises and slow price adjustment. The BSV model shows that conservatism causes prices to initially underreact, then drift as information gradually incorporates -- matching the post-earnings announcement drift anomaly.
- Mathematical Formulation:
  ```
  belief(t) = (1 - lambda_b) x belief(t-1) + lambda_b x F
  where lambda_b = 0.05 (learning rate); belief(0) = initial_price = 105.0
  Convergence: belief approaches F exponentially with half-life = -ln(2)/ln(1-lambda_b) ≈ 13.5 rounds
  90% convergence: ≈ 45 rounds (well within 200-round simulation)
  ```
- Empirical Evidence: Bernard & Thomas (1989, *Journal of Accounting and Economics*) document post-earnings announcement drift lasting 60-90 trading days; Barberis, Shleifer & Vishny (1998) attribute this to conservative belief updating with effective lambda_b ≈ 0.03-0.08.
- Relevance to This Investor: FundamentalAnalyst's lambda_b = 0.05 means its belief converges from 105 toward 100 over approximately 45 rounds -- matching the documented speed of institutional information incorporation. Early on, it is nearly as "anchored" as AnchoredTrader; late in the simulation, it is nearly as rational as RationalUpdater.

**Institutional Investor Conservatism**:
- Theory / Study: Limits to Arbitrage and Gradual Information Processing
- Citation: Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x
- Core Insight: Even when institutional investors recognise mispricing, they adjust portfolios gradually due to career concerns, benchmark tracking, and risk limits. This creates "limits to arbitrage" where correct fundamental information is priced in slowly rather than instantaneously.
- Relevance to This Investor: FundamentalAnalyst's gradual belief convergence models these institutional constraints -- even though F is known, the agent cannot instantly move to full fundamental trading.

#### 4.8.3  Design Purpose and Activation Scenarios

Purpose: FundamentalAnalyst fills the gap between AnchoredTrader (permanently biased) and RationalUpdater (instantly rational). It models the realistic middle ground: an investor who is correct eventually but slow to arrive. This creates a richer phase structure -- early rounds are dominated by anchoring, middle rounds see FundamentalAnalyst gradually joining RationalUpdater in correcting, and late rounds show strong convergence pressure.

Activation Scenarios:
- Price above belief by > 2%: Sells -- interprets price as overvalued relative to gradually-learned fair value.
- Price below belief by > 2%: Buys -- interprets price as undervalued relative to belief.
- Within ±2% of belief: Holds.

Market Contribution: **Weakly stabilizing -> increasingly stabilizing** -- correction force strengthens over time as belief converges to F. Creates a natural bridge between the persistence phase and correction phase of the anchoring lifecycle.

Interaction with other agents: In early rounds, may align with AnchoredTrader (both have elevated beliefs); in later rounds, aligns with RationalUpdater (both drive price toward F); provides a gradual transition between bias and rationality that smooths the correction path.

#### 4.8.4  Behavioral Framework

**4.8.4.1  Decision Information Set**

| Signal        | Type             | Rationale                                                                         |
|---------------|------------------|-----------------------------------------------------------------------------------|
| `price`       | Continuous       | Current market price; compared to evolving belief                                 |
| `fundamental` | Continuous       | True F; used for belief update each round                                         |
| `belief`      | Persistent state | Exponentially-smoothed estimate of fair value; starts at initial_price, converges |

**4.8.4.2  Core Behavioral Mechanism**

1. Initialises `belief = initial_price = 105.0` (starts biased, like AnchoredTrader).
2. Each round: updates belief: `belief = (1 - learning_rate) x belief + learning_rate x fundamental`.
3. Computes `dev_from_belief = (price - belief) / belief`.
4. If `dev_from_belief > +0.02`: sells (price above what FA believes is fair).
5. If `dev_from_belief < -0.02`: buys (price below FA's fair value belief).
6. Otherwise: holds.

**4.8.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Belief evolution:
  ```
  belief(t) = 0.95 x belief(t-1) + 0.05 x F
  belief(0) = 105.0; belief(∞) -> 100.0
  Half-life of belief convergence: ln(2)/ln(1/0.95) ≈ 13.5 rounds
  ```
- Trigger function:
  ```
  dev(t) = (P(t) - belief(t)) / belief(t)
  Sell: dev(t) > +0.02
  Buy:  dev(t) < -0.02
  ```
- Sizing function:
  ```
  Q*(t) = min(base_position_size, abs(dev(t)) x 1000)
  Bounded by cash (buy) or position (sell)
  ```
- Parameter definitions:

| Symbol                    | Meaning                                  | Config Path                      | Source                                                                    |
|---------------------------|------------------------------------------|----------------------------------|---------------------------------------------------------------------------|
| learning_rate = 0.05      | Exponential smoothing rate toward F      | players.yml -> FundamentalAnalyst | Barberis et al. (1998): institutional learning over ~45 rounds (≈60 days) |
| base_position_size = 25.0 | Maximum trade size (institutional scale) | players.yml -> FundamentalAnalyst | Slightly larger than retail agents                                        |

**4.8.4.4  Behavioral Properties**

- Time horizon: Long -- belief evolves slowly; full convergence in ~45 rounds
- Risk tolerance: Medium -- 2% threshold; institutional-scale position limits
- Information asymmetry: Has access to F but processes it with conservatism (slow incorporation)
- Psychological profile: Conservatism bias (Barberis et al. 1998); limits to arbitrage (Shleifer & Vishny 1997); institutional inertia

#### 4.8.5  Decision Process Walkthrough

```
Given:  round = 30,  price = 102.0,  fundamental = 100.0
        belief(29) = 102.8 (has partially converged from 105.0)

Step 1: Update belief
        belief(30) = 0.95 x 102.8 + 0.05 x 100.0 = 97.66 + 5.0 = 102.66

Step 2: Compute deviation from belief
        dev = (102.0 - 102.66) / 102.66 = -0.0064

Step 3: Compare to threshold
        |-0.0064| < 0.02 -> below threshold; HOLD

Result: Despite price being 2% above true fundamental, FundamentalAnalyst holds because
        its belief (102.66) is still elevated -- it has not yet fully learned that F = 100.
        By round 60, belief ≈ 100.25, and the same price would trigger selling.
```

#### 4.8.6  Worked Numerical Example

```
Market state:  round = 60,  price = 103.0,  fundamental = 100.0
               belief(59) = 100.75 (nearly converged after 60 rounds)

Calculation:
  belief(60) = 0.95 x 100.75 + 0.05 x 100.0 = 95.71 + 5.0 = 100.71
  dev = (103.0 - 100.71) / 100.71 = +0.0227  (>+0.02 -> sell)
  Q* = min(25.0, 0.0227 x 1000) = min(25.0, 22.7) = 22 shares

Decision: action = sell, quantity = 22, bid_price = 103.0
Rationale: After 60 rounds of exponential smoothing, FundamentalAnalyst's belief has nearly
converged to F = 100. It now detects that price = 103 is 2.3% above its fair value estimate
and sells -- adding correction pressure that was absent in early rounds. This demonstrates
the time-varying stabilization force that distinguishes FA from RationalUpdater.
```

#### 4.8.7  Academic References

| # | Citation                                                                                                                                                                        | Notes                                                                                |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| 1 | Barberis, N., Shleifer, A., & Vishny, R. (1998). A model of investor sentiment. *Journal of Financial Economics*, 49(3), 307-343. https://doi.org/10.1016/S0304-405X(98)00027-0 | Core foundation; conservatism -> slow belief updating -> post-announcement drift       |
| 2 | Bernard, V. L., & Thomas, J. K. (1989). Post-earnings-announcement drift. *Journal of Accounting and Economics*, 11(1), 1-36. https://doi.org/10.1016/0165-4101(89)90013-8      | Empirical: drift lasts 60-90 days; calibrates lambda_b ≈ 0.05                             |
| 3 | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                           | Institutional constraints explaining why convergence is slow despite correct beliefs |

---

## Source Docstring Excerpts

### Rule / `FundamentalAnalyst`

```text
Gradually learns fundamental value via exponential smoothing -- conservatism bias.

Implements simulation-bases.md Section 4.8 -- FundamentalAnalyst.
Theoretical basis: Barberis, Shleifer & Vishny (1998); Shleifer & Vishny (1997).

Decision rule:
    belief(t) = (1 - learning_rate) * belief(t-1) + learning_rate * F
    dev = (price - belief) / belief
    if abs(dev) > 0.02: trade proportionally

Parameters (simulation-bases.md Section 6):
    learning_rate: 0.05
    base_position_size: 25.0
```
