# Current State Audit

## Purpose

This file defines how to produce the **Current State Summary** — the mandatory first deliverable of every revision session. The Current State Summary is a table that maps every simulation in `00-simulations.md` to the exact compliance status of each file it should contain.

No repair work begins until the Current State Summary is complete.

---

## §1 The Audit Matrix

For each simulation, assess the following files:

| Symbol  | Meaning                                                 |
|---------|---------------------------------------------------------|
| ✓       | File exists and is spec-compliant                       |
| ✓(lean) | File exists but is thin / non-compliant (needs rewrite) |
| -       | File is missing entirely (needs creation)               |
| ✗       | File is missing at root level (needs creation)          |

### Columns

| Column           | Checks                                                                                |
|------------------|---------------------------------------------------------------------------------------|
| `sim-bases`      | `simulation-bases.md` exists AND has 9 sections AND uses 7-part investor standard     |
| `analysis-bases` | `analysis-bases.md` exists AND has 7 sections AND includes Python function signatures |
| `Rule[E/A]`      | `Rule/explain.md` / `Rule/analysis.md` — E=explain, A=analysis                        |
| `LLM[E/A]`       | `LLM/explain.md` / `LLM/analysis.md`                                                  |
| `RuleLLM[E/A]`   | `RuleLLM/explain.md` / `RuleLLM/analysis.md`                                          |
| `Rag[E/A]`       | `Rag/explain.md` / `Rag/analysis.md`                                                  |

### Template Matrix

```
| Simulation | sim-bases | analysis-bases | Rule[E/A] | LLM[E/A] | RuleLLM[E/A] | Rag[E/A] |
|------------|-----------|----------------|-----------|----------|--------------|----------|
| <Name>     |           |                | /         | /        | /            | /        |
```

---

## §2 How to Assess Each File

### §2.1 `simulation-bases.md` — compliant (✓) if ALL of:

1. File exists at `{Path}/simulation-bases.md`
2. Contains exactly 9 sections: §1 Phenomenon, §2 Theory, §3 Market Design, §4 Investor Taxonomy, §5 Agent Diversity, §6 Parameter Table, §7 Round Structure, §8 Historical Cases, §9 Variant Comparison
3. §4 has one entry per investor, each with all 7 parts (Summary, Theoretical Foundation, Design Purpose, Behavioral Framework, Decision Process, Worked Example, References)
4. §2 has DOI citations for all key references
5. §4 contains NO Rule-Based Behavior, LLM Persona, or RuleLLM Hybrid Notes

Mark `✓(lean)` if the file exists but is missing sections or uses a non-standard structure (e.g., only bullet lists instead of 7-part investor entries, no DOIs, fewer than 9 sections).

Mark `✗` if the file does not exist.

### §2.2 `analysis-bases.md` — compliant (✓) if ALL of:

1. File exists at `{Path}/analysis-bases.md`
2. Contains exactly 7 sections: §1 Objectives, §2 Core Metrics, §3 Analysis Dimensions, §4 Phase Analysis, §5 Cross-Variant Comparison, §6 Expected Results, §7 Visualization Catalogue
3. §2 has at least 5 metrics, each with: metric name, formula, Python function signature with argument names

Mark `✓(lean)` if fewer than 7 sections or metrics lack Python function signatures.

Mark `✗` if missing.

### §2.3 `{Variant}/explain.md` — compliant (✓) if ALL of:

1. File exists
2. Contains at least 8 sections beginning with `§1 Overview`
3. Has a `§2 Theory → Implementation Mapping` section with one subsection per investor type
4. Each subsection uses a 2-column table: `Theory Component | Implementation`
5. Each investor subsection explicitly cites `simulation-bases.md §4.N`
6. Contains NO re-explanation of theory already in `simulation-bases.md` — only cites it

Mark `✓(lean)` if the file exists but is a narrative description / agent parameter list / usage guide — i.e., it has no Theory→Implementation mapping tables, or does not cite `simulation-bases.md §4.N`.

Mark `-` if missing.

### §2.4 `{Variant}/analysis.md` — compliant (✓) if ALL of:

1. File exists
2. Contains exactly 7 sections beginning with `§1 Overview`
3. Has a `§2 Metric → Function Mapping` table with all 7 metrics from `analysis-bases.md §2`
4. Has `§3` dimension-by-dimension analysis linked to `analysis-bases.md §3`
5. Has `§4` variant-specific observable phenomena
6. Has `§5` scaling/sensitivity, `§6` output files reference, and `§7` cross-variant comparison notes
7. References `analysis-bases.md §2.X` for each metric

