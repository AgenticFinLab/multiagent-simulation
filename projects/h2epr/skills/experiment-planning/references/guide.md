# Experiment planning guide

## Planning boundary

An admitted plan fixes a comparison before execution. It does not launch a
run, prove backend/model availability, create an attempt ledger, or validate a
scientific hypothesis. Use this layer only after individual package/backend
releases exist and a comparison would answer a declared bounded question.

## Matrix rows

Every row has a stable row ID, event/package/binding identities, explicit seed
set, fresh ignored custody root, analysis contracts, and claim exclusions.
Model-backed rows also pin provider, model, version, service mode, prompt and
response contract hashes, all decoding values with provenance bases, and
attempt limit.

Use comparison groups deliberately:

- within-event backend comparison: same event, package core, shared settings,
  seeds, runtime, environment, and analysis contract;
- cross-event backend conformance: distinct events, same implemented backend,
  seed set, contract family, and event-neutral measures;
- LLM versus RuleLLM: same model-control signature unless one declared control
  is the treatment.

## Scheduling and attempt policy

Declare concurrency ceiling, capacity assumption, progress signal, poll
interval, wall timeout, stall timeout, retryable failure classes, finite retry
limit, and custody preservation. A retry is a new attempt with its own root and
parent reference. Never erase failed attempts or exclude them silently from a
denominator.

Classify at least admission, backend/model availability, provider, quota,
resource, stall, runtime, integrity, publication, and analysis failures. A
retry policy cannot convert a semantic or integrity defect into a transient
failure.

## Analysis contract

Pin definitions before results: required inputs, unit, denominator, missing
behavior, aggregation, exclusions, and event-local exceptions. A measure name
without a computation definition is not an analysis contract.

## Admission failures

Reject unavailable/planned backends, package or binding drift, aliased/unsafe/
reused custody, empty seeds, comparison parity mismatch, incomplete model
signature, unequal uncontrolled model settings, missing analysis bytes,
unbounded timeout or retry, overlapping row IDs, and incomplete claim
exclusions.

## Handoff

Record plan/receipt hashes, row/group/seed counts, custody roots, model-control
signatures, parity checks, scheduling and retry policy, analysis identities,
failure classes, validation, limitations, and next legal action. Stop after
admission unless execution is separately authorized.
