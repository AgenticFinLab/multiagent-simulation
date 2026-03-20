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

| Theory                  | Application                                                                          | Reference                                                                                                                                                                                 |
|-------------------------|--------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Momentum**            | MomentumInvestor: $P_{\text{bid}}=P(1+\lambda_m r)$, $Q=\beta_m r\cdot\text{Cash}/P$ | Jegadeesh, N. & Titman, S. (1993). *Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency*. Journal of Finance, 48(1), 65-91.                            |
| **Contrarian**          | ContrarianInvestor: $Q\propto(F-P)/P$                                                | De Bondt, W.F.M. & Thaler, R. (1985). *Does the Stock Market Overreact?* Journal of Finance, 40(3), 793-805.                                                                              |
| **Mean-Variance**       | RiskAverseInvestor: $Q\propto 1/\sigma^2$                                            | Markowitz, H. (1952). *Portfolio Selection*. Journal of Finance, 7(1), 77-91.                                                                                                             |
| **Noise Trader**        | NoiseTrader: $Q\sim\mathcal{N}(0,\sigma^2)$                                          | De Long, J.B., Shleifer, A., Summers, L.H. & Waldmann, R.J. (1990). *Noise Trader Risk in Financial Markets*. Journal of Political Economy, 98(4), 703-738.                               |
| **Positive Feedback**   | AggressiveInvestor: $Q=\beta_a r\cdot\text{Cash}/P+\delta a(t)$                      | Shiller, R.J. (1984). *Stock Prices and Social Dynamics*. Brookings Papers on Economic Activity, 1984(2), 457-510.                                                                        |
| **Information Cascade** | Emergent from agent interactions                                                     | Bikhchandani, S., Hirshleifer, D. & Welch, I. (1992). *A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades*. Journal of Political Economy, 100(5), 992-1026. |

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

### Notations

| Symbol                      | Meaning                                                                    |
|-----------------------------|----------------------------------------------------------------------------|
| $P(t)$                      | Market price at round $t$                                                  |
| $D(t)$                      | Net aggregate demand $=\sum_i Q_i(t)$                                      |
| $\lambda$                   | Price-impact / supply-elasticity coefficient (0.10)                        |
| $\gamma$                    | Walrasian tâtonnement speed toward fundamental (0.02)                      |
| $F$                         | Fundamental (intrinsic) value (100)                                        |
| $\varepsilon(t)$            | Microstructure noise $\sim\mathcal{N}(0,\,0.5^2)$                          |
| $r(t)$                      | Current-period return broadcast by market $=[P(t)-P(t-1)]/P(t-1)$          |
| $a(t)$                      | Price-acceleration signal $=[P(t)-P(t-1)]-[P(t-1)-P(t-2)]$                 |
| $\sigma^2(t)$               | Rolling variance of last $\text{lookback}$ prices                          |
| $N(t)$                      | Investor's current share position                                          |
| $\lambda_m$                 | Price-chasing intensity for MomentumInvestor (0.5)                         |
| $\kappa$                    | Price-chasing intensity for AggressiveInvestor (1.0)                       |
| $\beta_m, \beta_a, \beta_c$ | Capital-deployment fraction per agent type                                 |
| $\delta$                    | Acceleration bonus coefficient (`accel_bonus`)                             |
| $k$                         | Risk-tolerance constant for RiskAverseInvestor                             |
| $\rho$                      | Position mean-reversion coefficient for NoiseTrader                        |
| $\mathrm{CV}(t)$            | Coefficient of variation of bids: $\sigma_{\text{bids}}/\mu_{\text{bids}}$ |
| $\mathrm{DA}(t)$            | Directional agreement: $\lvert\sum_i\operatorname{sign}(Q_i)\rvert/N$      |
| $\mathrm{ICM}(t)$           | Information cascade measure: fraction of agents ignoring $F$               |

Price update (order-driven excess-demand model with mean reversion):

$$P(t+1) = P(t) + \lambda\cdot D(t) + \gamma\cdot[F - P(t)] + \varepsilon(t)$$

Steady-state equilibrium ($D=0$, $\varepsilon=0$):

$$P^* = F = 100$$

