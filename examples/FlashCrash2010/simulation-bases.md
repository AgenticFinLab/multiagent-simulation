# FlashCrash2010 Simulation Bases

## §1 Phenomenon

The May 6, 2010 Flash Crash was a specific market microstructure event in which the US equity market (DJIA) fell ~9 % in 36 minutes and recovered in approximately 20 minutes. The SEC-CFTC Joint Report (2010) and Kirilenko et al. (2017) establish the causal chain: a large institutional sell programme (Waddell & Reed, E-mini S&P futures) exhausted order-book depth; HFT market makers detected stress and progressively widened spreads then withdrew; momentum chasers accelerated the decline; stop-loss orders triggered in cascades; and fundamental traders eventually recognised the undervaluation and reversed the move. This scenario explicitly models order-book depth dynamics, spread widening, and HFT stress-response as the primary amplification mechanisms.

## §2 Theory

| Citation                                     | DOI / Reference                    | Relevance                                                |
|----------------------------------------------|------------------------------------|----------------------------------------------------------|
| Kirilenko, Kyle, Samadi & Tuzun (2017)       | 10.1111/jofi.12498                 | HFT behaviour in May 6 crash; stress-response withdrawal |
| CFTC-SEC Joint Report (2010)                 | —                                  | Official event reconstruction; order-book depth collapse |
| Biais, Foucault & Moinas (2015)              | 10.1016/j.jfineco.2015.03.004      | Equilibrium fast trading; spread widening under stress   |
| De Long, Shleifer, Summers & Waldmann (1990) | 10.2307/2328395                    | Positive-feedback momentum amplification                 |
| Brunnermeier & Pedersen (2005)               | 10.1111/j.1540-6261.2005.00781.x   | Stop-loss cascade via predatory trading                  |
| Shiller (1981)                               | 10.1257/aer.71.3.421               | Fundamental value as price anchor; excess volatility     |
| Black (1986)                                 | 10.1111/j.1540-6261.1986.tb04513.x | Noise traders; background volume                         |
| Abreu & Brunnermeier (2003)                  | 10.1111/1468-0262.00393            | Synchronised liquidity withdrawal; coordination risk     |

## §3 Market Design

**Order-book depth model:**

```
P(t+1) = P(t) + λ × NetOrderFlow / Depth(t) + γ × (F − P(t)) + ε

Depth(t) = base_depth × max(stress_factor, 0.1)

stress_factor = 1.0
if volatility > 0.01: stress_factor × = 0.5
if volatility > 0.02: stress_factor × = 0.3
if hft_participation < 0.30: stress_factor × = 0.5

spread = base_spread + volatility × 0.5
if hft_participation < 0.30: spread × = 3.0
if volatility > 0.02: spread × = 5.0
spread = min(spread, 0.05)
```

- `volatility` = mean |return| over last 10 rounds
- `hft_participation` = fraction of orders with `agent_type == "hft"`
- `Depth` collapses when both HFT withdraws AND volatility rises
- Broadcast keys: `price`, `prev_price`, `return_pct`, `fundamental`, `deviation`, `spread`, `depth`, `volume`, `volatility`, `round`
- Order keys: `bid_price`, `quantity`, `strategy`, `agent_type`, `provides_liquidity`

## §4 Investor Taxonomy

### §4.1 HFTMarketMaker

**Role:** HFT liquidity provider; withdraws under stress — primary amplification mechanism.

**Behavioural model:**
```python
# 5-round velocity computation
velocity = mean(|return_i| for i in last 5 rounds)
stressed = velocity > withdrawal_threshold

if not stressed:
    provides_liquidity = True
    quantity = 500                # normal liquidity provision
    spread = normal_spread
else:
    provides_liquidity = False
    quantity = 0                  # complete withdrawal
    spread = stress_spread
```

**Parameters:** `withdrawal_threshold`, `normal_spread`, `stress_spread`, `inventory_limit`

**Decision rule:** Provides liquidity (500 units) and uses tight spread in normal conditions; completely withdraws when 5-round price velocity exceeds `withdrawal_threshold`.

**Market effect:** Withdrawal increases `hft_participation` denominator drop → `stress_factor` collapses → `Depth` shrinks → price impact amplifies.

**Theory:** Kirilenko et al. (2017) — HFT stress response; Biais et al. (2015) — spread widening.

**Diversity:** Varied `withdrawal_threshold` (0.005–0.03) across instances — staggered withdrawal.

