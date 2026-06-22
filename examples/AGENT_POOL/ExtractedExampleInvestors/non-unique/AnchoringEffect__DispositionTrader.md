# AnchoringEffect / Disposition Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AnchoringEffect |
| Agent type | Disposition Trader |
| Canonical class | `DispositionTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

DispositionTrader represents the retail investor who systematically sells winning positions too early and holds losing positions too long. This agent models the Disposition Effect (Shefrin & Statman, 1985) -- a behavioural pattern rooted in Prospect Theory (Kahneman & Tversky, 1979) where the asymmetric value function makes realised gains feel less painful to lock in while realised losses feel disproportionately aversive. In the AnchoringEffect simulation, DispositionTrader introduces asymmetric liquidity: when prices are elevated above its cost basis (a gain scenario), it sells quickly, adding downward pressure that partially offsets anchoring-driven overvaluation. When prices fall below cost basis (a loss scenario), it refuses to sell, removing potential liquidity and allowing mispricings to persist with less corrective flow.

## Financial Theory / Theoretical Basis

### Rule / `DispositionTrader`
- Sells winners too early, holds losers too long -- Prospect Theory asymmetry.
- Theoretical basis: Shefrin & Statman (1985); Kahneman & Tversky (1979).

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `15.0` | Rule |
| custom_state_hot_limit | Rule: `3` | Rule |
| gain_threshold | Rule: `0.04` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `100.0` | Rule |
| loss_aversion_mult | Rule: `2.5` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | disposition_trader | Disposition Trader | `DispositionTrader` | 2 | `examples/AnchoringEffect/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.6 DispositionTrader

#### 4.6.1  Summary

DispositionTrader represents the retail investor who systematically sells winning positions too early and holds losing positions too long. This agent models the Disposition Effect (Shefrin & Statman, 1985) -- a behavioural pattern rooted in Prospect Theory (Kahneman & Tversky, 1979) where the asymmetric value function makes realised gains feel less painful to lock in while realised losses feel disproportionately aversive. In the AnchoringEffect simulation, DispositionTrader introduces asymmetric liquidity: when prices are elevated above its cost basis (a gain scenario), it sells quickly, adding downward pressure that partially offsets anchoring-driven overvaluation. When prices fall below cost basis (a loss scenario), it refuses to sell, removing potential liquidity and allowing mispricings to persist with less corrective flow.

#### 4.6.2  Theoretical and Empirical Foundation

**The Disposition Effect**:
- Theory / Study: Disposition to Sell Winners Too Early and Ride Losers Too Long
- Citation: Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long: Theory and evidence. *Journal of Finance*, 40(3), 777-790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x
- Core Insight: Investors are approximately 1.5-2.5x more likely to sell a position showing a gain than one showing a loss of equal magnitude. This asymmetry is a direct consequence of Prospect Theory's S-shaped value function and reference-point dependence. The reference point is the purchase price (cost basis).
- Mathematical Formulation:
  ```
  gain_pct(t) = (P(t) - cost_basis) / cost_basis
  If gain_pct > gain_threshold (+4%): sell (lock in profit)
  If gain_pct < -gain_threshold / loss_aversion_mult (< -1.6%): buy ("average down" into perceived bargain)
  Else: hold (loss aversion prevents selling losers; no trigger for winners)
  ```
- Empirical Evidence: Odean (1998, *Journal of Finance*) documents that individual investors at a large brokerage realise gains at 1.68x the rate of losses. Weber & Camerer (1998, *Journal of Economic Behavior and Organization*) confirm disposition effects in controlled experiments. The asymmetry ratio 1.5-2.5x calibrates the `loss_aversion_mult = 2.5` parameter.
- Relevance to This Investor: DispositionTrader's cost basis starts near the initial_price (≈105) because it holds position from round 1. As anchoring keeps prices elevated (101-105), the trader remains near breakeven and is inactive. Once prices rise above cost basis by 4%, it sells -- providing temporary downward pressure that partially counteracts anchoring-driven overvaluation.

