# SunkCostFallacy — Simulation Design Basis

## §1 Phenomenon Definition

| Item | Description |
|---|---|
| Phenomenon Name | Sunk cost fallacy and escalation of commitment in trading |
| Category | Behavioral bias / commitment escalation |
| Core Mechanism | Investors treat unrecoverable prior investment as relevant to current decisions. Losing positions are held or increased to avoid admitting prior error, while rational and opportunity-cost agents evaluate only forward-looking value. |
| Real-World Origin | Experimental sunk-cost evidence in Arkes and Blumer (1985), escalation of commitment in Staw (1976), and documented averaging-down behavior among individual investors. |
| Research Relevance | The scenario links individual reluctance to abandon prior commitments with market-level underreaction, excess demand in declining assets, and delayed capital reallocation. |

### §1.1 Origin and Source Analysis

#### §1.1.1 Intellectual Lineage

Staw (1976) introduced escalation of commitment as a behavioral pattern in which
decision makers allocate more resources to a failing course of action. The
simulation maps that mechanism to `CommitmentEscalator`, which buys more after
losses instead of reducing exposure.

Arkes and Blumer (1985) provided the canonical experimental account of the sunk
cost fallacy. Their evidence motivates `SunkCostHolder`, which treats the prior
entry cost as psychologically salient and therefore refuses to sell losing
positions.

Thaler (1980) connected sunk costs to mental accounting and positive behavioral
economics. The model preserves that insight by making the current position a
mental account: the biased agents evaluate the trade through prior commitment,
while rational agents evaluate the asset through future value.

The rational benchmark comes from expected-utility and portfolio-choice logic:
past costs are irreversible and should not determine current allocation.
`RationalCutter` and `OpportunityCostTrader` therefore act on valuation and
capital-allocation signals rather than emotional attachment.

#### §1.1.2 Real-World Event Catalogue

| Event Name | Date(s) | Market / Asset | Trigger | Magnitude | Duration | Correspondence to Simulation | Primary Source |
|---|---|---|---|---|---|---|---|
| Concorde project escalation | 1960s-1970s | Aerospace investment | Continued funding despite worsening economics | UK/French public costs exceeded several billion pounds | Multi-year program | `CommitmentEscalator` adds exposure after unfavorable signals | Arkes and Blumer (1985), *Organizational Behavior and Human Decision Processes*, https://doi.org/10.1016/0749-5978(85)90049-4 |
| NBA draft playing-time escalation | 1980-1990s sample | Professional sports labor allocation | Draft rank made prior investment salient | Higher draft picks received more playing time after performance controls | Multi-season player careers | `SunkCostHolder` keeps capital committed because initial investment is salient | Staw and Hoang (1995), *Administrative Science Quarterly*, https://doi.org/10.2307/2393785 |
| Individual investor averaging down | 1991-1996 | US discount brokerage accounts | Retail investors held and bought underperforming positions | Individual investors underperformed benchmarks by several percentage points annually | Multi-year account panel | `CommitmentEscalator` and `SunkCostHolder` reproduce holding and averaging-down pressure | Barber and Odean (2000), *Journal of Finance*, https://doi.org/10.1111/0022-1082.00226 |
| Disposition-related refusal to realize losses | 1987-1993 | US brokerage accounts | Realizing losses was psychologically costly | Investors were more likely to sell winners than losers | Multi-year account panel | `SunkCostHolder` preserves losing positions instead of selling | Odean (1998), *Journal of Finance*, https://doi.org/10.1111/0022-1082.00072 |
| Corporate project continuation after adverse information | 1970s-1990s evidence | Corporate capital budgeting | Prior capital expenditure increased commitment | Escalation persisted after negative feedback in experimental and field settings | Project-review cycles | `CommitmentEscalator` models reinvestment after negative signals | Staw (1976), *Organizational Behavior and Human Performance*, https://doi.org/10.1016/0030-5073(76)90005-2 |

#### §1.1.3 Book and Practitioner Literature

