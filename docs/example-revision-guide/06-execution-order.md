# Execution Order

## Purpose

This file defines the **step-by-step execution workflow** for revising simulations. It operationalizes the repair work defined in `03-documentation-repair.md`, `04-code-repair.md`, and `05-config-repair.md` into a concrete, repeatable process.

The workflow is organized as:
1. **Session setup** — read current state, plan tasks
2. **Per-simulation tasks** — one simulation at a time, four repair phases
3. **Session close** — validate and update progress records

---

## §1 Session Setup

### §1.1 Read `00-simulations.md`

Confirm the list of simulations to revise. Note any simulations already marked complete from previous sessions.

### §1.2 Build or update the Current State Summary

Follow `01-current-state-audit.md` to produce (or update) the audit matrix. The Current State Summary is the plan — every row must be understood before touching any file.

**Output**: A table like this:

```
| Simulation       | sim-bases | analysis-bases | Rule[E/A] | LLM[E/A]  | RuleLLM[E/A] | Rag[E/A]  | Task Type   |
|------------------|-----------|----------------|-----------|-----------|--------------|-----------|-------------|
| ArchegosCollapse | ✓         | ✓              | ✓/✓       | ✓/✓       | ✓/✓          | ✓/✓       | Patch-only  |
| DotComBubble     | ✗         | ✗              | ✓/✓(lean) | ✓/✓(lean) | ✓/✓(lean)    | ✓/✓(lean) | Full-create |
| CreditCycle      | ✗         | ✗              | ✓/-       | -/-       | -/-          | -/-       | Full-create |
```

### §1.3 Classify and order tasks

Order simulations from simplest to most complex (Patch-only → Partial-fill → Full-create), unless the user has specified a different priority.

---

## §2 Per-Simulation Execution

For each simulation, execute the four phases below in order. **Complete all phases for one simulation before moving to the next.**

---

### Phase 1 — Extract Ground Truth

**Goal**: understand what the simulation currently does before writing anything.

1. Read `Rule/players.py` — list all investor classes and their §4.N mappings
2. Read the `decide()` method of each investor — note thresholds, formulas, order_size
3. Read any existing `simulation-bases.md` or `explain.md` — extract reusable theory content
4. List all parameters used via `self.config.extras["key"]`
5. Record the investor-to-§4.N mapping table (this is reused across all subsequent phases)

**Output**: An investor mapping table:
```
§4.1 → ClassName (Rule), LLMClassName (LLM), RuleLLMClassName (RuleLLM), RagLLMClassName (Rag)
§4.2 → ...
```

---

### Phase 2 — Root Document Repair

**Goal**: produce spec-compliant `simulation-bases.md` and `analysis-bases.md`.

**Execute if**: sim-bases or analysis-bases is `✗` or `✓(lean)`.

**Steps**:

1. **Create/rewrite `simulation-bases.md`** (see `03-documentation-repair.md §2`)
   - §1–§3: Write phenomenon, theory, market design
   - §4: Write all investor entries using 7-part standard
   - §5–§9: Write diversity, parameters, round structure, historical cases, variant comparison
   - Verify: 9 sections present, §4 has correct number of entries, no Rule/LLM content in §4

2. **Create/rewrite `analysis-bases.md`** (see `03-documentation-repair.md §3`)
   - §1: Write objectives
   - §2: Write ≥5 metrics with Python function signatures
   - §3–§7: Write dimensions, phase analysis, cross-variant comparison, expected results, visualization
   - Verify: 7 sections present, all metrics have Python signatures

3. **Gate check**: Do NOT proceed to Phase 3 until both root documents pass the compliance checklist in `02-remediation-standard.md §1.4` and `§2.3`.

---

### Phase 3 — Variant Documentation Repair

**Goal**: produce spec-compliant explain.md and analysis.md for all four variants.

**Execute if**: any variant explain.md or analysis.md is `✓(lean)` or `-`.

**Steps** (for each variant: Rule → LLM → RuleLLM → Rag):

1. **Rule/explain.md**
   - Write §1 overview table (variant=Rule, mechanism=Threshold rules)
   - Write §2 with one subsection per investor — Theory→Implementation mapping tables
   - Write §3–§8 (market mechanism, config reference, running instructions, expected behavior, references)
   - Verify: §2 subsections cite `simulation-bases.md §4.N`