Mark `✓(lean)` if the file uses generic language ("Varies by scenario"), lacks
the metric→function mapping table, or has only the old 5-section structure.

Mark `-` if missing.

### §2.5 `players.py` docstrings — assessed separately in `04-code-repair.md`

For the Current State Summary, note whether player docstrings have been patched or not. This is a separate audit column or a note under the simulation row.

---

## §3 Producing the Current State Summary

### §3.1 For each simulation in `00-simulations.md`:

1. List all files under `{Path}/` and `{Path}/{Variant}/`
2. For each expected file, assign ✓ / ✓(lean) / - / ✗ per the criteria in §2
3. Fill one row of the matrix table

### §3.2 Quick file-existence scan

```bash
# Run from project root
for sim in <sim1> <sim2> ...; do
  echo "=== $sim ==="
  for f in simulation-bases.md analysis-bases.md \
            Rule/explain.md Rule/analysis.md \
            LLM/explain.md LLM/analysis.md \
            RuleLLM/explain.md RuleLLM/analysis.md \
            Rag/explain.md Rag/analysis.md; do
    path="examples/$sim/$f"
    if [ -f "$path" ]; then
      lines=$(wc -l < "$path")
      echo "  ✓ $f ($lines lines)"
    else
      echo "  - MISSING: $f"
    fi
  done
done
```

A file with fewer than 50 lines is almost certainly `✓(lean)` regardless of structure — investigate manually.

### §3.3 Quick content scan for section compliance

```bash
# Check if simulation-bases.md has 9 sections
grep -c "^## §" examples/<Scenario>/simulation-bases.md

# Check if explain.md has Theory→Implementation tables
grep -c "Theory Component" examples/<Scenario>/Rule/explain.md

# Check if analysis.md has metric→function mapping
grep -c "Function" examples/<Scenario>/Rule/analysis.md

# Check if docstrings cite simulation-bases.md §4
grep -c "simulation-bases.md §4" examples/<Scenario>/Rule/players.py
```

---

## §4 Task Classification

Once the matrix is complete, classify each simulation into a task type:

| Task Type        | Description                                                                          | Example Scenario     |
|------------------|--------------------------------------------------------------------------------------|----------------------|
| **Patch-only**   | All docs exist and are compliant; only `players.py` docstrings need `§4.N` citations | ArchegosCollapse     |
| **Partial-fill** | Root docs exist; some variant docs missing or lean                                   | AsianFinancialCrisis |
| **Full-create**  | Root docs missing; all variant docs missing or lean                                  | CreditCycle          |
| **Rewrite**      | Files exist but all are non-compliant (lean); everything needs rewriting             | DotComBubble         |
| **Mixed**        | Some variants complete, others missing                                               | DispositionEffect    |

This classification drives the execution order strategy in `06-execution-order.md`.

---

## §5 Current State Summary Format

The final output of the audit phase is a table like this, followed by the task classification:

```
## Current State Summary

| Simulation       | sim-bases | analysis-bases | Rule[E/A] | LLM[E/A]  | RuleLLM[E/A] | Rag[E/A]  |
|------------------|-----------|----------------|-----------|-----------|--------------|-----------|
| ArchegosCollapse | ✓         | ✓              | ✓/✓       | ✓/✓       | ✓/✓          | ✓/✓       |
| DotComBubble     | ✗         | ✗              | ✓/✓(lean) | ✓/✓(lean) | ✓/✓(lean)    | ✓/✓(lean) |
| CreditCycle      | ✗         | ✗              | ✓/-       | -/-       | -/-          | -/-       |

Legend: E=explain.md, A=analysis.md, ✓=compliant, ✓(lean)=exists but non-compliant, -=missing, ✗=root file missing

## Task Classification

| Simulation       | Task Type             | Priority Notes                               |
|------------------|-----------------------|----------------------------------------------|
| ArchegosCollapse | Patch-only            | Only docstring citations needed              |
| DotComBubble     | Full-create + Rewrite | Create root docs; rewrite all 8 variant docs |
| CreditCycle      | Full-create           | Create everything from scratch               |
```

---

## §6 Legend

| Symbol  | Full Description                                       |
|---------|--------------------------------------------------------|
| ✓       | Exists and fully spec-compliant                        |
| ✓(lean) | Exists but thin/non-compliant — rewrite required       |
| -       | Missing — create required                              |
| ✗       | Root-level file missing — create required              |
| E       | `explain.md`                                           |
| A       | `analysis.md`                                          |
| [E/A]   | Pair: left=explain.md status, right=analysis.md status |