| Title | Author(s) | Year | Publisher | Relevance to This Simulation |
|---|---|---|---|---|
| *Misbehaving* | Thaler | 2015 | W. W. Norton | Explains mental accounting and why sunk costs affect real decisions. |
| *Thinking, Fast and Slow* | Kahneman | 2011 | Farrar, Straus and Giroux | Connects loss aversion and commitment to intuitive decision errors. |

## §2 Theoretical Foundation

### §2.1 Sunk-Cost Fallacy

- **Primary Citation**: Arkes, H. R., and Blumer, C. (1985). "The psychology of sunk cost." *Organizational Behavior and Human Decision Processes*, 35(1), 124-140. https://doi.org/10.1016/0749-5978(85)90049-4
- **Core Mechanism**: A prior unrecoverable cost is treated as a reason to continue an action even when future expected value does not justify it.
- **Model**:
  ```text
  hold losing position when perceived_recovery_value + sunk_cost_salience > exit_value
  ```
- **Simulation Mapping**: `SunkCostHolder` in §4.1 holds losing positions and avoids selling after adverse price movement.

### §2.2 Escalation Of Commitment

- **Primary Citation**: Staw, B. M. (1976). "Knee-deep in the big muddy: A study of escalating commitment to a chosen course of action." *Organizational Behavior and Human Performance*, 16(1), 27-44. https://doi.org/10.1016/0030-5073(76)90005-2
- **Core Mechanism**: Decision makers invest additional resources to justify prior choices, especially when personal responsibility or reputational commitment is high.
- **Model**:
  ```text
  buy_more iff deviation < -theta_escalation
  Q(t) = escalation_size * |deviation| / theta_escalation
  ```
- **Simulation Mapping**: `CommitmentEscalator` in §4.2 buys after losses to average down.

### §2.3 Mental Accounting

- **Primary Citation**: Thaler, R. H. (1980). "Toward a positive theory of consumer choice." *Journal of Economic Behavior and Organization*, 1(1), 39-60. https://doi.org/10.1016/0167-2681(80)90051-7
- **Core Mechanism**: Investors evaluate a position inside a separate mental account, making the entry price and realized loss psychologically important.
- **Model**:
  ```text
  account_utility = current_value - purchase_price - psychological_realization_cost
  ```
- **Simulation Mapping**: Biased agents compare the current price path to prior commitment rather than only to forward-looking opportunity cost.

### §2.4 Forward-Looking Portfolio Choice

- **Primary Citation**: Markowitz, H. (1952). "Portfolio selection." *Journal of Finance*, 7(1), 77-91. https://doi.org/10.1111/j.1540-6261.1952.tb01525.x
- **Core Mechanism**: Rational allocation depends on future risk and return, not irreversible past costs.
- **Model**:
  ```text
  trade iff |deviation| > theta_forward
  Q(t) = position_size * |deviation| / theta_forward
  ```
- **Simulation Mapping**: `RationalCutter` in §4.3 trades on valuation and ignores sunk-cost attachment.

### §2.5 Opportunity Cost And Noise Trading

- **Primary Citations**: Buchanan, J. M. (1969). *Cost and Choice*; Black, F. (1986). "Noise." *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x
- **Core Mechanism**: Opportunity-cost agents compare the current holding with the best alternative, while noise traders add non-informational flow.
- **Model**:
  ```text
  reallocate iff |deviation| > theta_realloc
  noise_action ~ Bernoulli(trade_probability)
  ```
- **Simulation Mapping**: `OpportunityCostTrader` and `NoiseTrader` provide the rational-opportunity and stochastic baselines.

## §3 Market Design Principles

### §3.1 Price Formation Model

```text
P(t+1) = max(0.01, P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t))
```

| Symbol | Python Variable | Meaning | Config Path | Value |
|---|---|---|---|---|
| P(t) | `price` | Current market price | `extras.initial_price` | 100.0 |
| F | `fundamental` | Constant fundamental value | `extras.fundamental_value` | 100.0 |
| D(t) | `net_demand` | Buy quantity minus sell quantity | computed from orders | round-specific |
| lambda | `price_impact` | Demand impact coefficient | `extras.price_impact` | 0.02 |
| gamma | `mean_reversion` | Fundamental pull | `extras.mean_reversion` | 0.015 |
| epsilon(t) | `noise` | Gaussian market noise | `extras.noise_std` | 0.01 |

