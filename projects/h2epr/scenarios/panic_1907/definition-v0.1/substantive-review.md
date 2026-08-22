# H2EPR-0288 Event Scenario Definition substantive review

> Accepted substantive review · 2026-08-22 · local fixed-input review

## Review object

| Field | Value |
|---|---|
| Scenario | `h2epr.scenario.0288.panic_1907@0.1.0-candidate.1` |
| Scenario candidate SHA-256 | `d8a198495394e2ea942e3ca91f55e355ba54de533461bebb5893293cf30808c7` |
| Interface closure SHA-256 | `9d287ac24cf86dd63dc0f4e2a5127eba452d88f870dae3aaa468bcb344a4bf7c` |
| Roster input | `H2EPR-0288-ROSTER-DEFINITION-RELEASE-v0.1` |
| Mapping input | `H2EPR-0288-CONSOLIDATED-MAPPING-v0.1` |
| Carrier target | H2EPR Contracts V1; no mutation authorized |
| Evidence boundary | fixed local evidence ledger/source register; all focal outcomes exposed; no network or new evidence used |
| Review permission | semantic and interface review only; no implementation, simulation, Rule policy, LLM/RAG, G5, or Git promotion |
| Owner resolution | `OD-SC-01` through `OD-SC-04` accepted on 22 August 2026 |

The review restarts if either reviewed file changes materially after the hashes
above.

## Executive judgment

The candidate is suitable for project-owner review. It defines a bounded
event-process question, can produce trajectories that do not reproduce the
known historical outcome, gives every material decision and state transition
one owner, separates participant knowledge from world truth, and closes the
complete released interface without inventing a Contracts requirement.

No current Blocking or Major finding was found. One pre-review issue—an
unsupported exact 2 November horizon—was corrected before the reviewed hashes
were recorded. The candidate now requires the later configuration to pin and
justify an exact horizon inside the evidence-supported early-November interval.

## Substantive checks

### Boundary and causality — PASS

- Endogenous, initial, exogenous, and excluded processes are separate.
- Opportunity phases permit overlap, persistence, reversal, failure, and
  alternative outcomes; they do not force the historical chronology.
- Known run, suspension, assistance, pool, and market outcomes are explicitly
  exposed and are not baseline transition rules.
- Engineering closure, reconstruction, calibration, validation, and
  prediction claims remain distinct.
- The scenario stops and returns to the roster when an excluded actor would
  need to make an autonomous choice.

### Authority and ownership — PASS

- Seven named decision interfaces and five population products retain their
  released boundaries.
- Wider presidents' forum, Treasury, NYSE governance, examiner execution,
  transport, and reducer are explicit scenario processes rather than hidden
  Agents.
- Morgan, committee, intermediaries, contributors, facilities, venues, and
  resource owners remain distinct.
- Same-entity bank-resource and lender capabilities compose under one actor,
  authority graph, relationship state, and resource owner.
- Participant posture/reference state never competes with authoritative case,
  relationship, resource, service, loan, or result state.

### Time and information — PASS

- Material inputs require source/owner, event/as-of time, version, visibility,
  delivery state, and appropriate fallback.
- Publication, issue, transport, delivery, business acceptance, and result are
  distinguished.
- Missing, stale, disputed, corrected, superseded, unavailable, and unknown
  states have semantic consequences.
- Compound observations require a coherent frozen version set; references
  cannot dereference live hidden state.
- Future outcomes, later rules, other units' private state, Reference EPG,
  evaluation evidence, and system-only variant/audit labels are forbidden.

### Institutions, relationships, and resources — PASS

- Membership, mandate, jurisdiction, authority, procedure, relationship, and
  effective intervals are institutional state rather than personality.
- KT–NBC clearing, NBC–NYCH membership, Knickerbocker nonmembership,
  committee mandate, support routes, host claims, call contracts, and venue
  relations all have authoritative owners.
- Available, offered, reserved, committed, scheduled, transferred, repaid,
  released, failed, and reversed resources remain distinct.
- Collateral control, eligibility, valuation, encumbrance, custody, and
  realization remain distinct.
- Concurrent capabilities cannot double-count a resource prestate.

### Lifecycles, adjudication, and results — PASS

- Thirteen shared lifecycle families cover the full released surface.
- Stable identity, owner, state/version, predecessors, supersession, expiry,
  duplicate handling, adverse outcomes, and reopen/closure are defined.
