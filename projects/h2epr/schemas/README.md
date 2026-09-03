# Benchmark-simulation schemas

This directory is the single released machine-shape surface for the current
H2EPR workflow. [`catalog.json`](catalog.json) is its exhaustive inventory.
Protocol versions remain explicit inside schemas and artifacts; replaced
tracked bytes remain available through Git rather than parallel `v1/`, `v2/`,
or draft directories.

## Schema families

| Family | Schemas | Authority represented |
|---|---|---|
| dataset admission | `source-profile` | exact construction allow-list, exposure, and claims |
| participant semantics | `participant-roster`, `actor-map`, three registries, `participant-interface`, `participant-semantic-index` | roster accounting and portable actor capabilities |
| Scenario and values | `scenario-interface`, `scenario-mechanism`, `scenario-configuration`, configuration admission and coverage | world semantics and selected values |
| release and package | `semantic-release-manifest`, `semantic-asset-index`, `event-package-assembly`, compiled products, package manifest, backend realization and binding | immutable parents and compiled identity |
| runtime evidence | observation, decision, trace record, tick/run seals, run manifest/receipt, replay receipt, Generated EPG, determinism and conformance receipts | execution, integrity, replay, and graph evidence |
| experiment preflight | experiment plan and admission receipt | read-only comparison planning |
| repository discovery | current-event registry | sole current event publication paths |

Every schema has a stable `$id`, a reader-facing title and description,
closed-object boundaries where extensibility is not intentional, and an
explicit content-hash field when the artifact is an identity-bearing release.
Examples belong in templates and synthetic fixtures so they are executable and
cannot drift into decorative schema annotations.

## What JSON Schema does not prove

JSON Schema checks one document's local structure. The H2EPR loaders and
publishers additionally rederive:

- canonical self-hashes and exact file inventories;
- safe repository-relative paths and symlink boundaries;
- three-file source admission and event identity;
- semantic parent hashes, actor/interface/registry closure, and action-space
  non-widening;
- configuration pointer existence, uniqueness, domain validity, and exhaustive
  provenance coverage;
- package core, backend catalog, realization, configuration, binding, and
  implementation-source identities;
- trace hash chains, tick/run seals, replay, count maps, Generated EPG coverage,
  transport closure, determinism, and opaque-ID invariance.

A schema-valid producer assertion is therefore input to verification, never a
substitute for independent derivation.

## Change policy

Add or change a field first in a synthetic failing case, then update the
schema, owning loader/validator, template, Skill guide, and affected publication
logic as one contract change. A breaking change replaces the current schema
only after every consumer and test passes. Event vocabulary, slugs, actors,
state fields, and policy thresholds must not appear in a common schema.

The experiment schemas describe plan admission only. They do not imply a
matrix executor, attempt ledger, scientific metric, or implemented model
backend.