| Parameter             | Value  | Financial Meaning                         |
|-----------------------|--------|-------------------------------------------|
| λ (Supply Elasticity) | 0.1    | Higher = less liquid, more price impact   |
| γ (Mean Reversion)    | 0.02   | Speed of price correction to fundamentals |
| F (Fundamental)       | 100.0  | True intrinsic value                      |
| Initial Cash          | 10,000 | Per-investor starting capital             |
| Initial Position      | 0      | No initial holdings                       |

## Investor Strategies (5 Types - Emergent Model)

*See implementation*: `examples/HerdEffect/players.py`.

### 1. MomentumInvestor (⭐ Primary Positive Feedback)

Bid price and order quantity (*Implementation*: `MomentumInvestor.decide()`):

$$P_{\mathrm{bid}}(t) = P(t)\cdot(1 + \lambda_m\cdot r(t)), \qquad \lambda_m=0.5$$

$$Q_m(t) = \beta_m\cdot r(t)\cdot\frac{\text{Cash}(t)}{P_{\mathrm{bid}}(t)}, \qquad \beta_m=0.3$$

| Effect | **DESTABILIZING** — amplifies price trends, core herding driver |
| Risk | High — buys high, sells low |

### 2. AggressiveInvestor (⭐ Extreme Amplifier)

Price-acceleration signal and order quantity (*Implementation*: `AggressiveInvestor.decide()`):

$$a(t) = [P(t)-P(t-1)] - [P(t-1)-P(t-2)]$$

$$Q_a(t) = \beta_a\cdot r(t)\cdot\frac{\text{Cash}}{P_{\mathrm{bid}}(t)} + \delta\cdot a(t), \qquad \beta_a=0.5, \quad \delta=\text{accel\_bonus}$$

| Effect | **EXTREMELY DESTABILIZING** — leverage + price acceleration |
| Risk | Very High — can cause flash crashes |

### 3. ContrarianInvestor (Value Anchor)

(*Implementation*: `ContrarianInvestor.decide()`)

$$Q_c(t) = \beta_c\cdot\frac{F - P(t)}{P(t)}\cdot\frac{\text{Cash}}{P_{\mathrm{bid}}(t)}, \qquad \beta_c=0.5$$

| Effect | **STABILIZING** — dampens price deviations |
| Risk | Medium — may buy into falling knife |

### 4. RiskAverseInvestor (Early Exit Trigger)

(*Implementation*: `RiskAverseInvestor.decide()`)

Target position inversely proportional to variance; actual order is 30 % of position gap:

$$Q_r^{\text{target}}(t) = \frac{k}{\sigma^2(t)}\cdot\frac{\text{Cash}}{P(t)}, \qquad Q_r(t) = 0.3\cdot\bigl(Q_r^{\text{target}}(t) - N(t)\bigr)$$

| Effect | **EARLY EXIT** — reduces exposure when volatility spikes |
| Risk | Low — but may miss upside |

### 5. NoiseTrader (Random Trigger)

(*Implementation*: `NoiseTrader.decide()`)

$$P_{\mathrm{bid}}\sim\mathcal{N}(P(t),\,\sigma_{\text{price}}^2), \qquad Q_n\sim\mathcal{N}(0,\,\sigma_{\text{qty}}^2) - \rho\cdot N(t)$$

| Effect | **TRIGGER SOURCE** — random signal starts the cascade |
| Risk | Random — provides liquidity |

## Strategy Comparison (Emergent Model)

| Strategy       | Formula                                                 | Market Effect           | Risk      | Emergent Role   |
|----------------|---------------------------------------------------------|-------------------------|-----------|-----------------|
| **Momentum**   | $Q=\beta_m\,r\cdot\text{Cash}/P_{\text{bid}}$           | Destabilizing           | High      | ⭐ Core Feedback |
| **Aggressive** | $Q=\beta_a\,r\cdot\text{Cash}/P_{\text{bid}}+\delta\,a$ | Extremely Destabilizing | Very High | ⭐ Amplifier     |
| Contrarian     | $Q=\beta_c(F-P)/P\cdot\text{Cash}/P$                    | Stabilizing             | Medium    | Damper          |
| RiskAverse     | $Q=0.3(k/\sigma^2\cdot\text{Cash}/P - N)$               | Early Exit              | Low       | Crash Trigger   |
| **Noise**      | $Q\sim\mathcal{N}(0,\sigma_{\text{qty}}^2)-\rho N$      | Trigger/Liquidity       | Random    | ⭐ Initial Spark |

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

