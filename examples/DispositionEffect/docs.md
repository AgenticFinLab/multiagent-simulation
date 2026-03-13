# DispositionEffect Simulation - Prospect Theory Trading

## What is This?

| Item               | Description                                                           |
|--------------------|-----------------------------------------------------------------------|
| **Phenomenon**     | **Disposition Effect** - Sell winners too early, hold losers too long |
| **Model**          | Reference-point tracking with prospect theory valuation               |
| **Key Feature**    | Purchase price acts as psychological anchor (reference point)         |
| **Academic Value** | Tests Kahneman-Tversky Prospect Theory in market setting              |

## Financial Background

| Theory                   | Application                                        | Reference                                      |
|--------------------------|----------------------------------------------------|------------------------------------------------|
| **Prospect Theory**      | Loss aversion λ ≈ 2.25, S-shaped value function    | Kahneman & Tversky (1979). *Econometrica*      |
| **Disposition Effect**   | Sell winners, hold losers                          | Shefrin & Statman (1985). *Journal of Finance* |
| **Reference Dependence** | Utility relative to reference point, not absolute  | Thaler (1980). *Journal of Economic Behavior*  |
| **Mental Accounting**    | Segregate gains/losses in separate mental accounts | Thaler (1985). *Marketing Science*             |
| **PGR/PLR Methodology**  | Empirical measurement of disposition asymmetry     | Odean (1998). *Journal of Finance*             |

## Key Concepts

### Prospect Theory Value Function

```
V(x) =
    x^0.88           if x >= 0  (gains: concave)
    -λ × (-x)^0.88   if x < 0   (losses: convex)

Where λ ≈ 2.25 (loss aversion coefficient)
```

**Implications:**
- **Gains (concave)**: Diminishing sensitivity → sell early to "lock in" gains
- **Losses (convex)**: Risk-seeking → hold losers hoping for recovery
- **Loss Aversion**: Losing $100 hurts 2.25× more than gaining $100 feels good

### Reference Point

```
Reference Point = Purchase Price (average cost basis)

Gain/Loss = (Current Price - Purchase Price) / Purchase Price

Investor evaluates: "Am I up or down from where I bought?"
```

## Why These 5 Investor Types?

| Investor                  | Role                | Behavior                                                 |
|---------------------------|---------------------|----------------------------------------------------------|
| **DispositionInvestor**   | ⭐ Behavioral        | Sells winners, holds losers. Prospect theory driven.     |
| **RationalInvestor**      | Benchmark           | Expected utility maximizer. No disposition bias.         |
| **TaxAwareInvestor**      | Tax-Loss Harvesting | Sells losers for tax benefits. Opposite of disposition!  |
| **IndexHolder**           | Passive             | Buy-and-hold. No trading bias.                           |
| **InstitutionalInvestor** | Professional        | Less prone to disposition (career concerns, discipline). |

## Disposition Effect Mechanism

```
                    +------------------------------------------+
                    |     Disposition Effect Mechanism         |
                    |     (Reference Point + Loss Aversion)    |
                    +------------------------------------------+

  Scenario A: WINNER (Price > Purchase Price)
  ------------------------------------------
  Current Price = $110, Purchase = $100 -> GAIN of $10
                 |
                 v
  Value function (concave for gains):
  V(+10) = 10^0.88 = 7.59 utils
                 |
                 v
  Marginal utility declining -> "I've made enough"
                 |
                 v
         +---------------------------------+
         |   SELL EARLY (realize gains)    |
         |   "Bird in hand" mentality      |
         +---------------------------------+

  Scenario B: LOSER (Price < Purchase Price)
  ------------------------------------------
  Current Price = $90, Purchase = $100 -> LOSS of $10
                 |
                 v
  Value function (convex for losses):
  V(-10) = -2.25 × 10^0.88 = -17.1 utils
                 |
                 v
  Risk-seeking in losses -> "It might come back"
                 |
                 v
         +---------------------------------+
         |   HOLD LOSER (refuse to cut)    |
         |   Hope for recovery             |
         +---------------------------------+
```

