# Herd Effect Simulation - Emergent Herding Model

## What is This?

| Item               | Description                                                          |
|--------------------|----------------------------------------------------------------------|
| **Phenomenon**     | **Emergent Herding (涌现型羊群效应)** - 无预设模仿者的自发行为趋同   |
| **Model**          | Order-based market clearing with 5 heterogeneous investor types      |
| **Key Feature**    | Herd behavior EMERGES from positive feedback, not explicit imitation |
| **Academic Value** | Reveals MECHANISM of herding, not just the PHENOMENON                |

## Why Emergent Herding? (为什么选择涌现模型？)

传统羊群效应模拟通常包含一个**显式模仿者 (HerdingInvestor)**，直接复制他人行为。
然而，这种设计存在问题：

| 传统模型 (Explicit Herding)  | 涌现模型 (Emergent Herding)    |
|------------------------------|--------------------------------|
| 预设模仿者，结果必然出现羊群 | 无模仿者，羊群从交互中自发涌现 |
| 证明"羊群存在"               | 揭示"羊群如何形成"             |
| 观察现象 (Phenomenon)        | 解释机制 (Mechanism)           |
| 学术价值有限                 | 可发表的原创性贡献             |

**核心洞察**：即使没有"盲目跟随者"，仅靠**正反馈交易**（Momentum + Aggressive）就能自发形成信息级联。

## Financial Background

| Theory                  | Application                                   | Reference                                                                                                                                                                                 |
|-------------------------|-----------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Momentum**            | MomentumInvestor: P = P×(1+λr), Q = βr×cash/P | Jegadeesh, N. & Titman, S. (1993). *Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency*. Journal of Finance, 48(1), 65-91.                            |
| **Contrarian**          | ContrarianInvestor: Q ∝ (F-P)/P               | De Bondt, W.F.M. & Thaler, R. (1985). *Does the Stock Market Overreact?* Journal of Finance, 40(3), 793-805.                                                                              |
| **Mean-Variance**       | RiskAverseInvestor: Q ∝ 1/σ²                  | Markowitz, H. (1952). *Portfolio Selection*. Journal of Finance, 7(1), 77-91.                                                                                                             |
| **Noise Trader**        | NoiseTrader: Q ~ N(0, σ²)                     | De Long, J.B., Shleifer, A., Summers, L.H. & Waldmann, R.J. (1990). *Noise Trader Risk in Financial Markets*. Journal of Political Economy, 98(4), 703-738.                               |
| **Positive Feedback**   | AggressiveInvestor: Q = βr×cash/P + accel     | Shiller, R.J. (1984). *Stock Prices and Social Dynamics*. Brookings Papers on Economic Activity, 1984(2), 457-510.                                                                        |
| **Information Cascade** | Emergent from agent interactions              | Bikhchandani, S., Hirshleifer, D. & Welch, I. (1992). *A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades*. Journal of Political Economy, 100(5), 992-1026. |

## Why These 5 Investor Types? (为什么是这5类投资者？)

涌现型羊群效应的模拟需要**异质性代理人 (Heterogeneous Agents)**，但**不需要预设的模仿者**。

### Destabilizing Forces (不稳定力量 - 创造羊群)

| Investor               | Role                | Why Needed                                                                      |
|------------------------|---------------------|---------------------------------------------------------------------------------|
| **MomentumInvestor**   | ⭐ Primary Feedback  | 趋势跟随者，价格涨则买、跌则卖。形成**正反馈循环**，是涌现羊群的核心驱动力。    |
| **AggressiveInvestor** | ⭐ Extreme Amplifier | 杠杆动量 + 加速度交易。当动量信号出现时，**放大**信号强度，加速泡沫形成与崩盘。 |

> **关键洞察**：MomentumInvestor + AggressiveInvestor 的组合就足以产生涌现羊群，无需显式模仿者。

### Stabilizing Forces (稳定力量 - 抑制羊群)

| Investor               | Role          | Why Needed                                                                     |
|------------------------|---------------|--------------------------------------------------------------------------------|
| **ContrarianInvestor** | Value Anchor  | 价值投资者，高于基本面则卖，低于则买。提供**均值回复**力量，防止泡沫无限膨胀。 |
| **RiskAverseInvestor** | Early Warning | 波动率敏感型，高波动时减仓。可在崩盘前**提前离场**，触发多米诺骨牌效应。       |

> **对比实验**：若稳定力量足够强（资金多、人数多），可观察到羊群效应被抑制。

### Noise & Liquidity (噪声与流动性)

| Investor        | Role              | Why Needed                                                               |
|-----------------|-------------------|--------------------------------------------------------------------------|
| **NoiseTrader** | ⭐ Initial Trigger | 随机交易提供市场噪声。关键作用：**意外触发**动量交易者，启动正反馈链条。 |

