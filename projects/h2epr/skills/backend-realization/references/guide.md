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

Windowed rows have one accepted completion per run. Before acceptance, an
unchanged rejected attempt waits; changed visible state, received messages or
outgoing pending transport can reopen it. The fingerprint excludes the clock,
global state version and the denial itself. Priorities order competing rows
within their inclusive windows. Keep time bounds in configuration and explain
their semantic basis in the participant and Scenario products.

Use `message_received` for a delivery at the current tick and `message_known`
for received history, with `max_age_ticks` when freshness matters. A remembered
message does not imply that the world still satisfies the action preconditions.

For a content-bearing guard use `payload_equals`, a declared sender and
`selection: latest` over typed message fields. Test negative and withdrawn
updates, including simultaneous conflicting reports. Current event vocabularies
are exposed in advance; do not call this a prefix-clean policy test. Cite matched
guards and the hash-linked observation for decision evidence, keeping configured
`reason` text distinct from generated facts. A Rule window is a policy selection
unless a separate shared boundary is explicitly implemented.

Consider a synthetic issuer and responder with one-tick transport:

| Decision-time evidence | Rule response | Environment/result boundary |
|---|---|---|
| No received notice | wait | public status alone cannot impersonate private receipt |
| Notice arrives after the earliest eligible tick | decide within the remaining window | actual receipt, not the original calendar row, activates choice |
| Notice arrived earlier and remains applicable | use remembered information | current state still determines admission |
| Prior request was rejected; nothing material changed | wait | a new tick is not evidence of feasibility |
| Relevant information changes after rejection | reconsider within the window | another rejection remains a legitimate result |
| Request was accepted | do not resubmit that row | another decision situation requires its own declared row |

Exercise these with a synthetic fixture before adapting an event. Changing a
deadline or route latency in a contract test is not a second backend or a
scientific treatment by itself.

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
