# Validation Checklist

## Purpose

This file defines the **final verification gates** that must all pass before a simulation is marked complete. Run this checklist after all repair phases are done for a simulation.

The checklist is organized in four layers — from structure down to cross-consistency. Each layer must pass completely before moving to the next.

---

## Layer 1 — File Existence

All expected files must exist. Verify:

```bash
for f in simulation-bases.md analysis-bases.md \
          Rule/explain.md Rule/analysis.md Rule/players.py \
          LLM/explain.md LLM/analysis.md LLM/players.py LLM/prompts.py \
          RuleLLM/explain.md RuleLLM/analysis.md RuleLLM/players.py RuleLLM/prompts.py \
          Rag/explain.md Rag/analysis.md Rag/players.py Rag/prompts.py; do
  if [ ! -f "examples/<Scenario>/$f" ]; then
    echo "MISSING: examples/<Scenario>/$f"
  fi
done
```

**Pass criteria**: Zero missing files.

---

## Layer 2 — Documentation Structure

### §2.1 `simulation-bases.md`

```bash
# Must have exactly 9 sections
grep -c "^## §" examples/<Scenario>/simulation-bases.md
# Expected: 9

# Must have one entry per investor (§4.N headers)
grep "^### §4\." examples/<Scenario>/simulation-bases.md
# Expected: one line per investor class (excluding Market)

# Must have all 7 parts per investor
for part in "Summary" "Theoretical and Empirical" "Design Purpose" \
            "Behavioral Framework" "Decision Process" "Worked Numerical" "Academic References"; do
  count=$(grep -c "$part" examples/<Scenario>/simulation-bases.md)
  echo "$part: $count"
done
# Expected: each >= number of investors

# Must NOT contain Rule/LLM-specific content in §4
grep -n "if.*threshold\|System prompt\|LLM persona\|RuleLLM" examples/<Scenario>/simulation-bases.md
# Expected: zero matches
```

**Checklist**:
- [ ] 9 sections present (§1–§9)
- [ ] §4 has correct number of investor entries
- [ ] Every §4 entry has all 7 parts
- [ ] §4 contains no Rule/LLM/RuleLLM implementation content
- [ ] §2 has ≥3 DOI citations
- [ ] §6 parameter table present
- [ ] §8 has ≥2 historical cases

### §2.2 `analysis-bases.md`

```bash
# Must have exactly 7 sections
grep -c "^## §" examples/<Scenario>/analysis-bases.md
# Expected: 7

# Must have ≥5 metrics
grep -c "^### §2\." examples/<Scenario>/analysis-bases.md
# Expected: ≥5

# Must have Python function signatures
grep -c "def " examples/<Scenario>/analysis-bases.md
# Expected: ≥5 (one per metric)
```

**Checklist**:
- [ ] 7 sections present (§1–§7)
- [ ] ≥5 metrics in §2
- [ ] Every metric has a Python function signature with named arguments
- [ ] §6 expected results cover all agent types

### §2.3 `{Variant}/explain.md` — for all four variants

```bash
for variant in Rule LLM RuleLLM Rag; do
  echo "=== $variant/explain.md ==="
  # Must have §1 Overview
  grep -c "^## §1" examples/<Scenario>/$variant/explain.md
  # Must have §2 Theory → Implementation
  grep -c "^### §2\." examples/<Scenario>/$variant/explain.md
  # Must cite simulation-bases.md §4
  grep -c "simulation-bases.md §4\." examples/<Scenario>/$variant/explain.md
  # Must have mapping tables
  grep -c "Theory Component" examples/<Scenario>/$variant/explain.md
done
```

**Checklist** (for each variant):
- [ ] §1 present with overview table (5 rows)
- [ ] §2 has one subsection per investor
- [ ] Every §2 subsection has a 2-column mapping table
- [ ] Every §2 subsection cites `simulation-bases.md §4.N`
- [ ] §3 has price formula
- [ ] §7 has specific expected metric values (not "varies by scenario")
- [ ] §8 references `simulation-bases.md §2`

### §2.4 `{Variant}/analysis.md` — for all four variants

```bash
for variant in Rule LLM RuleLLM Rag; do
  echo "=== $variant/analysis.md ==="
  # Must have 5 sections
  grep -c "^## §" examples/<Scenario>/$variant/analysis.md
  # Must reference analysis-bases.md
  grep -c "analysis-bases.md §2\." examples/<Scenario>/$variant/analysis.md
  # Must have 7-metric table
  grep -c "^| " examples/<Scenario>/$variant/analysis.md
done
```

**Checklist** (for each variant):
- [ ] 5 sections present (§1–§5)
- [ ] §2 metric table has all 7 metrics
- [ ] Every metric row has `analysis-bases.md §2.X` reference
- [ ] §3 has variant-specific notes (not generic)
- [ ] §4 expected ranges are numeric (no "varies by scenario")
- [ ] §5 references both `analysis-bases.md §2` and `simulation-bases.md §4`

---

## Layer 3 — Code Compliance

### §3.1 Syntax check

