# Mandatory File Structure

## Purpose

Every simulation must conform to the fixed directory and file layout defined in this document. No simulation is considered complete without every listed file. This document is the authoritative reference for structural compliance checks.

---

## Canonical Variant Set (Current Version of `implement-simulation-skill`)

The `implement-simulation-skill/*.md` documents are written against a **fixed, explicitly-enumerated variant set**. Every variant listed below MUST be considered by every implementer, and every rule / checklist / template in these implement-* docs MUST name each variant explicitly. Generalisation ("every model-driven variant") is NOT sufficient at the implementation layer — implementers rely on named, exhaustive coverage.

**Current canonical variant set (v-current):**

| Variant   | Capability class            | Required per-variant files                                                                     |
|-----------|-----------------------------|------------------------------------------------------------------------------------------------|
| `Rule`    | rule-driven (deterministic) | `__init__.py`, `players.py`, `run_*.py`, `analysis.py`, `explain.md`, `analysis.md`            |
| `LLM`     | model-driven                | `__init__.py`, `players.py`, `prompts.py`, `run_*.py`, `analysis.py`, `explain.md`, `analysis.md` |
| `RuleLLM` | hybrid (rule + model)       | `__init__.py`, `players.py`, `prompts.py`, `run_*.py`, `analysis.py`, `explain.md`, `analysis.md` |
| `Rag`     | retrieval-augmented         | `__init__.py`, `players.py`, `prompts.py`, `run_*.py`, `analysis.py`, `explain.md`, `analysis.md` |

**Implementation guarantee.** Every variant declared `Yes` in target §10.1 Variant Build Matrix MUST be a member of this canonical set, and MUST have full coverage across:

- `configs/{Sim}/{V}/` (Step 3, see `07-step3-config.md`)
- `examples/{Sim}/{V}/players.py`, `analysis.py`, `run_*.py`, and `prompts.py` where applicable (Step 4, see `08-step4-implement.md`)
- `examples/{Sim}/{V}/explain.md` and `analysis.md` (per-variant docs, see `03-variant-documents-spec.md`)
- Cross-variant review & comparison (Steps 5–10, see `09-step5-to-10-review.md`)

No variant may be silently skipped or partially implemented. If target §10.1 declares only a subset (e.g. `Rule` and `LLM` for a prototype), the *unbuilt* variants MUST NOT have folders, and the scenario MUST be recorded as `prototype` in `simulation-build-log.md`.

**Introducing a new variant.** If a scenario needs a variant outside the canonical set (e.g. `Behavioural`, `EvolutionaryRule`, `MultiModelEnsemble`), the implement-* docs MUST be upgraded in the same commit:

1. Add the new variant as a named row in this table.
2. Extend every checklist and template in `01-mandatory-structure.md`, `03-variant-documents-spec.md`, `07-step3-config.md`, `08-step4-implement.md`, and `09-step5-to-10-review.md` to name the new variant explicitly and describe its required per-variant files, implementation obligations, and per-variant tests.
3. Extend `agent-design-skill.md §3.6.0` if the new variant introduces a new input surface or output field.
4. Bump the version of every touched skill doc and record the addition in its change log.

Renaming or removing a canonical variant follows the same rule — no implicit inheritance from a generic capability class is permitted at the implementation layer. The class labels (rule-driven / model-driven / hybrid / retrieval-augmented) are pedagogical categories only; they clarify *why* a variant has certain files, but they do NOT stand in for explicit enumeration.

> This convention is stricter than the agent-design layer. In `agent-design-skill.md` (the handbook governing per-agent design), obligations attach to capability classes so that a future variant automatically inherits the I/O contract. In the implement-* layer (this document and its siblings), obligations attach to **named variants** so that no variant is ever half-implemented.

---

## 1. Complete Required Layout