## Market Model

```
Price Model with News Shocks:
    P(t+1) = P(t) + lambda × NetDemand + gamma × [F - P(t)] + NewsShock + eps

News Shock:
    - Probability: 15% per period
    - Impact: Uniform(-5, +5)

This creates gain/loss situations for testing disposition effect.
```

| Parameter        | Value | Financial Meaning                     |
|------------------|-------|---------------------------------------|
| Price Impact     | 0.06  | Demand sensitivity                    |
| Mean Reversion   | 0.015 | Speed to fundamental                  |
| Noise Std        | 0.40  | Per-round price noise                 |
| News Probability | 15%   | Chance of random news each period     |
| News Impact      | ±5    | Magnitude of news shock               |
| Initial Position | 30    | Start with shares (creates reference) |

## Investor Strategy Logic

### DispositionInvestor (⭐ Behavioral Bias)

Four decision branches based on `gain_loss = (price - purchase_price) / purchase_price`:

```
Branch 1 (SELL_WINNER):  gain_loss >= 0.05
    -> Concave value function: diminishing marginal utility in gain domain
    -> Sell 40% of current position
    -> Empirical basis: Odean (1998) finds retail investors realize gains at ~3-5%

Branch 2 (SELL_LOSER):   gain_loss <= -0.30
    -> Convex value function: only at extreme loss does expected utility of selling
       exceed expected utility of holding (hoping for recovery)
    -> Sell only 20% (reluctant)
    -> Asymmetry: 0.30 >> 0.05 captures loss aversion λ ≈ 2.25

Branch 3 (BUY):          -0.02 <= gain_loss < 0.05 AND position < max_position
    -> Near reference point: investor perceives asset as "fairly valued"
    -> Willing to restore position modestly (buy_fraction = 0.2 of deficit)
    -> Cash limit: at most 20% of cash per round
    -> Behavioral basis: status quo comfort near purchase price

Branch 4 (HOLD):         otherwise (deep loss domain: -0.30 < gain_loss < -0.02)
    -> Risk-seeking in losses: hold and wait for recovery
```

### RationalInvestor (No Bias - Benchmark)

```python
# Rebalance based on portfolio allocation, ignoring purchase price
target_allocation = 0.5  # 50% equity
if abs(current_alloc - target_allocation) > rebalance_threshold:
    quantity = (target_position - position) * 0.5  # partial rebalance
```

### TaxAwareInvestor (Opposite Pattern)

```python
# Sell losers for tax benefit, hold winners for deferral
if gain_loss <= -0.05:  # Tax-loss harvest
    quantity = -position * 0.5
# Hold winners until gain_loss >= 0.20 (long-term deferral)
```

## Strategy Comparison

| Strategy                | Gain Response      | Loss Response      | Reference? |
|-------------------------|--------------------|--------------------|------------|
| **DispositionInvestor** | ⭐ Sell at 5%       | ⭐ Hold until -30%  | Yes (bias) |
| RationalInvestor        | Rebalance by alloc | Rebalance by alloc | No         |
| TaxAwareInvestor        | Hold (tax defer)   | Sell at -5% (tax)  | Yes (tax)  |
| IndexHolder             | Hold               | Hold               | No         |
| InstitutionalInvestor   | Sell at 25%        | Cut at -15%        | Partial    |

## Disposition Metric: PGR vs PLR (Odean 1998 Methodology)

