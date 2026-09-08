# AnchoringEffect — Experiment Progress

> **Default**: 200 rounds, 15 players, star topology, seed 42
> **Variants**: ☐ Rule · ☐ LLM · ☐ RuleLLM（Rag 暂不执行）
> **Agents 列**: = 1 Mkt + Σ(num_instances × 各 agent type)，即展开后的总玩家数

---

## Baseline

### Agent Inventory

| ID | Agent | ×N | Key Params | Source |
|----|-------|----|------------|--------|
| Mkt | Market | 1 | F=100, P₀=105, λ=0.01, γ=0.01, σ=0.5 | §3.1 |
| AT | Anchored Trader | 2 | α=0.3, b=20 | §4.1 |
| HA | Historical Anchor | 2 | w=0.5, lookback=60, b=20 | §4.2 |
| RU | Rational Updater | 1 | b=25 | §4.3 |
| MT | Momentum Trader | 2 | τ=0.02, b=20 | §4.4 |
| NT | Noise Trader | 2 | p=0.05, order 100–500 | §4.5 |
| DT | Disposition Trader | 2 | g=0.04, λ_LA=2.5, b=15 | §4.6 |
| CT | Contrarian Trader | 1 | lookback=10, τ_CT=0.05, b=20 | §4.7 |
| FA | Fundamental Analyst | 1 | η=0.05, b=25 | §4.8 |
| LP | Liquidity Provider | 1 | ema=20, h=0.015, b=30 | §4.9 |

---

## E0 — Baseline

| ID | Config Change | Rounds | Agents | Variants | Assignee |
|----|---------------|--------|--------|----------|----------|
| E01 | no change | 200 | 15 | ☐R ☐L ☐RL | Sijia |

---

## E1 — Agent Amplify（逐类型加倍 num_instances）

| ID | Config Change | Rounds | Agents | Variants | Assignee |
|----|---------------|--------|--------|----------|----------|
| E02 | AT ×2→×4 | 200 | 17 | ☐R ☐L ☐RL | Wenyou |
| E03 | AT ×2→×6 | 200 | 19 | ☐R ☐L ☐RL | Wenyou |
| E04 | HA ×2→×4 | 200 | 17 | ☐R ☐L ☐RL | Wenyou |
| E05 | HA ×2→×6 | 200 | 19 | ☐R ☐L ☐RL | Wenyou |
| E06 | RU ×1→×3 | 200 | 17 | ☐R ☐L ☐RL | Zihan |
| E07 | MT ×2→×4 | 200 | 17 | ☐R ☐L ☐RL | Zihan |
| E08 | MT ×2→×6 | 200 | 19 | ☐R ☐L ☐RL | Zihan |
| E09 | DT ×2→×4 | 200 | 17 | ☐R ☐L ☐RL | Ziqi |
| E10 | CT ×1→×3 | 200 | 17 | ☐R ☐L ☐RL | Ziqi |
| E11 | FA ×1→×3 | 200 | 17 | ☐R ☐L ☐RL | Ziqi |
| E12 | LP ×1→×3 | 200 | 17 | ☐R ☐L ☐RL | Ziqi |

---

## E2 — Mispricing（P₀ vs F=100 偏离度递增）

| ID | Config Change | Rounds | Agents | Variants | Assignee |
|----|---------------|--------|--------|----------|----------|
| E13 | P₀=108 (+8%) | 200 | 15 | ☐R ☐L ☐RL | Ziqi |
| E14 | P₀=110 (+10%) | 200 | 15 | ☐R ☐L ☐RL | Wenyou |
| E15 | P₀=115 (+15%) | 200 | 15 | ☐R ☐L ☐RL | Zihan |
| E16 | P₀=120 (+20%) | 200 | 15 | ☐R ☐L ☐RL | Ziqi |
| E17 | P₀=130 (+30%) | 200 | 15 | ☐R ☐L ☐RL | Ziqi |

---

## E3 — Time Scale（轮数递增）

| ID | Config Change | Rounds | Agents | Variants | Assignee |
|----|---------------|--------|--------|----------|----------|
| E18 | 400 rounds | 400 | 15 | ☐R ☐L ☐RL | Wenyou |
| E19 | 1000 rounds | 1000 | 15 | ☐R ☐L ☐RL | Zihan |
| E20 | 2000 rounds | 2000 | 15 | ☐R ☐L ☐RL | Wenyou |

---

## E4 — Scale（全部 agent 等比扩展）

| ID | Config Change | Rounds | Agents | Variants | Assignee |
|----|---------------|--------|--------|----------|----------|
| E21 | all ×2 | 200 | 25 | ☐R ☐L ☐RL | Wenyou |
| E22 | all ×4 | 200 | 50 | ☐R ☐L ☐RL | Zihan |
| E23 | all ×8 | 200 | 100 | ☐R ☐L ☐RL | Ziqi |

---

## E5 — Composite（多类型联合放大）

| ID | Config Change | Rounds | Agents | Variants | Assignee |
|----|---------------|--------|--------|----------|----------|
| E24 | AT×4 + HA×4 | 200 | 19 | ☐R ☐L ☐RL | Zihan |
| E25 | AT×6 + HA×6 | 200 | 23 | ☐R ☐L ☐RL | Zihan |
| E26 | MT×4 + DT×4 | 200 | 19 | ☐R ☐L ☐RL | Ziqi |
| E27 | AT×4 + MT×4 + DT×4 | 200 | 21 | ☐R ☐L ☐RL | Wenyou |
| E28 | RU×3 + FA×3 + CT×3 | 200 | 21 | ☐R ☐L ☐RL | Ziqi |
| E29 | RU×5 + FA×5 | 200 | 21 | ☐R ☐L ☐RL | Ziqi |
| E30 | AT×4 + RU×3 | 200 | 19 | ☐R ☐L ☐RL | Zihan |

---

## E6 — Topology

| ID | Config Change | Rounds | Agents | Variants | Assignee |
|----|---------------|--------|--------|----------|----------|
| E31 | star → full | 200 | 15 | ☐R ☐L ☐RL | Zihan |
