# Step 0: Load the Scenario Target File

## Purpose

Step 0 is the *handoff point* between the target file
(`{domain}-{scenario}.md`) — which is produced upstream by
`masim/skills/define-simulation-scenario-skill.md` from minimal user
inputs, and which users MUST NOT hand-author — and the per-step
methodology in this folder. Step 0 does **not** collect new user
input. It reads the target file, re-validates it, and seeds the
pipeline's build-log contract (`simulation-build-log.md`) so that
Steps 1 — 4 have a stable source of truth.

If a target file does not yet exist, **stop**. Direct the user to
invoke `masim/skills/define-simulation-scenario-skill.md` first; that
skill will emit the file at
`examples/{ScenarioName}/{domain}-{scenario}.md` in a single skill
run.

---

## Contract (Inputs / Outputs / Polish Hooks)

This block is the **stable I/O declaration** for Step 0. Both
`masim/skills/create-simulation-pipeline.md` and
`masim/skills/polish-simulation-pipeline.md` anchor to it.

**Inputs (consumed).**

| Source                                                  | Used for                                     |
|---------------------------------------------------------|----------------------------------------------|
| `examples/{ScenarioName}/{domain}-{scenario}.md`        | scenario target file, produced upstream by invoking `masim/skills/define-simulation-scenario-skill.md` (only input)       |
| `masim/skills/define-simulation-scenario-skill.md §11`  | validation checklist re-run inside the pipeline |

**Outputs (produced).**

| Artefact                                                        | Extent of write                                                 |
|-----------------------------------------------------------------|-----------------------------------------------------------------|
| `examples/{ScenarioName}/simulation-build-log.md`               | fresh file with the §0.3 skeleton; §0 Meta populated with pointers to the target file (create pipeline only) |
| Target file `Status: draft → locked`                            | the pipeline's single permitted edit to the target file        |
| `examples/AGENT_POOL/{Domain}/`                                 | folder created if missing (empty)                              |

**Polish Hooks (what a polish audit does at Step 0).**
For `polish-simulation-pipeline.md`, Step 0 has two variants:

- **Case A: target file already present.** Only re-run
  `define-simulation-scenario-skill.md §11` three consecutive times.
  Do not seed a new build-log; the polish pipeline does not maintain
  one. Update target §0 Meta CHANGELOG with a single line
  `YYYY-MM-DD  Polish target-file gate: existing`.
- **Case B: target file absent.** Halt to `AskUserQuestion` and offer
  the user two options: (i) invoke
  `masim/skills/define-simulation-scenario-skill.md` to produce the
  target file, then resume the polish pipeline; or (ii) opt into
  reverse-reconstruction. In (ii) the polish pipeline seeds the
  target file section-by-section from `simulation-bases.md`
  (including its `§4.{N}` embedded agent blocks), `analysis-bases.md`,
  and `configs/{ScenarioName}/`. Any field with no upstream source
  (Research Question, Success Criteria) is filled by re-invoking
  `define-simulation-scenario-skill.md` in *revise mode* on the
  reconstructed draft. Then run §11 three consecutive times and lock.
  Record the outcome in target §0 Meta CHANGELOG as
  `YYYY-MM-DD  Polish target-file gate: reconstructed`.

---

## 0.1 Required Inputs

Step 0 requires only one file from the user:

```
examples/{ScenarioName}/{domain}-{scenario}.md
```

This file MUST conform to `masim/skills/define-simulation-scenario-skill.md`.
It contains, in fixed order, ten sections (§1 Meta through §10 Variants and
Success Criteria) covering name, domain, phenomenon, research goals,
theory anchors, stylized facts, historical anchors, agent roster,
environment, parameter seeds, variants. See the spec for the exact
sub-section requirements.

No further user input is solicited at this step. The author may have
done their work entirely outside this pipeline (e.g., through a chat
with an LLM, or by writing the file by hand). The pipeline's job is
to *verify* and *consume* — not to extract more material.

---

## 0.2 Procedure

1. **Locate the target file.** Run
   `ls examples/{ScenarioName}/` and confirm a single file matches
   the pattern `{domain}-{scenario}.md`. Reject if:
   - Zero matches → instruct the user to author one per
     `define-simulation-scenario-skill.md`. Stop.
   - Two or more matches → instruct the user to merge or rename.
     Stop.

2. **Re-run target-file validation (§11 of the target spec).** Walk
   every box in `define-simulation-scenario-skill.md §11`:
   structural completeness, cross-section consistency, evidence
   provenance, domain compatibility, distinctiveness, style hygiene.

3. **Defect triage.** For each unchecked box, raise an
   `AskUserQuestion` defect to the target file's author with at most
   four repair options (use `Other` for free-text). The author edits
   the target file; the pipeline re-validates. Loop until §11
   passes three consecutive times.

4. **Resolve domain palette.** Check whether
   `examples/AGENT_POOL/{Domain}/` already exists.
   - If yes (e.g., `examples/AGENT_POOL/finance/`): use it.
   - If no: confirm the target file includes
     `§A Domain Palette Appendix` with the three required palettes
     (Theory Family list, Real-world counterpart enumeration,
     Stylized fact catalogue). Create the empty folder
     `examples/AGENT_POOL/{Domain}/`.
   - If neither: block and instruct the author to add the appendix.

5. **Seed `simulation-build-log.md`.** Create
   `examples/{ScenarioName}/simulation-build-log.md` with the skeleton
   below. Populate §0 Meta by *referencing* the target file (not
   duplicating its content).

6. **Lock the target file.** Edit the target file's §1 row
   `Status: draft` → `Status: locked`. This is the only edit the
   pipeline is permitted to make to the target file until the
   scenario is released.

