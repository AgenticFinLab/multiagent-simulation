# CurrencyCrisis RuleLLM Variant — analysis.md

## §1 Analysis Overview

The RuleLLM analysis evaluates agents that receive the same behavioral rule
structure as the Rule variant but express decisions through LLM reasoning. The
core question is whether language-mediated decisions preserve the deterministic
crisis mechanism while changing timing, quantities, or reasoning traces.

## §2 Metric Implementation

`RuleLLM/analysis.py` imports the Rule analysis functions:

| Function | Purpose | Root reference |
|---|---|---|
| `_load_data(results)` | Load market and canonical order records | `analysis-bases.md §2` |
| `_compute_attack_intensity_index(...)` | Compute attack depth from maximum negative deviation | `analysis-bases.md §2.1` |
| `_compute_peg_survival_duration(...)` | Compute rounds until peg breach | `analysis-bases.md §2.2` |
| `_compute_defense_exhaustion_rate(...)` | Compute central-bank intervention spending during crisis rounds | `analysis-bases.md §2.3` |
| `_compute_self_fulfilling_amplification_factor(...)` | Compare self-fulfilling sell flow with attacker sell flow | `analysis-bases.md §2.4` |
| `_compute_fundamental_anchor_strength(...)` | Compute stabilizing hedger buy activity during attack rounds | `analysis-bases.md §2.5` |
| `_compute_recovery_speed(...)` | Compute rounds from trough back toward the peg | `analysis-bases.md §2.6` |
| `_create_visualizations(...)` | Generate fixed diagnostic plots | `analysis-bases.md §7` |

## §3 Dimension-by-Dimension Interpretation

| Dimension | RuleLLM-specific interpretation |
|---|---|
| Attack depth | Should remain near Rule if embedded decision rules are followed. |
| Peg survival | Deviations from Rule indicate LLM quantity adjustment or delayed action. |
| Defense exhaustion | Should show rule-anchored central-bank defense with possible LLM smoothing. |
| Self-fulfilling amplification | Should preserve the expectation-channel direction from Rule. |
| Fundamental anchor | Should remain active during attack phases. |
| Recovery | Language reasoning may speed or slow post-trough stabilization. |
| Wealth transfer | Measures whether LLM reasoning shifts profits relative to the rule baseline. |

## §4 Variant-Specific Observable Phenomena

RuleLLM prompts must contain `== PERSONA ==` and `== DECISION RULES ==`
sections. The decision-rules section re-expresses the Rule variant's thresholds
and order limits in natural language, while the persona section supplies
institutional role and behavioral style. Every LLM decision is therefore
double-anchored: to the persona's role and to the embedded quantitative rule.

| Phenomenon                              | Description                                                                                                              | How to Observe                                                                | Contrast with Rule Baseline                       |
|-----------------------------------------|--------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|---------------------------------------------------|
| Rule-anchored attack timing             | SpeculativeAttacker fires near the rule-implied `|δ| > 0.03` boundary, with small LLM softening                          | `01_currencycrisis_dynamics.png` breach round close to Rule                   | Rule timing exact; RuleLLM timing tight but soft  |
| LLM-modulated attack quantity           | Under the same trigger, LLM selects a quantity within the rule-implied band                                              | `03_summary.png` shows attacker VWAP with widened per-round quantity variance | Quantity variance higher than Rule                |
| Rule-anchored defender spending         | CentralBankDefender engages at the rule-implied breach threshold; reserve depletion follows Rule schedule ± small drift  | Compare `defender_cash_history` with Rule schedule                            | RuleLLM DER close to Rule; slight smoothing       |
| SelfFulfillingTrader coherent momentum  | Reasoning cites the embedded threshold and prior-round sell flow simultaneously                                          | Grep `reasoning` for both rule and momentum keywords                          | Rule cannot cite reasoning; LLM lacks anchor      |
| Rule-fidelity risk                      | LLM may paraphrase the rule and drift in quantity; can be detected via rule-adherence table                              | Compare each LLM action's direction against the rule prescription             | Rule cannot deviate; LLM has nothing to deviate from |

RuleLLM sits between Rule (fully deterministic) and LLM (fully unanchored).
The `== DECISION RULES ==` block acts as **investor knowledge/habit**, not as an
executable mandate — the LLM may still exercise judgement on quantity and
occasionally on timing, but the direction and threshold structure should
survive. Expected calibration: AII within ±10 % of Rule, PSD within ±10 % of
Rule, DER close to the Rule schedule, and SFAF/FAS/RS/WTI in the same
directional band as Rule.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                    | Phenomenon Clarity | Recommended for  |
|--------------|------------------------------------------------------------------------|--------------------|------------------|
| 100          | Attack visible but recovery may be truncated; rule-adherence noisier    | Low                | Smoke testing    |
| 200          | Full Pre-Attack → Attack → Crisis → Recovery arc; RuleLLM anchoring visible | Medium         | Standard runs    |
| 500          | Rule-anchored AII/PSD stabilize; LLM quantity variance averages out    | High               | Research quality |

