# CurrencyCrisis LLM Variant — analysis.md

## §1 Analysis Overview

The LLM analysis evaluates whether persona-only language agents can reproduce
currency-crisis dynamics without explicit trading formulas. The same core
metrics from `analysis-bases.md §2` are used so results remain comparable with
the Rule baseline.

## §2 Metric Implementation

`LLM/analysis.py` imports the core Rule analysis functions:

| Function | Purpose | Root reference |
|---|---|---|
| `_load_data(results)` | Load market and canonical order records | `analysis-bases.md §2` |
| `_compute_attack_intensity_index(...)` | Compute attack depth from maximum negative deviation | `analysis-bases.md §2.1` |
| `_compute_peg_survival_duration(...)` | Compute rounds until peg breach | `analysis-bases.md §2.2` |
| `_compute_defense_exhaustion_rate(...)` | Compute central-bank intervention spending during crisis rounds | `analysis-bases.md §2.3` |
| `_compute_self_fulfilling_amplification_factor(...)` | Compare self-fulfilling sell flow with attacker sell flow | `analysis-bases.md §2.4` |
| `_compute_fundamental_anchor_strength(...)` | Compute stabilizing hedger buy activity during attack rounds | `analysis-bases.md §2.5` |
| `_compute_recovery_speed(...)` | Compute rounds from trough back toward the peg | `analysis-bases.md §2.6` |
| `_create_visualizations(...)` | Generate the fixed CurrencyCrisis diagnostic plots | `analysis-bases.md §7` |

LLM-specific review adds action-distribution and output-quality checks over raw
LLM decision records.

## §3 Dimension-by-Dimension Interpretation

| Dimension | LLM-specific interpretation |
|---|---|
| Attack depth | Higher variance than Rule indicates persona-driven crisis intensity. |
| Peg survival | Longer survival can indicate central-bank caution or delayed attack coordination. |
| Defense exhaustion | Smooth spending indicates adaptive intervention; abrupt spending indicates urgent peg defense. |
| Self-fulfilling amplification | High SFAF indicates LLM traders coordinated on crisis expectations. |
| Fundamental anchor | Low FAS indicates the fundamental hedger abandoned stabilizing behavior. |
| Recovery | Recovery speed reflects whether LLM agents recognize stabilization opportunities. |
| Wealth transfer | Positive WTI indicates LLM speculators profited from devaluation. |

## §4 Variant-Specific Observable Phenomena

Under the LLM variant, each agent receives a persona-only prompt and no
explicit trading rules; the observed decisions therefore reflect the
language model's interpretation of the market state and role. Deviations
from the Rule baseline can be attributed to reasoning variability rather
than mechanism differences.

| Phenomenon                                | Trigger condition                                                     | Expected metric signature                                          |
|-------------------------------------------|-----------------------------------------------------------------------|--------------------------------------------------------------------|
| Persona-driven attack timing              | Attacker persona infers pressure without explicit threshold           | AII broader distribution than Rule; attack rounds shift            |
| Coordinated self-fulfilling reasoning     | SelfFulfilling persona interprets prior sells as expectation signal   | `SFAF` may exceed Rule if LLM emphasises crowd behaviour           |
| Defender hesitation or over-commitment    | Central-bank persona reasons about reserves before spending           | `DER` smoother or spikier depending on framing                     |
| Hedger persona drift                      | FundamentalHedger reasoning may deprioritize buying                   | `FAS` variance rises; occasional dropouts                          |
| Reasoning-triggered recovery              | Persona identifies stabilization opportunity post-trough              | Recovery speed higher variance; some seeds fail to recover         |
| Reasoning parse-failure fallback          | Malformed LLM output forces canonical fallback order                  | Silent hold rounds; must be audited as quality failure             |

The LLM variant must **not** embed the deterministic formulas from the Rule
variant. Its quality depends on whether persona-only prompts produce coherent
trading actions and whether those actions reproduce the four canonical
crisis channels: speculative attack, self-fulfilling selling, peg defense,
and fundamental anchoring.

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Round count | Expected metric behavior                                                                                        |
|-------------|-----------------------------------------------------------------------------------------------------------------|
| 100         | Persona coherence assessable; AII distribution wide; sample too small to isolate seed effects                   |
| 200         | Central setting; full attack-defense-recovery cycle observable; parse-failure rate stabilizes                   |
| 500         | Long-horizon regime; watch for reasoning drift, repetitive actions, or context saturation                       |

### Agent Count Scaling

| Configuration                                       | Expected effect on metrics                                                                    |
|-----------------------------------------------------|-----------------------------------------------------------------------------------------------|
| +50% attacker/self-fulfilling personas              | AII deepens (like Rule) but with higher run-to-run variance                                   |
| +50% defender/hedger personas                       | Persona diversity may not fully offset LLM hesitation; FAS may still lag Rule                 |
| Uniform doubling                                    | LLM-call cost doubles; reasoning quality per agent may degrade under context pressure         |

