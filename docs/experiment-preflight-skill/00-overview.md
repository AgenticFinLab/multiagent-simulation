# Experiment Preflight Skill — Overview

This folder is the **authoritative preflight skill guide** for preparing
full-round experiment batches. It is intentionally separate from
`docs/example-revision-guide/`.

## What This Folder Is

This guide converts real experiment failures into a reusable preflight workflow
for full-round MASim batches. Use it after example repair and before launching
local or remote experiment jobs.

The guide is based on failures observed during the `fix-scenarios` and
`simulation-180` campaigns: prompt/parser contract drift, RAG embedding drift,
unsupported config schema, API quota contamination, native Ray aborts,
progress-hidden timeouts, and machine-level CPU overcommit.

## Folder Structure and Reading Order

| File | Stage | Purpose |
|---|---|---|
| `00-overview.md` | Orientation | This file: guide scope, reading order, and relation to adjacent docs. |
| `01-required-inputs-and-row-selection.md` | Scope | Required batch inputs, row selection, and output directory rules. |
| `02-repository-and-config-gates.md` | Static gates | Repository, environment, dry-run, config, class, topology, and persona checks. |
| `03-api-and-rag-contract-gates.md` | API gates | Prompt/parser contract, LLM model policy, RAG assets, and embedding checks. |
| `04-runtime-scheduling-and-timeouts.md` | Runtime plan | tmux/Ray CPU budgeting, RAG concurrency, stagger policy, and timeout settings. |
| `05-failure-classification-and-postrun.md` | Review | Failure classification, source-repair boundaries, and post-run intake review. |
| `06-launch-readiness-checklist.md` | Final gate | Short checklist to apply immediately before starting tmux jobs. |

## When To Use This Guide

- Use `docs/example-revision-guide/` when repairing an existing example.
- Use this guide when deciding whether a selected set of rows is ready to run
  on local or remote experiment machines.

## Relationship To Adjacent Guides

`docs/create-example-skill/` defines how examples should be built from scratch.
`docs/example-revision-guide/` defines how existing examples should be repaired
and standardized. This guide does not repair examples directly; it checks
whether already selected scenario-mode rows are safe to execute as full
experiments.

## Primary Execution Path

Read `01` through `05` in order, then apply
`06-launch-readiness-checklist.md` immediately before launching any full
configured-round batch.