```
examples/{SimulationName}/
├── {domain}-{scenario}.md         # UPSTREAM INPUT: scenario target file, produced by
│                                  #   invoking masim/skills/define-simulation-scenario-skill.md
│                                  #   (users MUST NOT hand-author this file)
│                                  #   Status: draft → locked → released
├── simulation-build-log.md           # PIPELINE LOG: AGENT_POOL gate (§A), research notes (§B),
│                                  #   open questions (§C), build log (§D)
├── __init__.py                    # Package init (empty or minimal)
├── simulation-bases.md            # ROOT: Theoretical & design foundation (all variants share this)
├── analysis-bases.md              # ROOT: Analysis methodology foundation (all variants share this)
│
├── Rule/
│   ├── __init__.py
│   ├── players.py                 # All rule-based agent class implementations
│   ├── run_{name}.py              # Simulation entry point
│   ├── analysis.py                # Authoritative analysis script (defines __all__)
│   ├── explain.md                 # How Rule variant implements simulation-bases.md
│   └── analysis.md                # How Rule variant implements analysis-bases.md
│
├── LLM/
│   ├── __init__.py
│   ├── players.py                 # Environment coordinator (copy from Rule) + LLM agent classes
│   ├── prompts.py                 # System + user prompt constants
│   ├── run_{name}_llm.py          # Simulation entry point
│   ├── analysis.py                # Imports from Rule/analysis.py, adds LLM-specific plots
│   ├── explain.md                 # How LLM variant implements simulation-bases.md
│   └── analysis.md                # How LLM variant implements analysis-bases.md
│
├── RuleLLM/
│   ├── __init__.py
│   ├── players.py                 # Environment coordinator (copy from Rule) + hybrid LLM agent classes
│   ├── prompts.py                 # == PERSONA == + == DECISION RULES == dual-section prompts
│   ├── run_{name}_rulellm.py      # Simulation entry point
│   ├── analysis.py                # Imports from Rule/analysis.py
│   ├── explain.md                 # How RuleLLM variant implements simulation-bases.md
│   └── analysis.md                # How RuleLLM variant implements analysis-bases.md
│
└── Rag/
    ├── __init__.py
    ├── players.py                 # Extends RuleLLM agents with KnowledgeStore + retrieval
    ├── prompts.py                 # System prompts (same as RuleLLM) + user template with {rag_context}
    ├── run_{name}_rag.py          # Simulation entry point
    ├── analysis.py                # Imports from Rule/analysis.py, adds analyze_rag_knowledge_effect()
    ├── explain.md                 # How Rag variant implements simulation-bases.md
    └── analysis.md                # How Rag variant implements analysis-bases.md
```

> **Variant folders are conditional.** Build only the variants
> declared `Yes` in target §10.1. The four canonical variants
> supported by the current version of `implement-simulation-skill`
> are `Rule`, `LLM`, `RuleLLM`, and `Rag` (see § Canonical Variant
> Set above). Target §10.1 MUST select from this set; introducing a
> new variant requires an explicit skill-doc upgrade (see the
> "Introducing a new variant" clause in § Canonical Variant Set).
> The variant folder names MUST match the exact labels in target
> §10.1. Variants declared `No` MUST NOT have a folder. The
> pipeline records the scenario as `prototype` if fewer than all
> four canonical variants are built (i.e. any of `Rule`, `LLM`,
> `RuleLLM`, `Rag` is missing on disk).

---

## 2. File Roles at a Glance

| File                       | Scope               | Purpose                                                                                                                                    |
|----------------------------|---------------------|--------------------------------------------------------------------------------------------------------------------------------------------|
| `{domain}-{scenario}.md`   | Root (all variants) | UPSTREAM INPUT — scenario target file, produced by invoking `masim/skills/define-simulation-scenario-skill.md`. Users MUST NOT hand-author this file. |
| `simulation-build-log.md`     | Root (all variants) | PIPELINE LOG — AGENT_POOL gate decisions (§A), research notes (§B), open questions (§C), per-phase build log (§D).                         |
| `simulation-bases.md`      | Root (all variants) | Single source of truth: phenomenon theory, environment design, agent taxonomy (behavioral archetypes), model parameters (finance appendix relabels agent → investor, environment → market)                        |
| `analysis-bases.md`        | Root (all variants) | Single source of truth: analysis dimensions, metrics, expected outcomes, evaluation rationale                                              |
| `{Variant}/explain.md`     | Per variant         | How this variant concretely implements the design in `simulation-bases.md` — every element traces to a `simulation-bases.md §N.M` citation |
| `{Variant}/analysis.md`    | Per variant         | How this variant concretely executes the analysis defined in `analysis-bases.md` — every metric traces to a function in `analysis.py`      |
| `{Variant}/players.py`     | Per variant         | All agent class implementations                                                                                                            |
| `{Variant}/prompts.py`     | LLM/RuleLLM/Rag     | System and user prompt constants                                                                                                           |
| `{Variant}/run_*.py`       | Per variant         | Simulation entry point using `SimulationRunner`                                                                                            |
| `{Variant}/analysis.py`    | Per variant         | Analysis script generating plots and reports                                                                                               |

---

## 3. Design Principle: Hierarchical Authority

```
simulation-bases.md          analysis-bases.md
        │                            │
        │ implements                 │ implements
        ▼                            ▼
{Variant}/explain.md        {Variant}/analysis.md
        │                            │
        │ documents                  │ documents
        ▼                            ▼
{Variant}/players.py        {Variant}/analysis.py
```