```bash
python3 -c "
import glob, py_compile, sys
files = sorted(glob.glob('examples/<Scenario>/**/*.py', recursive=True))
errors = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        errors.append(str(e))
if errors:
    for e in errors: print('ERROR:', e)
    sys.exit(1)
else:
    print(f'ALL OK: {len(files)} files')
"
```

**Pass criteria**: Zero errors.

### §3.2 Docstring citation coverage

```bash
for variant in Rule LLM RuleLLM Rag; do
  theory_count=$(grep -c "simulation-bases.md §4" examples/<Scenario>/$variant/players.py 2>/dev/null || echo 0)
  # Count investor classes (exclude Market and base classes)
  class_count=$(grep "^class [A-Z]" examples/<Scenario>/$variant/players.py | grep -v "class Market\|Investor:\|Player:" | wc -l)
  echo "$variant: $theory_count citations / $class_count investor classes"
done
```

**Pass criteria**: citation count = investor class count for every variant.

### §3.3 Import correctness

```bash
# Wrong modules
grep -rn "masim.interface.inference\|masim.utils.prompt\|masim.utils.llm_utils\|LLMClient" \
  examples/<Scenario>/*/players.py
# Expected: zero matches

# Wrong InferInput kwargs
grep -rn "InferInput(" examples/<Scenario>/*/players.py | grep -E "sys_message=|user_message=|\bsystem=|\buser="
# Expected: zero matches

# Wrong LangChainAPIInference kwargs
grep -rn "LangChainAPIInference" examples/<Scenario>/*/players.py | grep -E "api_key=|model=|base_url="
# Expected: zero matches

# Wrong method calls
grep -rn "\.ainfer\|\.infer(" examples/<Scenario>/*/players.py
# Expected: zero matches
```

**Checklist**:
- [ ] No `masim.interface.inference` imports
- [ ] No `masim.utils.prompt` imports
- [ ] No `LLMClient` usage
- [ ] `InferInput` uses `system_msg=` and `user_msg=`
- [ ] `LangChainAPIInference` uses only `lm_name=` and `generation_config=`
- [ ] No `.ainfer()` or `.infer()` calls (use `.run()`)

### §3.4 Output format tags in prompts

```bash
grep -rn "<think>" examples/<Scenario>/*/prompts.py
# Expected: zero matches
```

**Pass criteria**: all prompts use `<analysis>` tag, not `<think>`.

### §3.5 Ray serialization (LLM/RuleLLM/Rag)

```bash
for variant in LLM RuleLLM Rag; do
  echo "$variant:"
  grep -c "__getstate__\|__setstate__" examples/<Scenario>/$variant/players.py
  # Expected: 2 (one of each)
done
```

### §3.6 `analysis.py` output standard

Verify each `Rule/analysis.py` produces a structured validation report. Run the analysis script and check its output against the requirements in `docs/create-example-skill/08-step4-implement.md §4.1.4`.

```bash
# 1. Run Rule analysis
conda run -n LMSim python examples/<Scenario>/Rule/analysis.py \
    -c configs/<Scenario>/Rule/simulation.yml

# 2. Check output directory contents
ls EXPERIMENT/<Scenario>/Rule/analysis/
# Expected: 01_*.png  02_*.png  03_*.png  summary.json

# 3. Check summary.json has validation block
python3 -c "
import json
d = json.load(open('EXPERIMENT/<Scenario>/Rule/analysis/summary.json'))
print('score:', d['validation']['score'])
print('is_valid:', d['validation']['is_valid'])
print('criteria keys:', list(d['validation']['criteria'].keys()))
"

# 4. Check all four variants compile
conda run -n LMSim python -c "
import glob, py_compile, sys
for f in sorted(glob.glob('examples/<Scenario>/*/analysis.py')):
    try: py_compile.compile(f, doraise=True); print('OK:', f)
    except py_compile.PyCompileError as e: print('ERROR:', e); sys.exit(1)
"
```

**Pass criteria**:
- [ ] Console output contains `=== {SCENARIO} SIMULATION VALIDATION: VALID|INVALID ===`
- [ ] Console output contains `Overall Fit Score: XX.X% (threshold: 50%)`
- [ ] Console output contains `[1]`, `[2]` criterion blocks with `Observed:`, `Expected:`, `Score:`, `Assessment:`
- [ ] Console output contains `[SUMMARY]` block
- [ ] `01_*.png`, `02_*.png`, `03_*.png` all present in `analysis/`
- [ ] `summary.json` contains `validation.score`, `validation.is_valid`, `validation.criteria`
- [ ] All four variant `analysis.py` files pass `py_compile`

---

## Layer 4 — Cross-Consistency

### §4.1 §4.N numbering consistency

The `§4.N` numbers used in:
- `simulation-bases.md §4` headings (`### §4.1`, `### §4.2`, ...)
- `Rule/explain.md §2` subsection headings (`### §2.1 ... (simulation-bases.md §4.1)`)
- `Rule/players.py` class docstrings (`Theory: simulation-bases.md §4.1`)

All must refer to the same investor using the same number.

