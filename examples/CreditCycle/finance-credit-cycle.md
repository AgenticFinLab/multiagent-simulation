# CreditCycle — Scenario Target

## §0 Meta CHANGELOG

- 2026-07-13  Polish target-file gate (Case B): target file reverse-reconstructed from existing artefacts (simulation-bases.md, analysis-bases.md, configs/, variant implementations). Status set to `locked` for audit.
- 2026-07-13  Polish Step 1 audit (research). DOI-resolution PASS: Geanakoplos 2010 `10.1086/648285`, Adrian & Shin 2010 `10.1016/j.jfi.2008.12.002`, Brunnermeier & Pedersen 2009 `10.1093/rfs/hhn098` all resolve. Minsky 1986 and Reinhart & Rogoff 2009 are books (no DOI, confirmed valid). Six-field completeness PASS on all 5 `simulation-bases.md §2` Theory blocks (§2.1-§2.3 each carry Mechanism / Empirical relevance / Investor link). Bidirectional target-anchor coverage PASS: 5 target §4 anchors map to 5 simulation-bases.md §2 Theory subsections, 5 §5 stylized facts each cite a primary source.
- 2026-07-13  Polish Step 2 audit (agent + environment). AGENT_POOL three-stage match: all 5 archetypes (pro-cyclical-lender, minsky-borrower, counter-cyclical-lender, value-investor, noise-trader) resolve to existing pool profiles under `examples/AGENT_POOL/finance/`; outcome `reuse` for all. Pool profiles are stubs (except noise-trader which is full) — stub expansion deferred (shared-fabric ownership). Icon-resolution gate: 4 PNGs generated (finance-pro-cyclical-lender.png, finance-minsky-borrower.png, finance-counter-cyclical-lender.png, finance-value-investor.png); 4 mapping rows (#54-#57) added to `agent_images/design.md`; noise-trader already had row #14 + PNG. Environment audit PASS: §3 price formation fully specified. Diversity PASS: pro/counter-cyclical + leveraged/fundamental + informed/uninformed axes covered.
- 2026-07-13  Polish Step 3 audit (config). YAML parse PASS: all 16 config files parse cleanly. Variant-folder set PASS: `configs/CreditCycle/{Rule, LLM, RuleLLM, Rag}` matches target §10.1 four-`Yes`. `# Source:` comment coverage added: Rule/players.yml 27 sources, LLM/players.yml 30 sources, RuleLLM/players.yml 30 sources, Rag/players.yml 15+ sources (market + lead agent). All values trace to target §9 or simulation-bases.md §4.N.
- 2026-07-13  Polish Step 4 audit (implementation). py_compile PASS for all 8 variant `.py` files. Import smoke PASS for all 4 variants (Rule, LLM, RuleLLM, Rag). RuleLLM dual-section prompt invariant PASS: 5 `== PERSONA ==` and 5 `== DECISION RULES ==` markers in `RuleLLM/prompts.py`. `_RAG_FALLBACK` define+reference PASS: module-level sentinel added to `Rag/players.py` and consumed in `_build_prompt()`. No `.get(key, default)` violations on `extras` access. explain.md §2 bidirectional PASS (5 rows per variant). analysis.md §2 bidirectional PASS (6-7 metric rows per variant).
- 2026-07-13  Polish Steps 5-10 audit (scenario-level review + smoke). Pass 1 (theory-code) PASS: all 5 archetypes have matching classes across variants. Pass 2 (code + analysis) PASS: metrics import from local analysis module. Pass 3 (docs + cross-check) PASS: explain.md and analysis.md populated. Smoke PASS: Rule 5-round e2e completed without exceptions; LLM/RuleLLM/Rag setup-only smoke PASS.
- 2026-07-13  Round 1 Closeout. Traceability matrix resolved. Status `locked -> released`.
- 2026-07-13  Round 2 re-audit. Full re-verification: target §11 structure PASS (10 top-level sections, §7 has 5 agent rows, §9 has 18 parameter rows, §10.1 marks 4 variants Yes). DOI PASS (3 resolvable DOIs + 2 books). YAML PASS (16 files). py_compile PASS (8 files). Import PASS (4 variants). Icon-resolution PASS (5/5 agents have PNGs + mapping rows + profile Icon rows). Smoke PASS (Rule e2e + LLM/RuleLLM/Rag setup). Status confirmed `released`.

## §1 Meta

| Field         | Content                                                |
|---------------|--------------------------------------------------------|
| Name          | CreditCycle                                            |
| Domain        | finance                                                |
| Requested By  | a77                                                    |
| Produced By   | polish-simulation-pipeline.md (reverse-reconstruction) |
| Created       | 2026-07-13                                             |
| Pipeline      | masim/skills/polish-simulation-pipeline.md             |
| Target Spec   | masim/skills/define-simulation-scenario-skill.md (v1.0) |
| Status        | released                                               |

## §2 Phenomenon Statement

### §2.1 Trigger

The credit cycle begins from a period of macroeconomic stability in which asset prices remain close to fundamental value. Prolonged stability reduces perceived risk, loosens lending standards, and enables higher leverage. The trigger is not an exogenous shock but an endogenous coordination shift: more participants believe that credit expansion will continue, feeding a self-reinforcing boom.

### §2.2 Mechanism

The core mechanism is a pro-cyclical feedback loop: rising asset prices reduce perceived risk, which loosens credit supply, which increases demand, which pushes prices further above fundamentals. Minsky's financial instability hypothesis provides the trajectory: hedge finance evolves into speculative finance and then Ponzi finance as stability breeds fragility. When the deviation becomes large enough, a crisis threshold triggers forced deleveraging, creating a funding-liquidity spiral (Brunnermeier & Pedersen 2009) that amplifies the bust.

### §2.3 Participants

The causal participants are pro-cyclical lenders, Minsky borrowers, counter-cyclical lenders, value investors, and noise traders. Pro-cyclical lenders and Minsky borrowers supply destabilizing demand during booms and destabilizing selling during busts. Counter-cyclical lenders and value investors supply stabilizing liquidity during crises. Noise traders provide stochastic background flow independent of the cycle.

### §2.4 Resolution

The credit cycle resolves when forced deleveraging exhausts the selling pressure of destabilizers and stabilizing agents provide enough offsetting demand. Price converges toward fundamental value, potentially overshooting below fundamental during the bust before recovering. The end state is either convergence to fundamental or a prolonged deleveraging tail.

## §3 Research Goals

1. Can heterogeneous lending and borrowing rules generate an endogenous credit boom-bust cycle in which peak price exceeds fundamental value by at least 8%?
2. Does removing or weakening pro-cyclical lending measurably reduce boom amplitude and bust severity?
3. How sensitive are cycle amplitude and contraction speed to the price-impact coefficient and mean-reversion speed?
4. Does the Minsky borrower's stability-accumulation mechanism produce a measurably sharper bust when stable_rounds is high before onset?
5. Do Rule, LLM, RuleLLM, and Rag variants differ measurably in cycle timing, leverage amplitude, and counter-cyclical offset effectiveness?

## §4 Theoretical Anchors

### §4.1 Financial Instability Hypothesis

| Field | Content |
|-------|---------|
| Full citation | Minsky, H. P. (1986). *Stabilizing an Unstable Economy*. Yale University Press. |
| Key mechanism (≤30 words) | Stability changes financing from hedge to speculative to Ponzi; prolonged calm breeds fragility culminating in sudden credit seizure. |
| Key equation | `stable_rounds(t) += 1 if |delta(t)| < 0.02; reset to 0 otherwise`; Ponzi threshold triggers forced sell at 2x order_size. |
| Motivates agent | minsky-borrower |
| Parameter implication | `crisis_threshold` in [-0.08, -0.03], `order_size` in [300, 700]. |

### §4.2 Pro-Cyclical Leverage and Intermediary Balance Sheets

| Field | Content |
|-------|---------|
| Full citation | Adrian, T., & Shin, H. S. (2010). Liquidity and leverage. *Journal of Financial Intermediation*, 19(3), 418-437. https://doi.org/10.1016/j.jfi.2008.12.002 |
| Key mechanism (≤30 words) | Financial intermediaries expand balance sheets pro-cyclically with rising asset prices and contract when prices fall, amplifying both booms and busts. |
| Key equation | `qty(t) = order_size * credit_multiplier if delta(t) > expansion_threshold; order_size if delta(t) < -expansion_threshold` |
| Motivates agent | pro-cyclical-lender |
| Parameter implication | `expansion_threshold` in [0.005, 0.03], `credit_multiplier` in [1.5, 3.0], `order_size` in [400, 800]. |

### §4.3 Leverage Cycle and Collateral Feedback

| Field | Content |
|-------|---------|
| Full citation | Geanakoplos, J. (2010). The leverage cycle. *NBER Macroeconomics Annual*, 24(1), 1-65. https://doi.org/10.1086/648285 |
| Key mechanism (≤30 words) | Endogenous leverage rises with collateral values and collapses when collateral declines, creating amplification and sudden credit contraction. |
| Key equation | `P(t+1) = P(t) + lambda * D(t) + gamma * [F(t) - P(t)] + epsilon(t)` — price-leverage feedback channel. |
| Motivates agent | counter-cyclical-lender (tests dampening of leverage cycle) |
| Parameter implication | `crisis_buy_threshold` in [-0.08, -0.03], `boom_sell_threshold` in [0.03, 0.08]. |

### §4.4 Funding-Liquidity Spiral

| Field | Content |
|-------|---------|
| Full citation | Brunnermeier, M. K., & Pedersen, L. H. (2009). Market liquidity and funding liquidity. *Review of Financial Studies*, 22(6), 2201-2238. https://doi.org/10.1093/rfs/hhn098 |
| Key mechanism (≤30 words) | Falling prices reduce funding capacity, forcing sales that further depress prices in a self-reinforcing liquidity spiral. |
| Key equation | Crisis-triggered selling by MinskyBorrower (2x order_size) + ProCyclicalLender withdrawal creates the spiral; CounterCyclicalLender buying offsets. |
| Motivates agent | minsky-borrower (forced-sell leg), pro-cyclical-lender (withdrawal leg) |
| Parameter implication | Combined forced-sell volume during bust should exceed single-agent stabilizer capacity to produce visible overshoot. |

### §4.5 Fundamental Value Anchoring

| Field | Content |
|-------|---------|
| Full citation | Reinhart, C. M., & Rogoff, K. S. (2009). *This Time Is Different: Eight Centuries of Financial Folly*. Princeton University Press. |
| Key mechanism (≤30 words) | Credit booms eventually revert toward fundamental value; value-oriented investors provide the mean-reversion anchor. |
| Key equation | `qty(t) = order_size if delta(t) < -value_discount; order_size (sell) if delta(t) > value_discount` |
| Motivates agent | value-investor |
| Parameter implication | `value_discount` in [0.05, 0.15], `order_size` in [200, 600]. |

## §5 Stylized Facts

| # | Stylized Fact | Numeric Range | Primary Source | Acceptance Metric |
|---|---|---|---|---|
| F1 | Credit booms last longer than busts (asymmetric cycle shape) | PDR in [1.5, 3.0] | Reinhart & Rogoff (2009) | `phase_duration_ratio()` |
| F2 | Leverage amplifies boom amplitude relative to fundamental | LAI in [1.0, 2.0] | Geanakoplos (2010) | `leverage_amplitude_index()` |
| F3 | Minsky fragility accumulates during stable periods before bust | MFS in [4, 8] rounds | Minsky (1986) | `minsky_fragility_score()` |
| F4 | Credit contraction is rapid relative to expansion | CCS in [0.5, 1.5] units/round | Adrian & Shin (2010) | `credit_contraction_speed()` |
| F5 | Counter-cyclical intervention absorbs 40-60% of bust selling | CCOR in [0.3, 0.7] | Basel III CCyB (BIS 2010) | `counter_cyclical_offset_ratio()` |

## §6 Historical / Empirical Anchors

| # | Event | Year | Core Mechanism | Scenario Mapping |
|---|---|---|---|---|
| H1 | US Savings-and-Loan Crisis | 1980s | Deregulated pro-cyclical bank lending into real estate; abrupt tightening | ProCyclicalLender expansion and withdrawal |
| H2 | LTCM Crisis | 1998 | Leverage accumulation during calm; sudden deleveraging under margin stress | MinskyBorrower stable_rounds accumulation → forced sell |
| H3 | Global Financial Crisis | 2007-2009 | Subprime credit expansion, collateral feedback, forced deleveraging | Full five-agent taxonomy: boom, fragility, contraction, stabilization |

## §7 Agent Roster

| # | Kebab Name | Theory Family | Market Role | Time Horizon | Risk Tolerance | Information | Determinism |
|---|---|---|---|---|---|---|---|
| 1 | pro-cyclical-lender | Macro (Adrian & Shin 2010) | Destabilizing | Medium | High | Price deviation | Rule-deterministic |
| 2 | minsky-borrower | Macro (Minsky 1986) | Destabilizing | Medium-Long | Very High | Stability duration + deviation | Rule-deterministic |
| 3 | counter-cyclical-lender | Macro (Geanakoplos 2010) | Stabilizing | Long | Low | Price deviation | Rule-deterministic |
| 4 | value-investor | Fundamental (Reinhart & Rogoff 2009) | Stabilizing | Long | Low | Deviation from fundamental | Rule-deterministic |
| 5 | noise-trader | Behavioral (Black 1986) | Neutral | Short | High | None | Stochastic |

## §8 Environment Specification

### §8.1 Price Formation

Single credit-asset market with price determined by net demand, mean reversion, and noise:

```
P(t+1) = P(t) + lambda * D(t) + gamma * [F(t) - P(t)] + epsilon(t)
```

Where lambda = 0.05 (price impact), gamma = 0.02 (mean reversion), F(t) = 100.0 (fundamental), epsilon ~ N(0, 0.02^2).

### §8.2 Information Broadcast

Market broadcasts `{price, fundamental, deviation, round}` to all investors each round.

### §8.3 Constraints and Frictions

- No short selling (position >= 0 enforced per agent).
- Cash constraint (cannot buy more than cash allows).
- Position constraint (cannot sell more than held).

### §8.4 Round Granularity

Star topology: Market executes first (Level 0), all investors execute in parallel (Level 1). One round = one complete broadcast-decide-act cycle.

## §9 Parameter Seeds

| # | Parameter | Belongs to | Default | Empirical Range | Source Citation |
|---|---|---|---|---|---|
| 1 | initial_price | Market | 100.0 | — | Normalization |
| 2 | fundamental_value | Market | 100.0 | — | Normalization |
| 3 | price_impact (lambda) | Market | 0.05 | [0.02, 0.10] | Calibrated for visible feedback in 200 rounds |
| 4 | mean_reversion (gamma) | Market | 0.02 | [0.01, 0.05] | Slow reversion for persistent credit cycles |
| 5 | noise_std | Market | 0.02 | [0.01, 0.05] | Small relative to endogenous demand |
| 6 | expansion_threshold | pro-cyclical-lender | 0.01 | [0.005, 0.03] | Adrian & Shin (2010) collateral sensitivity |
| 7 | contraction_threshold | pro-cyclical-lender | -0.015 | [-0.03, -0.005] | Asymmetric credit tightening |
| 8 | credit_multiplier | pro-cyclical-lender | 2.0 | [1.5, 3.0] | Adrian & Shin (2010) |
| 9 | order_size | pro-cyclical-lender | 600 | [400, 800] | Calibration |
| 10 | crisis_threshold | minsky-borrower | -0.05 | [-0.08, -0.03] | Minsky (1986) Ponzi-threshold |
| 11 | max_leverage | minsky-borrower | 5.0 | [3.0, 8.0] | Minsky (1986) |
| 12 | order_size | minsky-borrower | 500 | [300, 700] | Calibration |
| 13 | crisis_buy_threshold | counter-cyclical-lender | -0.05 | [-0.08, -0.03] | Basel III CCyB trigger |
| 14 | boom_sell_threshold | counter-cyclical-lender | 0.05 | [0.03, 0.08] | Reserve build in booms |
| 15 | order_size | counter-cyclical-lender | 500 | [300, 700] | Calibration |
| 16 | value_discount | value-investor | 0.10 | [0.05, 0.15] | Graham (1949) margin of safety |
| 17 | order_size | value-investor | 400 | [200, 600] | Calibration |
| 18 | trade_probability | noise-trader | 0.3 | [0.2, 0.5] | Black (1986) |

## §10 Variants and Success Criteria

### §10.1 Variants to Build

| Variant | Build? | Notes |
|---------|--------|-------|
| Rule | Yes | Deterministic baseline — threshold rules on deviation and stable_rounds |
| LLM | Yes | LLM persona with credit-cycle context |
| RuleLLM | Yes | LLM with embedded numerical threshold rules (== PERSONA == / == DECISION RULES ==) |
| Rag | Yes | LLM + retrieved credit-cycle knowledge |

### §10.2 Pass / Fail Criteria

1. Rule variant must produce at least one complete boom-bust cycle (peak delta > +0.05 followed by trough delta < -0.05) within 200 rounds.
2. Leverage Amplitude Index (LAI) must be in [0.5, 4.0] — extreme asymmetry or absence of cycle is failure.
3. Counter-Cyclical Offset Ratio (CCOR) must be in [0.2, 0.9] — complete absence of stabilization or complete suppression of the cycle are both failures.
4. All variants must pass py_compile + import smoke without error.
