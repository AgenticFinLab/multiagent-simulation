# CurrencyCrisis — Scenario Target

## §1 Meta

| Field         | Content                                                |
|---------------|--------------------------------------------------------|
| Name          | CurrencyCrisis                                         |
| Domain        | finance                                                |
| Requested By  | a77                                                    |
| Produced By   | polish-simulation-pipeline.md (reverse-reconstruct)    |
| Created       | 2026-07-13                                             |
| Pipeline      | masim/skills/polish-simulation-pipeline.md             |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md       |
| Status        | released                                               |

## §2 Phenomenon Statement

### §2.1 Trigger

A currency crisis begins when speculative expectations of devaluation accumulate against a fixed exchange rate. The trigger is not necessarily a fundamental deterioration but rather a coordination shift: enough speculators come to believe that the central bank will be forced to abandon the peg, making their selling a rational bet.

### §2.2 Mechanism

The core mechanism is a self-fulfilling feedback loop: speculative selling weakens the currency, which depletes central bank reserves, which signals further weakness, which attracts more selling. Second-generation crisis models (Obstfeld 1996) show that multiple equilibria exist: the same fundamentals can sustain either a stable peg or a successful attack depending on market beliefs.

### §2.3 Participants

The causal participants are speculative attackers, self-fulfilling traders, central bank defenders, fundamental hedgers, and noise traders. Speculative attackers initiate reserve-depletion pressure. Self-fulfilling traders amplify by coordinating on the expectation of devaluation. Central bank defenders buy domestic currency using reserves. Fundamental hedgers provide mean-reversion anchoring. Noise traders add baseline liquidity.

### §2.4 Resolution

The crisis resolves either in peg collapse (attackers overwhelm reserves) or peg survival (defense and fundamental anchoring absorb selling pressure). Recovery speed depends on whether expectation coordination reverses after the attack phase.

## §3 Research Goals

1. Can self-fulfilling speculative dynamics force a peg collapse even when initial fundamentals are sound?
2. Does removing the SelfFulfillingTrader channel measurably reduce crisis depth (AII)?
3. How sensitive are peg survival duration and attack intensity to central bank reserve capacity?
4. Do Rule, LLM, RuleLLM, and Rag variants differ in crisis timing, depth, and recovery?
5. What is the amplification factor of expectation-coordination selling relative to initial speculative attack volume?

## §4 Theoretical Anchors

### §4.1 First-Generation Crisis Model (Reserve Depletion)

| Field | Content |
|-------|---------|
| Full citation | Krugman, P. (1979). A model of balance-of-payments crises. *Journal of Money, Credit and Banking*, 11(3), 311-325. https://doi.org/10.2307/1991793 |
| Key mechanism | Reserve depletion triggers speculative attack; fundamental unsustainability drives collapse. |
| Key equation | `qty(t) = order_size if deviation < -attack_threshold` |
| Motivates agent | speculative-attacker |
| Parameter implication | `attack_threshold` in [0.02, 0.05]; `order_size` in [400, 800]. |

### §4.2 Second-Generation Self-Fulfilling Crisis

| Field | Content |
|-------|---------|
| Full citation | Obstfeld, M. (1996). Models of currency crises with self-fulfilling features. *European Economic Review*, 40(3-5), 1037-1047. https://doi.org/10.1016/0014-2921(95)00111-5 |
| Key mechanism | Self-fulfilling expectations create multiple equilibria; coordinated selling makes devaluation inevitable. |
| Key equation | `qty(t) = order_size if deviation < -contagion_sensitivity` |
| Motivates agent | self-fulfilling-trader |
| Parameter implication | `contagion_sensitivity` in [0.005, 0.02]; `order_size` in [500, 900]. |

### §4.3 Global Games and Fundamental Thresholds