| Indicator                       | Formula                                                       | Description                                                   |
|---------------------------------|---------------------------------------------------------------|---------------------------------------------------------------|
| **Bid Convergence Index (CV)**  | $\mathrm{CV}(t)=\sigma_{\text{bids}}(t)/\mu_{\text{bids}}(t)$ | 出价变异系数，$\mathrm{CV}\downarrow$ = 行为趋同 = 羊群形成   |
| **Directional Agreement**       | $\mathrm{DA}(t)=\lvert\sum_i\operatorname{sign}(Q_i)\rvert/N$ | 方向一致性，$\mathrm{DA}>0.8$ = 强羊群                        |
| **Information Cascade Measure** | $\mathrm{ICM}(t)$ = 逆市交易者比例                            | 忽略私人信号跟随市场的比例，$\mathrm{ICM}\uparrow$ = 级联形成 |
| **Price Deviation**             | $\mathrm{PD}(t) = (P(t) - F) / F$                             | 价格偏离基本面程度                                            |
| **Rolling Volatility**          | $\sigma(\{P(t-w),\ldots,P(t)\})$                              | 波动率，泡沫期先升后降                                        |
| **Autocorrelation**             | $\mathrm{Corr}(r(t),\,r(t-k))$                                | 收益率自相关，$>0$ = 动量持续                                 |

### Expected Patterns in Emergent Herding

| Metric                | Normal Market | Herd Formation | Bubble Peak | Crash     |
|-----------------------|---------------|----------------|-------------|-----------|
| Bid CV                | 0.10-0.20     | **↓ < 0.05**   | < 0.03      | ↑ 0.15+   |
| Directional Agreement | 0.50-0.60     | **↑ > 0.80**   | > 0.90      | < 0.50    |
| Price Deviation       | ±5%           | **↑ 10-20%**   | > 25%       | ↓ rapidly |
| Volatility            | Low           | Rising         | **Peak**    | Spike     |

## Mathematical Foundations

### 1. Market Clearing — Price Update Equation

> **Source**: Walras (1874) [6] — tâtonnement process (price adjusts to clear excess demand); linear excess-demand model. *Implementation*: `examples/HerdEffect/players.py`, `Market.clear()`.

The order-driven price mechanism is a linear excess-demand model with mean reversion — Walrasian tâtonnement [6] (*Implementation*: `examples/HerdEffect/players.py`, `Market.clear()`):

$$P(t+1) = P(t) + \lambda\cdot D(t) + \gamma\cdot[F - P(t)] + \varepsilon(t)$$

> **What it does**: Price moves by $\lambda D(t)$ in the direction of net demand (positive = net buy pressure), weakly pulled toward fundamental $F$ at speed $\gamma=0.02$, plus microstructure noise $\varepsilon$. **Key property**: when $D(t)>0$ persistently (herding), $\gamma$ is too weak to prevent price from departing far from $F$. **Simulates**: Walrasian tâtonnement — the price gropes toward equilibrium through repeated demand-driven adjustments. Any persistent $D(t)>0$ (net buying pressure) drives price away from $F$, creating conditions for a herding cascade. The term $\gamma\cdot[F-P(t)]$ is the only restoring force.

---

### 2. MomentumInvestor — Positive Feedback Amplifier

> **Source**: Jegadeesh & Titman (1993) [1] — *Returns to Buying Winners and Selling Losers*: stocks with high recent returns continue outperforming. *Implementation*: `MomentumInvestor.decide()`.

Based on Jegadeesh & Titman (1993) [1] momentum strategy — stocks with high returns over the past 3–12 months tend to continue outperforming (*Implementation*: `MomentumInvestor.decide()`).

Bid price:

$$P_{\mathrm{bid}}(t) = P(t)\cdot\bigl(1 + \lambda_m\cdot r(t)\bigr), \qquad \lambda_m=0.5$$