### Parameter Sensitivity (±50%)

| Parameter                          | Effect on LLM-specific metrics                                                        |
|------------------------------------|---------------------------------------------------------------------------------------|
| Prompt temperature                 | Higher → wider AII/SFAF distribution; more parse failures                             |
| Persona verbosity                  | Longer personas can improve role adherence but risk context overflow                  |
| Max output tokens                  | Below decision-block size → increased parse failures                                  |
| `peg_target` / `initial_cash`      | Same directional effects as Rule, moderated by LLM interpretation                     |
| Retry budget                       | Higher → fewer fallback holds; audit trail more complete                              |

---

## §6 Output Files Reference

Running `LLM/analysis.py` writes the standard analysis artifacts under the
configured experiment output directory (`EXPERIMENT/CurrencyCrisis/LLM/analysis/`).
The variant delegates plot generation to `_create_visualizations()` (imported
from the Rule analysis) and emits a `summary.json` stamped with `variant="LLM"`.

| File | Generated By | Contents | How to Interpret |
|---|---|---|---|
| `00_investor_bids.png` | `_create_visualizations()` | Market price, peg line, and investor bid curves | Attacker/self-fulfilling bids cluster once `|δ| > 0.03`; defender curve mirrors reserve spending |
| `01_currencycrisis_dynamics.png` | `_create_visualizations()` | Exchange rate vs. peg and deviation thresholds (−5 %, −10 %) | Locate peg breach round (PSD) and trough round (AII); LLM breach timing more stochastic than Rule |
| `02_currencycrisis_analysis.png` | `_create_visualizations()` | Rolling volatility and per-round returns | Volatility spikes concentrated near attack and crisis phases; parse-failure rounds show gaps |
| `03_summary.png` | `_create_visualizations()` | Agent VWAP and total volume summary | Cross-check SFAF against attacker vs self-fulfilling VWAP disparity |
| `summary.json` | `main()` | Metrics (AII/PSD/DER/SFAF/FAS/RS/WTI) + validation criteria + agent VWAP data + variant label | Compare against calibration targets in `../analysis-bases.md §6.2`; check `variant == "LLM"` |

LLM reports should additionally record action-distribution and parse-quality
tables alongside `summary.json`. Any silent hold arising from a parse failure
must be logged as a quality failure rather than counted as a "hold" action.

## §7 Cross-Variant Comparison Notes

Compare LLM metrics against Rule, RuleLLM, and Rag along the axes in
`../analysis-bases.md §5` and §6.3:

| Metric | LLM Expected Reading vs Rule                                                       | vs RuleLLM                                                | vs Rag                                                              |
|--------|------------------------------------------------------------------------------------|-----------------------------------------------------------|---------------------------------------------------------------------|
| AII    | Higher dispersion; crisis reasoning is stochastic                                  | LLM AII typically wider band than rule-anchored RuleLLM   | Rag may moderate AII when historical crisis context is retrieved    |
| PSD    | Later or earlier breach depending on attacker/defender reasoning                    | Similar in mean; LLM has larger seed-to-seed variance     | Rag defender may extend PSD by recognizing familiar attack patterns |
| DER    | Adaptive spending pattern; smoother or spikier than Rule                            | RuleLLM closer to Rule schedule                           | Rag defender may pace reserves informed by historical exhaustion    |
| SFAF   | Can exceed Rule when LLMs infer crowd coordination                                  | RuleLLM SFAF anchored to Rule threshold                   | Rag may reduce SFAF via retrieved contagion warnings                |
| FAS    | Should remain positive if fundamental persona is preserved; may dip on some seeds   | RuleLLM FAS closer to Rule (threshold active)             | Rag PPP/fundamentals retrieval typically improves FAS               |
| RS     | Higher variance; some seeds fail to recover                                         | RuleLLM RS close to Rule                                  | Rag RS improved when recovery case studies retrieved                |
| WTI    | Captures whether language reasoning shifts gains toward attackers or defenders      | RuleLLM WTI near zero (rule symmetry)                     | Rag may favor defenders when retrieval succeeds                     |

**Comparison protocol**: run LLM under the same parameters and seed set as
Rule; report `Δ vs Rule = LLM − Rule` per metric across ≥ 3 seeds, plus
reasoning-quality summary (parse success rate, mean reasoning length,
persona-vocabulary hit rate). Any silent parse-failure fallback disqualifies
the sample.

## §8 Quality Checks

- Confirm the run completed 200 configured rounds.
- Audit LLM parse failures, retry counts, and fallback behavior before accepting
  the sample.
- Treat any silent fallback hold as a quality failure unless explicitly
  documented and justified.
- Confirm all accepted orders preserve valid `action`, numeric `bid_price`, numeric `quantity`, and non-empty `reasoning`.