### §3.2 Additional Mechanisms

| Mechanism | Trigger | Action | Economic Rationale |
|---|---|---|---|
| Affordability cap | Buy order exceeds cash | Quantity capped by `cash / price` | Prevents impossible leveraged buying. |
| Inventory cap | Sell order exceeds holdings | Quantity capped by current position | Prevents unintended short selling. |
| Commitment band | Loss is below threshold | Biased agent holds | Represents sunk-cost salience and realization avoidance. |

## §4 Investor Archetypes

### §4.1 SunkCostHolder

#### §4.1.1 Summary

This investor represents traders who keep a losing position because exiting
would make the prior mistake explicit.

Its simulation role is to create sticky supply: it withholds sell pressure after
losses and can continue buying when prior commitment appears vindicated.

#### §4.1.2 Theoretical and Empirical Foundation

Arkes and Blumer (1985) establish the sunk-cost fallacy experimentally. Odean
(1998) documents reluctance to realize losses in brokerage accounts.

#### §4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `deviation < 0` | Hold | Refuses to realize loss | §2.1 |
| `deviation > hold_threshold` | Buy modestly | Prior commitment is reinforced | §2.3 |
| Small deviation | Hold | No active reallocation | §2.1 |

#### §4.1.4 Behavioral Framework

The agent observes price, fundamental, and deviation. It does not sell losing
positions. It may buy when positive performance makes prior commitment feel
validated.

#### §4.1.5 Decision Process Walkthrough

At price 90 and fundamental 100, the agent holds rather than selling. At price
112 and `hold_threshold=0.10`, it may buy a small amount.

#### §4.1.6 Worked Numerical Example

```text
P=112, F=100, deviation=0.12, hold_threshold=0.10
Q = base_size * deviation / hold_threshold = 200 * 1.2 = 240 shares
```

#### §4.1.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Arkes and Blumer (1985), https://doi.org/10.1016/0749-5978(85)90049-4 | Sunk-cost mechanism. |
| 2 | Odean (1998), https://doi.org/10.1111/0022-1082.00072 | Refusal to realize losses. |

### §4.2 CommitmentEscalator

#### §4.2.1 Summary

This investor represents decision makers who add resources to a failing
position to justify prior choices.

It is the primary destabilizing biased buyer in declining markets because it
adds demand exactly when the position is losing.

#### §4.2.2 Theoretical and Empirical Foundation

Staw (1976) shows escalation after negative feedback. Staw and Hoang (1995)
document resource allocation affected by prior investment salience.

#### §4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `deviation < -escalation_threshold` | Buy to average down | Adds demand after losses | §2.2 |
| `deviation > escalation_threshold` | Buy smaller amount | Reinforces prior commitment | §2.2 |
| Small deviation | Hold | No escalation | §2.2 |

#### §4.2.4 Behavioral Framework

The agent uses `escalation_threshold` and `escalation_size`. Negative deviation
activates larger buying than positive deviation because losses intensify the
need to justify prior commitment.

#### §4.2.5 Decision Process Walkthrough

At a 10% loss and a 5% threshold, it buys to average down. At a 3% move it
holds because commitment pressure is not large enough.

#### §4.2.6 Worked Numerical Example

```text
P=90, F=100, deviation=-0.10, threshold=0.05
Q = escalation_size * |deviation| / threshold = 400 * 2 = 800 shares
```

#### §4.2.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Staw (1976), https://doi.org/10.1016/0030-5073(76)90005-2 | Escalation after negative feedback. |
| 2 | Staw and Hoang (1995), https://doi.org/10.2307/2393785 | Prior-investment effects in allocation. |

### §4.3 RationalCutter

#### §4.3.1 Summary

This investor represents forward-looking agents who ignore past costs and act
on valuation.

