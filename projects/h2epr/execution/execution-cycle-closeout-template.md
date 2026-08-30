# H2EPR Full-roster Rule Execution Cycle Template

Use this template after an event has accepted configuration admission and
bounded lineage conformance, and only when full-roster Rule execution is an
authorized extension. It keeps Policy Realization, executable assembly,
materialization, replay, and graph closure visible without turning them into
separate administrative gates.

Complete only the sections reached by the authorized endpoint. Prefer placing
the fields below in an existing manifest, release README, receipt, or review.
Create a separate instantiated record only when those artifacts cannot carry
the cycle boundary clearly.

## 1. Cycle boundary

| Field | Record |
|---|---|
| Event and purpose | `<event ID, title, slug, and the engineering question>` |
| Authorized endpoint | `<Policy Realization, executable successor, run and generated graph, or cross-event method review>` |
| Exact semantic parents | `<accepted identities and hashes for scenario, roster, mapping, configuration, admission, and bounded conformance>` |
| Rule and framework boundary | `<Rule-only implementation roots and public MASim interfaces consumed>` |
| Run identity and custody | `<seed, materialization identity policy, event-qualified ignored output root, and overwrite rule>` |
| Claim boundary | `<what the execution may establish and the historical, empirical, or scientific claims excluded>` |
| Stop conditions | `<changes or missing inputs that return work to an owning layer>` |

State the boundary in one sentence:

> This cycle may `<last authorized product>` from `<exact accepted parents>`
> and stops before `<excluded later work or claim>`.

## 2. Derived coverage inventory

Derive these values from accepted machine-readable parents. Do not maintain a
second hand-written inventory when an admitted artifact already owns it.

| Coverage family | Expected surface | Derivation authority | Closed by |
|---|---:|---|---|
| Actor-capability and population-unit placements | | | |
| Decision commitments | | | |
| Intent placements and explicit non-emitting branches | | | |
| Participant Rule implementations | | | |
| Selected Scenario policies | | | |
| Required lifecycle families | | | |
| Declared invalid, delayed, failed, expired, or duplicate paths | | | |
| Runtime components and routes | | | |

Record a difference only when it reflects a real product-level versus
actor-placement distinction. A shared semantic identity instantiated for
several actors is not a coverage discrepancy.

## 3. Product closeout

| Product | Result and exact identity | Admission or closure evidence | Verification | Status or limitation |
|---|---|---|---|---|
| Policy Realization | | | | |
| Executable successor and runtime bundle | | | | |
| Canonical and independent repeat materializations | | | | |
| Authoritative replay | | | | |
| Trace-derived generated EPG | | | | |
| Cross-event method finding, if this cycle exposes one | | | | |

Omit unreached rows. An omitted later product is not a defect when it lies
outside the authorized endpoint.

## 4. Cross-object checks

- [ ] Every configured placement, commitment, intent, selected policy,
  required lifecycle, and declared failure has exactly one implementation or
  explicit disposition.
- [ ] Accepted semantic parents retain their exact identities and have not
  been repaired or expanded in the execution layer.
- [ ] Participant observation and persistent state remain inside the accepted
  information and ownership boundaries.
- [ ] Intent creation, message transport, environment adjudication, reducer
  effects, and later observation remain distinguishable.
- [ ] One entity retains one canonical actor, authority graph, relationship
  set, and resource owner across composed capabilities.
- [ ] Unsupported inputs, missing bindings, ambiguous identities, hidden
  defaults, path escape, and partial assembly fail before execution.
- [ ] Two fresh same-input materializations satisfy the shared deterministic
  run-document and seal contract.
- [ ] Replay reconstructs the terminal state from sealed trace evidence.
- [ ] Every generated graph item resolves to deterministic sealed trace
  provenance.
- [ ] Large outputs remain in checksummed event custody, while tracked release
  evidence is compact and sufficient to verify identity and closure.

## 5. Verification and disposition

| Check | Command or method | Result | Scope or limitation |
|---|---|---|---|
| Focused behavior and negative branches | | | |
| Policy/executable admission | | | |
| Runtime, replay, and graph closure | | | |
| Repository JSON, links, checksums, and package integrity | | | |
| Full affected regression | | | |
| Publication and claim-boundary review | | | |

Use one disposition from the project closeout checklist. Conclude with:

> The cycle stops at `<accepted endpoint>` because additional `<work>` would
> test `<a different engineering, empirical, or scientific question>`.
