# DispositionEffect Simulation Bases

## §1 Phenomenon

**Disposition Effect** (Shefrin & Statman, 1985): Investors systematically sell winning positions too early and hold losing positions too long, relative to rational expected-utility maximization. The effect arises from asymmetric treatment of gains and losses anchored to the original purchase price.

**Core stylized facts** (Odean, 1998):
- Proportion of Gains Realized (PGR) ≈ 14.8%
- Proportion of Losses Realized (PLR) ≈ 9.8%
- PGR/PLR ≈ 1.5 (winners sold 60% more frequently than losers)
- Annual performance drag ≈ 3.2%–5.7%

## §2 Theory

### Primary: Prospect Theory (Kahneman & Tversky, 1979)

Investors evaluate outcomes relative to a reference point (purchase price), not in absolute terms. The value function is:
- **Concave for gains** (risk-averse when ahead)
- **Convex for losses** (risk-seeking when behind)
- **Steeper for losses**: loss aversion coefficient λ ≈ 2.25

**v(x)** = xᵅ if x ≥ 0 (α ≈ 0.88); **−λ(−x)ᵝ** if x < 0 (β ≈ 0.88, λ ≈ 2.25)

DOI: https://doi.org/10.2307/1914185

### Disposition Effect (Shefrin & Statman, 1985)

Four psychological mechanisms: (1) loss aversion, (2) mental accounting per position, (3) regret avoidance, (4) self-control failure.

DOI: https://doi.org/10.1111/j.1540-6261.1985.tb05002.x

### Empirical Evidence (Odean, 1998)

PGR/PLR methodology applied to 10,000 individual investor accounts. PGR ≈ 14.8%, PLR ≈ 9.8% across all months except December (tax-loss harvesting reversal).

DOI: https://doi.org/10.1111/0022-1082.00078

### Supporting: Tax-Loss Harvesting

TaxAwareInvestor exhibits anti-disposition behavior through deliberate tax-loss realization. This counter-acts the psychological bias via economic incentive.

Reference: Constantinides (1983) — DOI: https://doi.org/10.1086/261210

### Supporting: Institutional Discipline

Professional managers exhibit weaker disposition effect due to fiduciary duty, performance evaluation, and systematic risk management.

Reference: Shapira & Venezia (2001) — DOI: https://doi.org/10.1016/S0378-4266(00)00100-2

## §3 Market Design

**Price Formation**:
```
P(t+1) = P(t) + λ·NetDemand(t) + γ·[F(t)−P(t)] + ε(t) + N(t)
```
Where:
- λ = price impact coefficient (0.08)
- γ = mean reversion rate (0.05)
- F(t) = fundamental value (100.0)
- ε(t) ~ N(0, σ²) with σ = noise_std
- N(t) = news shock; arrives with probability 0.15, magnitude ~ Uniform(−4, 4)

**News shocks** create price movements that trigger gain/loss states relative to purchase price reference points.

**Reference Point Mechanism**: Each investor tracks `purchase_price` as psychological anchor. Gain/loss is computed as:
```
gain_loss(t) = (P(t) − purchase_price) / purchase_price
```

## §4 Investor Taxonomy

### §4.1 DispositionInvestor

#### §4.1.1 Summary

`DispositionInvestor` is the primary behavioral agent. It treats the original purchase price as a mental-accounting reference point, sells winners quickly, and realizes losers only after a larger drawdown.

#### §4.1.2 Theoretical and Empirical Foundation

The agent implements Prospect Theory's reference dependence and loss aversion (Kahneman & Tversky, 1979), Shefrin and Statman's (1985) disposition-effect mechanism, and Odean's (1998) PGR/PLR empirical benchmark.

#### §4.1.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `gain_loss >= gain_threshold` | sell winner | realizes gains quickly and raises PGR | Prospect Theory gain-domain risk aversion |
| `gain_loss <= loss_threshold` | reluctantly sell loser | realizes fewer losses and lowers PLR | Prospect Theory loss-domain risk seeking |
| `-0.01 <= gain_loss < 0.01` | buy near reference | reinforces anchoring to purchase price | Mental accounting |

