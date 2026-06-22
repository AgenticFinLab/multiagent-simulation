# AnchoringEffect / Contrarian Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AnchoringEffect |
| Agent type | Contrarian Trader |
| Canonical class | `ContrarianTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule |

## Definition and Goal

ContrarianTrader represents the disciplined mean-reversion investor who bets against recent trends without reference to fundamental value. Unlike RationalUpdater (who exploits the price-fundamental gap), ContrarianTrader uses purely statistical reasoning: when cumulative 10-round returns exceed ±5%, it trades in the opposite direction expecting mean reversion. This agent models the empirically documented overreaction-correction cycle (De Bondt & Thaler, 1985) and provides a correction mechanism distinct from fundamental arbitrage -- one that would operate even if F were unknown.

## Financial Theory / Theoretical Basis

### Rule / `ContrarianTrader`
- Theoretical basis: De Bondt & Thaler (1985); Jegadeesh (1990).

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `20.0` | Rule |
| custom_state_hot_limit | Rule: `3` | Rule |
| entry_threshold | Rule: `0.05` | Rule |
| initial_cash | Rule: `10000.0` | Rule |
| initial_position | Rule: `100.0` | Rule |
| lookback_window | Rule: `10` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | contrarian_trader | Contrarian Trader | `ContrarianTrader` | 1 | `examples/AnchoringEffect/Rule/players.py` |

## Scenario-Theory Excerpts

### Section 4.7 ContrarianTrader

#### 4.7.1  Summary

ContrarianTrader represents the disciplined mean-reversion investor who bets against recent trends without reference to fundamental value. Unlike RationalUpdater (who exploits the price-fundamental gap), ContrarianTrader uses purely statistical reasoning: when cumulative 10-round returns exceed ±5%, it trades in the opposite direction expecting mean reversion. This agent models the empirically documented overreaction-correction cycle (De Bondt & Thaler, 1985) and provides a correction mechanism distinct from fundamental arbitrage -- one that would operate even if F were unknown.

#### 4.7.2  Theoretical and Empirical Foundation

**Market Overreaction and Contrarian Profits**:
- Theory / Study: Long-Run Stock Market Overreaction
- Citation: De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreacttheta *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x
- Core Insight: Stocks that have performed extremely well ("winners") over 3-5 years subsequently underperform, while extreme "losers" subsequently outperform. This reversal pattern is consistent with investors overreacting to recent information and prices eventually mean-reverting. Contrarian strategies exploit this predictable overreaction.
- Mathematical Formulation:
  ```
  cumulative_return(t) = (P(t) - P(t-lookback)) / P(t-lookback)
  Sell if cumulative_return > +entry_threshold (+5%)
  Buy  if cumulative_return < -entry_threshold (-5%)
  ```
- Empirical Evidence: De Bondt & Thaler (1985) document 25% cumulative excess return to contrarian portfolios over 3 years; Jegadeesh (1990, *Journal of Finance*) confirms short-horizon reversals at 1-month intervals; Bondt (1993) and Chopra, Lakonishok & Ritter (1992) extend to multiple horizons.
- Relevance to This Investor: In the AnchoringEffect simulation, anchoring agents create a slow upward drift followed by correction. ContrarianTrader detects the cumulative upward drift and sells against it, providing an additional correction force beyond RationalUpdater. During the correction phase, it may buy the dip, partially cushioning the decline.

**Short-Horizon Mean Reversion**:
- Theory / Study: Evidence of Predictable Behavior of Security Returns
- Citation: Jegadeesh, N. (1990). Evidence of predictable behavior of security returns. *Journal of Finance*, 45(3), 881-898. https://doi.org/10.1111/j.1540-6261.1990.tb05110.x
- Core Insight: At short horizons (1-4 weeks), stock returns exhibit negative serial correlation -- reversals rather than momentum. This justifies a 10-round contrarian lookback window as the simulation-compressed equivalent of a 2-week reversal horizon.
- Relevance to This Investor: The `lookback_window = 10` parameter maps to Jegadeesh's documented short-horizon reversal window.

#### 4.7.3  Design Purpose and Activation Scenarios

Purpose: Provide a correction mechanism that is distinct from RationalUpdater. ContrarianTrader does not know or use the fundamental value -- it trades on pure price-path statistics. This tests whether price corrections in the simulation require fundamental knowledge or can emerge from statistical mean-reversion beliefs alone.

Activation Scenarios:
- 10-round cumulative return > +5%: Sells (expects reversal from overextension).
- 10-round cumulative return < -5%: Buys (expects bounce from oversold condition).
- Within ±5%: Holds -- insufficient trend to trigger contrarian response.

Market Contribution: **Stabilizing** -- provides correction force distinct from fundamental arbitrage; dampens both upward overextension and downward overshooting.

Interaction with other agents: Opposes MomentumTrader directly (when momentum signal is strong, contrarian signal fires in opposite direction); complements RationalUpdater during correction phase (both sell into overvaluation, but for different reasons); may temporarily oppose RationalUpdater during rapid corrections (ContrarianTrader buys the dip while RationalUpdater holds).

#### 4.7.4  Behavioral Framework

**4.7.4.1  Decision Information Set**

| Signal                           | Type       | Rationale                                               |
|----------------------------------|------------|---------------------------------------------------------|
| `price`                          | Continuous | Current price; end-point of lookback return calculation |
| `price_history` (last 10 rounds) | Series     | Required for cumulative return over lookback window     |

Does NOT use: `fundamental`, `deviation`. ContrarianTrader ignores fundamental value entirely -- its signal is purely statistical (price-path based).

**4.7.4.2  Core Behavioral Mechanism**

1. Maintains a rolling list of recent prices (up to `lookback_window = 10` rounds).
2. Each round: computes `cum_return = (price - price_10_rounds_ago) / price_10_rounds_ago`.
3. If `cum_return > entry_threshold (+0.05)`: sells -- expects mean reversion from upward overextension.
4. If `cum_return < -entry_threshold (-0.05)`: buys -- expects bounce from oversold.
5. Otherwise: holds.

**4.7.4.3  Mathematical Model**

- Decision variable: Trade quantity Q*(t)
- Trigger function:
  ```
  P_ref = price_history[max(0, t - lookback_window)]
  cum_return(t) = (P(t) - P_ref) / P_ref
  Sell: cum_return(t) > +0.05
  Buy:  cum_return(t) < -0.05
  ```
- Sizing function:
  ```
  Q*(t) = min(base_position_size, abs(cum_return(t)) x 400)
  Bounded by cash (buy) or position (sell)
  ```
- State variables: `price_history` -- rolling list of last 10 prices
- Parameter definitions:

| Symbol                    | Meaning                                               | Config Path                    | Source                                                         |
|---------------------------|-------------------------------------------------------|--------------------------------|----------------------------------------------------------------|
| lookback_window = 10      | Number of rounds for cumulative return                | players.yml -> ContrarianTrader | Jegadeesh (1990): short-horizon reversal at 1-4 week intervals |
| entry_threshold = 0.05    | Minimum cumulative return to trigger contrarian trade | players.yml -> ContrarianTrader | De Bondt & Thaler (1985): ~5% overreaction threshold           |
| base_position_size = 20.0 | Maximum trade size                                    | players.yml -> ContrarianTrader | Standardised                                                   |

**4.7.4.4  Behavioral Properties**

- Time horizon: Short-to-medium (10-round lookback; ~2 weeks compressed)
- Risk tolerance: Medium -- 5% threshold provides buffer against false signals
- Information asymmetry: None about fundamentals; uses only public price history
- Psychological profile: Statistical mean-reversion belief; contrarian temperament; De Bondt & Thaler (1985) overreaction hypothesis

#### 4.7.5  Decision Process Walkthrough

```
Given:  price = 107.5,  price_10_rounds_ago = 102.0,  entry_threshold = 0.05

