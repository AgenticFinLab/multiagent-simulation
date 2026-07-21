# DotComBubble LLM Variant — analysis.md

## §1 Analysis Objectives

Measure how LLM persona-driven decision-making shapes bubble amplitude, duration, crash severity, and momentum amplification relative to the Rule baseline. All metrics defined in `analysis-bases.md §2`.

## §2 Metric → Function Mapping

| Metric                              | Function                                                                   | analysis-bases.md ref |
|-------------------------------------|----------------------------------------------------------------------------|-----------------------|
| BAI (Bubble Amplitude Index)        | `bubble_amplitude_index(price_history, fundamental)`                       | §2 BAI                |
| BD (Bubble Duration)                | `bubble_duration(price_history, fundamental, bubble_threshold=0.10)`       | §2 BD                 |
| CS (Crash Severity)                 | `crash_severity(price_history)`                                            | §2 CS                 |
| MAF (Momentum Amplification Factor) | `momentum_amplification_factor(agent_orders, bubble_rounds)`               | §2 MAF                |
| SSR (Short-Seller Resistance)       | `short_seller_resistance(short_seller_orders, overvaluation_rounds)`       | §2 SSR                |
| RT (Recovery Time)                  | `recovery_time(price_history, fundamental, recovery_threshold=0.10)`       | §2 RT                 |
| AQR (API Quality)                   | `api_quality(agent_orders)`                                                | §2 AQR                |

## §3 LLM-Variant-Specific Notes

- **Stochastic paths**: Report replicated distributions rather than treating one sampled path as representative.
- **Persona attribution**: MAF uses recorded momentum-follower buy volume; SSR uses the constrained skeptical seller's recorded sell actions.
- **Fail-fast quality**: Provider or parse failures stop the run after the configured retry count; they are not converted into hidden hold actions.
- **Contract audit**: AQR verifies that every persisted decision has valid action, price, quantity, reasoning, and analysis fields.
- **Cross-run replication**: Re-run at least 3× and report mean ± standard deviation for BAI and BD.

## §4 Variant-Specific Observable Phenomena

| Phenomenon                              | Description                                                                                              | How to Observe                                                                | Contrast with Rule Baseline                            |
|-----------------------------------------|----------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|--------------------------------------------------------|
| Narrative-driven demand persistence     | LLM Evangelist persona continues buying based on story, not a hard threshold                             | Order `reasoning` cites "new economy", "network effects"; BAI band widens     | Rule stops exactly at crash trigger                    |
| Emergent caution near peaks             | LLM MomentumFollower occasionally pauses when previous rounds show consecutive drops                     | MAF is lower on average than Rule; some seeds show MAF near 0                 | Rule MAF is threshold-locked                           |
| Stochastic short-seller entry           | ShortSeller waits for narrative confirmation before entering; SSR variance widens                        | `06_...png` (if aliased) or `metrics.short_seller_resistance` variance         | Rule SSR is threshold-exact                             |
| Persona-consistent reasoning coherence  | Each agent's `reasoning` field cites persona-appropriate vocabulary                                       | Grep `reasoning` for persona keywords per agent class                          | Rule payloads carry no reasoning                        |
| Parse-quality risk                      | Rare malformed `<decision>` blocks; runs fail fast rather than hide holds                                 | Inspect logs for retry counts; AQR must be 1.0                                | Rule has no such failure mode                           |

**Diagnostic bands for LLM run acceptance**:

| Metric | Review signal                                                                                    |
|--------|--------------------------------------------------------------------------------------------------|
| BAI    | `< 0.10` suggests no visible bubble; `> 2.0` requires numerical-stability review.                |
| BD     | `0` means no persistent bubble; a near-full-run value suggests no resolution.                    |
| CS     | `< 0.30` is a mild correction; `> 0.80` requires numerical-stability review.                     |
| MAF    | Near zero means the momentum persona did not materially amplify bubble buying.                   |
| SSR    | Zero means the inventory-constrained skeptical seller supplied no overvaluation sell pressure.   |
| RT     | `null` means no post-trough recovery within the recorded horizon.                                |
| AQR    | `contract_compliance_rate` must equal `1.0` for an accepted run.                                 |

---

## §5 Scaling and Sensitivity Analysis

### Round Scaling

| Total Rounds | Expected Observable                                                | Phenomenon Clarity | Recommended for  |
|--------------|--------------------------------------------------------------------|--------------------|------------------|
| 100          | Bubble formation visible; crash may be truncated; parse rate stable | Low                | Smoke testing    |
| 200          | Full Bubble → Crash → Recovery arc; BAI/BD stable across seeds     | Medium             | Standard runs    |
| 500          | Persona replication signal tightens; RT/CS distributions converge   | High               | Research quality |

### Agent Count Scaling

| Agent Count | Expected Observable                                                | Environment Dynamics                                |
|-------------|--------------------------------------------------------------------|-----------------------------------------------------|
| 20          | BAI measurable but LLM cost dominates run time                     | Sparse orders; MAF variance elevated                |
| 40          | Recommended: clean phase separation with tractable LLM budget      | Full mechanism observable                           |
| 80          | Reduced variance across seeds; suitable for prompt-variation runs   | Baseline dynamics with statistical mass             |

### Parameter Sensitivity (Variant-Specific)

