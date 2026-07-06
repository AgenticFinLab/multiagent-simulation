# Steps 5–10: Validate, Review, Analyze, Document, Execute, and Final Review

## Contract (Inputs / Outputs / Polish Hooks)

This block is the **stable I/O declaration** for Steps 5 — 10. Both
`masim/skills/create-simulation-pipeline.md` and
`masim/skills/polish-simulation-pipeline.md` anchor to it.

**Inputs (consumed).** Everything produced by Steps 0 — 4:

- Target file (locked); `simulation-bases.md`, `analysis-bases.md`;
- Every `{V}/players.py`, `{V}/analysis.py`, `{V}/prompts.py`, `{V}/explain.md`, `{V}/analysis.md`;
- Every `configs/{ScenarioName}/{V}/*.yml`;
- `simulation-build-log.md` (build log so far).

**Outputs (produced or extended).**

| Artefact                                         | Written when                                                          |
|--------------------------------------------------|-----------------------------------------------------------------------|
| Analysis figures + tables                         | Step 9 execution — one figure set per built variant                    |
| `simulation-build-log.md §D`                      | one row per Step 5 — 9 review pass (`pass` / `fail` / `defect-raised`) |
| `simulation-build-log.md §C`                      | any newly surfaced open question or risk                               |
| Target file `Status: locked → released`           | Step 10 final-review closeout                                          |
| Target §0 Meta CHANGELOG                          | one line summarising the run                                           |

**Polish Hooks (what a polish audit re-verifies against Steps 5 — 10).**
When `polish-simulation-pipeline.md` audits Steps 5 — 10, it re-runs
the checklists **three consecutive times** with the perspective split
below. Any FAIL in any pass resets the count.

| Pass | Perspective                            | Anchors in this file            |
|------|----------------------------------------|---------------------------------|
| 1    | Theory–code alignment                  | §5.1, §5.2, §5.3, §5.4          |
| 2    | Code quality + analysis tools          | §6.1, §6.2, §6.3, §7.1          |
| 3    | Documentation + final cross-check      | §8, §9                          |

Additionally the polish audit re-runs Step 10.1 Complete Completion
Checklist as a whole and re-executes Step 9.1 Execution Sequence at
smoke-test scale for every variant marked `Yes` in target §10.1.

---

## Step 5: Validate Design

### 5.1 Theory-Code Alignment Check

For each agent (finance appendix: investor), verify that the implementation in `players.py._make_decision()` matches the behavioral framework in `simulation-bases.md §4.{N}.5.4`:

```
For each agent {ClassName}:
  □ Trigger condition in code matches §4.{N}.5.4 Trigger Function exactly
  □ Sizing formula in code matches §4.{N}.5.4 Sizing Function exactly
  □ State variables in code match §4.{N}.5.4 State Variables exactly
  □ Parameters loaded from config match §6 table values
```

### 5.2 Prompt Fidelity Check (LLM-based variants)

```
For each system prompt:
  □ Does NOT name the phenomenon or the environment event
    (finance-appendix example: does not name a specific market event)
  □ Does NOT mention the state-update law or its coefficients
    (finance-appendix example: no reference to the price formula or λ, γ, P(t))
  □ DOES describe agent personality, biases, and decision framework
    (finance-appendix example: investor personality)
  □ Ends with canonical OUTPUT FORMAT block using <analysis> tags
  □ JSON contains exactly the decision fields declared in target §4.1.{X} appendix
    (finance-appendix example: action, bid_price, quantity, reasoning)

For RuleLLM prompts additionally:
  □ == PERSONA == section present and non-empty
  □ == DECISION RULES == section present and non-empty
  □ Rules in DECISION RULES section match Rule variant _make_decision() exactly
  □ ±20% magnitude adjustment allowance explicitly stated
    (finance-appendix example: ±20% quantity adjustment)
```

### 5.3 Configuration Validation Check

```
For each variant's players.yml:
  □ Every numeric extras value has a # Source: comment
  □ Class paths match actual Python class names
  □ All instances are listed in topology.yml

Run YAML syntax validation:
  python -c "import yaml; [yaml.safe_load(open(f'configs/{Sim}/{v}/{f}')) for v in <variants marked Yes in target §10.1> for f in ['simulation.yml','players.yml','topology.yml','persona.yml']]"
```

### 5.4 Diversity Check

```
□ Different time horizons: [list examples]
□ Different information signals: [list which agents use which fields]
□ Conflicting incentives: [identify the conflicting-actions scenario
  — finance-appendix example: buy-vs-sell scenario]
□ Mix of stabilizing/destabilizing: [at least 1 stabilizing]
□ Range of sensitivity/tolerance parameters: [Low to Extreme]
  (finance-appendix example: range of risk tolerances)
```