2. **Rule/analysis.md**
   - Write §1–§5: objectives, 7-metric table with function names, Rule-specific notes, expected ranges, references
   - Verify: §2 table has all 7 metrics with `analysis-bases.md §2.X` references

3. **LLM/explain.md**
   - Same structure as Rule; §2 maps theory to system prompt instructions
   - §4 adds LLM Architecture table (base class, inference, context, parsing, retry)

4. **LLM/analysis.md**
   - Same structure as Rule; §3 notes LLM-specific variance; §4 compares vs. Rule baseline

5. **RuleLLM/explain.md**
   - §2 maps theory to embedded rule in system prompt

6. **RuleLLM/analysis.md**
   - §3 notes include rule fidelity check; §4 expected ranges vs. Rule and LLM

7. **Rag/explain.md**
   - §2 maps theory to RAG query + retrieval effect
   - §4 adds RAG Architecture table (KnowledgeStore, embedding, top_k)
   - §1 adds `Knowledge Sources` row to overview table

8. **Rag/analysis.md**
   - §3 notes include RAG moderation effect and knowledge coverage check

---

### Phase 4 — Code Repair

**Goal**: patch investor class docstrings in all four variants' `players.py`.

**Execute if**: any variant's `players.py` lacks `Theory: simulation-bases.md §4.N` citations.

**Steps**:

1. Verify syntax of all existing Python files first (`py_compile`)
2. For **Rule/players.py**: patch each investor class with multi-line docstring (§5.1 format)
3. For **LLM/players.py**: patch each investor class with one-liner docstring (§5.2 format)
4. For **RuleLLM/players.py**: patch each investor class with one-liner docstring
5. For **Rag/players.py**: patch each investor class with one-liner docstring
6. Run syntax check again after all patches
7. Count Theory citations vs. investor class count (see `04-code-repair.md §6`)

**Optional code compliance checks** (run if the simulation has not been previously audited):
- Import correctness (§2.2)
- lmbase API usage (§2.3)
- KnowledgeStore API (§2.5)
- HistoryBuffer constructor (§2.6)

---

### Phase 5 — Config Repair (conditional)

**Execute only if**:
- The simulation is newly created (Full-create task type), OR
- Configs are known to be broken (e.g., old topology format, missing required fields)

If the simulation currently runs and only documentation + docstrings were repaired, configs do NOT need to be touched.

**Steps** (if needed):
1. Check `simulation.yml` against §2 checklist in `05-config-repair.md`
2. Check `persona.yml` against §3 checklist
3. Check `topology.yml` against §4 checklist
4. Check `players.yml` against §5 checklist
5. Run cross-consistency check (§6)

---

### Phase 6 — Validation

**Goal**: confirm all deliverables are complete and compliant.

Run the full checklist from `07-validation-checklist.md`.

**Pass criteria**:
- All expected files exist (no `-` or `✗` remaining)
- All non-compliant files have been rewritten (no `✓(lean)` remaining)
- All investor docstrings cite `simulation-bases.md §4.N`
- All Python files pass `py_compile`
- All section counts pass (9 for sim-bases, 7 for analysis-bases, etc.)

**Record the result** in the Current State Summary: update the simulation row to reflect the new status.

---

### Phase 7 — Runtime Drift And Rerun Decision

**Goal**: decide whether existing full-round success samples can be inherited or
whether affected scenario-mode rows must be rerun after repair.

This phase is mandatory whenever a simulation already has experiment artifacts.
It prevents unnecessary reruns after docs-only repairs while also preventing
stale samples from representing changed runtime inputs.

**Default principle**: preserve existing runtime semantics whenever the original
implementation does not violate this guide or `masim/format/implement-simulation-skill`.

**Steps**:

1. List every changed file for the simulation.
2. Classify each change:
   - `docs-only`: `simulation-bases.md`, `analysis-bases.md`,
     `{Variant}/explain.md`, `{Variant}/analysis.md` only.
   - `runtime-input`: `players.py`, `prompts.py`, `configs/`, parser/fallback
     logic, market/order construction, topology, model id, RAG embedding/index
     configuration, or player counts.
3. For docs-only repairs, existing clean samples may be inherited. Mark the
   row `docs-inherited`.