#### §4.1.4 Behavioral Framework

```python
gain_loss = (price - purchase_price) / purchase_price
if gain_loss >= gain_threshold:
    quantity = -position * sell_fraction_gain
elif gain_loss <= loss_threshold:
    quantity = -position * sell_fraction_loss
elif -0.01 <= gain_loss < 0.01 and position < max_position:
    quantity = min((max_position - position) * buy_fraction, cash * 0.15 / price)
else:
    quantity = 0
```

#### §4.1.5 Decision Process Walkthrough

At a 3% gain, the investor sells half of the position to lock in gains. At a 7% loss, the investor holds because the loss threshold has not been reached. At a 10% loss, it sells only a small fraction.

#### §4.1.6 Worked Numerical Example

With `position = 30`, `purchase_price = 100`, `price = 103`, and `gain_threshold = 0.03`, `gain_loss = 0.03`; the sell order is `-30 * 0.5 = -15` shares.

#### §4.1.7 Academic References

Kahneman & Tversky (1979); Shefrin & Statman (1985); Odean (1998).

---

### §4.2 RationalInvestor

#### §4.2.1 Summary

`RationalInvestor` is the expected-utility benchmark. It ignores purchase-price anchoring and rebalances toward a target equity allocation.

#### §4.2.2 Theoretical and Empirical Foundation

The agent represents von Neumann-Morgenstern expected utility and standard portfolio rebalancing. It provides the non-behavioral comparison required to measure disposition-effect performance drag.

#### §4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| allocation above target band | sell | trims overweight exposure | Expected utility |
| allocation below target band | buy | restores target exposure | Portfolio rebalancing |
| allocation within band | hold | avoids unnecessary trading | Transaction discipline |

#### §4.2.4 Behavioral Framework

```python
equity_value = position * price
total_value = cash + equity_value
current_alloc = equity_value / total_value
if abs(current_alloc - target_allocation) > rebalance_threshold:
    quantity = (target_position - position) * 0.5
else:
    quantity = 0
```

#### §4.2.5 Decision Process Walkthrough

If the stock position rises above the 50% target by more than 10 percentage points, the investor sells part of the position. If it falls below the lower band, it buys.

#### §4.2.6 Worked Numerical Example

With `cash = 10000`, `position = 30`, and `price = 100`, equity value is 3000 and allocation is 23.1%. The investor buys toward the 50% target.

#### §4.2.7 Academic References

Von Neumann & Morgenstern (1944); Markowitz portfolio-selection tradition.

---

### §4.3 TaxAwareInvestor

#### §4.3.1 Summary

`TaxAwareInvestor` deliberately reverses the disposition effect by realizing losses for tax benefits and deferring gains.

#### §4.3.2 Theoretical and Empirical Foundation

The design follows Constantinides (1983) on optimal tax-loss trading and Odean's observation that loss realization rises in December when tax motives dominate psychology.

#### §4.3.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `gain_loss <= tax_loss_threshold` | sell loser | harvests tax loss and increases PLR | Tax-loss harvesting |
| `gain_loss >= capital_gains_hold` | hold winner | defers capital gains tax | Tax optimization |
| otherwise | hold | no tax trigger | Transaction discipline |

#### §4.3.4 Behavioral Framework

```python
if gain_loss <= tax_loss_threshold:
    quantity = -position * tax_harvest_fraction
elif gain_loss >= capital_gains_hold:
    quantity = 0
else:
    quantity = 0
```

#### §4.3.5 Decision Process Walkthrough

At a 5% loss, the investor sells part of the position to realize a tax loss. At a 15% gain, it avoids selling to defer taxes.

#### §4.3.6 Worked Numerical Example

