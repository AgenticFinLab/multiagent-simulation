# Experiment preflight guide

## When this layer applies

Use experiment admission only for a planned matrix of multiple event,
backend, or seed rows. Building or reproducing one event does not require an
experiment plan. Admission is read-only and does not launch runs.

## Required decisions

Before writing a plan, fix:

- the comparison question stated as an engineering or descriptive objective;
- accepted event packages and implemented backend bindings;
- explicit seed sets and generated-identity mode;
- a unique ignored custody root for every row;
- model identity, prompt/response contracts, decoding controls, and attempt
  limit for any model backend;
- within-event or cross-event comparison groups;
- analysis definitions and unavailable-value behavior;
- concurrency, progress polling, stall timeout, wall timeout, retries, and
  preservation of failures;
- supported and excluded claims.

## Admission gates

| Gate | Pass condition | Failure owner |
|---|---|---|
| row identity | package and binding reload with pinned hashes | plan or package |
| backend availability | selected binding is implemented | backend realization |
| custody | normalized paths are unique and below experiment custody | plan |
| seed | finite, unique integers; group parity where required | plan |
| model provenance | complete and equal controls for compared model rows | plan/backend |
| comparison | distinct backends within event or distinct events across event | plan |
| analysis | every group has a matching pinned definition | plan/analysis |
| scheduling | poll < stall <= wall; positive limits | plan |
| retry | only declared transient/resource/stall classes; failed custody retained | plan/executor |
| claim | all mandatory scientific exclusions retained | plan |

Rule rows carry no model provenance. A provider endpoint or model name does not
make LLM or RuleLLM implemented; package admission must find a real binding.
No failure may silently fall back to another backend.

## Comparison parity

Within one event, compared backends share package hash, actor and observation
universe, environment, timeline, seed set, runtime, trace, output roles, and
analysis definition. LLM and RuleLLM rows additionally share model controls so
the constraint layer is the intended difference.

Across events, rows share one backend, seed set, contract family, output role
surface, runtime/kernel identities, closure requirements, and claim boundary.
Event vocabulary and event-local metrics may differ. Missing measures remain
unavailable rather than receiving invented zeros or forced mappings.

## Attempts and closeout

A future executor must allocate distinct custody per attempt, define progress
from durable sealed milestones, preserve the first failure, and account for all
planned rows in the final denominator. Retry is a new attempt, never an
overwrite or continuation assumed safe by default.

The closeout distinguishes admission failure, model-contract failure,
provider transient, resource exhaustion, stall, runtime contract, evidence
integrity, and analysis failure. Only independently verified run releases may
enter a published comparison.

## Current implementation boundary

The repository implements plan schema validation and admission receipts. It
does not yet implement a generic experiment executor, attempt ledger, or
experiment release publisher. Rule is the only implemented backend. These are
explicit stage limits, not skipped tests.