```
For each round, for each investor:

  IF sell occurred (quantity < 0):
    realized_qty  = shares sold
    remaining_qty = shares still held after sell = position - realized_qty

    IF price > purchase_price (unit_gain > 0):
      realized_gains  += realized_qty  × unit_gain
      paper_gains     += remaining_qty × unit_gain
    ELSE:
      realized_losses += realized_qty  × |unit_gain|
      paper_losses    += remaining_qty × |unit_gain|

  IF hold (quantity = 0):
    paper_gains  += position × unit_gain   (if unit_gain > 0)
    paper_losses += position × |unit_gain| (if unit_gain < 0)

  IF buy (quantity > 0):
    Only update average cost basis (weighted average).
    NOT a sell-opportunity observation.
    Do NOT count paper gains here — would double-count same shares.

PGR = realized_gains  / (realized_gains  + paper_gains)
PLR = realized_losses / (realized_losses + paper_losses)

Disposition Effect confirmed when: PGR > PLR
Disposition Coefficient (DC) = PGR - PLR
  DC > 0.15 -> strong effect
  DC > 0.10 -> moderate effect
  DC > 0.05 -> weak effect
```

**Key design principle — BUY rounds excluded from paper gain/loss:**
Odean's framework measures the asymmetry in *sell decisions*. A buy is not a choice
between realizing and holding — it does not create a "sell opportunity" observation.
Including paper gain on buy rounds would inflate the denominators and systematically
bias PGR and PLR downward, destroying the signal.

## Scoring (validate_disposition_effect)

Defined in `masim/evaluation/finance/validation.py` (line 2472):

```
comparison_score = 1.0 if PGR > PLR else 0.2

dc_score:
  DC > 0.15  ->  1.0
  DC > 0.10  ->  0.7 + (DC - 0.10) × 6
  DC > 0.05  ->  0.4 + (DC - 0.05) × 6
  DC > 0     ->  DC × 8
  DC <= 0    ->  0.0

overall_score = comparison_score × 0.4 + dc_score × 0.6

valid = overall_score > 0.5 AND PGR > PLR
```

Target for a well-functioning simulation: `overall_score > 0.5` (DC > ~0.08 with PGR > PLR).

## Configuration Parameters (DispositionInvestor)

| Parameter            | Value | Theoretical Basis                                                                       |
|----------------------|-------|-----------------------------------------------------------------------------------------|
| `gain_threshold`     | 0.05  | Odean (1998): retail gain realization ~3-5%; concave value function triggers early sell |
| `loss_threshold`     | -0.30 | Odean: strong loss aversion, must reach large loss before selling; convex loss domain   |
| `sell_fraction_gain` | 0.4   | Partial sell preserves position for repeated gain-realization cycles                    |
| `sell_fraction_loss` | 0.2   | Minimal sell at loss; reflects extreme reluctance (loss aversion asymmetry)             |
| `max_position`       | 30.0  | = initial_position; no speculative buildup beyond original stake                        |
| `buy_fraction`       | 0.2   | Modest replenishment near reference point; 20% of deficit per round                     |
| `loss_aversion` λ    | 2.25  | Kahneman-Tversky canonical estimate                                                     |

## Known Issues Fixed

### Issue 1: Trade Loader Loading Zero Trades
**File**: `examples/DispositionEffect/analysis.py`, `load_simulation_data()`  
**Bug**: Checked `if "strategy" in turn_data` on the outer block dict (keys are `turn_r000001_...`), not the inner payload.  
**Fix**: Now iterates `turn_block -> turn_key -> step_results[0] -> decision_payload`, extracting `{round, quantity, bid_price, strategy}` per trade.

### Issue 2: PGR/PLR Double-Counting on BUY Rounds
**File**: `examples/DispositionEffect/analysis.py`, `calculate_pgr_plr()`  
**Bug**: The BUY branch added `position × unit_gain` to paper gains before updating the reference price — inflating the paper gains denominator for the same shares already counted on HOLD rounds.  
**Fix**: BUY branch only updates average cost basis. Paper gain/loss is counted exclusively on SELL and HOLD rounds (Odean 1998 methodology).