---

## 0.3 `simulation-build-log.md` Skeleton

The pipeline's build-log contract has four numbered blocks. They
are filled progressively across Phases 0 — 6 of
`create-simulation-pipeline.md`.

```markdown
# {ScenarioName} — Pipeline Build Log

## §0 Meta

| Field        | Content                                                              |
|--------------|----------------------------------------------------------------------|
| Name         | {ScenarioName}                                                       |
| Target file  | examples/{ScenarioName}/{domain}-{scenario}.md                       |
| Target spec  | masim/skills/define-simulation-scenario-skill.md (v1.0)                |
| Domain       | {Domain from target §1}                                              |
| Pipeline     | masim/skills/create-simulation-pipeline.md                              |
| Status       | draft  (upgraded to `released` on Phase 6 closeout)                  |

## §A AGENT_POOL Reuse-or-Create Gate Log

| Candidate archetype | Stage reached | Outcome            | Pool file (if reused / created)                |
|---------------------|---------------|--------------------|------------------------------------------------|
| {populated by Phase 3} |             |                    |                                                |

## §B Research Notes (extends target §4 — §6)

### B.1 Core Theories
For each target §4.{k} entry: verified DOI, key equation, calibration values,
mechanism detail uncovered during research.

### B.2 Empirical Stylized Facts
For each target §5 row: verified range, supporting datasets, replication notes.

### B.3 Historical Events
For each target §6 entry: timeline, participant accounts, primary sources.

### B.4 Agent Taxonomy (mirrors target §7; finance appendix relabels §7 as "Investor Taxonomy")
Canonical taxonomy table with one extra column `Pipeline confirmation`
(`confirmed` / `defect raised`).

### B.5 Parameter Estimates (mirrors target §9)
Every target §9 row, expanded with cross-references from research.

## §C Open Questions and Risks

| Issue | First raised in phase | Status (`open` / `deferred: <reason>` / `resolved`) |
|-------|-----------------------|------------------------------------------------------|

## §D Build Log

| Phase | Date | Outcome (`pass` / `fail` / `defect-raised`) | Reviewer | Notes |
|-------|------|---------------------------------------------|----------|-------|
```

Every block has zero rows at the end of Step 0 except `§0 Meta`,
which is fully populated.

---

## 0.4 What Step 0 Does NOT Do

To avoid duplicating effort with `define-simulation-scenario-skill.md`,
the following are explicitly **out of scope** for Step 0:

| Concern                                            | Owned by                                                       |
|----------------------------------------------------|----------------------------------------------------------------|
| Authoring phenomenon description, agent roster, … | `define-simulation-scenario-skill.md` (the target file's author) |
| Choosing simulation name                           | `define-simulation-scenario-skill.md §2`                          |
| Identifying theory anchors                         | `define-simulation-scenario-skill.md §4`                          |
| Choosing real-world events                         | `define-simulation-scenario-skill.md §6`                          |
| Choosing agent archetypes                          | `define-simulation-scenario-skill.md §7`                          |
| Choosing variants to build                         | `define-simulation-scenario-skill.md §10.1`                       |
| Expanding theories with research notes             | `05-step1-research.md` (Step 1)                                 |
| Running the AGENT_POOL gate                        | `06-step2-agent-design.md §2.2.0` (Step 2)                      |

If a downstream step finds that the target file is missing one of
the items the user owns, the step halts and the pipeline raises a
defect — it does NOT fall back to in-pipeline AskUserQuestion
collection.

---

## 0.5 Distinctiveness Re-Check

Even though the target file's §11 checklist already includes a
distinctiveness check, re-run the cheap version here:

```
ls examples/ | grep -v __init__ | grep -v Demo | grep -v UTEST | grep -v document-sources | grep -v failed
```

For every existing scenario folder, skim the file
`examples/{X}/{*-*}.md` (target) or
`examples/{X}/simulation-bases.md §1` if no target file is present
(legacy scenarios). Check that:

- [ ] Core mechanism in target §2 differs from the existing
      scenario's mechanism.
- [ ] At least two §7 agents differ from those used by the existing
      scenario.
- [ ] §4 theory anchors are not all identical to those of the
      existing scenario.
- [ ] §6 historical anchor is not already the primary anchor of an
      existing scenario.

If the new scenario is too similar to an existing one, consider
extending the existing one with an additional historical case in its
`simulation-bases.md §8` rather than creating a new scenario. Stop
Step 0; surface the recommendation to the author.

---

## 0.6 Exit Conditions for Step 0

Step 0 is complete when:

- [ ] Target file exists at
      `examples/{ScenarioName}/{domain}-{scenario}.md`.
- [ ] Target file §11 has three consecutive PASS runs.
- [ ] Target file `Status: locked`.
- [ ] Domain folder `examples/AGENT_POOL/{Domain}/` exists.
- [ ] `examples/{ScenarioName}/simulation-build-log.md` exists with the
      §0.3 skeleton; §0 Meta references the target file by path.
- [ ] §D Build Log has one row recording Phase 0 outcome.

Proceed to Step 1 (`05-step1-research.md`) only after every box is
ticked.

---

## 0.7 Compatibility Note for Legacy Scenarios

A handful of scenarios under `examples/` were authored before the
target-file requirement was introduced. For those scenarios, the
build-log contract `simulation-build-log.md` may exist *without* a
sibling `{domain}-{scenario}.md`. When such a legacy scenario is
modified, the pipeline SHOULD prompt the author to back-fill a
target file before the modification proceeds. Greenfield scenarios
(authored after this change) MUST always have a target file.
