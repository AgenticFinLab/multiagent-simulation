# EquityPremium / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EquityPremium |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

**Information set**: `stock_price` (used only for portfolio constraint)

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Theory: simulation-bases.md Section 4.5 -- NoiseTrader
- Theoretical basis: Black (1986) noise trading; uninformed random rebalancing

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_stock | Rule: `0.0` | Rule |
| noise_std | Rule: `8.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noise_trader | Noise Trader | `NoiseTrader` | 2 | `examples/EquityPremium/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.5 NoiseTrader

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
2. Clamp to [-10, +10]
3. Execute trade if portfolio constraints allow

#### Worked Numerical Example

Given: noise_std = 3
- stock_qty = gauss(0, 3) -> e.g., -1.7 -> sell 1.7 units

#### Academic References
- Black, F. (1986). *Noise*. Journal of Finance. DOI: https://doi.org/10.1111/j.1540-6261.1986.tb04513.x

---

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Noise trader -- random allocation changes, provides baseline liquidity.

Theory: simulation-bases.md Section 4.5 -- NoiseTrader
Theoretical basis: Black (1986) noise trading; uninformed random rebalancing
creates excess volatility and distorts the observed equity premium.
See simulation-bases.md Section 4.5 for mathematical model.
```