It provides the benchmark that separates economically justified trades from
commitment-driven trades.

#### §4.3.2 Theoretical and Empirical Foundation

Portfolio-choice theory implies that irreversible costs are irrelevant to
current allocation. Expected future value, not psychological commitment,
determines trade direction.

#### §4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `deviation < -cut_threshold` | Buy | Treats undervaluation as opportunity | §2.4 |
| `deviation > cut_threshold` | Sell | Reduces overvalued exposure | §2.4 |
| Small deviation | Hold | Avoids noise churn | §2.4 |

#### §4.3.4 Behavioral Framework

The agent uses `cut_threshold` and `position_size`. It is not emotionally
attached to prior entry price.

#### §4.3.5 Decision Process Walkthrough

At price 94 and fundamental 100, the agent buys because the asset is
undervalued, regardless of whether the current position is losing relative to
entry.

#### §4.3.6 Worked Numerical Example

```text
P=94, F=100, deviation=-0.06, cut_threshold=0.05
Q = position_size * |deviation| / cut_threshold = 350 * 1.2 = 420 shares
```

#### §4.3.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Markowitz (1952), https://doi.org/10.1111/j.1540-6261.1952.tb01525.x | Forward-looking allocation benchmark. |
| 2 | Thaler (1980), https://doi.org/10.1016/0167-2681(80)90051-7 | Contrast with mental accounting. |

### §4.4 OpportunityCostTrader

#### §4.4.1 Summary

This investor compares current exposure with the best available use of capital.

Its role is to counter sunk-cost attachment through explicit opportunity-cost
reasoning.

#### §4.4.2 Theoretical and Empirical Foundation

Buchanan (1969) formalizes opportunity cost as the value of the best foregone
alternative. Portfolio theory applies this principle to capital allocation.

#### §4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| `deviation < -realloc_threshold` | Buy | Reallocate into undervalued capital use | §2.5 |
| `deviation > realloc_threshold` | Sell | Reallocate away from overvalued exposure | §2.5 |
| Small deviation | Hold | Opportunity cost is not large enough | §2.5 |

#### §4.4.4 Behavioral Framework

The agent uses `realloc_threshold` and `position_size`. It is more selective
than `RationalCutter` because it waits for a larger opportunity-cost signal.

#### §4.4.5 Decision Process Walkthrough

At an 8% threshold, a 6% deviation is ignored, but a 10% deviation triggers
capital reallocation.

#### §4.4.6 Worked Numerical Example

```text
P=110, F=100, deviation=0.10, realloc_threshold=0.08
Q = 300 * 0.10 / 0.08 = 375 shares sold, capped by inventory
```

#### §4.4.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Buchanan (1969), *Cost and Choice* | Opportunity-cost principle. |
| 2 | Markowitz (1952), https://doi.org/10.1111/j.1540-6261.1952.tb01525.x | Capital-allocation benchmark. |

### §4.5 NoiseTrader

#### §4.5.1 Summary

This investor represents uninformed liquidity and idiosyncratic retail flow.

It adds background volume without systematically encoding the sunk-cost
mechanism.

#### §4.5.2 Theoretical and Empirical Foundation

Black (1986) defines noise trading as non-informational order flow that remains
essential to market functioning.

#### §4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Relevant Theory |
|---|---|---|---|
| Random draw below `trade_probability` | Random buy or sell | Baseline liquidity | §2.5 |
| Otherwise | Hold | No informational action | §2.5 |

#### §4.5.4 Behavioral Framework

The agent uses `trade_probability` and `noise_size`. Direction is random and
quantity is bounded by cash or inventory.

#### §4.5.5 Decision Process Walkthrough

If the random draw activates, the order direction is sampled and quantity is
drawn from `1..noise_size`.

#### §4.5.6 Worked Numerical Example

```text
trade_probability=0.30, noise_size=100
draw=0.12 -> active; quantity=64; direction=random
```

#### §4.5.7 Academic References

| # | Citation | Contribution |
|---|---|---|
| 1 | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x | Noise-trader baseline. |