### Agent Count Scaling

| Configuration                            | Expected Observable                                                     | Environment Dynamics                                |
|------------------------------------------|-------------------------------------------------------------------------|-----------------------------------------------------|
| +50 % attacker/self-fulfilling personas  | AII deepens toward Rule upper band; SFAF rises with LLM smoothing       | Attack pressure dominates; defender may capitulate  |
| +50 % defender/hedger personas           | PSD extends; DER slower; RuleLLM defense keeps peg longer than Rule     | Balanced-to-defensive market                        |
| Uniform doubling                          | LLM-call cost doubles; reasoning quality may degrade at high round load | Full mechanism observable; watch context saturation |

### Parameter Sensitivity (±50 %)

| Parameter                                | Change | Expected Effect on RuleLLM Analysis                                                        |
|------------------------------------------|--------|--------------------------------------------------------------------------------------------|
| Prompt rule wording (paraphrase)         | Test   | Adherence to embedded thresholds may drift; use as rule-fidelity probe                     |
| LLM temperature                          | +50 %  | AII/PSD variance widens but stays centered on Rule value                                   |
| `peg_target` / `initial_cash`            | ±50 %  | Rule-consistent directional response with LLM-added variance                               |
| `breach_threshold` (in rule text)        | +50 %  | Rule-anchored PSD lengthens; AII may deepen before defender fires                          |
| SpeculativeAttacker share                | +50 %  | AII deeper; SFAF rises; DER accelerates; RuleLLM tracks Rule direction                     |
| Retry budget                             | Higher | Fewer fallback holds; rule-adherence table more complete                                   |

---

## §6 Output Files Reference

Running `RuleLLM/analysis.py` writes standard artifacts under
`EXPERIMENT/CurrencyCrisis/RuleLLM/analysis/`. Plot generation is delegated to
`_create_visualizations()` imported from the Rule analysis; `summary.json` is
stamped with `variant="RuleLLM"`.

| File | Generated By | Contents | How to Interpret |
|---|---|---|---|
| `00_investor_bids.png` | `_create_visualizations()` | Market price, peg line, and investor bid curves | Attacker/self-fulfilling bids anchored to rule threshold; quantities show LLM variance |
| `01_currencycrisis_dynamics.png` | `_create_visualizations()` | Exchange rate vs. peg and deviation thresholds (−5 %, −10 %) | Locate peg breach round (PSD) and trough (AII); RuleLLM breach timing close to Rule |
| `02_currencycrisis_analysis.png` | `_create_visualizations()` | Rolling volatility and per-round returns | Volatility spikes concentrated near attack/crisis phases; rule adherence keeps timing tight |
| `03_summary.png` | `_create_visualizations()` | Agent VWAP and total volume summary | Cross-check SFAF against attacker vs self-fulfilling VWAP disparity |
| `summary.json` | `main()` | Metrics (AII/PSD/DER/SFAF/FAS/RS/WTI) + validation criteria + agent VWAP data + variant label | Compare against `../analysis-bases.md §6.2`; check `variant == "RuleLLM"` |

RuleLLM reports may additionally record a rule-adherence table classifying
whether each LLM action's direction matches the embedded `== DECISION RULES ==`
prescription; this artifact lives alongside `summary.json` and stays outside
the standard PNG contract.

## §7 Cross-Variant Comparison Notes

RuleLLM is the direct control for measuring the effect of embedded rule text
on LLM behavior. Cross-variant axes follow `../analysis-bases.md §5` and §6.3.

| Comparison | RuleLLM's Expected Position                                                                    | Detection                                                                             |
|------------|------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------|
| RuleLLM vs Rule | AII, PSD, DER within ±10 % of Rule; SFAF/FAS same direction                              | Compare `summary.json` metrics; check breach round in `01_currencycrisis_dynamics.png`|
| RuleLLM vs LLM  | Tighter timing, tighter FAS; lower AII dispersion                                        | Compare cross-seed std of AII and PSD                                                 |
| RuleLLM vs Rag  | RuleLLM lacks retrieved crisis history; Rag may improve FAS and reduce SFAF              | Cross-check `rag_stats.json` retrieval bucket vs `summary.json`                       |

**Comparison protocol**: run RuleLLM under the same parameters and seed set as
Rule. Report `Δ vs Rule = RuleLLM − Rule` per metric across ≥ 3 seeds, plus a
rule-adherence rate (fraction of decisions matching the embedded rule
direction). If any metric drifts outside ±10 % of Rule, inspect the
rule-adherence table first — significant drift usually indicates the LLM is
overriding the rule (rule text too weak or persona too strong).

## §8 Quality Checks

- Confirm 200 configured rounds completed.
- Confirm no LLM parse failures or retries remain unresolved.
- Confirm prompt sections include both persona and decision-rule labels.
- Confirm order actions and quantities remain valid after LLM parsing.
