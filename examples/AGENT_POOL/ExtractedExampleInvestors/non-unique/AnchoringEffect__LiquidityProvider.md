# AnchoringEffect / Liquidity Provider

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AnchoringEffect |
| Agent type | Liquidity Provider |
| Canonical class | `LiquidityProvider` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

LiquidityProvider represents the passive market-maker or algorithmic liquidity provider that quotes around a short-term exponential moving average (EMA), supplying two-sided liquidity without any fundamental view. It buys when price dips below its fair quote minus a half-spread, and sells when price rises above fair quote plus half-spread. This agent smooths price volatility, dampens short-term oscillations, and provides the continuous liquidity that allows other agents' strategies to execute without excessive slippage. In the anchoring lifecycle, LiquidityProvider dampens noise-driven spikes while having no systematic effect on the direction of mispricing.

## Financial Theory / Theoretical Basis

### Rule / `LiquidityProvider`
- Theoretical basis: Glosten & Milgrom (1985); Hendershott et al. (2011).

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `30.0` | Rule |
| custom_state_hot_limit | Rule: `3` | Rule |
| ema_window | Rule: `20` | Rule |
| half_spread | Rule: `0.015` | Rule |
| initial_cash | Rule: `15000.0` | Rule |
| initial_position | Rule: `150.0` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | liquidity_provider | Liquidity Provider | `LiquidityProvider` | 1 | `examples/AnchoringEffect/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.9 LiquidityProvider

#### 4.9.1  Summary

LiquidityProvider represents the passive market-maker or algorithmic liquidity provider that quotes around a short-term exponential moving average (EMA), supplying two-sided liquidity without any fundamental view. It buys when price dips below its fair quote minus a half-spread, and sells when price rises above fair quote plus half-spread. This agent smooths price volatility, dampens short-term oscillations, and provides the continuous liquidity that allows other agents' strategies to execute without excessive slippage. In the anchoring lifecycle, LiquidityProvider dampens noise-driven spikes while having no systematic effect on the direction of mispricing.

#### 4.9.2  Theoretical and Empirical Foundation

**Market Making and Bid-Ask Dynamics**:
- Theory / Study: Bid-Ask Spread and Market Making
- Citation: Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices in a specialist market with heterogeneously informed traders. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3
- Core Insight: Market makers quote bid and ask prices around their expectation of fair value, earning the spread as compensation for adverse selection risk. The spread widens when information asymmetry increases. In this simulation, LiquidityProvider uses an EMA as its fair-value estimate (agnostic to true fundamental) and quotes with a fixed half-spread.
- Mathematical Formulation:
  ```
  ema(t) = alpha_ema x P(t) + (1 - alpha_ema) x ema(t-1),  alpha_ema = 2 / (ema_window + 1)
  fair_quote(t) = 0.5 x (P(t) + ema(t))
  Buy:  P(t) < fair_quote(t) - half_spread x fair_quote(t)
  Sell: P(t) > fair_quote(t) + half_spread x fair_quote(t)
  ```
- Empirical Evidence: Huang & Stoll (1997, *Review of Financial Studies*) estimate effective half-spreads of 0.5-2% for actively traded stocks. Comerton-Forde et al. (2010, *Journal of Financial Economics*) document that algorithmic market makers reduce intraday volatility by 15-25% through liquidity provision.
- Relevance to This Investor: LiquidityProvider with `half_spread = 0.015` (1.5%) provides realistic two-sided quoting that dampens NoiseTrader-driven price spikes and smooths the anchoring-driven drift path without directionally biasing the market.

**Volatility Dampening and Price Stabilization**:
- Theory / Study: Algorithmic Market Making and Volatility
- Citation: Hendershott, T., Jones, C. M., & Menkveld, A. J. (2011). Does algorithmic trading improve liquiditytheta *Journal of Finance*, 66(1), 1-33. https://doi.org/10.1111/j.1540-6261.2010.01624.x
- Core Insight: Algorithmic liquidity providers narrow spreads and reduce short-term volatility by providing continuous two-sided liquidity. They do not speculate on direction -- they profit from the spread between buy and sell executions.
- Relevance to This Investor: LiquidityProvider absorbs NoiseTrader shocks and MomentumTrader-driven spikes, reducing rolling volatility without altering the fundamental correction process.

#### 4.9.3  Design Purpose and Activation Scenarios

Purpose: Provide realistic two-sided liquidity that smooths the price path; model the institutional/algorithmic market-making layer that exists in all modern equity markets; prevent NoiseTrader large orders from creating unrealistically large price dislocations.

Activation Scenarios:
- Price below fair_quote - 1.5% spread: Buys (provides bid-side liquidity).
- Price above fair_quote + 1.5% spread: Sells (provides ask-side liquidity).
- Within ±1.5% spread of fair_quote: Holds (no profit opportunity within spread).

Market Contribution: **Neutral/stabilizing** -- reduces price volatility; does not systematically correct toward F (agnostic to fundamental); absorbs demand shocks.

Interaction with other agents: Absorbs NoiseTrader random orders (dampens their price impact); partially offsets MomentumTrader trend-following (provides counter-side liquidity); does not interact with anchoring mechanism directly (no fundamental view).

#### 4.9.4  Behavioral Framework

**4.9.4.1  Decision Information Set**

| Signal  | Type             | Rationale                                                   |
|---------|------------------|-------------------------------------------------------------|
| `price` | Continuous       | Current market price; compared to fair_quote                |
| `ema`   | Persistent state | 20-round exponential moving average; basis for fair quoting |

Does NOT use: `fundamental`, `deviation`. LiquidityProvider is fundamentals-agnostic -- it quotes around recent price average, not intrinsic value.

**4.9.4.2  Core Behavioral Mechanism**

1. Maintains `ema` with decay factor `alpha = 2 / (ema_window + 1) = 2/21 ≈ 0.095`.
2. Each round: updates `ema = alpha x price + (1 - alpha) x ema`.
3. Computes `fair_quote = 0.5 x (price + ema)` (midpoint of current and smoothed).
4. Computes `spread_band = half_spread x fair_quote`.
5. If `price < fair_quote - spread_band`: buys (price is below bid threshold).
6. If `price > fair_quote + spread_band`: sells (price is above ask threshold).
7. Otherwise: holds (price within no-trade spread zone).

**4.9.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- EMA evolution:
  ```
  alpha = 2 / (20 + 1) = 0.0952
  ema(t) = alpha x P(t) + (1 - alpha) x ema(t-1)
  ema(0) = initial_price = 105.0
  ```
- Trigger function:
  ```
  fair_quote(t) = 0.5 x (P(t) + ema(t))
  band(t) = half_spread x fair_quote(t) = 0.015 x fair_quote(t)
  Buy:  P(t) < fair_quote(t) - band(t)
  Sell: P(t) > fair_quote(t) + band(t)
  ```
- Sizing function:
  ```
  deviation_from_band = abs(P(t) - fair_quote(t)) / fair_quote(t)
  Q*(t) = min(base_position_size, deviation_from_band x 2000)
  Bounded by cash (buy) or position (sell)
  ```
- Parameter definitions:

| Symbol                    | Meaning                                  | Config Path                     | Source                                                                |
|---------------------------|------------------------------------------|---------------------------------|-----------------------------------------------------------------------|
| ema_window = 20           | EMA lookback window                      | players.yml -> LiquidityProvider | Hendershott et al. (2011): algorithmic MM update window ~20 intervals |
| half_spread = 0.015       | Half-spread as fraction of fair quote    | players.yml -> LiquidityProvider | Huang & Stoll (1997): 0.5-2% effective half-spread for mid-caps       |
| base_position_size = 30.0 | Maximum trade size (high liquidity role) | players.yml -> LiquidityProvider | Larger than other agents; reflects MM capital commitment              |

**4.9.4.4  Behavioral Properties**

- Time horizon: Very short -- responds to current price vs. EMA; no long-term view
- Risk tolerance: Low directional risk -- earns spread, not directional gains; large position capacity
- Information asymmetry: None -- uses only public price data; fundamentals-agnostic
- Psychological profile: No cognitive bias -- pure mechanical market-making; models the algorithmic/institutional liquidity layer

#### 4.9.5  Decision Process Walkthrough

```
Given:  price = 102.0,  ema(prev) = 103.5,  half_spread = 0.015