**Distinguishing feature:** `agent_type = "hft"` flag drives the market's depth calculation; withdrawal is the single largest amplifier.

---

### §4.2 MomentumChaser

**Role:** HFT trend-follower; amplifies directional moves.

**Behavioural model:**
```python
velocity = (price_history[-1] - price_history[-lookback]) / price_history[-lookback]
if abs(velocity) > entry_threshold:
    quantity = int(min(abs(velocity) * position_multiplier, 1000))
    quantity = quantity if velocity > 0 else -quantity
else:
    quantity = 0
# constrained by cash (buy) or position (sell)
provides_liquidity: False
agent_type: "hft"
```

**Parameters:** `lookback_window`, `entry_threshold`, `position_multiplier`

**Decision rule:** Enters in the direction of price move if the `lookback_window` return exceeds `entry_threshold`; position size proportional to velocity.

**Market effect:** Adds net sell flow during crash, contributing to HFT participation count and reinforcing the momentum.

**Theory:** De Long et al. (1990) — positive-feedback speculation.

**Diversity:** Varied `lookback_window` (3–10) and `entry_threshold` (0.005–0.02).

**Distinguishing feature:** Unlike HFTMarketMaker, MomentumChaser always participates in the direction of the trend; `agent_type = "hft"` keeps it counted in `hft_participation`.

---

### §4.3 FundamentalTrader

**Role:** Value-based contrarian; stabilising and recovery force.

**Behavioural model:**
```python
deviation = (price - fundamental) / fundamental
if deviation < -value_trigger:
    quantity = min(order_size, int(cash / price))   # buy undervalued
elif deviation > value_trigger:
    quantity = -min(order_size, position)            # sell overvalued
else:
    quantity = 0
provides_liquidity: True
agent_type: "fundamental"
```

**Parameters:** `value_trigger`, `order_size`

**Decision rule:** Buys (sells) when price deviates more than `value_trigger` below (above) fundamental; fixed order size.

**Market effect:** Absorbs sell pressure at the trough; drives price recovery toward fundamental.

**Theory:** Shiller (1981) — excess volatility correction; fundamental value gravity.

**Diversity:** Varied `value_trigger` (0.03–0.10) and `order_size` (200–1000) across instances.

**Distinguishing feature:** `provides_liquidity: True` and `agent_type = "fundamental"` — does not count toward HFT participation; provides stabilising force.

---

### §4.4 StopLossTrader

**Role:** Stop-loss cascade generator; forced seller at pre-set level.

**Behavioural model:**
```python
stop_level = entry_price * (1 - stop_percentage)
if price <= stop_level and position > 0 and not stopped:
    quantity = -position              # sell entire position
    stopped = True
else:
    quantity = 0
provides_liquidity: False
agent_type: "stoploss"
```

**Parameters:** `stop_percentage`, `initial_position`, `entry_price`

**Decision rule:** Holds position until price touches `stop_level`; then sells the entire position in one round (one-shot exit).

**Market effect:** Large, sudden sell orders that deplete `Depth` and trigger further price drops, setting off the next wave of stop-losses.

**Theory:** Brunnermeier & Pedersen (2005) — stop-level predatory targeting.

**Diversity:** Varied `stop_percentage` (0.02–0.08) → multi-wave cascade as successive levels are hit.

**Distinguishing feature:** Fires once and permanently exits (`stopped = True`); `agent_type = "stoploss"`.

---

### §4.5 NoiseTrader

**Role:** Uninformed background participant.

**Behavioural model:**
```python
if random.random() > trade_probability:
    quantity = 0
else:
    size = random.randint(min_order, max_order)
    quantity = size if random.random() > 0.5 else -size
# constrained by cash / position
provides_liquidity: False
agent_type: "noise"
```

**Parameters:** `trade_probability`, `min_order`, `max_order`

**Decision rule:** Trades with probability `trade_probability` per round; random direction; random size in `[min_order, max_order]`.

**Market effect:** Provides steady low-volume background flow; does not intentionally amplify or dampen.

**Theory:** Black (1986) — noise trading model.

**Diversity:** Varied `trade_probability` (0.03–0.10) and order size range.

**Distinguishing feature:** Purely random; `agent_type = "noise"`.

## §5 Agent Diversity