| Field | Content |
|-------|---------|
| Full citation | Morris, S., & Shin, H.S. (1998). Unique equilibrium in a model of self-fulfilling currency attacks. *American Economic Review*, 88(3), 587-597. https://www.jstor.org/stable/116850 |
| Key mechanism | Fundamental threshold determines whether attack succeeds; sound fundamentals anchor against self-fulfilling dynamics. |
| Key equation | `qty(t) = order_size if deviation < -hedge_ratio [buy]` |
| Motivates agent | fundamental-hedger |
| Parameter implication | `hedge_ratio` in [0.03, 0.08]. |

### §4.4 Empirical Crisis Indicators and Contagion

| Field | Content |
|-------|---------|
| Full citation | Eichengreen, B., Rose, A.K., & Wyplosz, C. (1995). Exchange market mayhem. *Economic Policy*, 10(21), 249-296. https://doi.org/10.2307/1344591 |
| Key mechanism | Exchange Market Pressure (EMP) index; contagion across currencies; empirical crisis severity benchmarks. |
| Key equation | EMP = weighted(exchange rate change, reserve change, interest rate change) |
| Motivates agent | (calibration targets for all agents) |
| Parameter implication | AII target [0.10, 0.25] from empirical EMP severity. |

### §4.5 Rational Contagion and Herding

| Field | Content |
|-------|---------|
| Full citation | Calvo, G.A., & Mendoza, E.G. (2000). Capital-markets crises and economic collapse in emerging markets. *American Economic Review*, 90(2), 59-64. https://doi.org/10.1257/aer.90.2.59 |
| Key mechanism | Rational contagion under information costs; herding behavior amplifies crisis. |
| Key equation | Herding multiplier on sell flow during crisis phase. |
| Motivates agent | self-fulfilling-trader (amplification channel) |
| Parameter implication | SFAF target [0.5, 1.5]. |

## §5 Stylized Facts

| # | Fact | Source | Acceptance metric |
|---|------|--------|-------------------|
| F1 | Currency crises produce 10-25% devaluations from peg | Eichengreen et al. (1995) | AII in [0.10, 0.25] |
| F2 | Central bank defense sustains peg for 15-30 rounds before breach | Obstfeld (1996) | PSD in [15, 30] |
| F3 | Self-fulfilling selling amplifies but does not dominate initial attack | Obstfeld (1996) | SFAF in [0.5, 1.5] |
| F4 | Fundamental anchoring activates during 50-80% of attack rounds | Morris & Shin (1998) | FAS in [0.5, 0.8] |
| F5 | Recovery from crisis trough takes 10-25 rounds | Calvo & Mendoza (2000) | RS in [10, 25] |

## §6 Historical / Empirical Anchors

| # | Event | Year | Key mechanism | Source |
|---|-------|------|---------------|--------|
| H1 | ERM/EMS Crisis (GBP, ITL) | 1992 | Soros coordinated attack; reserve depletion | Eichengreen et al. (1995) |
| H2 | Asian Currency Crisis (THB, IDR, MYR, KRW) | 1997 | Self-fulfilling expectations; contagion | Obstfeld (1996); Calvo & Mendoza (2000) |
| H3 | Mexican Peso Crisis (MXN) | 1994 | Reserve depletion; current account imbalance | Krugman (1979) |

## §7 Agent Roster

| # | Agent (kebab) | Theory family | Market role | Time horizon | Risk tolerance | Primary signals |
|---|---------------|---------------|-------------|--------------|----------------|-----------------|
| 1 | speculative-attacker | Krugman (1979) | Destabilizing | Short | High | deviation, attack_threshold |
| 2 | self-fulfilling-trader | Obstfeld (1996) | Destabilizing | Short | High | deviation, contagion_sensitivity |
| 3 | central-bank-defender | Central bank intervention | Stabilizing | Medium | Low | deviation, defense_threshold |
| 4 | fundamental-hedger | Morris & Shin (1998) | Stabilizing | Medium | Low | deviation, hedge_ratio |
| 5 | noise-trader | Black (1986) | Neutral | Random | Medium | trade_probability |