Step 1: Update EMA
        alpha = 0.0952
        ema = 0.0952 x 102.0 + 0.9048 x 103.5 = 9.71 + 93.65 = 103.36

Step 2: Compute fair quote
        fair_quote = 0.5 x (102.0 + 103.36) = 102.68

Step 3: Compute spread band
        band = 0.015 x 102.68 = 1.54

Step 4: Compare
        lower = 102.68 - 1.54 = 101.14
        upper = 102.68 + 1.54 = 104.22
        price = 102.0 -> within band [101.14, 104.22]; HOLD

Result: Price is within the no-trade spread zone. LiquidityProvider does not trade.
```

#### 4.9.6  Worked Numerical Example

```
Market state:  price = 99.0 (sharp drop from NoiseTrader sell),  ema = 103.2

Calculation:
  ema_new = 0.0952 x 99.0 + 0.9048 x 103.2 = 9.42 + 93.38 = 102.80
  fair_quote = 0.5 x (99.0 + 102.80) = 100.90
  band = 0.015 x 100.90 = 1.51
  lower = 100.90 - 1.51 = 99.39
  price = 99.0 < 99.39 -> buy condition (price below bid threshold)
  deviation = abs(99.0 - 100.90) / 100.90 = 0.0188
  Q* = min(30.0, 0.0188 x 2000) = min(30.0, 37.6) = 30 shares (capped)

