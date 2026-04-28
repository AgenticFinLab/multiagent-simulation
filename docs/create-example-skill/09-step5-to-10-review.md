# Steps 5–10: Validate, Review, Analyze, Document, Execute, and Final Review

## Step 5: Validate Design

### 5.1 Theory-Code Alignment Check

For each investor, verify that the implementation in `players.py._make_decision()` matches the behavioral framework in `simulation-bases.md §4.{N}.4.3`:

```
For each investor {ClassName}:
  □ Trigger condition in code matches §4.{N}.4.3 Trigger Function exactly
  □ Sizing formula in code matches §4.{N}.4.3 Sizing Function exactly
  □ State variables in code match §4.{N}.4.3 State Variables exactly
  □ Parameters loaded from config match §6 table values
```

### 5.2 Prompt Fidelity Check (LLM/RuleLLM/Rag)

```
For each system prompt:
  □ Does NOT name the phenomenon or the market event
  □ Does NOT mention the price formula or its symbols (λ, γ, P(t))
  □ DOES describe investor personality, biases, and decision framework
  □ Ends with canonical OUTPUT FORMAT block using <analysis> tags
  □ JSON contains action, bid_price, quantity, reasoning fields

For RuleLLM prompts additionally:
  □ == PERSONA == section present and non-empty
  □ == DECISION RULES == section present and non-empty
  □ Rules in DECISION RULES section match Rule variant _make_decision() exactly
  □ ±20% quantity adjustment allowance explicitly stated
```

### 5.3 Configuration Validation Check

```
For each variant's players.yml:
  □ Every numeric extras value has a # Source: comment
  □ Class paths match actual Python class names
  □ All instances are listed in topology.yml

Run YAML syntax validation:
  python -c "import yaml; [yaml.safe_load(open(f'configs/{Sim}/{v}/{f}')) for v in ['Rule','LLM','RuleLLM','Rag'] for f in ['simulation.yml','players.yml','topology.yml','persona.yml']]"
```

### 5.4 Diversity Check

```
□ Different time horizons: [list examples]
□ Different information signals: [list which agents use which fields]
□ Conflicting incentives: [identify the buy-vs-sell scenario]
□ Mix of stabilizing/destabilizing: [at least 1 stabilizing]
□ Range of risk tolerances: [Low to Extreme]
```

---

## Step 6: Code Quality Review

### 6.1 Required Documentation Check

```
For each Python file:
  □ Module docstring present with phenomenon, theory references, and sim-bases citations
  □ Market class docstring: price formula (1-line), parameter list with sim-bases §6 references
  □ Investor class docstring: role (1 sentence), cites sim-bases §4.{N}, §6
  □ Every method has a docstring
  □ Complex formula lines have inline comments
```

### 6.2 Correctness Check

```
  □ Price calculations use max(price, 0.01) or similar floor
  □ Position checks: sell quantity ≤ position; buy quantity ≤ cash/price
  □ Division by zero guarded: fundamental ≠ 0 in deviation calculation
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

Minimum plots from `analysis-bases.md §7`:
1. Price vs. Fundamental over time (with threshold lines)
2. Phenomenon intensity metric over time (e.g., deviation %, drawdown %)
3. Agent/portfolio performance comparison
4. Phase detection overlay on price chart
5. Cross-variant comparison summary

### 7.2 Variant-Specific Analysis Functions

```
LLM variant:
  □ analyze_action_distribution(agent_records) implemented

RuleLLM variant:
  □ analyze_rule_adherence(agent_records) implemented
  □ Returns adherence_rate per agent; meets_target (≥0.80) per agent

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
3. Rule/players.py             ← Implement first variant
4. Rule/explain.md             ← Write IMMEDIATELY after Rule/players.py
5. Rule/analysis.py            ← Implement Rule analysis
6. Rule/analysis.md            ← Write immediately after Rule/analysis.py
7. [Repeat steps 3-6 for LLM, RuleLLM, Rag]
8. Update simulation-bases.md §9 (Variant Comparison Preview) with actual observations
```

### Documentation Quality Gate

Before any variant is considered complete:

```
simulation-bases.md:
  □ All 9 sections present
  □ §2: ≥2 theories with DOIs and mathematical formulations
  □ §4: Every investor has all 7 parts (including numerical examples)
  □ §4: NO Rule-Based Behavior, LLM Persona, RuleLLM Hybrid Notes present
  □ §6: Every parameter has source citation

