# Scenario Configuration template

## Identity and purpose

Name the event, semantic parents, configuration version, comparison group,
exposure, and engineering claim.

## Exact inputs

Pin roster, interfaces, Scenario Definition, schema, environment and annotation
implementations by path and content identity.

## Shared comparison settings

Declare ordered logical coordinates with Draft stage/episode anchors, active
actor IDs, typed initial state, explicit routes, observation contract,
termination flags, exogenous schedule if any, and assumptions. Mark each value
as dataset-derived, structural, synthetic, sensitivity, model, or run-local.
Every top-level `/settings/<name>` pointer must appear exactly once in the
configuration's `value_provenance`. Publish a separate, self-hashed
`provenance-coverage.json` that proves the declared pointers cover the whole
selected setting surface. If a value genuinely has no available source, put
its pointer in a typed exemption with review authority and a successor trigger;
silence is not an exemption.

## Backend settings

For a backend-specific configuration, record only decision-production settings.
Rule, LLM, and RuleLLM may differ here without renaming the shared package.
Backend configurations use the same exhaustive provenance and coverage rule.

## Validation and promotion

Require schema validity, exact parent hashes, actor/interface closure, no hidden
defaults, exhaustive provenance coverage, and a typed admission receipt. The
compiler must rederive the receipt
from the configuration, roster, actor map, participant/scenario interfaces,
Scenario Mechanism, and exposed Draft; a self-hashed producer assertion is not
admission evidence. Configuration admission does not prove policy behavior or
runtime success.