```bash
# Extract §4.N headings from simulation-bases.md
grep "^### §4\." examples/<Scenario>/simulation-bases.md

# Compare with explain.md §2 subsections (should match)
grep "simulation-bases.md §4\." examples/<Scenario>/Rule/explain.md

# Compare with players.py docstrings (should match)
grep "simulation-bases.md §4\." examples/<Scenario>/Rule/players.py
```

### §4.2 Investor class count consistency

The number of investor classes in `Rule/players.py` (excluding Market and base classes) must equal:
- The number of §4.N entries in `simulation-bases.md`
- The number of §2.N subsections in `Rule/explain.md`
- The number of rows in `Rule/analysis.md §2` metric table (same metrics, all variants)

### §4.3 Function name consistency (analysis)

Python function names in `analysis-bases.md §2` must exactly match function names in all variant `analysis.md §2` tables.

```bash
# Extract function names from analysis-bases.md
grep "def " examples/<Scenario>/analysis-bases.md | grep -o "def [a-z_]*()"

# Compare with all analysis.md tables
grep "`[a-z_]*(" examples/<Scenario>/Rule/analysis.md
```

---

## §5 Validation Pass/Fail Summary

Use this table to track results:

```
## Validation Results — <SimulationName>

| Layer   | Check                         | Status      |
|---------|-------------------------------|-------------|
| Layer 1 | File existence                | PASS / FAIL |
| Layer 2 | simulation-bases.md structure | PASS / FAIL |
| Layer 2 | analysis-bases.md structure   | PASS / FAIL |
| Layer 2 | Rule/explain.md               | PASS / FAIL |
| Layer 2 | Rule/analysis.md              | PASS / FAIL |
| Layer 2 | LLM/explain.md                | PASS / FAIL |
| Layer 2 | LLM/analysis.md               | PASS / FAIL |
| Layer 2 | RuleLLM/explain.md            | PASS / FAIL |
| Layer 2 | RuleLLM/analysis.md           | PASS / FAIL |
| Layer 2 | Rag/explain.md                | PASS / FAIL |
| Layer 2 | Rag/analysis.md               | PASS / FAIL |
| Layer 3 | Syntax check                  | PASS / FAIL |
| Layer 3 | Docstring citations           | PASS / FAIL |
| Layer 3 | Import correctness            | PASS / FAIL |
| Layer 3 | Output format tags            | PASS / FAIL |
| Layer 3 | Ray serialization             | PASS / FAIL |
| Layer 3 | analysis.py output standard   | PASS / FAIL |
| Layer 4 | §4.N numbering consistency    | PASS / FAIL |
| Layer 4 | Investor count consistency    | PASS / FAIL |
| Layer 4 | Function name consistency     | PASS / FAIL |

Overall: COMPLETE / INCOMPLETE
```

**Definition of COMPLETE**: All checks PASS. The simulation's audit row in the Current State Summary can be updated to all ✓.

---

## §6 Quick Final Check Command Set

Run these commands as the final confirmation before marking any simulation complete:

```bash
SIM=<Scenario>

echo "=== FILE EXISTENCE ==="
for f in simulation-bases.md analysis-bases.md \
  Rule/explain.md Rule/analysis.md \
  LLM/explain.md LLM/analysis.md \
  RuleLLM/explain.md RuleLLM/analysis.md \
  Rag/explain.md Rag/analysis.md; do
  [ -f "examples/$SIM/$f" ] && echo "OK: $f" || echo "MISSING: $f"
done

echo ""
echo "=== SECTION COUNTS ==="
echo "simulation-bases.md sections: $(grep -c '^## §' examples/$SIM/simulation-bases.md)"
echo "analysis-bases.md sections: $(grep -c '^## §' examples/$SIM/analysis-bases.md)"
echo "analysis-bases.md metrics: $(grep -c '^### §2\.' examples/$SIM/analysis-bases.md)"

echo ""
echo "=== DOCSTRING CITATIONS ==="
for variant in Rule LLM RuleLLM Rag; do
  count=$(grep -c "simulation-bases.md §4" examples/$SIM/$variant/players.py 2>/dev/null || echo 0)
  echo "$variant: $count"
done

echo ""
echo "=== SYNTAX CHECK ==="
python3 -c "
import glob, py_compile, sys
files = sorted(glob.glob('examples/$SIM/**/*.py', recursive=True))
errors = []
for f in files:
    try: py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e: errors.append(str(e))
print(f'ERRORS: {len(errors)}' if errors else f'ALL OK: {len(files)} files')
"

echo ""
echo "=== WRONG IMPORTS ==="
grep -rn "masim.interface.inference\|masim.utils.prompt\|LLMClient" examples/$SIM/*/players.py | wc -l

echo ""
echo "=== DEPRECATED THINK TAG ==="
grep -rn "<think>" examples/$SIM/*/prompts.py | wc -l
```

**Expected output for a fully complete simulation**:
- All files: `OK`
- simulation-bases.md sections: `9`
- analysis-bases.md sections: `7`
- analysis-bases.md metrics: `≥5`
- All variant docstring citation counts: `≥N` (where N = number of investor classes)
- Syntax check: `ALL OK`
- Wrong imports: `0`
- Deprecated think tag: `0`
