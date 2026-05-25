# Required Inputs and Row Selection

## Purpose

Use this file before any concrete row checks. It defines the minimum inputs
needed to decide whether a planned experiment batch is well-scoped and avoids
rerunning already accepted samples by accident.

## Required Inputs

Prepare these before checking:

- Git commit/branch expected on each machine.
- Row list as `Scenario__Mechanism`.
- Machine plan: tmux session names, CPU budget per session, RAG/nonRAG split.
- Output directories.
- API/env expectations: `ARK_API_KEY`, `HUNYUAN_API_KEY`, `MINERU_API_KEY`.
- Current accepted-success ledger, so already accepted rows are not rerun.

## Row Selection Rules

- Exclude accepted success samples unless a rerun is intentional.
- Treat full configured rounds as the only final sample policy.
- Do not use 20-round canaries as final samples.
- If a row failed before, read its latest failure record before scheduling it.
- If a row is being rerun after source changes, use a clean output directory.

## Output Directory Rules

Every real run must write to a new, explicit batch directory. The directory name
should encode the branch, date, wave, and purpose strongly enough that later
resource-pack intake can trace provenance without reading tmux history.

Final output directories must not already exist unless the rerun policy
explicitly says they are disposable.