> **涌现机制起点**：NoiseTrader 的随机买入 → 价格微涨 → MomentumInvestor 跟进 → 羊群效应启动。

### Emergent Herding Mechanism (涌现羊群形成机制)

```
                    ┌──────────────────────────────────────────┐
                    │     Emergent Herding Mechanism           │
                    │     (无模仿者的自发行为趋同)             │
                    └──────────────────────────────────────────┘

  Phase 1: TRIGGER (触发)
  ─────────────────────────
  NoiseTrader 随机买入 → 价格小幅上涨 (ΔP > 0)
                 │
                 ▼
  Phase 2: POSITIVE FEEDBACK (正反馈)
  ─────────────────────────────────────
  MomentumInvestor 检测到 ΔP > 0 → 买入
                 │
                 ▼
  价格进一步上涨 + 成交量放大
                 │
                 ▼
  Phase 3: AMPLIFICATION (放大)
  ───────────────────────────────
  AggressiveInvestor 看到 "价↑量↑" → 杠杆加仓 + 加速度交易
                 │
                 ▼
  价格急速上涨，偏离基本面
                 │
                 ▼
  Phase 4: BEHAVIORAL CONVERGENCE (行为趋同)
  ───────────────────────────────────────────
  ContrarianInvestor 试图卖出 → 但资金/影响力有限
  RiskAverseInvestor 观望或减仓 → 不足以阻止趋势
                 │
                 ▼
         ┌─────────────────────────────────┐
         │   EMERGENT RESULT (涌现结果)    │
         │   所有人行为趋同 → 买入         │
         │   虽然没有模仿者！              │
         └─────────────────────────────────┘
                 │
                 ▼
  Phase 5: BUBBLE PEAK & CRASH (泡沫顶峰与崩盘)
  ───────────────────────────────────────────────
  RiskAverseInvestor 波动率过高 → 集体撤退
  正反馈反转为负反馈 → 崩盘
```

### Agent Interaction Dynamics (代理人交互动力学)

```
         DESTABILIZING (创造羊群)              STABILIZING (抑制羊群)
                    │                                  │
    ┌───────────────┼───────────────┐  ┌──────────────┼──────────────┐
    │               │               │  │              │              │
    ▼               ▼               │  │              ▼              ▼
 Aggressive    Momentum             │  │         Contrarian     RiskAverse
 (极端放大)    (趋势跟随)           │  │         (价值锚定)     (波动规避)
    │               │               │  │              │              │
    └───────┬───────┘               │  │              └──────┬───────┘
            │                       │  │                     │
            │  正反馈循环           │  │        负反馈/均值回复
            │  (Positive Feedback)  │  │        (Negative Feedback)
            │                       │  │                     │
            └───────────────────────┼──┼─────────────────────┘
                                    │  │
                                    ▼  ▼
                         ┌─────────────────────┐
                         │   NoiseTrader       │
                         │   (随机触发/流动性) │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Market Clearing   │
                         │   Price = f(demand) │
                         └─────────────────────┘
```

### Complete Bubble Lifecycle (完整泡沫周期)

| Phase             | Dominant Agents               | Mechanism                          |
|-------------------|-------------------------------|------------------------------------|
| **1. Trigger**    | NoiseTrader                   | 随机波动被动量交易者误读为信号     |
| **2. Build-up**   | MomentumInvestor              | 趋势跟随，价格上涨，正反馈启动     |
| **3. Cascade**    | MomentumInvestor + Aggressive | **涌现级联**：无模仿者，但行为趋同 |
| **4. Mania**      | AggressiveInvestor            | 极端正反馈，杠杆放大，泡沫峰值     |
| **5. Correction** | ContrarianInvestor            | 价值回归力量介入，但可能被淹没     |
| **6. Crash**      | RiskAverseInvestor            | 波动规避触发集体撤退，正反馈反转   |

## Price-Volume Feedback Loop

```
                    ┌──────────────────────────────────────────┐
                    │     Price-Volume Positive Feedback       │
                    └──────────────────────────────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         ▼                             ▼                             ▼
┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
│   Last Round    │          │   Investor      │          │   This Round    │
│   P↑ + V↑       │────────▶ │   Interprets    │────────▶ │   P↑↑ + V↑↑    │
│   (price+volume)│          │   as "strong    │          │   (amplified)   │
└─────────────────┘          │   trend signal" │          └─────────────────┘
                             └─────────────────┘
                                       │
                                       ▼
                    ┌──────────────────────────────────────────┐
                    │   Result: Bubble Formation               │
                    │   Price deviates from fundamental (100)  │
                    └──────────────────────────────────────────┘
```