## §5 Agent Diversity Verification

| Role | Agents | Diversity Contribution |
|---|---|---|
| Sunk-cost inertia | `SunkCostHolder` | Holds losers and suppresses sell pressure. |
| Escalation | `CommitmentEscalator` | Buys after losses and amplifies commitment. |
| Forward-looking valuation | `RationalCutter` | Trades on future value, not prior cost. |
| Opportunity-cost discipline | `OpportunityCostTrader` | Reallocates when alternative use is sufficiently better. |
| Noise flow | `NoiseTrader` | Adds non-informational liquidity. |

## §6 Parameter Table

| Parameter | Meaning | Used By | Value | Source / Rationale | Sensitivity |
|---|---|---|---:|---|---|
| `initial_price` | Starting market price | Market | 100.0 | Normalized entry/cost base | Medium |
| `fundamental_value` | Forward-looking value anchor | Market | 100.0 | Normalized fundamental | High |
| `price_impact` | Demand impact coefficient | Market | 0.02 | Allows visible but bounded order impact | High |
| `mean_reversion` | Pull toward fundamental | Market | 0.015 | Slow correction preserves behavioral persistence | High |
| `noise_std` | Market shock standard deviation | Market | 0.01 | Low background volatility | Low |
| `hold_threshold` | Positive reinforcement threshold | SunkCostHolder | 0.10 | Sunk-cost holder avoids selling losers | High |
| `base_size` | Sunk-cost holder sizing base | SunkCostHolder | 200 | Small reinforcement order size | Medium |
| `escalation_threshold` | Loss threshold for doubling down | CommitmentEscalator | 0.05 | Escalation activates quickly after losses | High |
| `escalation_size` | Escalation sizing base | CommitmentEscalator | 400 | Larger than passive holder to represent doubling down | High |
| `cut_threshold` | Forward-looking valuation threshold | RationalCutter | 0.05 | Rational trade threshold | Medium |
| `realloc_threshold` | Opportunity-cost threshold | OpportunityCostTrader | 0.08 | More selective than rational cutter | Medium |
| `position_size` | Rational/opportunity sizing base | RationalCutter, OpportunityCostTrader | 300-350 | Bounded strategic trade size | Medium |
| `trade_probability` | Noise activation probability | NoiseTrader | 0.30 | Background liquidity rate | Low |
| `noise_size` | Maximum noise order | NoiseTrader | 100 | Keeps noise below strategic order flow | Low |

## §7 Communication And Round Structure

1. The market aggregates prior orders and broadcasts `price`, `fundamental`,
   `deviation`, and `round`.
2. Investors update cash, position, and current market state.
3. Rule agents compute config-driven orders; API agents request canonical
   `<decision>` JSON.
4. Orders return to the market with `action`, `bid_price`, `quantity`,
   `agent_type`, and `reasoning`.
5. The market updates price through demand impact, mean reversion, and noise.

## §8 Historical Case Studies

### §8.1 Concorde Escalation

The Concorde project is a canonical sunk-cost example because public investment
continued after poor commercial prospects became visible. It maps to
`CommitmentEscalator` and the escalation-size parameter.

### §8.2 Retail Averaging Down

Retail investors often add to losing positions to lower average cost. This maps
directly to `CommitmentEscalator` buying after negative deviation.

### §8.3 Brokerage Loss Realization

Odean (1998) documents that investors realized gains more readily than losses.
This maps to `SunkCostHolder` withholding sell orders after losses.

## §9 Variant Comparison Preview

| Variant | Decision Mechanism | Research Use |
|---|---|---|
| Rule | Config-driven deterministic sunk-cost and opportunity-cost rules | Establishes baseline mechanism. |
| LLM | Persona-only language reasoning with canonical order JSON | Tests whether language agents rationalize sunk-cost holding. |
| RuleLLM | Persona plus explicit rule guidance | Tests whether rule text constrains LLM escalation and cutting. |
| Rag | RuleLLM-style persona plus retrieved behavioral evidence | Tests whether domain knowledge changes escalation or loss-cutting behavior. |
