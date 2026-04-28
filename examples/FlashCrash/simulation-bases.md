# FlashCrash Simulation Bases

## §1 Phenomenon

A flash crash is an intraday episode in which prices plunge by several percent within minutes and then largely recover, with no fundamental news. The archetypal event is the May 6, 2010 US equity flash crash in which the DJIA fell ~1,000 points (~9 %) in 36 minutes. Academic analysis (Kirilenko et al., 2017; CFTC-SEC, 2010) identifies three interlocking causes: (1) a large institutional sell programme that depleted order-book liquidity, (2) HFT market-makers withdrawing quotes when short-term price velocity exceeded their risk tolerance, and (3) stop-loss cascades from retail and institutional participants holding loss-stop levels. Fundamental traders eventually recognise undervaluation and provide the recovery force.

## §2 Theory

| Citation                                     | DOI / Reference                    | Relevance                                                        |
|----------------------------------------------|------------------------------------|------------------------------------------------------------------|
| Kirilenko, Kyle, Samadi & Tuzun (2017)       | 10.1111/jofi.12498                 | HFT market-maker stress behaviour; "hot potato" liquidity vacuum |
| CFTC-SEC Joint Report (2010)                 | —                                  | Official reconstruction of May 6, 2010 events                    |
| Grossman & Miller (1988)                     | 10.1111/j.1540-6261.1988.tb02607.x | Market-maker liquidity provision and withdrawal                  |
| De Long, Shleifer, Summers & Waldmann (1990) | 10.2307/2328395                    | Positive-feedback trading amplifying directional moves           |
| Brunnermeier & Pedersen (2005)               | 10.1111/j.1540-6261.2005.00781.x   | Predatory trading against stop-loss traders                      |
| Shiller (1981)                               | 10.1257/aer.71.3.421               | Excess volatility; fundamental value as price anchor             |
| Black (1986)                                 | 10.1111/j.1540-6261.1986.tb04513.x | Noise traders; random background volume                          |

## §3 Market Design

**Liquidity-sensitive price formation:**

```
P(t+1) = P(t) + base_price_impact × net_demand × liquidity_factor
         + mean_reversion × (fundamental − P(t)) + ε

liquidity_factor = high_impact_multiplier  if total_liquidity < low_liquidity_threshold
                 = 1.0 + (low_liquidity_threshold / total_liquidity − 1.0) × 0.5  otherwise
```

- `total_liquidity` = sum of `provides_liquidity` flags across all investors' orders
- When `provides_liquidity` providers withdraw, `liquidity_factor` jumps → amplified impact
- `mean_reversion` pulls price toward `fundamental_value`
- Broadcast keys: `price`, `prev_price`, `return`, `return_pct`, `volume`, `net_demand`, `liquidity`, `round`, `fundamental`
- Order keys: `bid_price`, `quantity`, `strategy`, `investor`, `provides_liquidity`

## §4 Investor Taxonomy

### §4.1 HighFrequencyTrader

**Role:** Ultra-fast momentum trader; primary crash trigger.

**Behavioural model:**
```python
short_momentum = price_history[-1] / price_history[-short_window] - 1
signal = short_momentum * momentum_sensitivity
quantity = signal * base_position_size * speed_advantage  # clamped ±60
provides_liquidity: False
```

**Parameters:** `momentum_sensitivity`, `base_position_size`, `speed_advantage`, `short_window`

**Decision rule:** Buys (sells) proportionally to short-term positive (negative) momentum. Never provides liquidity.

**Market effect:** Amplifies initial directional move; executes before slower agents.

**Theory:** Kirilenko et al. (2017) §4.1; positive-feedback momentum trading.

**Diversity:** Varied `momentum_sensitivity` (0.5–2.0) and `speed_advantage` (1.2–2.0) across instances.

**Distinguishing feature:** Fastest agent; drives the initial crash phase.

---

### §4.2 MarketMaker

**Role:** Liquidity provider that withdraws under stress; key amplification mechanism.

**Behavioural model:**
```python
price_return = abs((price - prev_price) / prev_price)
if price_return > volatility_threshold:
    provides_liquidity = False
    quantity = -position * 0.3        # sell 30 % of inventory
else:
    provides_liquidity = True
    quantity = -position * 0.2        # rebalance toward zero inventory
```

**Parameters:** `volatility_threshold`, `base_position_size`