---

## Step 6: Code Quality Review

### 6.1 Required Documentation Check

```
For each Python file:
  □ Module docstring present with phenomenon, theory references, and sim-bases citations
  □ Coordinator class docstring: state-update law (1-line), parameter list with sim-bases §6 references
    (finance-appendix example: Market class docstring with price formula)
  □ Agent class docstring: role (1 sentence), cites sim-bases §4.{N}, §6
    (finance-appendix example: Investor class docstring)
  □ Every method has a docstring
  □ Complex formula lines have inline comments
```

### 6.2 Correctness Check

```
  □ State-value floor guards: computed state values that must remain positive
    have an explicit floor
    (finance-appendix example: max(price, 0.01))
  □ Action-magnitude constraints: outgoing actions respect resource caps
    (finance-appendix example: sell quantity ≤ position; buy quantity ≤ cash / price)
  □ Denominator-nonzero guards on any deviation / ratio computation
    (finance-appendix example: fundamental ≠ 0 in the deviation calculation)
  □ State initialized once via _initialized flag pattern
```

### 6.3 Style Check

```
  □ Follows project naming conventions (snake_case methods, PascalCase classes)
  □ Uses self.state.custom_state dict for all custom state (not instance variables)
  □ logger.debug() for high-frequency logs; logger.info() for key events only
  □ No print() statements in production code
```

Run `get_problems` on all modified Python files before finalizing.

---

## Step 7: Create Analysis Tools

### 7.1 `Rule/analysis.py` Requirements

All metrics from `analysis-bases.md §2` must be implemented in `calculate_metrics()`. Verify:

```
For each metric in analysis-bases.md §2:
  □ Metric is computed in calculate_metrics()
  □ Formula in code matches formula in analysis-bases.md §2 exactly
  □ Data source file pattern is documented in analysis-bases.md §2 Implementation Notes
```

#### Evaluation-First Import Compliance (MANDATORY)

> Reference: `masim/skills/implement-simulation-skill/10-evaluation-architecture.md`

```
For each analysis.py file in every built variant:
  □ All reusable imports come from masim.evaluation (the sole home for shared evaluation code)
  □ All time-series metrics imported from masim.evaluation.finance.timeseries
  □ All behavioral metrics imported from masim.evaluation.finance.behavioral
  □ All volatility metrics imported from masim.evaluation.finance.volatility
  □ All microstructure metrics imported from masim.evaluation.finance.microstructure
  □ All reusable plot functions imported from masim.evaluation.finance.visualization
  □ Scenario validation function imported from masim.evaluation.finance.validation
  □ Metric registry types (if used) imported from masim.evaluation.registry
  □ Data loading utilities imported from masim.evaluation.data_loader
  □ Any NEW reusable function was FIRST added to masim/evaluation/ before being called
  □ Only scenario-specific orchestration logic (analyze_{scenario}, _validate_{scenario}) remains local
```

If a needed metric/function does NOT yet exist in `masim/evaluation/`:
1. Implement it in the correct `masim/evaluation/` submodule
2. Add to `__all__` and re-export through `__init__.py`
3. Then import it in the scenario's `analysis.py`

Minimum plots from `analysis-bases.md §7`:
1. Environment state vs. Anchor / Reference over time (with threshold lines)
   — finance-appendix example: Price vs. Fundamental over time
2. Phenomenon intensity metric over time (e.g., deviation %, drawdown %, adoption %, prevalence %)
3. Agent participation / performance comparison
   — finance-appendix example: Agent portfolio performance
4. Phase detection overlay on the environment-state trajectory
   — finance-appendix example: overlay on the price chart
5. Cross-variant comparison summary

### 7.2 Variant-Specific Analysis Functions

```
LLM variant:
  □ analyze_action_distribution(agent_records) implemented

RuleLLM variant:
  □ analysis.py reuses core metrics from Rule/analysis.py
  □ No additional variant-specific analysis function required

Rag variant:
  □ _RAG_FALLBACK = "(No relevant knowledge retrieved this round.)" defined
  □ analyze_rag_knowledge_effect(agent_records) implemented
  □ Returns retrieval_success_rate per agent; meets_target (≥0.70) per agent
```

---

## Step 8: Create Documentation

### Writing Order

