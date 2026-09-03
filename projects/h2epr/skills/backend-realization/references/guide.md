# Backend realization guide

## Shared versus backend-specific semantics

All backends receive the same actor identities, observations, lifecycle state,
admissible intent vocabulary, environment, routes, and clock. A backend may
choose an intent; it may not alter the shared package, admit its own request,
write world state, or declare success.

Build a coverage matrix with one row per actor and decision situation:

| Field | Required content |
|---|---|
| activation | observations and lifecycle conditions |
| available responses | exact shared intent IDs including justified no-op |
| implementation entry | Rule row or prompt/proposal path |
| ordering/precedence | deterministic order or explicit model protocol |
| pending behavior | wait, revise, cancel, or other declared response |
| failure route | typed terminal code or bounded retry/repair |

Every non-no-op shared intent needs at least one reachable decision path.

## Backend contracts

### Rule

Use the registered declarative implementation. Put selected thresholds and
ordered categories in Rule configuration, not the Agent Definition. Deny
network/model access. Require typed default no-op, decision-row coverage,
permitted payloads, stable semantic actor prefixes, deterministic ordering,
opaque-ID invariance, and two byte-identical same-input runs.

### LLM

Pin renderer, prompt contract, response schema, parser, provider/model/version,
service mode, decoding values and bases, timeout, attempt limit, and all source
hashes. Invalid, unavailable, or exhausted output is a typed failure; do not
silently substitute Rule behavior.

### RuleLLM

Pin the same proposal surface plus constraint catalog, validator, bounded
repair, rejection, and declared safe fallback. A fallback may be a typed
failure or explicit safe intent, never an undisclosed full Rule policy.

Planned catalog status is not implementation. Package load must fail closed
until the exact binding and registered factory exist.

## Adversarial verification

Exercise every permitted intent and failure family; invalid top-level carrier,
actor, target, payload, range, authority, and lifecycle; missing observation;
pending result; generated-ID and row-order perturbation; concurrent reducer
permutation; implementation source tamper; configuration drift; backend
substitution; model timeout/malformed response where applicable; and
environment rejection after a valid decision.

## Attachment and handoff

Publish human realization, machine realization, configuration parents,
implementation source inventory, manifest, and checksums. Attachment must
preserve backend-neutral `package_sha256` while changing the catalog/binding
surface in the documented way.

Report backend status, implementation ID/version, actor/situation/intent
coverage, configuration and source hashes, model/network access, failure codes,
negative tests, core-identity result, limitations, and next legal action.