### Issue 3: `remaining` Double-Counting Sold Shares
**File**: `examples/DispositionEffect/analysis.py`, `calculate_pgr_plr()`  
**Bug**: `remaining = position - abs(quantity)` included the sold shares in the paper gain count.  
**Fix**: `remaining = max(0, position - realized_qty)` — excludes sold shares correctly.

### Issue 4: Position Depletion to Near-Zero
**File**: `examples/DispositionEffect/players.py`, `configs/DispositionEffect/players.yml`  
**Bug**: `sell_fraction_gain = 0.6` with `gain_threshold = 0.10` depleted position to ~2 shares after 3-4 sell events. Near-zero position produces near-zero PGR/PLR signal.  
**Fix**: `sell_fraction_gain = 0.4`, `gain_threshold = 0.05` (more frequent triggers, less depletion per trigger).

### Issue 5: Unconditional Replenishment Buy (No Behavioral Basis)
**File**: `examples/DispositionEffect/players.py`  
**Bug**: Buy fired every round when `position < max_position` regardless of price level — not grounded in Prospect Theory. `max_position = 60` doubled the initial stake without justification.  
**Fix**: Buy fires only when `-0.02 <= gain_loss < gain_threshold` (near reference point), reflecting status quo comfort. `max_position = initial_position = 30` prevents speculative buildup.

## Topology

```
                         +-------------------+
                         |      market       | <-- News shocks create +/-
                         +---------+---------+
                                   |
     +-----------+-----------------+-----------------+-----------+
     v           v                 v                 v           v
 disposition   rational        tax_aware        index      institutional
 (⭐ biased)   (benchmark)    (opposite!)     (passive)   (disciplined)
```

## Files

| File                                            | Purpose                     |
|-------------------------------------------------|-----------------------------|
| `examples/DispositionEffect/players.py`         | Market + 5 investor classes |
| `examples/DispositionEffect/analysis.py`        | PGR/PLR calculation + plots |
| `examples/DispositionEffect/run_disposition.py` | Entry point                 |
| `configs/DispositionEffect/simulation.yml`      | Main config                 |
| `configs/DispositionEffect/players.yml`         | Player definitions          |
| `configs/DispositionEffect/topology.yml`        | Star topology               |

## Running

```bash
# Run simulation
python examples/DispositionEffect/run_disposition.py -c configs/DispositionEffect/simulation.yml

# Run analysis on recorded data
python examples/DispositionEffect/analysis.py -c configs/DispositionEffect/simulation.yml
```

## Expected Behavior

| Phase     | Observation                                                   |
|-----------|---------------------------------------------------------------|
| News (+)  | DispositionInvestor sells quickly after price rises above +5% |
| News (-)  | DispositionInvestor holds until -30% loss (rarely sells)      |
| Near ref  | DispositionInvestor modestly buys back (-2% to +5% range)     |
| Over time | PGR >> PLR for disposition investor; PGR ≈ PLR for rational   |
| Score     | DC = PGR - PLR > 0.10 (moderate-strong); overall score > 0.5  |

## Real-World Mapping

| Simulation         | Real-World Example                        |
|--------------------|-------------------------------------------|
| Sell winners early | Retail investors locking in profits       |
| Hold losers        | "Diamond hands" on losing stocks          |
| Tax-loss harvest   | Year-end selling for tax benefits         |
| Institutional      | Mutual funds with disciplined rebalancing |

## References

1. Kahneman, D. & Tversky, A. (1979). *Prospect Theory: An Analysis of Decision under Risk*. Econometrica.
2. Shefrin, H. & Statman, M. (1985). *The Disposition to Sell Winners Too Early and Ride Losers Too Long*. Journal of Finance.
3. Odean, T. (1998). *Are Investors Reluctant to Realize Their Losses?*. Journal of Finance.
4. Thaler, R. (1980). *Toward a Positive Theory of Consumer Choice*. Journal of Economic Behavior.
5. Thaler, R. (1985). *Mental Accounting and Consumer Choice*. Marketing Science.