```
1. simulation-bases.md         ← Write BEFORE any code; drives all implementations
2. analysis-bases.md           ← Write alongside simulation-bases.md
3. Rule/players.py             ← Implement the deterministic-baseline variant first
4. Rule/explain.md             ← Write IMMEDIATELY after Rule/players.py
5. Rule/analysis.py            ← Implement Rule analysis
6. Rule/analysis.md            ← Write immediately after Rule/analysis.py
7. Repeat steps 3-6 for each remaining variant declared Yes in target §10.1
   (finance-default sequence: LLM, RuleLLM, Rag)
8. Update simulation-bases.md §9 (Variant Comparison Preview) with actual observations
```

### Documentation Quality Gate

Before any variant is considered complete:

```
simulation-bases.md:
  □ All 9 sections present
  □ §2: ≥2 theories with DOIs and mathematical formulations
  □ §4: Every agent has all 7 parts (including numerical examples)
    (finance-appendix example: every investor has all 7 parts)
  □ §4: NO variant-specific behavior sections present
    (finance-default forbidden section names: Rule-Based Behavior /
     LLM Persona / RuleLLM Hybrid Notes)
  □ §6: Every parameter has source citation

analysis-bases.md:
  □ All 7 sections present
  □ §2: ≥6 metrics with formulas and DOIs
  □ §6: Calibration targets with specific literature ranges

{Variant}/explain.md:
  □ All 9 sections present
  □ §2: Every agent maps to code location using sim-bases §N.M notation
    (finance-appendix example: every investor maps to code)
  □ §3: Every state-update law symbol maps to Python variable + config path
    (finance-appendix example: every price-formula symbol maps to Python variable + config path)
  □ §4: Variant-specific features documented with sim-bases §9 justification

{Variant}/analysis.md:
  □ All 7 sections present
  □ §2: Every metric maps to analysis.py function
  □ §4: Variant-specific observable phenomena documented
```

---

## Step 9: Execute and Debug

### 9.1 Execution Sequence

Run the four canonical variants in this fixed order — `Rule` → `LLM` → `RuleLLM` → `Rag` — for every variant declared `Yes` in target §10.1. Any variant declared `No` is skipped in place (its step becomes a no-op), but no re-ordering is permitted. The canonical set is fixed by `01-mandatory-structure.md § Canonical Variant Set`; adding a variant requires an explicit implement-* upgrade.

```bash
# Step 1: Run Rule variant
python examples/{Sim}/Rule/run_{name}.py -c configs/{Sim}/Rule/simulation.yml

# Step 2: Verify outputs exist
ls EXPERIMENT/{Sim}/Rule/records/

# Step 3: Run analysis
python examples/{Sim}/Rule/analysis.py -c configs/{Sim}/Rule/simulation.yml

# Step 4: Check plots
ls EXPERIMENT/{Sim}/Rule/analysis/

# Step 5: Run LLM variant (requires API key in .env)
python examples/{Sim}/LLM/run_{name}_llm.py -c configs/{Sim}/LLM/simulation.yml

# Step 6: Run RuleLLM
python examples/{Sim}/RuleLLM/run_{name}_rulellm.py -c configs/{Sim}/RuleLLM/simulation.yml

# Step 7: Run Rag (first run builds index — slow)
python examples/{Sim}/Rag/run_{name}_rag.py -c configs/{Sim}/Rag/simulation.yml
```

### 9.2 Common Issues

| Issue                       | Diagnosis                  | Solution                                           |
|-----------------------------|----------------------------|----------------------------------------------------|
| ImportError on run          | sys.path not set up        | Verify project root in sys.path; check __init__.py |
| No agent actions generated (finance appendix: no orders) | Trigger threshold too strict | Relax trigger threshold in players.yml           |
| Environment state collapses to a degenerate value early (finance appendix: price goes to 0 immediately) | Coordinator response coefficient too high (finance-appendix example: λ too high) | Reduce the coordinator response coefficient (finance-appendix example: reduce `price_impact`) |
| LLM returns invalid JSON    | Prompt unclear             | Strengthen OUTPUT FORMAT section; add example      |
| Phenomenon not appearing    | Restoring/mean-reversion coefficient too high (finance-appendix example: γ too high, fast recovery) | Reduce the restoring coefficient (finance-appendix example: reduce `mean_reversion`) |
| Rag index fails to build    | docs_dir empty             | Add documents to docs_dir                          |

### 9.3 Phenomenon Verification

After a successful 200-round run, verify:

```
□ Environment-state deviation chart shows the target phenomenon
  (finance-appendix example: price deviation chart with cascade / bubble / bias)
□ Phenomenon intensity metric reaches the calibration target range from analysis-bases.md §6
□ Each agent type acts as expected
  (finance-appendix example: volume-by-agent-type chart, each type trades as expected)
□ Phase transitions visible at expected rounds
```

