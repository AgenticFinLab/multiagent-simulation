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

**Role**: Primary disposition-effect driver exhibiting Prospect Theory behavior.

**Economic Archetype**: Individual retail investor with loss aversion and mental accounting.

**Theoretical Basis**: Kahneman & Tversky (1979) Prospect Theory; Shefrin & Statman (1985) disposition effect; Odean (1998) PGR/PLR evidence.

**Decision Logic**:
- Sell 50% of position when `gain_loss ≥ gain_threshold (0.03)` — quick profit-taking in gain domain
- Sell 15% of position when `gain_loss ≤ loss_threshold (−0.10)` — reluctant loss realization only at extreme loss
- Buy when `|gain_loss| < 0.01` — add near reference point (perceived "fair value")

**Key Parameters**:
- `gain_threshold = 0.03` (Odean 1998 PGR analysis)
- `loss_threshold = −0.10` (empirical average)
- `loss_aversion = 2.25` (Kahneman & Tversky 1979)
- `sell_fraction_gain = 0.50` (quick profit-taking)
- `sell_fraction_loss = 0.15` (reluctant loss realization)

**Market Impact**: Creates asymmetric price pressure — selling resistance above purchase price, holding support below.

**Performance**: Expected to underperform RationalInvestor by 3–5% annually due to premature winner selling.

---

### §4.2 RationalInvestor

**Role**: Expected-utility baseline — rational fundamental trader without reference point bias.

**Economic Archetype**: Neoclassical expected-utility maximizer; ignores sunk costs.

**Theoretical Basis**: Expected Utility Theory (von Neumann & Morgenstern, 1944); trades on fundamental value, not purchase price.

**Decision Logic**:
- Buy when `current_alloc < target_allocation - rebalance_threshold` (underpowered)
- Sell when `current_alloc > target_allocation + rebalance_threshold` (overpowered)
- Target allocation as portfolio weight; `rebalance_threshold` prevents over-trading

**Key Parameters**:
- `target_allocation = 0.5` (50% equity target weight)
- `rebalance_threshold = 0.10` (10% band before rebalancing)

**Market Impact**: Stabilizing mean-reversion force; buys dips, sells rallies relative to fundamental.

**Performance**: Expected to outperform DispositionInvestor; sets rational benchmark.

---

### §4.3 TaxAwareInvestor

**Role**: Anti-disposition investor who deliberately harvests tax losses.

**Economic Archetype**: Tax-optimizing investor who reverses disposition bias through economic incentive.

**Theoretical Basis**: Constantinides (1983) tax-loss harvesting theory; exhibits opposite behavior to DispositionInvestor — sells losers, holds winners.

**Decision Logic**:
- Sell `tax_harvest_fraction` of position when `gain_loss ≤ tax_loss_threshold` — harvest tax losses
- Hold winners when `gain_loss ≥ capital_gains_hold` — defer capital gains tax

**Key Parameters**:
- `tax_loss_threshold = −0.05` (trigger tax loss harvest)
- `capital_gains_hold = 0.15` (hold winners above this gain)
- `tax_harvest_fraction = 0.30` (sell 30% for tax benefit)

**Market Impact**: Creates December effect — additional selling of losers at year-end.

**Performance**: Expected to outperform DispositionInvestor by eliminating loser-holding bias.

---

### §4.4 IndexHolder

**Role**: Passive buy-and-hold baseline; provides market liquidity without active trading.

**Economic Archetype**: Index fund / passive investor with no active disposition behavior.

**Theoretical Basis**: Sharpe (1991) passive investing; no reference point tracking, no rebalancing.

**Decision Logic**: `quantity = 0` always — pure hold, no buying or selling.

**Key Parameters**: None (fully passive).

**Market Impact**: Liquidity anchor; zero net contribution to order imbalance.

**Performance**: Performance equals market return minus zero transaction costs; benchmark for active strategies.

---

### §4.5 InstitutionalInvestor

**Role**: Professional money manager with symmetric, disciplined gain/loss thresholds.

**Economic Archetype**: Professional portfolio manager with fiduciary duty; exhibits weaker disposition effect than retail investors.

**Theoretical Basis**: Shapira & Venezia (2001) institutional vs. individual disposition; professional training reduces psychological bias through systematic rules.

**Decision Logic**:
- Sell `sell_fraction` of position when `gain_loss ≥ gain_threshold` — disciplined profit taking
- Sell `sell_fraction` of position when `gain_loss ≤ loss_threshold` — symmetric loss cutting (unlike DispositionInvestor)

**Key Parameters**:
- `gain_threshold = 0.08` (wider threshold than retail)
- `loss_threshold = −0.08` (symmetric — no reluctance to realize losses)
- `sell_fraction = 0.30` (same fraction for gains and losses — no asymmetry)

**Market Impact**: Symmetric stabilizing force; reduces market volatility relative to DispositionInvestor population.

**Performance**: Expected to outperform DispositionInvestor; confirms institutional discipline advantage.

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
| `noise_std`                            | 0.5     | σ for Gaussian noise                |
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
| `initial_purchase_price`               | 100.0   | Reference point at t=0              |

## §7 Round Structure

1. **Market.perceive()**: Collects all investor orders from previous round.
2. **Market.decide()**: Computes net demand; applies price equation including news shock.
3. **Market.act()**: Broadcasts `{price, prev_price, return, volume, net_demand, news_shock}` to all investors.
4. **Investor.perceive()**: Updates `market_data`; tracks `price_history`.
5. **Investor.decide()**: Computes `gain_loss` relative to `purchase_price`; applies investor-specific logic; returns `{bid_price, quantity, strategy}`.
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