> **What it does**: The MomentumInvestor bids above market when prices are rising ($r>0$) and below when falling ($r<0$). With $\lambda_m=0.5$, a $1\%$ price increase causes the investor to bid $0.5\%$ above the current price — "paying up" to get into a trend. **Simulates**: technical momentum traders who chase price trends.

Order quantity:

$$Q_m(t) = \beta_m\cdot r(t)\cdot\frac{\text{Cash}(t)}{P_{\mathrm{bid}}(t)}, \qquad \beta_m=0.3$$

> **What it does**: Order size scales with the return signal $r(t)$ and available capital. Positive feedback loop in net demand (using $r(t)\approx\lambda\cdot D(t-1)/P(t-1)$):

$$D_m(t) \approx 0.3\,\lambda\cdot D(t-1)\cdot\frac{\text{Cash}}{P^2}$$

> **What it does**: The demand from MomentumInvestors in round $t$ is proportional to demand in round $t-1$ — an autoregressive structure. When capital is large, this first-order AR process becomes explosive: a single noise-triggered spike in $D(t-1)$ causes a growing sequence $D(t), D(t+1), D(t+2)\ldots$ — the mechanism by which a small noise event triggers a cascade without any explicit imitation.

---

### 3. AggressiveInvestor — Acceleration + Leverage

> **Source**: Shiller (1984) [5] — *Stock Prices and Social Dynamics*: investors respond to the acceleration of price changes, not just their level. *Implementation*: `AggressiveInvestor.decide()`.

Extends momentum with a price-acceleration term — Shiller (1984) [5] social dynamics: investors respond to the acceleration of price changes, not just their level (*Implementation*: `AggressiveInvestor.decide()`):

$$a(t) = [P(t)-P(t-1)] - [P(t-1)-P(t-2)]$$

> **What it does**: Price acceleration — the second difference of prices. $a(t)>0$ means the price is increasing faster this round than last round (an accelerating trend). $a(t)<0$ means a decelerating trend. **Simulates**: Shiller's observation that investors don't just react to price levels or even returns, but to the **velocity of change** in those returns — an accelerating rally creates disproportionate excitement and buying.

$$Q_a(t) = \beta_a\cdot r(t)\cdot\frac{\text{Cash}}{P_{\mathrm{bid}}(t)} + \delta\cdot a(t), \qquad \beta_a=0.5,\quad \delta=\text{accel\_bonus}$$

> **What it does**: Total order = momentum component (like MomentumInvestor but larger $\beta_a=0.5$) + acceleration bonus. When both $r>0$ and $a>0$ (rising and accelerating), orders are superlinear.

Amplification ratio relative to MomentumInvestor (ignoring acceleration term):

$$\frac{Q_a}{Q_m} \approx \frac{\beta_a}{\beta_m} = \frac{0.5}{0.3} \approx 1.67$$

> **What it does**: Even without the acceleration bonus, AggressiveInvestor trades 67% more than MomentumInvestor on the same signal. When $a(t)>0$ (accelerating trend), total $Q_a > 1.67\,Q_m$ — the superlinear amplification that drives the exponential phase of the bubble.

---

### 4. ContrarianInvestor — Value Anchor (Mean-Reversion Force)

> **Source**: De Bondt & Thaler (1985) [2] — *Does the Stock Market Overreact?* — contrarian investing exploits overreaction. *Implementation*: `ContrarianInvestor.decide()`.

De Bondt & Thaler (1985) [2] contrarian investing — overreaction to news creates mean-reverting price patterns that contrarians exploit (*Implementation*: `ContrarianInvestor.decide()`):

$$Q_c(t) = \beta_c\cdot\frac{F - P(t)}{P(t)}\cdot\frac{\text{Cash}}{P(t)}, \qquad \beta_c=0.5$$

> **What it does**: Buys when $P<F$ (undervalued) and sells when $P>F$ (overvalued), with order size scaling with the deviation. Provides a restoring force toward the fundamental.

Restoring force per unit price deviation:

$$\frac{\partial Q_c}{\partial(P-F)} = -\frac{\beta_c\cdot\text{Cash}}{P^2} < 0$$

> **What it does**: A linear restoring force (analogous to a spring) that pushes price back toward $F$. **Critical limitation**: when overwhelmed by Momentum + Aggressive combined capital, it cannot prevent the cascade. **Simulates**: De Bondt & Thaler's finding that while contrarians eventually profit, the correction is slow — markets can remain irrational long enough to make contrarians question their position.

