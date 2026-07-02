# Polish Guidance — Upgrading `examples/` Scenarios

## 1. Objective

Bring every simulation scenario under `examples/` into full compliance with
the current skill baseline (`define-simulation-scenario-skill.md`,
`agent-design-skill.md`, `implement-simulation-skill/`). After polishing, each
scenario should be:

- Structurally complete (all required files and sections present)
- Theoretically grounded (evidence-backed agent designs, cited sources)
- Internally consistent (cross-references, parameter tables, config alignment)
- Runnable (every declared variant executes without error)

## 2. Why Polish?

The `examples/` scenarios were built incrementally over time. As the skill
specifications evolved (domain-agnosticism, evidence provenance, venue-agnostic
design, mathematical model flexibility, etc.), older scenarios fell out of
conformance. The polish process:

1. **Eliminates technical debt** — outdated formats, missing sections, stale
   cross-references.
2. **Enforces research rigor** — every design choice must trace to academic
   evidence, not ungrounded assumptions.
3. **Enables reproducibility** — a polished scenario can be re-run by anyone
   with zero ad-hoc fixes.
4. **Maintains team consistency** — all 45 scenarios follow one standard,
   making review and comparison straightforward.

## 3. How to Polish (Step-by-Step)

### 3.1 Choose scenarios to polish

Pick one or more scenarios from `examples/tracking.md` that are still ⬜ (Not
Started). Coordinate with the team — if a scenario is 🟡, someone else is
already working on it.

### 3.2 Invoke the polish pipeline via LLM

Give the LLM the following prompt pattern:

```
用 masim/skills/polish-simulation-pipeline.md 依次调整、更新、修复
examples/VolatilityClustering, TulipMania, SVBBankRun, SunkCostFallacy,
StatusQuoBias, SouthSeaBubble, SorosPound, ShortSqueeze。
每一个都需要深入、全面、详细、准确，且反复检查确保没任何问题。
```

The LLM will:
1. Read `masim/skills/polish-simulation-pipeline.md` as its operational guide
2. For each scenario in order, execute the full Step 0 → Step 10 audit-and-patch pipeline
3. At each step, anchor to the corresponding skill file's `## Contract` block
4. Patch any defects found, re-run validation 3× to confirm
5. Halt and ask if materially new research is needed (never fabricates)

### 3.3 Update the tracking table

After each scenario is polished, update `examples/tracking.md`:
- Set **Status** to 🟢
- Fill **Modified By** with your name
- Fill **Date** with today's date
- Fill **Executed Variants** with whichever variants were successfully run (e.g. `Rule, LLM`)

## 4. Expected Outcome per Scenario

After a successful polish, each scenario directory should contain:

| Artefact               | State                                                               |
|------------------------|---------------------------------------------------------------------|
| `simulation-bases.md`  | Conforms to `02-simulation-bases-creation.md`                       |
| `analysis-bases.md`    | Conforms to `03-analysis-bases-creation.md`                         |
| Agent design specs     | Each conforms to `agent-design-skill.md` §3.1–§3.11                 |
| Variant subdirectories | All declared variants built and verified                            |
| Target file            | Locked, validated against `define-simulation-scenario-skill.md` §11 |
| Config files           | All parameters match agent specs; no stale defaults                 |

## 5. Key Principles During Polish

- **Audit, don't rewrite from scratch** — preserve the scenario's research
  intent; only fix what violates current standards.
- **Never fabricate** — if evidence is missing, halt and source it properly.
- **One scenario at a time** — finish and validate one before moving to the
  next.
- **Track progress** — always update `examples/tracking.md` so others know
  what's done.

## 6. Reference Files

| File                                               | Role                                    |
|----------------------------------------------------|-----------------------------------------|
| `masim/skills/polish-simulation-pipeline.md`       | The operational pipeline (Step 0–10)    |
| `masim/skills/define-simulation-scenario-skill.md` | Target file specification               |
| `masim/skills/agent-design-skill.md`               | Universal agent design standard         |
| `masim/skills/implement-simulation-skill/`         | Per-step methodology files              |
| `examples/tracking.md`                             | Team coordination and progress tracking |