4. For runtime-input repairs, mark affected modes
   `rerun-required-runtime-change`.
5. For prompt-rule alignment repairs in `RuleLLM`, mark both `RuleLLM` and
   `Rag` affected if Rag aliases the RuleLLM prompts.
6. Keep clean old samples as `legacy-clean` evidence for the branch/commit that
   produced them. Do not mark them failed solely because the standardized branch
   now differs.
7. Record the decision in the experiment ledger before launching any rerun.

**Examples**:

- Adding missing root docs and variant docs only: no simulation rerun.
- Adding required LLM output fields that `players.py` reads: rerun affected API
  modes.
- Changing RuleLLM prompt formulas or numeric parameters to match Rule/config:
  rerun affected `RuleLLM`; rerun `Rag` too if Rag imports those prompts.
- Adding class docstrings only: no simulation rerun.

---

## §3 Task Type Execution Profiles

### Patch-only

```
Phase 1: Extract Ground Truth (verify §4.N mapping)
Phase 4: Code Repair (docstring patches only)
Phase 6: Validation
```

Estimated effort: 15–30 minutes per simulation.

### Partial-fill

```
Phase 1: Extract Ground Truth
Phase 2: Root Document Repair (only if sim-bases or analysis-bases is ✗/lean)
Phase 3: Variant Documentation Repair (only for missing/lean variants)
Phase 4: Code Repair (docstring patches)
Phase 6: Validation
```

Estimated effort: 1–2 hours per simulation.

### Full-create

```
Phase 1: Extract Ground Truth
Phase 2: Root Document Repair (create both root docs)
Phase 3: Variant Documentation Repair (create all 8 variant docs)
Phase 4: Code Repair (docstring patches)
Phase 5: Config Repair (if configs are missing or broken)
Phase 6: Validation
```

Estimated effort: 3–5 hours per simulation.

### Rewrite

```
Phase 1: Extract Ground Truth (read existing files for content to preserve)
Phase 2: Root Document Repair (rewrite both root docs)
Phase 3: Variant Documentation Repair (rewrite all 8 variant docs)
Phase 4: Code Repair (docstring patches + full compliance check)
Phase 6: Validation
```

Estimated effort: 2–4 hours per simulation.

---

## §4 Progress Tracking

### §4.1 Task status table

Maintain a task status table throughout the session:

```
| ID | Simulation | Phase        | Status      |
|----|------------|--------------|-------------|
| t1 | <Sim1>     | Root docs    | COMPLETE    |
| t2 | <Sim1>     | Variant docs | IN_PROGRESS |
| t3 | <Sim1>     | Code repair  | PENDING     |
| t4 | <Sim2>     | All phases   | PENDING     |
```

### §4.2 File-level progress

Track each file individually for complex simulations:

```
<Simulation>:
  simulation-bases.md     [COMPLETE]
  analysis-bases.md       [COMPLETE]
  Rule/explain.md         [COMPLETE]
  Rule/analysis.md        [COMPLETE]
  LLM/explain.md          [IN_PROGRESS]
  LLM/analysis.md         [PENDING]
  RuleLLM/explain.md      [PENDING]
  RuleLLM/analysis.md     [PENDING]
  Rag/explain.md          [PENDING]
  Rag/analysis.md         [PENDING]
  Rule/players.py         [PENDING docstring patches]
  LLM/players.py          [PENDING docstring patches]
  RuleLLM/players.py      [PENDING docstring patches]
  Rag/players.py          [PENDING docstring patches]
```

---

## §5 Context Resumption (Cross-Session Work)

When resuming work in a new session:

1. Read `00-simulations.md` — identify which simulations are listed
2. Read the last Current State Summary — identify which simulations are IN_PROGRESS
3. For each IN_PROGRESS simulation, check which files were last modified
4. Resume from the last incomplete phase
5. Re-run `py_compile` on any Python files already patched to confirm they are still valid

**Key files to check for IN_PROGRESS simulation**:
```bash
# What was most recently modified?
ls -lt examples/<Scenario>/ examples/<Scenario>/*/  | head -20

# What phases are complete?
grep -c "Theory: simulation-bases.md §4" examples/<Scenario>/*/players.py
wc -l examples/<Scenario>/simulation-bases.md
wc -l examples/<Scenario>/*/explain.md
```
