# Whitefly — Agent Definition

## 1. Model overview

| Field | Account |
|---|---|
| Semantic ID | `h2epr.0616.agent.whitefly.v0.4` |
| Runtime actor | `whitefly` |
| Benchmark event | SingHealth Data Breach (`H2EPR-0616`) |
| Source participant | `P_1` — Whitefly |
| Representation | `agent` |
| Event role | intrusion actor |
| Dataset exposure | Full Draft exposed; construction practice only |

## 2. Benchmark participant and representation

This semantic parent retains the participant as an autonomous action-bearing boundary because one or more Draft episodes assign it an exposed transition. Attribution is a dataset assertion; tactics and private intent are not reconstructed.

The runtime boundary represents one decision interface, not every employee, member, or internal subunit. Split it when the exposed Draft requires simultaneous independent internal choices that cannot share one authority boundary; narrow it when an admissible intent is shown to belong to another participant. Either change requires a successor.

## 3. Dataset basis and provenance

Source anchors:

- `draft_epg:S1/E1/P_1`
- `draft_epg:S1/E2/P_1`
- `draft_epg:S4/E8/P_1`

These anchors are benchmark records, not independently verified history. The asset adds no external evidence or hidden participant state.

## 4. Event role, relationships, and authority

Role: intrusion actor.

Authority boundary: May execute the two intrusion transitions exposed by the Draft EPG.

Routes and eligible targets are declared by the participant interface and shared configuration. Relationship status and event outcomes remain authoritative scenario state.

## 5. Decision situations, observations, and state

At each coordinate the runtime provides the same sealed public state, any actor-private projection, delivered messages, pending message lifecycles, and this actor's permitted intents. The definition grants no undeclared source access.

Unavailable observations are not reconstructed. If required information is missing or stale, the participant must choose an admissible response that does not claim that information, normally `no_op`. A pending lifecycle remains pending until the transport layer records delivery, expiry, or failure; it cannot be treated as a completed communication.

The environment, rather than the participant object, owns authoritative state. This participant can propose transitions affecting:

- `entities.intrusion.access_status`
- `entities.patient_data.theft_status`

## 6. Admissible decision semantics

The backend may choose only:

- `establish_persistent_access`
- `exfiltrate_patient_data`
- `no_op`

Activation requires both a current logical coordinate and a permitted intent in the shared interface. Outside that condition the response is `no_op`. Delay or abstention is represented only by an admissible `no_op` and is reopened by a later coordinate or newly delivered observation. When several intents remain eligible, the backend may choose among them but may not widen authority or declare an environment result. Rule selects with published coordinate and guard rows; LLM and RuleLLM remain planned and fail closed. A Draft-supported autonomous choice that cannot be expressed within this set falsifies the Definition and requires a successor.

## 7. Intent and environment-result boundary

The participant emits one typed action intent and zero or more typed message
intents. The H2EPR environment owns domain admission and constructs typed
dispositions and state deltas. The MASim reducer owns the single authoritative
commit; MASim also owns transport, trace, seals, and replay. The participant
cannot declare success.

## 8. Configurable dimensions and uncertainty

Logical coordinates, initial values, and routes are selected by shared configuration. Rule rows belong to backend configuration. This semantic parent fixes no probability, personality, threshold, model prompt, or fitted historical parameter.

## 9. Worked cases and contract falsification

- **Normal operation:** at a declared coordinate with satisfied guards, the backend may emit one listed intent. Admission and state effect remain environment decisions.
- **Missing information:** when an observation required for a substantive intent is absent or stale, the actor emits `no_op` or another listed response that does not claim the missing fact.
- **Pending state:** a pending message or action lifecycle is observed as pending; the actor cannot treat it as delivered, accepted, or effective.
- **Authority denial:** an intent with an unknown target, undeclared parameter, or actor outside the eligible set is rejected without expanding the actor boundary.
- **Adverse environment result:** a permitted intent may be rejected, may have no effect, or may lose a concurrent write; the participant cannot rewrite that disposition as success.
- **Perturbation:** changing a relevant guard, route, or delivered observation may change the admissible choice, while changing only an opaque runtime identifier must not. A source-supported action outside the published intent set requires a successor.

## 10. Limitations and source anchors

Attribution is a dataset assertion; tactics and private intent are not reconstructed. Full Draft exposure makes this a dataset-conditioned construction baseline, not a held-out reconstruction or calibrated behavioral model. Any change to identity, representation kind, authority, or intent scope requires a successor and regenerated downstream identities.

Anchors retained by the machine semantic index:

- `draft_epg:S1/E1/P_1`
- `draft_epg:S1/E2/P_1`
- `draft_epg:S4/E8/P_1`