Decision: action = buy, quantity = 30, bid_price = 99.0
Rationale: A NoiseTrader sell pushed price below LiquidityProvider's bid threshold.
LP buys 30 shares, absorbing the shock and dampening the drop. This is the
classic liquidity-provision role -- buying into short-term dislocations.
```

#### 4.9.7  Academic References

| # | Citation                                                                                                                                                                                 | Notes                                                                           |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| 1 | Glosten, L. R., & Milgrom, P. R. (1985). Bid, ask and transaction prices. *Journal of Financial Economics*, 14(1), 71-100. https://doi.org/10.1016/0304-405X(85)90044-3                  | Core market-making theory; spread as adverse selection compensation             |
| 2 | Huang, R. D., & Stoll, H. R. (1997). The components of the bid-ask spread. *Review of Financial Studies*, 10(4), 995-1034. https://doi.org/10.1093/rfs/10.4.995                          | Calibrates half_spread = 0.015 from empirical spread decomposition              |
| 3 | Hendershott, T., Jones, C. M., & Menkveld, A. J. (2011). Does algorithmic trading improve liquiditytheta *Journal of Finance*, 66(1), 1-33. https://doi.org/10.1111/j.1540-6261.2010.01624.x | Algorithmic MMs reduce volatility 15-25%; motivates LiquidityProvider dampening |

## Source Docstring Excerpts

### Rule / `LiquidityProvider`

```text
Passive market-maker quoting around short-term EMA -- two-sided liquidity.

Implements simulation-bases.md Section 4.9 -- LiquidityProvider.
Theoretical basis: Glosten & Milgrom (1985); Hendershott et al. (2011).

Decision rule:
    ema = alpha * price + (1-alpha) * ema_prev;  alpha = 2/(ema_window+1)
    fair_quote = 0.5 * (price + ema)
    band = half_spread * fair_quote
    if price < fair_quote - band: buy
    if price > fair_quote + band: sell

Parameters (simulation-bases.md Section 6):
    ema_window: 20
    half_spread: 0.015
    base_position_size: 30.0
```