**Decision rule:** Provides liquidity and rebalances inventory in calm conditions; withdraws and partially liquidates when single-round return exceeds `volatility_threshold`.

**Market effect:** Withdrawal reduces `total_liquidity`, raises `liquidity_factor`, amplifying all subsequent orders.

**Theory:** Grossman & Miller (1988); Kirilenko et al. (2017) — liquidity vacuum mechanism.

**Diversity:** Varied `volatility_threshold` (0.005–0.02) — some pull back earlier than others.

**Distinguishing feature:** The only agent whose `provides_liquidity` flag toggles; the sole driver of the liquidity multiplier.

---

### §4.3 AlgorithmicTrader

**Role:** Trend-following algorithm; mid-speed amplifier.

**Behavioural model:**
```python
trend = price_history[-1] / price_history[-trend_window] - 1
quantity = trend * trend_sensitivity * base_position_size * trend_multiplier
quantity = clamp(quantity, -40, 40)
provides_liquidity: False
```

**Parameters:** `trend_sensitivity`, `base_position_size`, `trend_multiplier`, `trend_window`

**Decision rule:** Buys (sells) in proportion to the return over a medium lookback window.

**Market effect:** Reinforces trend after HFT initiates it; sustains selling pressure during crash.

**Theory:** De Long et al. (1990) — positive-feedback speculation.

**Diversity:** Varied `trend_sensitivity` (0.5–2.0) and `trend_window` (3–10 rounds).

**Distinguishing feature:** Medium lookback window; bridges HFT and slower stop-loss agents.

---

### §4.4 StopLossTrader

**Role:** Stop-loss cascade generator; forced seller at predetermined levels.

**Behavioural model:**
```python
stop_price = recent_high * (1 - stop_loss_percent)
if price < stop_price and position > 0:
    quantity = -position    # sell entire position
    stop_triggered = True
provides_liquidity: False
```

**Parameters:** `stop_loss_percent`, `base_position_size`

**Decision rule:** Holds until price breaches `stop_price`; then sells all shares in a single round.

**Market effect:** Lumpy cascade selling that arrives in waves as successive stop levels are hit.

**Theory:** Brunnermeier & Pedersen (2005) — predatory stop-level targeting.

**Diversity:** Varied `stop_loss_percent` (0.02–0.10) → different agents trigger at different price levels, creating multi-wave cascade.

**Distinguishing feature:** One-shot seller; once triggered, exits completely and stays out.

---

### §4.5 FundamentalTrader

**Role:** Value buyer; provides the recovery force.

**Behavioural model:**
```python
deviation = (fundamental - price) / fundamental
if deviation > value_threshold:
    quantity = deviation * base_position_size * value_sensitivity * value_multiplier
elif deviation < -value_threshold:
    quantity = deviation * base_position_size * value_sensitivity * value_multiplier  # sell
quantity = clamp(quantity, -50, 50)
provides_liquidity: True
```

**Parameters:** `value_threshold`, `base_position_size`, `value_sensitivity`, `value_multiplier`

**Decision rule:** Buys when market price is sufficiently below fundamental; sells when it is above. Always provides liquidity.

**Market effect:** Absorbs selling pressure during the crash trough; supplies stabilising net demand for recovery.

**Theory:** Shiller (1981) — fundamental value as gravity.

**Diversity:** Varied `value_threshold` (0.03–0.10) — more aggressive traders provide earlier stabilisation.

**Distinguishing feature:** Only consistently pro-cyclical liquidity provider; drives recovery phase.

---

### §4.6 RetailTrader

**Role:** Uninformed background participant.

**Behavioural model:**
```python
if round_num % trade_frequency != 0:
    quantity = 0.0          # only trades every trade_frequency rounds
else:
    quantity = gauss(0, noise_std) + (-position_mean_reversion * position)
    quantity = clamp(quantity, -15, 15)
```

**Parameters:** `trade_frequency`, `noise_std`, `position_mean_reversion`

**Decision rule:** Mostly silent; trades at fixed intervals with random direction and a position mean-reversion drag.

**Market effect:** Provides steady low-volume background; prevents market from being trivially one-sided.

**Theory:** Black (1986) — noise traders.

**Diversity:** Varied `trade_frequency` (1–5 rounds) and `noise_std` (1.0–5.0).

**Distinguishing feature:** Infrequent; adds stochastic volume without directional bias.

## §5 Agent Diversity