- KT–NBC–NYCH request hops preserve sender, represented party, intermediary
  role, final recipient, and delivery identity.
- The seven-stage adjudication ladder separates semantic admission,
  institutional admissibility, feasibility, execution, result, and later
  observation.
- Invalid and adverse attempts remain observable; only the authoritative
  reducer changes world state.

### Operationalization and variants — PASS WITH LATER CONFIGURATION REQUIRED

- Qualitative/bounded representations match the evidence limits and prohibit
  arbitrary numerical precision.
- Each structural alternative changes a named uncertain mechanism and retains
  a fixed shared boundary.
- Structural choices and participant profiles/postures are immutable,
  system-only, and included in run identity.
- `NORMAL_COMPLETE`, `BOUNDED_INCOMPLETE`, and `FAILED_CLOSED` are separate.
- Exact actor units, resources, event times, service/venue rules, population
  composition, and posture assignments intentionally remain a configuration
  task. This prevents the scholarly Definition from becoming a hidden
  executable policy.

### Falsification and usability — PASS

- Ten worked cases cover multi-hop routing, missing/incoherent information,
  authority failure, host isolation, resource concurrency, route separation,
  independent commitments, partial funding, message failure, duplicates, and
  replay.
- Perturbations predict observable differences and route failures to evidence,
  Definition, scenario, mapping, implementation, or Contracts.
- A domain reader can understand the modeled event, institutional roles,
  information restrictions, and causal processes without runtime class names
  or carrier slots. Detailed placement mechanics remain in the closure
  companion.

### Release-interface closure — PASS

- Loader-derived inventory: 12 products, 62 commitments, 115 observation
  placements, 107 intent placements.
- The closure contains exactly 115 unique capability-qualified observation
  rows and exactly 107 unique capability-qualified intent rows; set equality
  with the accepted loader output passed with no missing or extra placement.
- All 12 private-state accounts, 13 lifecycle families, and mapping rules
  `C01`–`C34` are covered.
- Each observation row has a semantic producer/product family, recipient
  scope, time/missing rule, and Scenario reference. Each intent row has a
  target/authority class, business lifecycle, adjudicator/result owner, and
  Scenario reference.
- Configuration-dependent instances are marked `CONFIG_REQUIRED`, not hidden
  behind a false executable-completeness claim.

## Findings

### Blocking

None.

### Major

None in the reviewed candidate.

### Minor

None requiring revision before owner review.

### Observations and later work

1. Exact configuration values and actor/population assembly remain the next
   necessary artifact before implementation. Semantic closure must not be
   interpreted as executable readiness.
2. The abbreviated conventional bibliography is appropriate here because the
   source register remains the page-level provenance authority. A future
   publication artifact should format those references to the paper's chosen
   style without duplicating evidence-status ownership.
3. Full-event breadth should not become the first implementation slice. The
   worked cases support staged conformance tests before any broad run.
4. Because all focal outcomes are exposed, later evaluation must either use
   genuinely independent process evidence or state a non-held-out evaluation
   design. This review cannot create a held-out boundary retroactively.

## Verification evidence

| Check | Result |
|---|---|
| Scenario modules 1–10 present | PASS |
| Observation catalog rows / exact set | 115 / PASS |
| Intent catalog rows / exact set | 107 / PASS |
| Lifecycle rows | 13 / PASS |
| Cross-object rule rows | 34 / PASS |
| Owner decisions isolated | 4 / PASS |
| Roster release `SHA256SUMS` | PASS, all 26 assets |
| Consolidated mapping `SHA256SUMS` | PASS |
| Existing mapping/roster tests | PASS, 35 tests in `LMSim` environment |
| Fixed Definition/release files changed | none |
| Network/simulation/model access | none |

## Owner decision resolution

The project owner accepted `OD-SC-01` through `OD-SC-04` together. They
preserve the accepted roster and mapping, make excluded decision ownership
explicit, choose the most conservative current structural baseline, and keep
exact executable configuration in a separate next cycle.

## Verdict

`ACCEPTED_BY_OWNER`

The scenario semantics and complete release interface are accepted for design
use. This verdict does not authorize implementation, simulation, Rule v2,
Contracts changes, LLM/RAG, G5, or any historical or scientific-validity
claim.
