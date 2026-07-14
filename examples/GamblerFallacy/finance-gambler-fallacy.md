# GamblerFallacy

## §0 Meta CHANGELOG

- 2026-07-22  Polish Round 2 re-audit — all gates green (re-audit on Round-1-polished artefacts). Preflight: scenario tree intact; `finance-gambler-fallacy.md` §1 Status = `released`. Step 0 target-file re-audit: §1–§10 canonical structure PASS, 5 §4 theory anchors with resolvable DOIs PASS (Tversky-Kahneman 1971 `10.1037/h0031322`; Gilovich-Vallone-Tversky 1985 `10.1016/0010-0285(85)90010-6`; Rabin 2002 `10.1162/003355302760193896`; Shleifer-Vishny 1997 `10.1111/j.1540-6261.1997.tb03807.x`; Black 1986 `10.1111/j.1540-6261.1986.tb04513.x`), §5 F1–F4 acceptance metrics resolve to `analysis.py` surface, §7 five agent rows aligned to §4 theories, §9 12-row parameter grid unchanged, §10.1 four-variant `Yes` marks unchanged. Step 1 research: 5 DOIs unchanged and matching Round 1 verifications; §2 Theory blocks bidirectional with §4 (5↔5). Step 2 agent+env: rank-precedence PASS on 5 archetypes (StreakReversalTrader/HotHandTrader/IndependentAssessor/Arbitrageur/NoiseTrader), icon-four-check gate PASS (5/5 profiles have Icon rows, 5/5 PNGs present at `agent_images/icons/finance-{stem}.png`, 5/5 mapping rows in `agent_images/design.md` — rows #14, #104–#107), structural framework + environment + diversity + communication PASS. Step 3 config: 16 YAMLs parse via `yaml.safe_load`; `# Source:` traceability PASS; §9-authority PASS with 12/12 numeric defaults matching target; four `configs/GamblerFallacy/{V}/` folders present. Step 4 impl: py_compile PASS on all 4 variants × {players.py, analysis.py, prompts.py, run_*.py}; import smoke PASS (`import examples.GamblerFallacy.{Rule,LLM,RuleLLM,Rag}.players`); no-defaults PASS; RuleLLM dual-section invariant PASS; `_RAG_FALLBACK` sentinel present in `Rag/players.py`; `explain.md` §2 bidirectional 5↔5 PASS all four variants; `analysis.md` §2 bidirectional PASS. Steps 5-10 smoke: Rule 5-round end-to-end via `GeneralSimulator.setup()+run()+shutdown()` completes with 8 actors (1 Market + 7 investors: `rule_streak_reversal_trader_{1,2}`, `rule_hot_hand_trader_{1,2}`, `rule_independent_assessor`, `rule_arbitrageur`, `rule_noise_trader`) and no exception; LLM/RuleLLM/Rag setup-only smokes complete cleanly. Round 2 Closeout: no regression detected, no repair needed. Status confirmed `released`.
- 2026-07-22  Polish Round 1 Closeout (traceability + status). Traceability matrix resolved: `simulation-bases.md §1 Phenomenon` → target §2 + §6; `simulation-bases.md §2 Theory` → target §4 (5↔5); `simulation-bases.md §3 Environment` → target §5 + §8; `simulation-bases.md §4.{1..5} Agent blocks` → target §7 rows + §4 theories; `simulation-bases.md §5 Diversity` → target §7; `simulation-bases.md §6 Parameter Table` → target §9; `simulation-bases.md §7 Communication` → target §8; `analysis-bases.md §1 Objectives` → target §3; `analysis-bases.md §2 Metrics` → target §10.2; `configs/GamblerFallacy/{V}/players.yml extras` → target §9; variant classes → `simulation-bases.md §4.{N}` via `explain.md §2`; variant analysis functions → `analysis-bases.md §2` via `analysis.md §2`; `AGENT_POOL/finance/{streak-reversal-trader,hot-hand-trader,independent-assessor,arbitrageur,noise-trader}.md` → target §7 rows + §3.11 Provenance. Step 2 icon-resolution HARD GATE satisfied: 4 missing PNGs generated (`finance-streak-reversal-trader.png`, `finance-hot-hand-trader.png`, `finance-independent-assessor.png`, `finance-arbitrageur.png`), 4 mapping rows (#104–#107) added to `agent_images/design.md`, all 5 pool profiles confirmed Icon rows present. Step 4 HARD GATE: py_compile + import smoke PASS all 4 variants (Rule/LLM/RuleLLM/Rag). Steps 5-10 smoke: Rule 5-round e2e PASS via `GeneralSimulator`, LLM/RuleLLM/Rag setup-only PASS. Status walked `locked → released`.

## §1 Meta

| Field       | Content                                                                                                                                                                                                |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name        | GamblerFallacy                                                                                                                                                                                         |
| Domain      | finance                                                                                                                                                                                                |
| Phenomenon  | Streak-conditioned trading: gambler's-fallacy reversal traders and hot-hand extrapolators react to the same deviation signal, producing return-predictability patterns bounded by limits-to-arbitrage. |
| Pipeline    | masim/skills/create-simulation-pipeline.md                                                                                                                                                             |
| Target Spec | masim/skills/define-simulation-scenario-skill.md (v1.0)                                                                                                                                                |
| Status      | released                                                                                                                                                                                               |

## §2 Phenomenon Statement

### §2.1 Trigger

The scenario begins with a market at fundamental value and a small stochastic perturbation that produces a positive or negative deviation. Because the deviation persists for at least a few rounds, it acts as a proxy streak signal that activates two behaviourally biased populations — streak-reversal traders and hot-hand traders — while rational agents remain inactive below their higher activation threshold.

### §2.2 Mechanism

The core mechanism is streak-conditioned mispricing. Once `|deviation|` exceeds the biased-agent activation threshold, streak-reversal traders and hot-hand traders both trade with the sign of the deviation (they buy on positive deviation and sell on negative deviation) but rationalize the trade in opposite ways: reversal traders are betting on an overdue reversal, hot-hand traders are extrapolating continuation. Their combined co-directional pressure amplifies the deviation until rational agents (independent-assessor, arbitrageur) cross their own threshold and fade the mispricing, subject to a capacity cap consistent with limits to arbitrage.

### §2.3 Participants

The causally relevant participants are streak-reversal traders, hot-hand traders, independent-assessors, arbitrageurs, and noise traders. Biased traders amplify streaks; rational agents fade extreme deviations with limited capacity; noise traders provide baseline liquidity and produce the small stochastic perturbations that seed perceived streaks. The market coordinator aggregates orders and updates the price.

### §2.4 Resolution

The deviation reverts toward fundamental when rational-agent capacity relative to biased-agent flow becomes large enough to dominate, or when the mean-reversion coefficient in the price formation model pulls price back into a range below the biased-agent activation threshold. Because rational agents are capped at a smaller per-round order size than biased agents, resolution is gradual rather than immediate, matching the empirical persistence of momentum and reversal effects.

## §3 Research Goals

1. Measure whether streak-conditioned biased trading produces short-horizon return autocorrelation consistent with Jegadeesh-Titman-scale momentum and eventual reversal.
2. Test by ablation whether removing either the streak-reversal or hot-hand agent materially changes the amplitude and persistence of deviations from fundamental.
3. Sweep the biased-agent `activation_threshold`, `quantity_scale`, and `max_order` alongside the rational-agent `activation_threshold` to characterize when limits to arbitrage allow the phenomenon to persist.
4. Compare Rule, LLM, RuleLLM, and Rag variants to see whether persona reasoning or retrieved streak-behavior literature reduces streak-following intensity.

## §4 Theoretical Anchors

### §4.1 Law of small numbers and gambler's fallacy

| Field                     | Content                                                                                                                                                                    |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Tversky, A., & Kahneman, D. (1971). Belief in the law of small numbers. *Psychological Bulletin*, 76(2), 105-110. https://doi.org/10.1037/h0031322                         |
| Key mechanism (≤30 words) | Agents believe short random sequences should reflect the long-run distribution, generating reversal beliefs after streaks that show up in trading behavior as fade orders. |
| Key equation              | Order direction follows the sign of `deviation` when `abs(deviation) > activation_threshold`; interpreted as an overdue-reversal bet.                                      |
| Motivates agent           | streak-reversal-trader                                                                                                                                                     |
| Parameter implication     | `activation_threshold` 0.01-0.05 with candidate default 0.02, `quantity_scale` 3000-8000, `max_order` 500-1000 in §9.                                                      |

### §4.2 Hot-hand fallacy and momentum belief

| Field                     | Content                                                                                                                                                                                                     |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Gilovich, T., Vallone, R., & Tversky, A. (1985). The hot hand in basketball: On the misperception of random sequences. *Cognitive Psychology*, 17(3), 295-314. https://doi.org/10.1016/0010-0285(85)90010-6 |
| Key mechanism (≤30 words) | Agents extrapolate that a recent streak of price moves will continue and buy or sell in the direction of the streak, reinforcing the deviation from fundamental.                                            |
| Key equation              | Buy when `deviation > activation_threshold`; sell when `deviation < -activation_threshold`; quantity scales with `abs(deviation) * quantity_scale` capped by `max_order`.                                   |
| Motivates agent           | hot-hand-trader                                                                                                                                                                                             |
| Parameter implication     | `activation_threshold` 0.01-0.05 with candidate default 0.02, `quantity_scale` 3000-8000, `max_order` 500-1000 in §9.                                                                                       |

### §4.3 Rational streak assessment

| Field                     | Content                                                                                                                                                                            |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Rabin, M. (2002). Inference by believers in the law of small numbers. *Quarterly Journal of Economics*, 117(3), 775-816. https://doi.org/10.1162/003355302760193896                |
| Key mechanism (≤30 words) | An agent that correctly treats price moves as independent trades against the direction of large deviations, but only above a stricter activation threshold than the biased agents. |
| Key equation              | Buy when `deviation < -activation_threshold_rational`; sell when `deviation > activation_threshold_rational`; quantity capped by rational-agent `max_order`.                       |
| Motivates agent           | independent-assessor                                                                                                                                                               |
| Parameter implication     | Rational `activation_threshold` 0.03-0.10 with candidate default 0.05, `max_order` 300-800 with candidate default 500 in §9.                                                       |

### §4.4 Limits to arbitrage against streak-based mispricing

| Field                     | Content                                                                                                                                                                             |
|---------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Shleifer, A., & Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55. https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                               |
| Key mechanism (≤30 words) | A dedicated arbitrageur fades streak-based mispricing but must operate under a capacity cap smaller than biased-agent flow, so mispricing corrects gradually rather than instantly. |
| Key equation              | Same contrarian rule as independent-assessor but conceptually represents dedicated capital; both share `max_order` at the rational cap.                                             |
| Motivates agent           | arbitrageur                                                                                                                                                                         |
| Parameter implication     | Rational-agent `max_order` 300-800 (≈ 60% of biased-agent cap) in §9, matching Pontiff (2006) idiosyncratic-variance capacity reduction.                                            |

### §4.5 Noise and background microstructure

| Field                     | Content                                                                                                                                  |
|---------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| Full citation             | Black, F. (1986). Noise. *Journal of Finance*, 41(3), 529-543. https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                        |
| Key mechanism (≤30 words) | Random uninformed order flow provides baseline liquidity and creates the short-run perturbations that biased agents perceive as streaks. |
| Key equation              | `trade ~ Bernoulli(trade_probability)` with direction uniform and quantity drawn from `[min_order, max_order]`.                          |
| Motivates agent           | noise-trader                                                                                                                             |
| Parameter implication     | `trade_probability` 0.1-0.5 with candidate default 0.3, `min_order` 50-200, `max_order` 300-800 in §9.                                   |

## §5 Stylized Facts

| #  | Fact (one sentence)                                                                                   | Quantitative range                 | Citation                                                                      | Acceptance metric                                             |
|----|-------------------------------------------------------------------------------------------------------|------------------------------------|-------------------------------------------------------------------------------|---------------------------------------------------------------|
| F1 | The index exhibits short-horizon positive return autocorrelation during momentum episodes.            | AC1 in [0.10, 0.60]                | Jegadeesh & Titman (1993), https://doi.org/10.1111/j.1540-6261.1993.tb04702.x | `analysis.py: _compute_autocorrelation()` in [0.10, 0.60]     |
| F2 | Absolute deviations exceed the biased activation threshold for a nontrivial share of rounds.          | active-round share in [0.20, 0.80] | Croson & Sundali (2005), https://doi.org/10.1287/mnsc.1040.0312               | `analysis.py: _compute_biased_active_share()` in [0.20, 0.80] |
| F3 | Biased-agent order flow dominates during high-deviation rounds.                                       | biased share of volume >= 0.50     | Bloomfield, O'Hara, & Saar (2009), https://doi.org/10.1093/rfs/hhn044         | `analysis.py: agent_vwap` biased share >= 0.50                |
| F4 | Rational-agent flow becomes dominant only at extreme deviations, consistent with limits-to-arbitrage. | rational-share cross at `          | deviation                                                                     | ` in [0.05, 0.10]                                             |

## §6 Historical / Empirical Anchors

### §6.1 Jegadeesh-Titman short-horizon momentum

| Field             | Content                                                                                                                                                           |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Cross-sectional momentum on US NYSE/AMEX equities, 1965-1989.                                                                                                     |
| Trigger           | Past-return signals over 3-12 months produced statistically significant continuation of returns in the next 3-12 months.                                          |
| Quantitative arc  | 12-month formation, 3-month holding: approximately 1.01% average monthly return; momentum reverses at 3-5 year horizons.                                          |
| Agent mapping     | hot-hand-trader maps to short-horizon momentum extrapolation; streak-reversal-trader maps to long-horizon reversal beliefs; arbitrageur maps to constrained fade. |
| Primary source(s) | Jegadeesh, N., & Titman, S. (1993). *Journal of Finance*, 48(1), 65-91. https://doi.org/10.1111/j.1540-6261.1993.tb04702.x                                        |

### §6.2 Croson-Sundali casino field evidence

| Field             | Content                                                                                                                                         |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| Name + dates      | Field study of roulette players in Atlantic City casinos, 2005.                                                                                 |
| Trigger           | Streaks of three or more same-color outcomes reliably shifted bets against continuation, matching gambler's fallacy predictions.                |
| Quantitative arc  | About 8% probability distortion after streaks of 3+; roughly 73% of players exhibited gambler's fallacy at some point in a session.             |
| Agent mapping     | streak-reversal-trader maps to the majority of biased players; independent-assessor maps to the minority that treated each spin as independent. |
| Primary source(s) | Croson, R., & Sundali, J. (2005). *Management Science*, 51(1), 58-69. https://doi.org/10.1287/mnsc.1040.0312                                    |

## §7 Agent Roster

| Agent name (kebab)     | Real-world counterpart               | Theory family (§4 anchor)                   | Domain role       | Primary signals               | Intent line                                                                       | Expected pool match                                   |
|------------------------|--------------------------------------|---------------------------------------------|-------------------|-------------------------------|-----------------------------------------------------------------------------------|-------------------------------------------------------|
| streak-reversal-trader | retail investor with reversal bias   | Behavioural / Gambler's fallacy (§4.1)      | Destabilising     | price, fundamental, deviation | Exists to trade in the sign of deviation while rationalizing an overdue reversal. | examples/AGENT_POOL/finance/streak-reversal-trader.md |
| hot-hand-trader        | momentum-chasing retail investor     | Behavioural / Hot-hand extrapolation (§4.2) | Destabilising     | price, fundamental, deviation | Exists to extrapolate streaks and buy or sell in the direction of the deviation.  | examples/AGENT_POOL/finance/hot-hand-trader.md        |
| independent-assessor   | quantitative rational investor       | Rational Streak Assessment (§4.3)           | Stabilising       | price, fundamental, deviation | Exists to fade large deviations from fundamental with limited capacity.           | examples/AGENT_POOL/finance/independent-assessor.md   |
| arbitrageur            | dedicated statistical arbitrage desk | Limits to arbitrage (§4.4)                  | Stabilising       | price, fundamental, deviation | Exists to exploit streak-based mispricing subject to a per-round capacity cap.    | examples/AGENT_POOL/finance/arbitrageur.md            |
| noise-trader           | uninformed retail order flow         | Noise / Liquidity-providing noise (§4.5)    | Context-dependent | price, round, rng_state       | Exists to supply Bernoulli-timed random order flow.                               | examples/AGENT_POOL/finance/noise-trader.md           |

## §8 Environment Specification

### §8.1 Price Formation

The environment is a single-price index market. Price follows `P(t+1) = P(t) + lambda * D(t) + gamma * [F - P(t)] + epsilon(t)`, where `D(t)` is buy quantity minus sell quantity. The price-impact coefficient is moderate and mean reversion is small, allowing biased-agent flow to sustain short-horizon deviations that the rational agents then fade.

### §8.2 Information Broadcast

Each round broadcasts `price`, `fundamental`, `deviation`, and `round`. These signals are sufficient for the deviation-threshold triggers used by biased and rational agents; the current-deviation acts as the streak proxy in the simplified encoding.

### §8.3 Constraints and Frictions

There is no circuit breaker. Agents are constrained by cash, inventory, per-round `max_order`, and `quantity_scale`. Biased agents have a larger `max_order` (up to 800) than rational agents (up to 500), reflecting the Pontiff (2006) capacity ratio for arbitrage against noise-trader risk.

### §8.4 Round Granularity

One round represents approximately one trading day, matching the daily frequency at which gambler's-fallacy and hot-hand patterns have been documented in financial markets (PEAD, lottery data).

## §9 Parameter Seeds

| Parameter                     | Symbol    | Belongs to (agent / environment)             | Empirical range       | Candidate default | Source citation                                                                                   |
|-------------------------------|-----------|----------------------------------------------|-----------------------|-------------------|---------------------------------------------------------------------------------------------------|
| biased activation threshold   | `theta_b` | streak-reversal-trader, hot-hand-trader (§7) | 0.01-0.05             | 0.02              | Croson & Sundali (2005), https://doi.org/10.1287/mnsc.1040.0312                                   |
| biased quantity scale         | `s_b`     | streak-reversal-trader, hot-hand-trader (§7) | 3000-8000             | 5000              | Calibrated                                                                                        |
| biased max order              | `q_b`     | streak-reversal-trader, hot-hand-trader (§7) | 500-1000              | 800               | Pontiff (2006), https://doi.org/10.1016/j.jfineco.2005.10.002                                     |
| rational activation threshold | `theta_r` | independent-assessor, arbitrageur (§7)       | 0.03-0.10             | 0.05              | Shleifer & Vishny (1997), https://doi.org/10.1111/j.1540-6261.1997.tb03807.x                      |
| rational quantity scale       | `s_r`     | independent-assessor, arbitrageur (§7)       | 2000-5000             | 3000              | Calibrated                                                                                        |
| rational max order            | `q_r`     | independent-assessor, arbitrageur (§7)       | 300-800               | 500               | Pontiff (2006), https://doi.org/10.1016/j.jfineco.2005.10.002                                     |
| noise trade probability       | `p_n`     | noise-trader (§7)                            | 0.1-0.5               | 0.3               | Black (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                                  |
| noise min order               | `q_min_n` | noise-trader (§7)                            | 50-200                | 100               | Normalization                                                                                     |
| noise max order               | `q_max_n` | noise-trader (§7)                            | 300-800               | 500               | Pontiff (2006), https://doi.org/10.1016/j.jfineco.2005.10.002                                     |
| price impact                  | `lambda`  | environment (§8.1)                           | 0.01-0.10             | 0.05              | LeBaron (2006), *Agent-based computational finance*, in Handbook of Computational Economics vol 2 |
| mean reversion                | `gamma`   | environment (§8.1)                           | 0.01-0.15             | 0.02              | Summers (1986), https://doi.org/10.1111/j.1540-6261.1986.tb04513.x                                |
| noise std                     | `sigma`   | environment (§8.1)                           | 0.005-0.05            | 0.01              | Shiller (1981), https://doi.org/10.2307/1802789                                                   |
| fundamental value             | `F`       | environment (§8.1)                           | Source: normalization | 100.0             | Source: normalization                                                                             |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Rationale (≤1 sentence)                                                                                        |
|---------|--------|----------------------------------------------------------------------------------------------------------------|
| Rule    | Yes    | Required deterministic baseline for streak-conditioned trading with limits to arbitrage.                       |
| LLM     | Yes    | Tests whether persona reasoning modifies the frequency or size of biased-agent activation.                     |
| RuleLLM | Yes    | Tests whether explicit rule prompts preserve streak-conditioned dynamics under model reasoning.                |
| Rag     | Yes    | Tests whether retrieved streak-behavior literature (Tversky-Kahneman 1971, Rabin 2002) dampens the phenomenon. |

### §10.2 Pass / Fail Criteria

| Criterion                                                            | Status when satisfied |
|----------------------------------------------------------------------|-----------------------|
| All §5 stylized facts reproduced within their ranges                 | green                 |
| Every §3 research question answerable from analysis                  | green                 |
| Ablating any §7 agent produces a measurable change                   | green                 |
| All variants marked `Yes` in §10.1 build without uncaught exceptions | green                 |