| Agent             | Instances | Key varied parameters                                       |
|-------------------|-----------|-------------------------------------------------------------|
| HFTMarketMaker    | 3–5       | `withdrawal_threshold`, `normal_spread`                     |
| MomentumChaser    | 2–4       | `lookback_window`, `entry_threshold`, `position_multiplier` |
| FundamentalTrader | 2–3       | `value_trigger`, `order_size`                               |
| StopLossTrader    | 5–10      | `stop_percentage`                                           |
| NoiseTrader       | 5–10      | `trade_probability`, `min_order`, `max_order`               |

## §6 Parameter Table

| Parameter              | Default | Range          | Effect                          |
|------------------------|---------|----------------|---------------------------------|
| `initial_price`        | 40.0    | 35–50          | Starting price level            |
| `fundamental_value`    | 40.0    | 38–42          | Mean-reversion anchor           |
| `base_depth`           | 10000   | 2000–10000     | Order-book depth baseline       |
| `price_impact` (lambda) | 0.05   | 0.00005–0.05   | Price sensitivity to order flow |
| `mean_reversion`       | 0.02    | 0.02–0.10      | Speed of fundamental pull       |
| `noise_std`            | 0.01    | 0.005–0.05     | Market noise                    |
| `withdrawal_threshold` | 0.02    | 0.005–0.03     | HFT stress velocity             |
| `stop_percentage`      | 0.03    | 0.02–0.08      | Stop-loss level                 |
| `value_trigger`        | 0.05    | 0.03–0.10      | FT entry deviation              |
| `entry_threshold` (MC) | 0.001   | 0.001–0.02     | Momentum-chaser trigger         |

## §7 Round Structure

```
Round t:
  1. Market.perceive()     — collect all investor orders; compute hft_participation
  2. Market.decide()       — compute volatility, stress_factor, Depth, spread, new_price
  3. Market.act()          — broadcast market_data to all investors
  4. Investors.perceive()  — read market_data; update price_history
  5. Investors.decide()    — compute quantity, agent_type, provides_liquidity
  6. Investors.act()       — send order to Market

Phase mapping (illustrative 200-round full run):
  Normal      early rounds          : HFT provides liquidity; depth near base_depth
  Trigger     after a directional move: MomentumChasers detect trend; first HFT stress
  Cascade     stress window         : HFT withdrawal; depth collapses; stop-losses fire
  Trough      crash minimum         : minimum depth; maximum spread; FT buying begins
  Recovery    post-trough rounds    : HFT returns; depth rebuilds; price moves toward fundamental
```

## §8 Historical Cases

| Event                               | Date       | Magnitude         | Duration | Key cause                           |
|-------------------------------------|------------|-------------------|----------|-------------------------------------|
| May 6, 2010 Flash Crash             | 2010-05-06 | −9 % DJIA         | 36 min   | W&R sell programme + HFT withdrawal |
| 2010 Mini Flash (individual stocks) | 2010-05-06 | −50 %+ (P&G etc.) | Minutes  | Quote stuffing + depth collapse     |
| Knight Capital Algo Error           | 2012-08-01 | −70 % (KCG stock) | 45 min   | Runaway algorithm                   |
| 2015 ETF Flash Crash                | 2015-08-24 | −30 % (ETFs)      | 30 min   | Market-on-open imbalance            |

## §9 Variant Comparison

| Dimension              | Rule                                    | LLM                                 | RuleLLM                       | Rag                         |
|------------------------|-----------------------------------------|-------------------------------------|-------------------------------|-----------------------------|
| HFT withdrawal trigger | Fixed velocity > `withdrawal_threshold` | LLM judges "stressed" qualitatively | Rule threshold + LLM override | RAG historical case + LLM   |
| Depth dynamics         | Deterministic formula                   | LLM order sizes and class-mapped `agent_type` modulate depth | Rule depth + LLM timing and class-mapped `agent_type` | History-informed with class-mapped `agent_type` |
| MomentumChaser entry   | Fixed threshold + multiplier            | LLM momentum assessment             | Rule signal + LLM size        | RAG-augmented               |
| Stop-loss cascade      | Fixed stop levels, one-shot             | LLM decides cut-loss timing         | Predefined + LLM override     | Historical pattern guidance |
| Recovery               | Fixed FT `value_trigger`                | LLM "undervalued" perception        | Rule entry + LLM size         | RAG-guided entry            |
| Spread model           | Deterministic (volatility/hft)          | Implicit in order volumes           | Hybrid                        | Context-augmented           |
| Determinism            | High                                    | Low                                 | Medium                        | Medium-low                  |