---

### 5. RiskAverseInvestor — Volatility-Scaled Position

> **Source**: Markowitz (1952) [3] — *Portfolio Selection*: mean-variance framework where optimal allocation decreases as variance increases. *Implementation*: `RiskAverseInvestor.decide()`.

Markowitz (1952) [3] mean-variance framework — optimal portfolio allocates less to an asset as its variance increases (*Implementation*: `RiskAverseInvestor.decide()`):

Target quantity (inversely proportional to variance):

$$Q_r^{\text{target}}(t) = \frac{k}{\sigma^2(t)}\cdot\frac{\text{Cash}}{P(t)}, \qquad k=\text{risk tolerance}$$

> **What it does**: The ideal position size is $\propto 1/\sigma^2$ — doubling variance halves the optimal position. This is directly from Markowitz's mean-variance optimization: for a given expected return, the optimal allocation to a risky asset scales inversely with its variance.

Actual order (gradual 30 % adjustment toward target):

$$Q_r(t) = 0.3\cdot\bigl(Q_r^{\text{target}}(t) - N(t)\bigr)$$

> **What it does**: Implements partial rebalancing — 30% of the gap per round. **Key effect**: as $\sigma^2\to\infty$ at bubble peak, $Q_r^{\text{target}}\to 0$, so the investor sells down. This endogenous withdrawal at peak volatility acts as the crash trigger — net demand suddenly collapses, reversing positive to negative feedback. **Simulates**: the empirical pattern where risk-parity and volatility-targeting funds simultaneously reduce exposure at bubble peaks, converting the bubble's implosion from gradual to sudden.

---

### 6. NoiseTrader — Stochastic Trigger

> **Source**: De Long, Shleifer, Summers & Waldmann (1990) [4] — *Noise Trader Risk in Financial Markets*: noise traders create unpredictable price fluctuations that rational arbitrageurs cannot always offset. *Implementation*: `NoiseTrader.decide()`.

De Long et al. (1990) [4] — noise traders create unpredictable, self-fulfilling price fluctuations that rational arbitrageurs cannot always offset (*Implementation*: `NoiseTrader.decide()`):

$$P_{\mathrm{bid}}\sim\mathcal{N}(P(t),\,\sigma_{\text{price}}^2), \qquad Q_n\sim\mathcal{N}(0,\,\sigma_{\text{qty}}^2) - \rho\cdot N(t)$$

> **What it does**: Both bid price and order quantity are random. The $-\rho\cdot N(t)$ term provides weak position mean-reversion (prevents the noise trader accumulating a runaway position). **Simulates**: De Long et al.'s noise trader who submits orders based on random sentiment rather than information — unpredictable enough to periodically trigger momentum signals.

where $\sigma_{\text{price}}$ = `price_noise_std`, $\sigma_{\text{qty}}$ = `qty_noise_std`, and $\rho$ = `position_mean_reversion` provides a weak mean-reversion in position size.

Trigger probability per round (for a large noise event $|Q_n|>\sigma_{\text{qty}}$, using default $\sigma_{\text{qty}}=5$):

$$P\bigl(|Q_n|>5\bigr) = 2\bigl[1-\Phi(1)\bigr] \approx 31.7\%$$

> **What it does**: On average, a noise trade large enough to trigger a cascade occurs every $\sim3$ rounds. **Effect**: the simulation never stays in equilibrium for long — the frequent large noise events ensure that momentum traders are regularly presented with spurious signals, making emergent cascades a near-certainty over 50 rounds.

---

### 7. Emergent Information Cascade — Bikhchandani-Hirshleifer-Welch (1992) [7]

> **Source**: Bikhchandani, Hirshleifer & Welch (1992) [7] — *A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades*.

Cascade condition (positive feedback exceeds stabilising forces):

$$D_m(t) + D_a(t) > \bigl|D_c(t)\bigr| + \bigl|D_r(t)\bigr|$$

> **What it does**: The tipping condition for an emergent cascade. When total momentum/aggressive buying exceeds the combined contrarian and risk-averse selling, net demand becomes self-sustaining positive — prices accelerate away from fundamentals. **Simulates**: Bikhchandani et al.'s cascade theory, but without explicit imitation: the cascade emerges purely from the capital weights of agents on each side.