Step 1: Compute cumulative return
        cum_return = (107.5 - 102.0) / 102.0 = +0.0539

Step 2: Compare to threshold
        +0.0539 > +0.05 -> sell condition (contrarian reversal bet)

Step 3: Compute quantity
        Q* = min(20.0, 0.0539 x 400) = min(20.0, 21.6) = 20 shares (capped)

Result: action = sell, quantity = 20, bid_price = 107.5
Rationale: Cumulative 10-round return exceeded +5%; ContrarianTrader bets on mean reversion.
This sells into the anchoring-driven overvaluation, adding corrective pressure from a
purely statistical (non-fundamental) perspective.
```

#### 4.7.6  Worked Numerical Example

```
Market state:  price = 96.5,  price_10_rounds_ago = 103.0

Calculation:
  cum_return = (96.5 - 103.0) / 103.0 = -0.0631  (6.3% decline over 10 rounds)
  -0.0631 < -0.05 -> buy condition (contrarian buy-the-dip)
  Q* = min(20.0, 0.0631 x 400) = min(20.0, 25.2) = 20 shares (capped)

Decision: action = buy, quantity = 20, bid_price = 96.5
Rationale: 10-round cumulative return is -6.3%, exceeding the 5% reversal threshold.
ContrarianTrader bets that the decline is an overreaction and prices will bounce.
Note: unlike RationalUpdater who buys because price < F, ContrarianTrader buys purely
because the decline is "too large" statistically -- a fundamentally different information set.
```

#### 4.7.7  Academic References

| # | Citation                                                                                                                                                                           | Notes                                                        |
|---|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------|
| 1 | De Bondt, W. F. M., & Thaler, R. H. (1985). Does the stock market overreacttheta *Journal of Finance*, 40(3), 793-805. https://doi.org/10.1111/j.1540-6261.1985.tb05004.x              | Core foundation; documents 25% reversal profits over 3 years |
| 2 | Jegadeesh, N. (1990). Evidence of predictable behavior of security returns. *Journal of Finance*, 45(3), 881-898. https://doi.org/10.1111/j.1540-6261.1990.tb05110.x               | Short-horizon reversals; calibrates lookback_window = 10     |
| 3 | Chopra, N., Lakonishok, J., & Ritter, J. R. (1992). Measuring abnormal performance. *Journal of Financial Economics*, 31(2), 235-268. https://doi.org/10.1016/0304-405X(92)90005-I | Cross-validates overreaction effects across market caps      |

---

## Source Docstring Excerpts

### Rule / `ContrarianTrader`

```text
Bets against recent trends -- sells after cumulative gains, buys after declines.

Implements simulation-bases.md Section 4.7 -- ContrarianTrader.
Theoretical basis: De Bondt & Thaler (1985); Jegadeesh (1990).

Decision rule:
    cum_return = (price - price_N_rounds_ago) / price_N_rounds_ago
    if cum_return > entry_threshold: sell (expect reversal)
    if cum_return < -entry_threshold: buy (expect bounce)

Parameters (simulation-bases.md Section 6):
    lookback_window: 10
    entry_threshold: 0.05
    base_position_size: 20.0
```