With `position = 30`, `price = 95`, `purchase_price = 100`, and `tax_harvest_fraction = 0.5`, the tax-aware sell order is `-15` shares.

#### §4.3.7 Academic References

Constantinides (1983); Odean (1998).

---

### §4.4 IndexHolder

#### §4.4.1 Summary

`IndexHolder` is the passive buy-and-hold baseline. It does not actively trade, so it has no realized-gain or realized-loss timing bias.

#### §4.4.2 Theoretical and Empirical Foundation

The design follows Sharpe's passive-investing benchmark logic: a passive holder captures market return without behavioral trading mistakes.

#### §4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| any market state | hold | no active order-flow contribution | Passive benchmark |

#### §4.4.4 Behavioral Framework

```python
quantity = 0
```

#### §4.4.5 Decision Process Walkthrough

The investor receives market prices but never buys or sells. It provides a clean comparison for active behavioral and rational strategies.

#### §4.4.6 Worked Numerical Example

At `price = 110` and `position = 50`, the order remains `quantity = 0`; portfolio value changes only through mark-to-market price movement.

#### §4.4.7 Academic References

Sharpe (1991); passive index-investing benchmark literature.

---

### §4.5 InstitutionalInvestor

#### §4.5.1 Summary

`InstitutionalInvestor` is the professional active manager. It still tracks position outcomes, but uses symmetric sell discipline rather than asymmetric retail loss aversion.

#### §4.5.2 Theoretical and Empirical Foundation

The design follows Shapira and Venezia (2001), who show that professional investors exhibit weaker disposition effects than individual retail investors because of process discipline and oversight.

#### §4.5.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `gain_loss >= gain_threshold` | sell | disciplined profit taking | Professional risk management |
| `gain_loss <= loss_threshold` | sell | symmetric loss cutting | Fiduciary discipline |
| otherwise | hold | no threshold breach | Trading discipline |

#### §4.5.4 Behavioral Framework

```python
if gain_loss >= gain_threshold:
    quantity = -position * sell_fraction
elif gain_loss <= loss_threshold:
    quantity = -position * sell_fraction
else:
    quantity = 0
```

#### §4.5.5 Decision Process Walkthrough

Unlike the retail disposition investor, the institutional investor sells the same fraction after a large gain or a large loss. This weakens PGR/PLR asymmetry.

#### §4.5.6 Worked Numerical Example

With `position = 30`, `sell_fraction = 0.4`, and `gain_loss = 25%`, the sell order is `-12` shares. At `gain_loss = -15%`, the sell order is also `-12` shares.

#### §4.5.7 Academic References

Shapira & Venezia (2001); institutional discipline literature.

---

## §5 Agent Diversity

| Investor              | Theoretical Archetype                             | Bias Direction     | Ref Point Tracking |
|-----------------------|---------------------------------------------------|--------------------|--------------------|
| DispositionInvestor   | Prospect Theory (Kahneman & Tversky, 1979)        | Strong disposition | Yes (asymmetric)   |
| RationalInvestor      | Expected Utility Theory                           | None               | No (fundamental)   |
| TaxAwareInvestor      | Tax-loss harvesting (Constantinides, 1983)        | Anti-disposition   | Yes (tax-aware)    |
| IndexHolder           | Passive (Sharpe, 1991)                            | None               | No                 |
| InstitutionalInvestor | Professional discipline (Shapira & Venezia, 2001) | Weak/symmetric     | Yes (symmetric)    |

## §6 Parameter Table

