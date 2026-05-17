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
| `08-runtime-failure-patterns.md` | Runtime | Empirical failure patterns discovered during full-round experiment execution              |

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

### Step 5 — Runtime lessons (`08-runtime-failure-patterns.md`)

After a scenario reaches structural compliance, use the runtime failure
patterns to decide whether a failed full-round run indicates:
- a config/schema bug that must be fixed before rerun,
- a prompt/parser contract bug that should be audited across related modes,
- an API/quota/runtime contamination that invalidates the batch evidence, or
- a Level-2/Level-3 quality issue that can only be judged after execution.

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

### 6. Root-cause fixes only — NO defaults, NO skips, NO safety fallbacks
When a runtime error occurs (e.g., `KeyError`, `AttributeError: module has no attribute`), the fix **must** trace back to the root cause and correct the authoritative source of truth:
- **Class name mismatch** (`AttributeError`): The `class:` field in `players.yml` must match the actual class name in `players.py`. Fix the config (or the code) — NEVER rename the class to match a wrong config.
- **Config key mismatch** (`KeyError`): The `extras:` keys in `players.yml` must exactly match the `extras["key"]` accesses in `players.py`. Fix whichever side is wrong according to `simulation-bases.md §4`.
- **Identity mismatch**: `config.identity` in `players.yml` must match the agent key in `topology.yml`. Fix both to match the design.
- **Variant prefix mismatch**: Rag classes use `RagLLM` prefix, RuleLLM classes use `RuleLLM` prefix. Never mix `LLM` prefix in Rag/RuleLLM code.

**FORBIDDEN**: `.get(key, default)` fallbacks, `try/except` to skip missing keys, renaming design-defined class names to match wrong configs, or any other workaround that masks the underlying inconsistency.

**Runtime exception for stochastic API modes**: external LLM responses and
network/API calls are not authoritative config data. A scenario may add a
scenario-local fallback for malformed LLM output or transient provider errors
only if all conditions hold:
- the prompt/parser/player contract has already been fixed at the source;
- fallback is explicit in code, never silent;
- fallback counts or reasons are recorded in logs/artifacts;
- auth, quota, missing-key, config, parser-reference, and framework schema
  errors still fail loudly;
- the final sample is later reviewed for fallback rate and scenario quality.

This exception does not weaken the root-cause rule. It separates deterministic
project bugs from stochastic provider behavior.

#### 6.1 Strict No-Default, No-Defensive-Programming Policy

Beyond root-cause error handling, **all simulation code** (`players.py` and `analysis.py` across all four variants) must follow strict fail-fast principles. This is a universal, non-negotiable constraint.

**The 8 prohibited pattern categories**:

| # | Pattern                            | Wrong                                          | Correct                                                |
|---|------------------------------------|------------------------------------------------|--------------------------------------------------------|
| 1 | LLM parse failure → silent hold    | `if decision is None: action, qty = "hold", 0` | Fix the prompt/parser contract; if stochastic malformed output remains, use an explicit counted fallback |
| 2 | `.get()` on LLM response           | `decision.get("action", "hold")`               | `decision["action"]`                                   |
| 3 | `.get()` on message payload        | `decision_payload.get("quantity", 0)`          | `decision_payload["quantity"]`                         |
| 4 | `.get()` on coordinator data       | `fundamentals.get(r, 100.0)`                   | `fundamentals[r]`                                      |
| 5 | Ternary fallback for required data | `if fundamentals else 1.0`                     | `if not fundamentals: raise ValueError(...)`           |
| 6 | `.get()` on analysis payload       | `payload.get("rag_context", None)`             | `payload["rag_context"]`                               |
| 7 | Empty-collection fallback          | `if rates else 0.0`                            | `if not rates: raise ValueError(...)`                  |
| 8 | Index fallback                     | `prices[i] if i < len(prices) else 0.0`        | `prices[i]` (let IndexError surface)                   |

**Scope**: applies to ALL `players.py` and `analysis.py` files in all four variants.

**Legitimate exceptions** (these `.get()` patterns are allowed):
- RAG config resolution: `resolved_rag.get("embed_model", ...)` — external library config with genuine optional fields
- `__getstate__`/`__setstate__` serialization infrastructure
- Truly optional config sections: `extras.get("private_knowledge", {})`
- Matplotlib styling defaults (colors, line widths)
- `state.get("state", {})` in serialization methods

See `04-code-repair.md §12` for the full audit protocol with detection scripts.

### 7. Config-Code-Topology triple consistency
Every scenario must maintain strict three-way consistency:
1. `simulation-bases.md` defines investor names and parameter names (authoritative source)
2. `players.py` implements classes matching those names
3. `players.yml` references those exact class names **and** parameter names in `extras:`
4. `topology.yml` uses identity keys matching `players.yml`
5. Every `extras["key"]` access in code has a matching key in the **specific player's** `config.extras` section

When inconsistency is found, the fix priority is: documentation → code → config → topology (upstream wins).

> **Audit record**: Comprehensive programmatic audits:
> 1. **Class name audit** (t1, 2026-02-03): verified all `class:` references across 45 scenarios × 4 variants → 39 mismatches fixed + 0 remaining
> 2. **Extras key audit** (t2, 2026-02-03): verified all `extras["key"]` accesses per-player across 263 player-config pairs → 28 mismatches fixed + 0 remaining
> 3. **LLM sub-config + forbidden `.get()` audit** (t3, 2026-04-29):
>    - LLM init pattern: `llm_cfg["model"]` → `llm_cfg["lm_name"]` and manual `generation_config` dicts → `llm_cfg["generation_config"]` across 46 code files
>    - Forbidden `.get()` elimination: 295 `extras.get("key", default)` calls → direct `extras["key"]` access across 73 code files + 11 run scripts
>    - Config backfill: 53 missing extras keys added to 11 Rule variant config YAML files
>    - Final verification: 283 player-config pairs checked, 0 mismatches remaining

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
