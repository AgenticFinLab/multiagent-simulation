# Step 0: Ingest the Scenario Target File

## Purpose

Step 0 is the *handoff point* between the user-authored intent file
(`{domain}-{scenario}.md`, specified by
`masim/skills/create-simulation-target-skill.md`) and the per-step
methodology in this folder. Step 0 does **not** collect new user
input. It reads the target file, re-validates it, and seeds the
pipeline's build-log contract (`simulation-define.md`) so that
Steps 1 — 4 have a stable source of truth.

If a target file does not yet exist, **stop**. Direct the user (or
upstream LLM) to `masim/skills/create-simulation-target-skill.md`
and have them author the file there first.

---

## 0.1 Required Inputs

Step 0 requires only one file from the user:

```
examples/{ScenarioName}/{domain}-{scenario}.md
```

This file MUST conform to `masim/skills/create-simulation-target-skill.md`.
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
     `create-simulation-target-skill.md`. Stop.
   - Two or more matches → instruct the user to merge or rename.
     Stop.

2. **Re-run target-file validation (§11 of the target spec).** Walk
   every box in `create-simulation-target-skill.md §11`:
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

5. **Seed `simulation-define.md`.** Create
   `examples/{ScenarioName}/simulation-define.md` with the skeleton
   below. Populate §0 Meta by *referencing* the target file (not
   duplicating its content).

6. **Lock the target file.** Edit the target file's §1 row
   `Status: draft` → `Status: locked`. This is the only edit the
   pipeline is permitted to make to the target file until the
   scenario is released.

---

## 0.3 `simulation-define.md` Skeleton

The pipeline's build-log contract has four numbered blocks. They
are filled progressively across Phases 0 — 6 of
`create-simulation-skill.md`.

```markdown
# {ScenarioName} — Pipeline Build Log

## §0 Meta

| Field        | Content                                                              |
|--------------|----------------------------------------------------------------------|
| Name         | {ScenarioName}                                                       |
| Target file  | examples/{ScenarioName}/{domain}-{scenario}.md                       |
| Target spec  | masim/skills/create-simulation-target-skill.md (v1.0)                |
| Domain       | {Domain from target §1}                                              |
| Pipeline     | masim/skills/create-simulation-skill.md                              |
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

### B.4 Investor Taxonomy (mirrors target §7)
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

To avoid duplicating effort with `create-simulation-target-skill.md`,
the following are explicitly **out of scope** for Step 0:

| Concern                                            | Owned by                                                       |
|----------------------------------------------------|----------------------------------------------------------------|
| Authoring phenomenon description, agent roster, … | `create-simulation-target-skill.md` (the target file's author) |
| Choosing simulation name                           | `create-simulation-target-skill.md §2`                          |
| Identifying theory anchors                         | `create-simulation-target-skill.md §4`                          |
| Choosing real-world events                         | `create-simulation-target-skill.md §6`                          |
| Choosing investor archetypes                       | `create-simulation-target-skill.md §7`                          |
| Choosing variants to build                         | `create-simulation-target-skill.md §10.1`                       |
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
- [ ] `examples/{ScenarioName}/simulation-define.md` exists with the
      §0.3 skeleton; §0 Meta references the target file by path.
- [ ] §D Build Log has one row recording Phase 0 outcome.

Proceed to Step 1 (`05-step1-research.md`) only after every box is
ticked.

---

## 0.7 Compatibility Note for Legacy Scenarios

A handful of scenarios under `examples/` were authored before the
target-file requirement was introduced. For those scenarios, the
build-log contract `simulation-define.md` may exist *without* a
sibling `{domain}-{scenario}.md`. When such a legacy scenario is
modified, the pipeline SHOULD prompt the author to back-fill a
target file before the modification proceeds. Greenfield scenarios
(authored after this change) MUST always have a target file.
