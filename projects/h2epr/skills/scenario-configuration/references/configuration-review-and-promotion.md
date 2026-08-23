# Configuration review and promotion

Use this reference for a separate substantive review of a Scenario
Configuration and for a later, explicitly authorized atomic promotion.

## Review boundary

Review the candidate against its pinned authorities, public design, and
closure record. Do not use implementation behavior, simulation output, known
later outcomes, or private authoring notes to repair or justify the candidate.

Prefer a different reviewer or a clean review context when available. When
that is not available, perform a new pass from the released inputs and record
the limitation.

Classify findings:

- `BLOCKER` — identity/integrity failure, authority duplication, future
  leakage, outcome forcing, execution enabled with missing prerequisites, or a
  semantic contradiction that invalidates the package;
- `MAJOR` — missing configuration family, ambiguous target, opening/input
  inconsistency, unsupported default, incomplete closure, or a material claim
  mismatch; and
- `MINOR` — a local clarity, traceability, naming, or packaging defect that
  cannot change behavior or claims.

## Substantive review checklist

### Purpose, claims, and provenance

- Is there exactly one primary declared purpose?
- Are historical calibration, historical validation, and known-outcome
  fitting stated explicitly rather than inferred?
- Do all semantic inputs identify exact accepted bytes?
- Does every material selection or projection retain its source class and
  identification status?
- Is a mechanism-coverage or sensitivity configuration kept distinct from a
  historical baseline or scientific-validity claim?

### Definition and mapping closure

- Does every required Definition configuration family have one carrier or an
  explicit routed gap?
- Are actor, unit, capability, observation, intent, lifecycle, policy, and
  invariant counts derived from the pinned authorities?
- Does the candidate preserve scenario, participant, mapping, contract, and
  reducer ownership instead of becoming a second authority?
- Are all references unique, resolvable, and type-compatible?

### Time, information, and exogenous inputs

- Does the clock preserve evidenced precedence and bounded uncertainty?
- Are issue, route, delivery, receipt, freshness, correction, and visibility
  distinct where behaviorally material?
- Does each exogenous input have a basis, activation, exact target, typed
  effect, visibility rule, causal limit, and outcome-forcing assessment?
- Do opening records agree with later activation instead of silently
  preloading a future input?

### Assembly, authority, and resources

- Is each entity represented by one canonical actor interface, authority
  graph, relationship set, and resource owner across capabilities?
- Does every population unit retain its own host, private state, weight status,
  and resource scope?
- Are authority, title, routing, recommendation, willingness, and owned
  resources kept distinct?
- Are unknown, unavailable, disputed, and synthetic values explicit rather
  than replaced with zeros, infinities, or unsupported estimates?

### Policies, sensitivities, and completion

- Is every required policy selected semantically and assigned a binding
  status?
- Does execution remain disabled while any required policy, loader,
  projection, or authorization is absent?
- Does every sensitivity operation name an exact target kind, ID, field, and
  allowed replacement value?
- Are structural uncertainty and parameter/input uncertainty kept distinct?
- Are normal, bounded-incomplete, fail-closed, and carry-forward outcomes
  inspectable?

### Minimality and scalability

- Does every field serve the declared purpose or an accepted invariant?
- Did the candidate avoid adding event narrative, participant behavior,
  implementation design, calibration, evaluation, or full-runtime planning?
- Can the method be reused on the next event without importing event-specific
  IDs or conclusions into the template or Skill?

## Review verdict

Use one of:

- `ACCEPT_FOR_OWNER_REVIEW_AS_NON_EXECUTABLE_CONFIGURATION`;
- `RETURN_FOR_CONFIGURATION_REVISION`;
- `RETURN_TO_SCENARIO_MAPPING_OR_EVIDENCE`; or
- `BLOCKED_BY_OWNER_DECISION`.

List limitations and nonblocking watchpoints separately. A review verdict does
not authorize promotion, engineering admission, policy implementation,
simulation, or evaluation.

## Owner decision record

Before promotion, record:

- stable decision IDs;
- the exact question and alternatives considered;
- the selected disposition and rationale;
- affected configuration fields and claims;
- whether the disposition changes semantics or only authorizes promotion;
- unresolved limitations; and
- the next legal stage.

If a decision changes semantics, revise the candidate and repeat substantive
review before promotion.

## Atomic promotion checklist

Treat promotion as one reviewable integrity change set. It need not imply any
particular version-control operation.

- [ ] All `BLOCKER` and `MAJOR` findings are resolved or routed out of the
  package; no semantic finding is waived silently.
- [ ] Every required owner decision is recorded and accepted.
- [ ] The reviewed semantic payload is frozen before integrity values are
  computed.
- [ ] Promotion-only identity, version, status, decision-link, and provenance
  changes are enumerated; no other semantic delta is present.
- [ ] `README.md` identifies scope, files, claims, verification, execution
  boundary, limitations, and next legal stage.
- [ ] `manifest.json` pins all semantic inputs, lists every promoted artifact,
  records owner decisions and claim boundaries, and carries hashes for every
  non-self payload member according to one declared integrity envelope.
- [ ] `SHA256SUMS` covers the final manifest, semantic payload, review, and
  closure files owned by the release directory; the manifest records upstream
  and owner-decision identities.
- [ ] Every hash is recomputed after final bytes settle and each local package
  verifies from its owning directory.
- [ ] The package remains non-executable unless a separate later authority has
  satisfied every execution prerequisite.
- [ ] No schema, loader, carrier projection, policy implementation, trace,
  simulation, evaluation, or validity claim has entered through promotion.

Any semantic edit after the integrity check invalidates the promotion and
returns the package to review.