**Prospect Theory Foundation**:
- Theory / Study: Asymmetric Value Function and Reference-Point Dependence
- Citation: Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185
- Core Insight: The value function is concave for gains (risk averse) and convex for losses (risk seeking), with losses weighted approximately 2.25x more heavily than equivalent gains. This creates the disposition effect: the disutility of realising a $X loss exceeds the utility of realising a $X gain by factor ~2.25.
- Mathematical Formulation: `V(x) = x^alpha if x >= 0; -lambda(-x)^β if x < 0` where alpha ≈ 0.88, β ≈ 0.88, lambda ≈ 2.25 (Tversky & Kahneman 1992).
- Relevance to This Investor: The `loss_aversion_mult = 2.5` parameter approximates lambda = 2.25 from cumulative prospect theory, controlling the asymmetry between gain-triggered selling and loss-triggered inaction.

#### 4.6.3  Design Purpose and Activation Scenarios

Purpose: DispositionTrader introduces realistic asymmetric liquidity provision that interacts with the anchoring lifecycle in a phase-dependent manner. During the overvaluation phase (Phase 2), when prices hover above fundamental but near cost basis, the agent is largely inactive. During rallies above cost basis, it sells -- providing temporary downward pressure. During corrections below cost basis, it holds -- removing potential selling flow and allowing mispricings to persist on the downside.