| Parameter                              | Change | Expected Effect on This Variant's Analysis                                          |
|----------------------------------------|--------|-------------------------------------------------------------------------------------|
| LLM temperature (sampling)             | +50 %  | BAI/BD variance widens; MAF becomes more bimodal across seeds                       |
| Prompt persona strength                | Test   | Stronger narrative → BAI approaches Rule; softer narrative → bubble may not form    |
| `bubble_threshold` (analysis-side)     | +50 %  | Recorded BD drops mechanically; BAI is unchanged                                    |
| `borrow_limit` (ShortSeller)           | +50 %  | LLM ShortSeller sells more aggressively; SSR rises; CS softens                      |
| Recovery threshold (analysis-side)     | −50 %  | RT recorded more frequently; interpretation of "recovered" widens                   |

---

## §6 Output Files Reference

All outputs written to `EXPERIMENT/DotComBubble/LLM/analysis/`.

| Output File                          | Generated By                    | Contents                                                             | How to Interpret                                                                     |
|--------------------------------------|---------------------------------|----------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| `summary.json`                       | `main()`                        | Metrics (BAI/BD/CS/MAF/SSR/RT/AQR) + validation + variant label      | AQR `contract_compliance_rate` must be 1.0; report BAI/BD as mean ± std over ≥ 3 seeds |
| `dotcombubble_llm_dynamics.png`      | `create_visualizations()`       | Price vs fundamental with bubble/crash phase annotations             | Bubble arc softer than Rule; crash timing more variable                              |

Run the analysis with:

```bash
python -m examples.DotComBubble.LLM.analysis \
  -c configs/DotComBubble/LLM/simulation.yml
```

Quality gates: (a) run completes 200 rounds, (b) parse failures / retries stay within accepted bounds and are logged, (c) accepted decisions have valid `action` and numeric `quantity`, (d) `summary.json` contains all seven metrics, (e) hold-action rate stays below the acceptability threshold.

## §7 Quality Checks

- Confirm the run completed the configured 200 rounds.
- Audit parse failures and retry counts before acceptance; deterministic parser or provider failures should fail fast rather than become hidden holds.
- Confirm accepted decisions produce valid `action` and numeric `quantity` fields.
- Confirm `summary.json` contains BAI, BD, CS, MAF, SSR, RT, and AQR.
- Review action distribution for excessive holds that would indicate unusable output quality.
- Outputs default to `EXPERIMENT/DotComBubble/LLM/analysis/summary.json` and `dotcombubble_llm_dynamics.png`.

---

## §8 Cross-Variant Comparison Notes

The LLM variant is compared against Rule (deterministic baseline), RuleLLM (rule-anchored LLM), and Rag (retrieval-augmented LLM) using the axes in `../analysis-bases.md §5` and §6.3.

| Comparison Axis                        | LLM's Expected Position                                                 | Reason                                                                                                                                       |
|----------------------------------------|-------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| Bubble amplitude (BAI)                 | Possibly higher than Rule; typically higher than RuleLLM; comparable to Rag | Narrative-driven Evangelist persona sustains buying beyond hard thresholds; conviction language extends overvaluation                        |
| Bubble duration (BD)                   | Longer than Rule; comparable to or shorter than Rag                     | LLM Evangelist and MomentumFollower personas resist mean reversion until narrative confidence breaks; Rag may inject historical caution      |
| Crash severity (CS)                    | High variance vs Rule; typically comparable to Rule                     | Once narrative confidence collapses, LLM capitulation drives similar drawdown magnitudes; timing more stochastic                             |
| Momentum amplification (MAF)           | Below Rule on average; occasional near-zero seeds                       | LLM MomentumFollower may pause after consecutive drops; Rule MAF is threshold-locked                                                         |
| Short-seller resistance (SSR)          | Higher variance than Rule; typically comparable                         | Narrative-triggered entry produces stochastic timing; inventory constraint still binds                                                       |
| API/output quality (AQR)               | Primary quality gate — must equal 1.0                                   | Malformed decision blocks fail fast rather than becoming hidden holds; parse quality is variant-critical                                     |
| Reasoning traceability                 | Available — every accepted order carries persona-consistent `reasoning` | Grep for persona vocabulary ("new economy", "network effects", "priced for perfection") per agent class                                      |

**Comparison protocol**: run LLM under the same parameters and seed set as Rule; report BAI, BD, CS, MAF, SSR, RT as mean ± std over ≥ 3 replications. Report AQR `contract_compliance_rate` for every run — any value below 1.0 disqualifies the sample from cross-variant claims.

| Cross-Variant Test | Expected Signature                                                                                                             | Detection                                                                                                     |
|--------------------|--------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| LLM vs Rule        | Wider BAI/BD dispersion; possibly higher BAI; softer MAF; comparable CS                                                        | `summary.json` metrics side by side across seeds; `dotcombubble_llm_dynamics.png` bubble arc softer           |
| LLM vs RuleLLM     | LLM's timing more diffuse; RuleLLM's activation edges tighter                                                                  | Compare `bubble_rounds` counts and MAF                                                                        |
| LLM vs Rag         | LLM lacks retrieved crash history; BAI ≥ Rag when Rag retrieval succeeds; Rag reduces excessive bubble amplitude               | `rag_stats.json` from Rag run; segment Rag metrics by retrieval bucket                                        |

If LLM produces `BAI < Rule` or `BD = 0`, verify prompt persona strength: too-weak narrative may prevent bubble formation entirely. If `AQR contract_compliance_rate < 1.0`, treat every downstream metric as suspect — a run with silent parse failures is not comparable to the deterministic Rule baseline.