| Parameter                              | Default | Description                         |
|----------------------------------------|---------|-------------------------------------|
| `initial_price`                        | 100.0   | Starting market price               |
| `fundamental_value`                    | 100.0   | Long-run fundamental                |
| `price_impact`                         | 0.08    | λ in price equation                 |
| `mean_reversion`                       | 0.05    | γ in price equation                 |
| `noise_std`                            | 0.6     | σ for Gaussian noise                |
| `news_probability`                     | 0.15    | Probability of news shock per round |
| `news_impact_range`                    | 4.0     | Max absolute news shock             |
| `gain_threshold` (DispositionInvestor) | 0.03    | Gain sell trigger                   |
| `loss_threshold` (DispositionInvestor) | −0.10   | Loss sell trigger                   |
| `loss_aversion`                        | 2.25    | Kahneman & Tversky λ                |
| `sell_fraction_gain`                   | 0.50    | Fraction sold on gain               |
| `sell_fraction_loss`                   | 0.15    | Fraction sold on loss               |
| `target_allocation`                    | 0.50    | RationalInvestor equity target      |
| `tax_loss_threshold`                   | −0.05   | TaxAwareInvestor harvest trigger    |
| `capital_gains_hold`                   | 0.15    | TaxAwareInvestor hold threshold     |
| `tax_harvest_fraction`                 | 0.50    | Fraction sold for tax benefit       |
| `gain_threshold` (InstitutionalInvestor) | 0.25  | Professional gain-taking trigger    |
| `loss_threshold` (InstitutionalInvestor) | −0.15 | Professional loss-cutting trigger   |
| `sell_fraction` (InstitutionalInvestor) | 0.40   | Fraction sold on threshold breach   |
| `initial_purchase_price`               | 100.0   | Reference point at t=0              |

## §7 Round Structure

1. **Market.perceive()**: Collects all investor orders from previous round.
2. **Market.decide()**: Computes net demand; applies price equation including news shock.
3. **Market.act()**: Broadcasts `{price, prev_price, return, volume, net_demand, news_shock}` to all investors.
4. **Investor.perceive()**: Updates `market_data`; tracks `price_history`.
5. **Investor.decide()**: Computes `gain_loss` relative to `purchase_price`; applies investor-specific logic; returns signed `quantity` plus `bid_price`, `strategy`, and API reasoning fields when present.
6. **Investor.act()**: Executes trade — updates `cash`, `position`, `purchase_price`.

## §8 Historical Cases

### Odean (1998) US Individual Investors

10,000 discount brokerage accounts (1987–1993). PGR = 14.8%, PLR = 9.8%, PGR/PLR = 1.51. December reversal: PLR temporarily > PGR for tax-loss harvesting. Annual return drag ≈ 3.2%.

### Grinblatt & Keloharju (2001) Finland

Helsinki Stock Exchange. Disposition effect confirmed cross-culturally: PGR/PLR ≈ 1.60. Institutional investors showed weaker effect.

### China (Chen et al., 2007)

Shanghai and Shenzhen exchanges. PGR/PLR ≈ 1.67 — stronger disposition effect in retail-dominated markets.

### Barber et al. (2007) Taiwan

Full market data. PGR/PLR ≈ 1.50. Disposition effect contributes to short-term momentum and long-run reversal.

## §9 Variant Comparison

| Aspect             | Rule                           | LLM                                            | RuleLLM                                 | Rag                                      |
|--------------------|--------------------------------|------------------------------------------------|-----------------------------------------|------------------------------------------|
| Reference tracking | Exact mathematical computation | LLM reasons about gain/loss emotionally        | Embedded formula + LLM reasoning        | RAG literature + emotional reasoning     |
| PGR/PLR ratio      | Deterministic from thresholds  | Variable; may be stronger (emotional language) | Close to Rule; LLM may widen thresholds | RAG academic knowledge may moderate bias |
| Loss aversion      | Hard-coded λ = 2.25            | Emergent from "losses hurt" persona            | Rule states λ = 2.25 explicitly         | RAG retrieves prospect theory studies    |
| Consistency        | Guaranteed by threshold logic  | Stochastic; may drift across runs              | High consistency from embedded rules    | Moderate; RAG context varies             |
| Research value     | Mechanism validation baseline  | LLM emotional realism                          | Rule compliance + LLM reasoning         | Literature-grounded bias                 |