| Agent               | Instances | Key varied parameters                     |
|---------------------|-----------|-------------------------------------------|
| HighFrequencyTrader | 3–5       | `momentum_sensitivity`, `speed_advantage` |
| MarketMaker         | 3–5       | `volatility_threshold`                    |
| AlgorithmicTrader   | 2–4       | `trend_sensitivity`, `trend_window`       |
| StopLossTrader      | 5–10      | `stop_loss_percent`                       |
| FundamentalTrader   | 2–4       | `value_threshold`, `value_sensitivity`    |
| RetailTrader        | 5–10      | `trade_frequency`, `noise_std`            |

## §6 Parameter Table

| Parameter                   | Default | Range      | Effect                      |
|-----------------------------|---------|------------|-----------------------------|
| `initial_price`             | 100.0   | 80–120     | Starting price level        |
| `fundamental_value`         | 100.0   | 90–110     | Mean-reversion anchor       |
| `base_price_impact`         | 0.005   | 0.001–0.02 | λ in price equation         |
| `low_liquidity_threshold`   | 3       | 1–5        | Liquidity alarm level       |
| `high_impact_multiplier`    | 3.0     | 2.0–5.0    | Amplification when illiquid |
| `mean_reversion`            | 0.02    | 0.01–0.05  | Speed of fundamental pull   |
| `noise_std`                 | 0.1     | 0.05–0.5   | Market noise                |
| `volatility_threshold` (MM) | 0.01    | 0.005–0.02 | MM withdrawal trigger       |
| `stop_loss_percent`         | 0.05    | 0.02–0.10  | SL trigger depth            |
| `value_threshold`           | 0.05    | 0.03–0.10  | FT entry deviation          |

## §7 Round Structure

```
Round t:
  1. Market.perceive()  — collect all investor orders from round t-1
  2. Market.decide()    — compute total_liquidity, liquidity_factor, new price
  3. Market.act()       — broadcast market_data to all investors
  4. Investors.perceive() — read market_data; update price_history
  5. Investors.decide()   — compute quantity and provides_liquidity flag
  6. Investors.act()      — send order to Market

Phase mapping (typical 50-round run):
  Normal      rounds  1–10   : mixed activity; MM provides liquidity
  Trigger     rounds 11–15   : HFT detects momentum; initial selling
  Cascade     rounds 16–25   : MM withdraws; stop-losses trigger; deep crash
  Trough      rounds 26–30   : maximum deviation; FT buys aggressively
  Recovery    rounds 31–50   : price returns toward fundamental
```

## §8 Historical Cases

| Event                    | Date       | Magnitude            | Duration | Key cause                                   |
|--------------------------|------------|----------------------|----------|---------------------------------------------|
| May 6, 2010 Flash Crash  | 2010-05-06 | −9 % DJIA            | 36 min   | W&R institutional sell + HFT withdrawal     |
| Mini Flash Crash (AAPL)  | 2012-04-23 | −10 % in seconds     | <60 s    | Fat-finger algorithmic order                |
| 2015 NYSE Outage + Flash | 2015-07-08 | −5 % (select stocks) | ~3 h     | System outage + dark pool rerouting         |
| ETF Flash Crash          | 2015-08-24 | −30 % (ETFs)         | 30 min   | Market-on-open imbalance + circuit breakers |

## §9 Variant Comparison

| Dimension              | Rule                          | LLM                               | RuleLLM                           | Rag                                |
|------------------------|-------------------------------|-----------------------------------|-----------------------------------|------------------------------------|
| MM withdrawal trigger  | Fixed `volatility_threshold`  | LLM judges "stress" qualitatively | Rule threshold + LLM override     | RAG case retrieval + LLM judgment  |
| HFT momentum detection | Deterministic formula         | LLM sentiment on returns          | Rule signal + LLM confirmation    | History-augmented LLM              |
| Stop-loss cascade      | Fixed stop levels             | LLM decides when to cut losses    | Predefined stops + LLM adjustment | LLM informed by historical crashes |
| Recovery mechanism     | Deviation > `value_threshold` | LLM "undervalued" assessment      | Rule entry + LLM sizing           | RAG-guided fundamental entry       |
| `provides_liquidity`   | Boolean from formula          | LLM decision field                | Rule logic dominant               | RAG-enhanced decision              |
| Determinism            | High                          | Low                               | Medium                            | Medium-low                         |
| Theoretical fidelity   | Exact                         | Emergent                          | Hybrid                            | Historically grounded              |