## §8 Environment Specification

### §8.1 Price Formation

```
P(t+1) = P(t) + lambda * D(t) + gamma * [F(t) - P(t)] + epsilon(t)
```

Where lambda = 0.01, gamma = 0.02, F(t) = 100.0 (peg level), epsilon ~ N(0, 0.5^2).

### §8.2 Information Broadcast

Market broadcasts: `{price, fundamental, deviation, round}`.

### §8.3 Constraints and Frictions

- Position constraints: sell limited by held position; buy limited by cash/price.
- Central bank reserve constraint: defense limited by initial_cash.
- Crisis threshold: deviation < -0.15 signals peg collapse.

### §8.4 Round Granularity

Single-step per round; Market perceive → all agents perceive/decide/act → Market aggregates next round.

## §9 Parameter Seeds

| # | Parameter | Belongs to | Default | Empirical range | Source citation |
|---|-----------|------------|---------|-----------------|----------------|
| 1 | initial_price | Market | 100.0 | normalization | Peg level |
| 2 | fundamental_value | Market | 100.0 | normalization | F(t) |
| 3 | price_impact (lambda) | Market | 0.01 | [0.005, 0.02] | FX market calibration |
| 4 | mean_reversion (gamma) | Market | 0.02 | [0.01, 0.05] | Weaker than equity |
| 5 | noise_std | Market | 0.5 | [0.2, 1.0] | FX volatility |
| 6 | attack_threshold | speculative-attacker | 0.03 | [0.02, 0.05] | Krugman (1979) |
| 7 | order_size | speculative-attacker | 600 | [400, 800] | Calibration |
| 8 | initial_position | speculative-attacker | 5000 | [3000, 7000] | Inventory |
| 9 | contagion_sensitivity | self-fulfilling-trader | 0.01 | [0.005, 0.02] | Obstfeld (1996) |
| 10 | order_size | self-fulfilling-trader | 700 | [500, 900] | Calibration |
| 11 | initial_position | self-fulfilling-trader | 5000 | [3000, 7000] | Inventory |
| 12 | defense_threshold | central-bank-defender | 0.05 | [0.03, 0.08] | Intervention lit. |
| 13 | order_size | central-bank-defender | 500 | [300, 700] | Calibration |
| 14 | initial_cash | central-bank-defender | 5000000 | [3M, 10M] | Reserve capacity |
| 15 | initial_position | central-bank-defender | 3000 | [2000, 5000] | Reserve inventory |
| 16 | hedge_ratio | fundamental-hedger | 0.05 | [0.03, 0.08] | Morris & Shin (1998) |
| 17 | order_size | fundamental-hedger | 400 | [200, 600] | Calibration |
| 18 | initial_position | fundamental-hedger | 2000 | [1000, 3000] | Hedge inventory |
| 19 | trade_probability | noise-trader | 0.3 | [0.2, 0.5] | Black (1986) |
| 20 | initial_position | noise-trader | 500 | [200, 1000] | Baseline inventory |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Notes |
|---------|--------|-------|
| Rule | Yes | Deterministic threshold baseline |
| LLM | Yes | Persona-only LLM agents |
| RuleLLM | Yes | Rule-anchored with LLM narration |
| Rag | Yes | RAG-augmented with FX crisis knowledge |

### §10.2 Pass / Fail Criteria

| # | Criterion | Target | Weight |
|---|-----------|--------|--------|
| 1 | Attack Intensity Index (AII) | [0.10, 0.25] | 0.30 |
| 2 | Peg Survival Duration (PSD) | [15, 30] rounds | 0.25 |
| 3 | Self-Fulfilling Amplification Factor (SFAF) | [0.5, 1.5] | 0.25 |
| 4 | Fundamental Anchor Strength (FAS) | [0.5, 0.8] | 0.20 |
