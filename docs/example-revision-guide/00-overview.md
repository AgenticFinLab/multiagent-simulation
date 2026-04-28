# Example Revision Guide — Overview

## What This Folder Is

This folder is the **authoritative revision guide** for auditing, repairing, and upgrading existing financial multi-agent simulations in `examples/`. Each phase is covered in a dedicated, deeply specified file.

This guide is **reusable for any simulation in `examples/`** — not tied to any specific scenario or modification task. It encodes the complete workflow demonstrated during the 10-simulation audit and repair session and is designed to be followed by an agent or developer for any future revision work.

---

## Relationship to `docs/create-example-skill/`

| Guide                                            | Purpose                               | When to Use                                          |
|--------------------------------------------------|---------------------------------------|------------------------------------------------------|
| `docs/create-example-skill/`                     | Build a new simulation from scratch   | Creating a new `examples/<Scenario>`                 |
| `docs/example-revision-guide/` ← **this folder** | Audit and repair existing simulations | Updating, fixing, or upgrading `examples/<Scenario>` |

Both guides share the same compliance standard — the difference is direction: creation goes forward, revision goes backward from the standard.

---

## Folder Structure and Reading Order

| File                         | Phase      | Purpose                                                                                   |
|------------------------------|------------|-------------------------------------------------------------------------------------------|
| `00-overview.md`             | —          | This file: orientation and reading order                                                  |
| `01-current-state-audit.md`  | Pre-work   | How to fill the `00-simulations.md` state table and produce an audit matrix               |
| `02-remediation-standard.md` | Standard   | The compliance criteria every file must meet — for documentation, code, and config        |
| `03-documentation-repair.md` | Repair     | How to create or rewrite `simulation-bases.md`, `analysis-bases.md`, and all variant docs |
| `04-code-repair.md`          | Repair     | How to audit and fix `players.py` and `prompts.py` for all four variants                  |
| `05-config-repair.md`        | Repair     | How to audit and fix YAML config files for all four variants                              |
| `06-execution-order.md`      | Execution  | The per-simulation step-by-step workflow: one simulation at a time                        |
| `07-validation-checklist.md` | Validation | Final verification gates before marking a simulation complete                             |

---

## How to Use This Guide

### Step 0 — Fill in `00-simulations.md`

Before doing anything else, create or update `docs/example-revision-guide/00-simulations.md`:
- Column 1 `Simulation`: the name of each simulation you want to revise
- Column 2 `Path`: the path to its root directory (e.g., `examples/DotComBubble`)

This is the user-supplied input. Everything else in the workflow operates on this list.

### Step 1 — Audit current state (`01-current-state-audit.md`)

For each simulation in `00-simulations.md`, build the audit matrix: which files exist, which are missing, which are non-compliant. This produces a Current State Summary table.

### Step 2 — Understand compliance standard (`02-remediation-standard.md`)

Read the remediation standard to know exactly what "compliant" means for each file type. This is the reference you return to throughout the repair work.

### Step 3 — Execute repairs, one simulation at a time (`06-execution-order.md`)

Follow the execution order file, working through simulations one at a time. For each simulation:
- Documentation repairs → `03-documentation-repair.md`
- Code repairs → `04-code-repair.md`
- Config repairs → `05-config-repair.md`

### Step 4 — Validate (`07-validation-checklist.md`)

After each simulation is repaired, run the validation checklist to confirm all gates pass before moving to the next simulation.

---

## Key Principles

### 1. One simulation at a time
Never attempt to repair multiple simulations in parallel. Each simulation is fully repaired and validated before the next begins. This prevents cross-contamination and ensures verifiable progress.

### 2. Current State Summary first
Every revision session starts with a complete Current State Summary table (see `01-current-state-audit.md`). This ensures nothing is missed and provides a clear map before any repair work starts.

### 3. Documentation drives code
`simulation-bases.md` and `analysis-bases.md` are written or repaired **before** any code docstrings are patched. Variant `explain.md` files are repaired **after** the root documents are complete. Code cites documentation — never the reverse.

### 4. Spec compliance, not content replication
Every repaired file must satisfy the structural and content requirements in `02-remediation-standard.md`. The content (investors, metrics, theory) is drawn from the existing code and literature — the repair work maps it into the correct spec-compliant format.

### 5. Variant-agnostic root documents
`simulation-bases.md §4` must contain only economic archetypes — no Rule-Based Behavior, LLM Persona, or RuleLLM Hybrid Notes. Those belong in the respective variant `explain.md §2`.

---

## Reference: Compliance Standard Summary

Full details are in `02-remediation-standard.md`. Quick reference:

| File Type               | Sections Required | Key Constraint                                                            |
|-------------------------|-------------------|---------------------------------------------------------------------------|
| `simulation-bases.md`   | 9 sections        | §4 investor entries must use 7-part standard; no variant-specific content |
| `analysis-bases.md`     | 7 sections        | §2 metrics must include Python function signatures                        |
| `{Variant}/explain.md`  | 9 sections        | §2 Theory→Implementation mapping tables; cites `simulation-bases.md §4.N` |
| `{Variant}/analysis.md` | 5 sections        | §2 Metric→Function mapping; variant-specific notes in §3                  |
| `players.py` docstrings | Class-level       | Each investor class must cite `Theory: simulation-bases.md §4.N`          |

---

## Reference: Docstring Citation Patterns

These patterns are enforced during code repair (see `04-code-repair.md §3`):

**Rule/players.py — multi-line format**:
```python
class ClassName(GeneralPlayer):
    """Brief description.

    Theory: simulation-bases.md §4.N — ClassName
    Theoretical basis: Author (Year) theory name; description of mechanism.
    See simulation-bases.md §4.N for mathematical model.
    """
```

**LLM / RuleLLM / Rag players.py — one-liner format**:
```python
class LLMClassName(LLMInvestor):
    """LLM-driven class description — brief mechanism. Theory: simulation-bases.md §4.N."""
```

---

## Relationship to Code

```
docs/example-revision-guide/      ← This folder: revision methodology
        │
        │ drives repair of
        ▼
examples/{SimulationName}/
├── simulation-bases.md         ← Audited per 02-remediation-standard.md §SIM
├── analysis-bases.md           ← Audited per 02-remediation-standard.md §ANA
└── {Variant}/
    ├── explain.md              ← Repaired per 03-documentation-repair.md
    ├── analysis.md             ← Repaired per 03-documentation-repair.md
    └── players.py              ← Docstrings patched per 04-code-repair.md §3
```