- `simulation-bases.md` and `analysis-bases.md` are written **once** and are the authoritative source for every variant built. The current canonical variant set (see § Canonical Variant Set at the top of this document) is `Rule`, `LLM`, `RuleLLM`, `Rag`; each of these four variants MUST be considered by every skill-doc rule, and the subset actually built is declared `Yes` in target §10.1.
- `explain.md` and `analysis.md` **inherit** from the root documents and specify variant-specific implementation details. They must NOT re-state theory — they must cite `simulation-bases.md §N.M` and then state what the code does.
- The code (`players.py`, `analysis.py`) always has a corresponding documentation file that explains it through the lens of the root documents.

---

## 4. Variant Construction Principles

Each variant has a distinct construction approach, goal, and set of non-negotiable constraints. Use this table as the primary reference when building or reviewing any variant.

| Variant     | What to Build                                                                                                                                                            | How to Build It                                                                                                                                                                                                                                                            | Goal / Research Purpose                                                                                                                                                                    |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Rule**    | `players.py` (all rule-based agents), `run_*.py`, `analysis.py`, `explain.md`, `analysis.md`                                                                             | Implement each investor as deterministic formulas; all thresholds and parameters loaded from config; no LLM calls anywhere                                                                                                                                                 | Establish the deterministic baseline; verify that the target phenomenon emerges purely from mathematical rules and agent interactions                                                      |
| **LLM**     | `players.py` (Market rule-based + LLM investors), `prompts.py`, `run_*_llm.py`, `analysis.py`, `explain.md`, `analysis.md`                                               | Market is identical to Rule variant; each investor has a system prompt (persona only — no phenomenon name) and a user prompt template; LLM output parsed as `<analysis>` reasoning + `<decision>` JSON                                                                     | Test whether LLM agents, guided only by personality and market data, can reproduce realistic investor psychology and emergent phenomena without explicit quantitative rules                |
| **RuleLLM** | `players.py`, `prompts.py` (PERSONA + DECISION RULES dual-section), `run_*_rulellm.py`, `analysis.py`, `explain.md`, `analysis.md`                                       | Every system prompt has two mandatory sections: `== PERSONA ==` (who the agent is, risk style, emotional traits) and `== DECISION RULES ==` (the exact Rule-variant formulas re-expressed in plain text); LLM may adjust quantities by ±20% but must follow sign and scale | Isolate the effect of language reasoning: with identical quantitative constraints embedded in the prompt, does LLM reasoning alter phenomenon dynamics compared to the pure Rule baseline? |
| **Rag**     | `players.py` (RAG pipeline added to RuleLLM base), `prompts.py` (PERSONA + DECISION RULES + `{rag_context}`), `run_*_rag.py`, `analysis.py`, `explain.md`, `analysis.md` | Extends RuleLLM: at initialization, each agent builds a personal `KnowledgeStore` from documents; at every decision round, the agent queries the store and injects top-k retrieved chunks into the user prompt as `{rag_context}`                                          | Test the effect of external domain knowledge: does access to retrieved financial literature change decision quality and phenomenon intensity compared to RuleLLM?                          |

---

## 5. Variant-Specific Non-Negotiable Constraints

### Universal: No Defaults, No Defensive Programming

This constraint applies to **every one of the four canonical variants** `Rule`, `LLM`, `RuleLLM`, `Rag` equally (subset built per target §10.1 — see § Canonical Variant Set at the top of this document). Every `players.py` and `analysis.py` file in every built variant folder must follow strict fail-fast principles:

- **No `.get(key, default)`** on simulation data dicts (config extras, message payloads, LLM responses, coordinator data, analysis records). Use direct `dict["key"]` access.
- **No `if X else fallback`** for required data fields (e.g., `if fundamentals else 1.0` is forbidden — use `if not fundamentals: raise ValueError(...)`).
- **No silent error recovery** — when an LLM returns `None` or an unparseable response, code must either `raise RuntimeError(...)` or use the explicit stochastic API fallback policy in `00-overview.md` Principle #6. It must never silently substitute `{"action": "hold", "quantity": 0}`.
- **No `if rates else 0.0`** for computed metrics — if no data was collected, raise `ValueError`, do not fabricate a zero.

Legitimate exceptions: RAG config resolution (`resolved_rag.get()`), `__getstate__`/`__setstate__` serialization, truly optional config sections (`extras.get("private_knowledge", {})`), and matplotlib styling defaults.

See `masim/skills/implement-simulation-skill/00-overview.md` Principle #6 for the full policy.

### Rule Variant
- **No hardcoded values.** Every numeric threshold, position size, or parameter must be read from `extras` in `players.yml`.
- **Every parameter in `players.yml` must have a source citation comment.**
- **Validation**: Run 100 rounds → target phenomenon clearly visible. Swap parameter values → behavior changes predictably.