---

## Step 10: Final Review

### 10.1 Complete Completion Checklist

**Root Documentation**:
- [ ] `simulation-bases.md` — all 9 sections
- [ ] `simulation-bases.md §4` — every agent has all 7 parts (finance-appendix example: every investor)
- [ ] `simulation-bases.md §4` — NO variant-specific behavior sections (finance-default forbidden section names: Rule-Based Behavior / LLM Persona / RuleLLM Hybrid Notes)
- [ ] `simulation-bases.md §6` — every parameter has source citation
- [ ] `analysis-bases.md` — all 7 sections
- [ ] `analysis-bases.md §2` — ≥6 metrics with formulas and DOI citations
- [ ] `analysis-bases.md §6` — calibration targets with literature ranges

**Code** — every canonical variant declared `Yes` in target §10.1 MUST pass its named checks below. The canonical set is exactly four variants: `Rule`, `LLM`, `RuleLLM`, `Rag` (see `01-mandatory-structure.md § Canonical Variant Set`). No variant may be silently skipped; introducing a new variant requires an explicit implement-* upgrade first.
- [ ] `Rule/players.py` — all agents; docstrings cite sim-bases §4.{N}
- [ ] `Rule/run_*.py` — works with `python run.py -c config.yml`
- [ ] `Rule/analysis.py` — exports `__all__`; all metrics implemented
- [ ] `Rule/analysis.py` — evaluation-first: all reusable metrics/viz/validation imported from `masim/evaluation/` (see `10-evaluation-architecture.md`)
- [ ] `LLM/prompts.py` — no phenomenon name; correct output format per §3.6.0 I/O Contract; `<analysis>` tags present
- [ ] `LLM/players.py` — LLM decision-field access rule (§4.2.3) honoured; fail-fast on unparseable model output
- [ ] `LLM/analysis.py` — exports `__all__`; imports shared loaders from `Rule/analysis.py`
- [ ] `RuleLLM/prompts.py` — `== PERSONA ==` + `== DECISION RULES ==` present; decision rules exactly reproduce `Rule/players.py` formulas
- [ ] `RuleLLM/players.py` — same output schema as `LLM`; hybrid path fail-fast when LLM output diverges from encoded rules
- [ ] `RuleLLM/analysis.py` — reuses `Rule` core metrics; no variant-specific analysis function unless declared in `analysis-bases.md`
- [ ] `Rag/players.py` — `_initialize_rag()`, `_formulate_knowledge_query()`, `_get_rag_context()` implemented; retrieval fallback sentinel injected verbatim when retrieval is empty
- [ ] `Rag/prompts.py` — retrieval context slot present in user template; retrieval-fallback sentinel string declared and matches `_RAG_FALLBACK`
- [ ] `Rag/analysis.py` — `_RAG_FALLBACK` defined; `analyze_rag_knowledge_effect()` implemented

**Per-Variant Documentation** — repeat each check below independently for each of `Rule`, `LLM`, `RuleLLM`, `Rag` declared `Yes` in target §10.1 (the four canonical variants — see `01-mandatory-structure.md § Canonical Variant Set`):
- [ ] `explain.md` — all 9 sections
- [ ] `explain.md §2` — every agent traces to code location via sim-bases §N.M (finance-appendix example: every investor)
- [ ] `analysis.md` — all 7 sections
- [ ] `analysis.md §2` — every metric traces to analysis.py function

**Integration**:
- [ ] Every built variant runs successfully
- [ ] Analysis scripts produce output for at least the deterministic-baseline variant (finance-default: Rule)
- [ ] Phenomenon clearly visible in the environment-state chart output (finance-appendix example: price chart)
- [ ] `SCENARIO_PATH_MAP` in WebUI updated to include new simulation
- [ ] WebUI discovers simulation (run WebUI and verify it appears in scenario list)

### 10.2 Quality Standards Summary

| Standard              | Requirement                                                    |
|-----------------------|----------------------------------------------------------------|
| Theory quality        | Every claim backed by DOI citation; equations present          |
| Parameter quality     | Every value has empirical source; no "intuition"               |
| Code quality          | No hardcoded values; all docstrings cite sim-bases; no print() |
| Documentation quality | No duplication between sim-bases and explain.md                |
| Prompt quality        | No phenomenon name; canonical output format                    |
| Analysis quality      | All analysis-bases.md §2 metrics implemented; DRY imports      |