Activation Scenarios:
- Price above cost basis by > 4% (gain zone): Sells to lock in profit. Adds downward pressure that partially offsets anchoring-driven overvaluation.
- Price below cost basis by > 1.6% (loss_threshold = gain_threshold / loss_aversion_mult): Buys ("averaging down" -- the disposition investor's tendency to reinforce losing positions). Adds upward pressure.
- Price within ±4% / ±1.6% of cost basis: Holds -- the asymmetric inaction zone where neither gain-taking nor loss-aversion-driven buying is triggered.

Market Contribution: **Asymmetrically destabilizing** -- accelerates profit-taking when prices are elevated, but removes liquidity during corrections. The asymmetry interacts with anchoring to create sharper peaks and slower troughs.

Interaction with other agents: Partially offsets AnchoredTrader's upward support (by selling winners above cost basis); reinforces HistoricalAnchor's inertia during declines (both refuse to sell into falling markets, though for different reasons).

#### 4.6.4  Behavioral Framework

**4.6.4.1  Decision Information Set**

| Signal       | Type             | Rationale                                                                                |
|--------------|------------------|------------------------------------------------------------------------------------------|
| `price`      | Continuous       | Current market price; compared to cost_basis reference point                             |
| `cost_basis` | Persistent state | Running weighted-average purchase price; updated on each buy; the Prospect Theory anchor |

Does NOT use: `fundamental`, `deviation`, `prev_price`. DispositionTrader's reference is its own purchase history, not any external fundamental or momentum signal.

**4.6.4.2  Core Behavioral Mechanism**

1. Maintains `cost_basis` = weighted average of all historical purchase prices (initial = initial_price at round 1).
2. Each round: computes `gain_pct = (price - cost_basis) / cost_basis`.
3. If `gain_pct > gain_threshold (+0.04)`: sells -- disposition effect profit-taking.
4. If `gain_pct < -gain_threshold / loss_aversion_mult (-0.016)`: buys -- averaging down into perceived bargain.
5. Otherwise: holds -- the asymmetric inaction zone.
6. On each buy, `cost_basis` updates: `cost_basis = (old_cost_basis x old_position + price x quantity) / (old_position + quantity)`.

**4.6.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger function:
  ```
  gain_pct(t) = (P(t) - cost_basis) / cost_basis
  Sell: gain_pct(t) > gain_threshold = 0.04
  Buy:  gain_pct(t) < -gain_threshold / loss_aversion_mult = -0.016
  Hold: otherwise
  ```
- Sizing function:
  ```
  Q*(t) = min(base_position_size, abs(gain_pct(t)) x 500)
  Bounded by cash (buy) or position (sell)
  ```
- State variables: `cost_basis` -- updated on every buy trade
- Parameter definitions:

| Symbol                    | Meaning                               | Config Path                     | Source                                                               |
|---------------------------|---------------------------------------|---------------------------------|----------------------------------------------------------------------|
| gain_threshold = 0.04     | Minimum gain to trigger profit-taking | players.yml -> DispositionTrader | Odean (1998): median disposition investors realise gains at 4-8%     |
| loss_aversion_mult = 2.5  | Loss aversion asymmetry multiplier    | players.yml -> DispositionTrader | Kahneman & Tversky (1979): lambda ≈ 2.25; rounded to 2.5 for conservatism |
| base_position_size = 15.0 | Maximum trade size                    | players.yml -> DispositionTrader | Smaller than anchoring agents; retail scale                          |

**4.6.4.4  Behavioral Properties**

- Time horizon: Medium -- reference point is static (cost basis); unchanged until next trade
- Risk tolerance: Asymmetric -- risk-averse for gains (quick selling), risk-seeking for losses (holding)
- Information asymmetry: None about fundamentals; unique private reference (cost basis)
- Psychological profile: Prospect Theory (Kahneman & Tversky 1979); Disposition Effect (Shefrin & Statman 1985); Mental Accounting (Thaler 1985)

#### 4.6.5  Decision Process Walkthrough

```
Given:  price = 108.0,  cost_basis = 103.5,  gain_threshold = 0.04,  loss_aversion_mult = 2.5

Step 1: Compute gain percentage
        gain_pct = (108.0 - 103.5) / 103.5 = +0.0435

Step 2: Compare to thresholds
        +0.0435 > +0.04 -> sell condition satisfied (profit-taking)

Step 3: Compute quantity
        Q* = min(15.0, 0.0435 x 500) = min(15.0, 21.7) = 15 shares (capped)

Result: action = sell, quantity = 15, bid_price = 108.0
Rationale: Price 4.35% above cost basis triggers disposition-effect profit-taking.
This selling adds downward pressure during the anchoring overvaluation phase.
```

#### 4.6.6  Worked Numerical Example

```
Market state:  price = 97.0,  cost_basis = 105.0,  position = 100 shares

Calculation:
  gain_pct = (97.0 - 105.0) / 105.0 = -0.0762  (7.6% loss)
  Compare: -0.0762 < -0.016 -> buy condition (averaging down)
  Q* = min(15.0, 0.0762 x 500) = min(15.0, 38.1) = 15 shares (capped)
  Cash check: 15 x 97.0 = $1,455 (sufficient from initial $10,000)

Decision: action = buy, quantity = 15, bid_price = 97.0
Update: cost_basis = (105.0 x 100 + 97.0 x 15) / 115 = 103.96

Rationale: Despite price being 3% below fundamental (100), DispositionTrader buys because it
perceives a loss relative to cost basis and "averages down" -- the classic disposition-effect
behaviour of reinforcing losing positions. This buying adds upward price support at levels
where rational agents would hold or sell.
```

#### 4.6.7  Academic References

| # | Citation                                                                                                                                                                                         | Notes                                                                                     |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| 1 | Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early and ride losers too long. *Journal of Finance*, 40(3), 777-790. https://doi.org/10.1111/j.1540-6261.1985.tb05002.x  | Core theoretical foundation; establishes gain/loss asymmetry in individual investors      |
| 2 | Kahneman, D., & Tversky, A. (1979). Prospect theory. *Econometrica*, 47(2), 263-292. https://doi.org/10.2307/1914185                                                                             | Grounds the disposition effect in value function asymmetry; calibrates lambda ≈ 2.25           |
| 3 | Odean, T. (1998). Are investors reluctant to realize their lossestheta *Journal of Finance*, 53(5), 1775-1798. https://doi.org/10.1111/0022-1082.00072                                               | Empirical confirmation: gains realised 1.68x more frequently than losses; large brokerage |
| 4 | Weber, M., & Camerer, C. F. (1998). The disposition effect in securities trading. *Journal of Economic Behavior and Organization*, 33(2), 167-184. https://doi.org/10.1016/S0167-2681(97)00089-9 | Controlled experiment confirming disposition effect magnitude                             |

---

## Source Docstring Excerpts

### Rule / `DispositionTrader`

```text
Sells winners too early, holds losers too long -- Prospect Theory asymmetry.

Implements simulation-bases.md Section 4.6 -- DispositionTrader.
Theoretical basis: Shefrin & Statman (1985); Kahneman & Tversky (1979).

Decision rule:
    gain_pct = (price - cost_basis) / cost_basis
    if gain_pct > gain_threshold: sell (lock profit)
    if gain_pct < -(gain_threshold / loss_aversion_mult): buy (average down)
    else: hold

Parameters (simulation-bases.md Section 6):
    gain_threshold: 0.04
    loss_aversion_mult: 2.5
    base_position_size: 15.0
```