### LLM Variant
- **System prompts define personality only** — they must NOT name the phenomenon, mention the price formula, or hint at what market event is occurring.
- **Output format is always** `<analysis>...</analysis><decision>...</decision>` with JSON containing `action`, `bid_price`, `quantity`, `reasoning`.
- **Never use `<think>` tags** — `<analysis>` is the canonical tag.
- **`bid_price` and `quantity` must be numeric literals**, not formulas or strings.
- **Validation**: LLM agents produce varied but coherent reasoning traces. Phenomenon still emerges.

### RuleLLM Variant
- **`== PERSONA ==` and `== DECISION RULES ==` are mandatory labeled sections** in every system prompt.
- **DECISION RULES must reproduce the exact formulas** from the Rule variant, expressed step-by-step in plain text.
- The embedded rules serve as **deeper investor characterization** — they define the investor's knowledge, habits, and decision-making framework. The LLM uses these rules as guidance alongside its persona to make intelligent decisions.
- **If Rule parameters change, the embedded prompt rules must be updated.**
- **Validation**: Phenomenon still emerges with LLM-driven decisions informed by embedded rules.

### Rag Variant
- **Knowledge retrieval is per-agent** (each agent has its own `KnowledgeStore`, not shared).
- **Index built and persisted on first run; loaded from disk on subsequent runs.**
- **`{rag_context}` is always populated** — if no documents are retrieved, inject `"(No relevant knowledge retrieved this round.)"`.
- **`analyze_rag_knowledge_effect()` in `analysis.py` measures retrieval quality** — target ≥70% retrieval success rate.
- **Validation**: RAG index builds successfully. Retrieved context is visible in agent reasoning traces.

---

## 6. Analysis Module Architecture

The `analysis.py` files follow a DRY hierarchy:

```
Rule/analysis.py
  __all__ = ["load_simulation_data", "calculate_metrics", "create_visualizations"]
  # Authoritative implementations of all 3 core functions
        ▲
        │ imports from
        │
LLM/analysis.py
RuleLLM/analysis.py
Rag/analysis.py        # adds analyze_rag_knowledge_effect() + _RAG_FALLBACK constant
```

- `Rule/analysis.py` is the single authoritative source for `load_simulation_data`, `calculate_metrics`, `create_visualizations`.
- All other variants import these three functions from `Rule/analysis.py` — they do not re-implement them.
- LLM variant adds action distribution analysis.
- RuleLLM variant reuses core metrics from Rule — no additional variant-specific analysis function.
- Rag variant adds `analyze_rag_knowledge_effect()` and defines `_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"`.

---

## 7. Completeness Checklist

Use this to verify any simulation's structural completeness.

**Root level:**
- [ ] `{domain}-{scenario}.md` present and `Status: locked` (or `released`)
- [ ] `simulation-build-log.md` present with §0, §A, §B, §C, §D blocks
- [ ] `__init__.py` present
- [ ] `simulation-bases.md` present and has all 9 sections
- [ ] `analysis-bases.md` present and has all 7 sections

**Per built variant — every variant declared `Yes` in target §10.1 Variant Build Matrix MUST be from the canonical set `Rule / LLM / RuleLLM / Rag` (see § Canonical Variant Set at the top of this document). Repeat this checklist independently for each of `Rule`, `LLM`, `RuleLLM`, and `Rag` that the target declares `Yes`:**
- [ ] `__init__.py` present
- [ ] `players.py` present
- [ ] `prompts.py` present (required for `LLM`, `RuleLLM`, and `Rag`; MUST NOT be present for `Rule`)
- [ ] `run_*.py` present (correct naming convention)
- [ ] `analysis.py` present
- [ ] `explain.md` present
- [ ] `analysis.md` present

**Section coverage in `simulation-bases.md`:**
- [ ] §1 Phenomenon Definition
- [ ] §2 Theoretical Foundation (≥2 theories with DOI citations)
- [ ] §3 Environment Design (§3.1 state dynamics model, §3.2 mechanisms, §3.3 broadcast)
- [ ] §4 Agent Taxonomy — **every agent has all 7 parts** (see `02-root-documents-spec.md`; finance appendix §4.1.F relabels §4 as "Investor Taxonomy" and each agent as "Investor")
- [ ] §5 Agent Diversity Verification
- [ ] §6 Parameter Table (every value has source citation)
- [ ] §7 Communication and Round Structure
- [ ] §8 Historical Case Studies
- [ ] §9 Variant Comparison Preview

**Section coverage in `analysis-bases.md`:**
- [ ] §1 Analysis Objectives (≥3, each mapped to metric)
- [ ] §2 Core Metrics Catalogue (≥6 metrics, each with formula + DOI)
- [ ] §3 Analysis Dimensions (≥3)
- [ ] §4 Phase Analysis Framework
- [ ] §5 Cross-Variant Comparison Framework
- [ ] §6 Expected Results and Validation
- [ ] §7 Visualization Catalogue