## Market Clearing Model

```
Order-Based Clearing:

  1. Collect all orders (P_i, Q_i) from investors
  2. Calculate net demand: D = Σ(buy_qty) - Σ(sell_qty)
  3. Price update:
  
     P(t+1) = P(t) + λ×D(t) + γ×[F - P(t)] + ε
     
     Where:
       λ = 0.1   (supply elasticity / market depth)
       γ = 0.02  (mean reversion speed)
       F = 100.0 (fundamental value)
       ε ~ N(0, 0.5)
```

| Parameter             | Value  | Financial Meaning                         |
|-----------------------|--------|-------------------------------------------|
| λ (Supply Elasticity) | 0.1    | Higher = less liquid, more price impact   |
| γ (Mean Reversion)    | 0.02   | Speed of price correction to fundamentals |
| F (Fundamental)       | 100.0  | True intrinsic value                      |
| Initial Cash          | 10,000 | Per-investor starting capital             |
| Initial Position      | 0      | No initial holdings                       |

## Investor Strategies (5 Types - Emergent Model)

### 1. Momentum Investor (⭐ Primary Positive Feedback)
```
P = P_last × (1 + λ × r)      where λ = 0.5
Q = β × r × cash / P          where β = 0.3
```
| Effect | **DESTABILIZING** - amplifies price trends, core herding driver |
| Risk | High - buys high, sells low |

### 2. Aggressive Investor (⭐ Extreme Amplifier)
```
P = P_last × (1 + κ × r)       where κ = 1.0
Q = β × r × cash / P + 0.3 × acceleration
acceleration = (P[-1] - P[-2]) - (P[-2] - P[-3])
```
| Effect | **EXTREMELY DESTABILIZING** - leverage + acceleration |
| Risk | Very High - can cause flash crashes |

> **涌现机制核心**：Momentum + Aggressive 的组合产生足够强的正反馈，无需显式模仿者。

### 3. Contrarian Investor (Value Anchor)
```
P = F + ε                     bid around fundamental (100)
Q = β × (F - P) / P × cash / P   where β = 0.5
```
| Effect | **STABILIZING** - dampens price deviations |
| Risk | Medium - may buy into falling knife |

### 4. Risk-Averse Investor (Early Exit Trigger)
```
σ² = variance(P[-5:])
Q = k / σ² × cash / P          where k = 0.5
```
| Effect | **EARLY EXIT** - reduces exposure in volatility |
| Risk | Low - but may miss upside |

### 5. Noise Trader (Random Trigger)
```
P ~ N(P_last, 2.0²)
Q ~ N(0, 5.0²) - 0.1 × position
```
| Effect | **TRIGGER SOURCE** - random signal starts the cascade |
| Risk | Random - provides liquidity |

## Strategy Comparison (Emergent Model)

| Strategy       | Formula                 | Market Effect           | Risk      | Emergent Role   |
|----------------|-------------------------|-------------------------|-----------|-----------------|
| **Momentum**   | Q = 0.3r×cash/P         | Destabilizing           | High      | ⭐ Core Feedback |
| **Aggressive** | Q = 0.5r×cash/P + accel | Extremely Destabilizing | Very High | ⭐ Amplifier     |
| Contrarian     | Q = 0.5(F-P)/P×cash/P   | Stabilizing             | Medium    | Damper          |
| RiskAverse     | Q = 0.5/σ²×cash/P       | Early Exit              | Low       | Crash Trigger   |
| **Noise**      | Q ~ N(0, 25)            | Trigger/Liquidity       | Random    | ⭐ Initial Spark |

## Emergent Herd Formation Mechanism (涌现机制详解)

### Why Does Herding EMERGE Without an Imitator?

传统模型依赖**显式模仿者**来产生羊群效应。本模型证明：**正反馈交易者**足以产生相同效果。

```
  传统模型 (Explicit)              涌现模型 (Emergent)
  ─────────────────────            ────────────────────────
  HerdingInvestor 复制他人行为     MomentumInvestor 追随价格趋势
        │                                  │
        ▼                                  ▼
  直接模仿 → 羊群                  价格↑ → 买入 → 价格↑↑ → 更多买入
        │                                  │
        ▼                                  ▼
  行为一致 (设计使然)              行为一致 (涌现结果)
```

### Volume as Social Proof (成交量作为社会验证)
```
Price Signal  → "Market is rising"
Volume Signal → "Many people are buying with real money" (社会验证)

Combined → AggressiveInvestor sees "价↑量↑" → Bold position → Amplification
```

### Typical Emergent Bubble Evolution