analysis-bases.md:
  □ All 7 sections present
  □ §2: ≥6 metrics with formulas and DOIs
  □ §6: Calibration targets with specific literature ranges

{Variant}/explain.md:
  □ All 9 sections present
  □ §2: Every investor maps to code location using sim-bases §N.M notation
  □ §3: Every price formula symbol maps to Python variable + config path
  □ §4: Variant-specific features documented with sim-bases §9 justification

{Variant}/analysis.md:
  □ All 7 sections present
  □ §2: Every metric maps to analysis.py function
  □ §4: Variant-specific observable phenomena documented
```

---

## Step 9: Execute and Debug

### 9.1 Execution Sequence

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
| No orders generated         | Threshold too strict       | Relax trigger threshold in players.yml             |
| Price goes to 0 immediately | λ too high                 | Reduce price_impact                                |
| LLM returns invalid JSON    | Prompt unclear             | Strengthen OUTPUT FORMAT section; add example      |
| Phenomenon not appearing    | γ too high (fast recovery) | Reduce mean_reversion                              |
| Rag index fails to build    | docs_dir empty             | Add documents to docs_dir                          |

### 9.3 Phenomenon Verification

After a successful 200-round run, verify:

```
□ Price deviation chart shows the target phenomenon (e.g., cascade, bubble, bias)
□ Phenomenon intensity metric reaches the calibration target range from analysis-bases.md §6
□ Each agent type trades as expected (volume by agent type chart)
□ Phase transitions visible at expected rounds
```

---

## Step 10: Final Review

### 10.1 Complete Completion Checklist

**Root Documentation**:
- [ ] `simulation-bases.md` — all 9 sections
- [ ] `simulation-bases.md §4` — every investor has all 7 parts
- [ ] `simulation-bases.md §4` — NO variant-specific sections (Rule-Based Behavior / LLM Persona / RuleLLM Hybrid Notes)
- [ ] `simulation-bases.md §6` — every parameter has source citation
- [ ] `analysis-bases.md` — all 7 sections
- [ ] `analysis-bases.md §2` — ≥6 metrics with formulas and DOI citations
- [ ] `analysis-bases.md §6` — calibration targets with literature ranges

**Code**:
- [ ] `Rule/players.py` — all agents; docstrings cite sim-bases §4.{N}
- [ ] `Rule/run_*.py` — works with `python run.py -c config.yml`
- [ ] `Rule/analysis.py` — exports `__all__`; all metrics implemented
- [ ] `LLM/prompts.py` — no phenomenon name; correct output format; `<analysis>` tags
- [ ] `RuleLLM/prompts.py` — `== PERSONA ==` + `== DECISION RULES ==` present
- [ ] `Rag/players.py` — `_initialize_rag()`, `_formulate_knowledge_query()`, `_get_rag_context()`
- [ ] `Rag/analysis.py` — `_RAG_FALLBACK` defined; `analyze_rag_knowledge_effect()` implemented

**Per-Variant Documentation** (Rule, LLM, RuleLLM, Rag):
- [ ] `explain.md` — all 9 sections
- [ ] `explain.md §2` — every investor traces to code location via sim-bases §N.M
- [ ] `analysis.md` — all 7 sections
- [ ] `analysis.md §2` — every metric traces to analysis.py function

**Integration**:
- [ ] All 4 variants run successfully
- [ ] Analysis scripts produce output for at least Rule variant
- [ ] Phenomenon clearly visible in price chart output
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
