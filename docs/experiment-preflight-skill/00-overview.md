# Experiment Preflight Skill

This folder defines the reusable preflight procedure for full-round experiment
batches. It is intentionally separate from `docs/example-revision-guide/`.

Use:

- `docs/example-revision-guide/` when repairing an existing example.
- `docs/experiment-preflight-skill/SKILL.md` when deciding whether a selected
  set of rows is ready to run on local or remote experiment machines.

The skill is based on real failures observed during the `fix-scenarios`
campaign: prompt/parser contract drift, RAG embedding drift, unsupported config
schema, API quota contamination, native Ray aborts, progress-hidden timeouts,
and machine-level CPU overcommit.

Primary file:

- `SKILL.md`: executable preflight checklist for future agents/developers.