| Round | Observation        | Price   | Volume    | Mechanism                                  |
|-------|--------------------|---------|-----------|--------------------------------------------||
| 1-5   | Baseline           | ~100    | Low       | Strategies interact, near equilibrium      |
| 6-15  | Noise triggers     | 100→105 | Rising    | NoiseTrader random buy → Momentum follows  |
| 16-30 | **Emergent Cascade** | 105→115 | High      | Momentum + Aggressive amplify each other   |
| 31-40 | Bubble peak        | 115→125 | Very High | All strategies converge (without imitator) |
| 41-50 | Correction/Crash   | 125→100 | Volatile  | RiskAverse exits → Negative feedback       |

## Simulation Setup

| Component | Count | Role                                            |
|-----------|-------|-------------------------------------------------|
| Market    | 1     | Order clearing, price broadcast                 |
| Investors | 5     | Heterogeneous strategies (no explicit imitator) |
| Rounds    | 50    | Price discovery iterations                      |

## Topology (Emergent Model)

```
                         ┌───────────────────┐
                         │      market       │ ◄── Level 0 (clears orders, broadcasts)
                         └─────────┬─────────┘
                                   │
         ┌───────────┬─────────────┼─────────────┬───────────┐
         ▼           ▼             ▼             ▼           ▼
    momentum    contrarian    risk_averse   aggressive    noise   ◄── Level 1
    (⭐feedback) (stabilize)    (early exit)  (⭐amplify)  (⭐trigger)
```

**Note**: No HerdingInvestor - herding EMERGES from Momentum + Aggressive interaction.

## Files

| File                                | Purpose                                      |
|-------------------------------------|----------------------------------------------|
| `players.py`                        | Market + 5 investor classes (emergent model) |
| `run_herd.py`                       | Entry point                                  |
| `analysis.py`                       | Emergent herding metrics & visualization     |
| `configs/HerdEffect/simulation.yml` | Main config                                  |
| `configs/HerdEffect/players.yml`    | Player definitions (5 investors)             |
| `configs/HerdEffect/topology.yml`   | Star topology                                |

## Running

```bash
# Run simulation
python examples/HerdEffect/run_herd.py -c configs/HerdEffect/simulation.yml

# Analyze results
python examples/HerdEffect/analysis.py -c configs/HerdEffect/simulation.yml
```

## Expected Behavior

| Phase      | Rounds | Observation                             |
|------------|--------|-----------------------------------------|
| Initial    | 1-10   | Price fluctuates near fundamental (100) |
| Build-up   | 11-30  | Price↑ + Volume↑ as herd forms          |
| Bubble     | 31-45  | Price peaks, deviates from fundamental  |
| Correction | 46-50  | Mean reversion pulls price back         |

## Emergent Herding Detection Metrics (涌现羊群检测指标)

| Indicator                       | Formula                    | Description                                 |
|---------------------------------|----------------------------|---------------------------------------------|
| **Bid Convergence Index (CV)**  | CV = σ(bids) / μ(bids)     | 出价变异系数，CV↓ = 行为趋同 = 羊群形成     |
| **Directional Agreement**       | DA = \|Σ(sign(ΔBid))\| / N | 方向一致性，DA > 0.8 = 强羊群               |
| **Information Cascade Measure** | ICM = 逆市交易者比例       | 忽略私人信号跟随市场的比例，ICM↑ = 级联形成 |
| **Price Deviation**             | PD = (P - F) / F           | 价格偏离基本面程度                          |
| **Rolling Volatility**          | σ(P[-window:])             | 波动率，泡沫期先升后降                      |
| **Autocorrelation**             | corr(r_t, r_{t-lag})       | 收益率自相关，>0 = 动量持续                 |

### Expected Patterns in Emergent Herding

| Metric                | Normal Market | Herd Formation | Bubble Peak | Crash     |
|-----------------------|---------------|----------------|-------------|-----------|
| Bid CV                | 0.10-0.20     | **↓ < 0.05**   | < 0.03      | ↑ 0.15+   |
| Directional Agreement | 0.50-0.60     | **↑ > 0.80**   | > 0.90      | < 0.50    |
| Price Deviation       | ±5%           | **↑ 10-20%**   | > 25%       | ↓ rapidly |
| Volatility            | Low           | Rising         | **Peak**    | Spike     |

## Real-World Mapping

| Simulation           | Real-World Example                        |
|----------------------|-------------------------------------------|
| Noise triggers       | Unexpected news, social media buzz        |
| Momentum amplifies   | Technical traders follow breakout         |
| **Emergent cascade** | Retail FOMO without explicit "leader"     |
| Bubble peak          | GME squeeze (Jan 2021), Dot-com (2000)    |
| Crash                | Flash crash, position liquidation cascade |
