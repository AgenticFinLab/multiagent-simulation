# Launch Readiness Checklist

## Purpose

Use this as the final gate immediately before starting tmux jobs. All earlier
preflight files should already be satisfied; this file is intentionally short
and checklist-oriented.

Start the batch only when all are true:

- [ ] Row list excludes accepted success samples unless a rerun is intentional.
- [ ] Every row dry-runs to one experiment.
- [ ] Config/class/prompt/RAG checks pass.
- [ ] Output directories are clean.
- [ ] API keys and embedding assets are present.
- [ ] Machine CPU budget is documented and not overcommitted.
- [ ] Timeout/stall flags are included.
- [ ] tmux session names are unique.
- [ ] RAG rows are limited to the planned RAG concurrency.
- [ ] Known issue classes from
  `docs/example-revision-guide/08-runtime-failure-patterns.md` are reviewed.