Substituting agent formulas:

$$\frac{[0.3\cdot r\cdot W_m + 0.5\cdot r\cdot W_a]}{P} > \frac{0.5(P-F)\cdot W_c}{P^2} + \frac{k\cdot W_r}{\sigma^2\cdot P}$$

> **What it does**: Expresses the cascade condition in terms of agent parameters and capital. The left side (destabilizing) grows $\propto r$ while the right side (stabilizing) grows $\propto(P-F)$. Since $r$ can be large during a cascade while $P-F$ starts small, the left side initially dominates, making the cascade self-sustaining once started.

---

### 8. Emergent Herding Strength — Bid Convergence Mathematics

> **Source**: Bikhchandani et al. (1992) [7]; standard econometric measures of herding behavior.

Coefficient of Variation of investor bids:

$$\mathrm{CV}(t) = \frac{\sigma_{\mathrm{bids}}(t)}{\mu_{\mathrm{bids}}(t)}$$

> **What it does**: CV measures the dispersion of bid prices relative to their mean. **Herding signal**: when all agents converge to bid near the same price (chasing the trend), CV $\to0$. In normal markets, agents have heterogeneous bids (CV $\approx0.15$–0.20). A drop in CV is the quantitative signature of emergent herding — agents behave more similarly without any explicit coordination.

Information Cascade Measure:

$$\mathrm{ICM}(t) = \frac{\#\{\text{agents bidding above }F\text{ when }P>F\}}{N}$$

> **What it does**: Counts what fraction of agents are ignoring the fundamental signal and instead bidding into an overvalued market. ICM $\to1$ means all agents have joined the cascade — the information content of the fundamental $F$ has been completely overwhelmed by price-trend signals. **Simulates**: Bikhchandani et al.'s definition of a cascade: individuals abandon their private information and follow the crowd.

Directional Agreement (correlated order flow):

$$\mathrm{DA}(t) = \frac{\left|\displaystyle\sum_i \operatorname{sign}(Q_i(t))\right|}{N}$$

> **What it does**: Measures correlated order flow. DA $=1$ means all agents are on the same side (all buying or all selling) — the maximum herding state. DA $=0.5$ is the random baseline. DA $>0.8$ is the criterion for confirming the emergent herd. **Simulates**: the empirical herding measure developed in the literature, applied here to an agent simulation to test whether emergent behavior (without explicit imitators) produces the same correlated order flow as explicit herding models.

---

## Real-World Mapping

| Simulation           | Real-World Example                        |
|----------------------|-------------------------------------------|
| Noise triggers       | Unexpected news, social media buzz        |
| Momentum amplifies   | Technical traders follow breakout         |
| **Emergent cascade** | Retail FOMO without explicit "leader"     |
| Bubble peak          | GME squeeze (Jan 2021), Dot-com (2000)    |
| Crash                | Flash crash, position liquidation cascade |

## References

\[1\] Jegadeesh, N. & Titman, S. (1993). *Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency*. Journal of Finance, 48(1), 65–91.

\[2\] De Bondt, W.F.M. & Thaler, R. (1985). *Does the Stock Market Overreact?* Journal of Finance, 40(3), 793–805.

\[3\] Markowitz, H. (1952). *Portfolio Selection*. Journal of Finance, 7(1), 77–91.

\[4\] De Long, J.B., Shleifer, A., Summers, L.H. & Waldmann, R.J. (1990). *Noise Trader Risk in Financial Markets*. Journal of Political Economy, 98(4), 703–738.

\[5\] Shiller, R.J. (1984). *Stock Prices and Social Dynamics*. Brookings Papers on Economic Activity, 1984(2), 457–510.

\[6\] Walras, L. (1874). *Éléments d'économie politique pure*. Corbaz (trad. W. Jaffé as *Elements of Pure Economics*, 1954).

\[7\] Bikhchandani, S., Hirshleifer, D. & Welch, I. (1992). *A Theory of Fads, Fashion, Custom, and Cultural Change as Informational Cascades*. Journal of Political Economy, 100(5), 992–1026.
