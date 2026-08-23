# Configuration content and closure

Use this reference while creating or revising an H2EPR Scenario Configuration.
The configuration is a declared-purpose instantiation of accepted semantic
authorities, not a second Scenario Definition and not a runtime bundle.

## Authority boundary

| Authority | Configuration may consume | Configuration may not redefine |
|---|---|---|
| Event Scenario Definition | time domains, state families, exogenous families, structural alternatives, policy families, completion semantics | event question, causal ownership, world or lifecycle meaning |
| Roster release and participant products | entity, actor, capability, unit, observation, private-state, intent, and authority semantics | participant behavior or information entitlement |
| Consolidated mapping | canonical identities, assembly, carrier placements, cross-object constraints, and derived counts | released meaning or contract semantics |
| Evidence ledger and source register | claim status, participant-time availability, source class, and unresolved questions | historical support or exposure status |
| Scenario Configuration | declared purpose, allowed selections, assembly instances, opening projections, exact overlays, and implementation-binding status | policy implementation, authoritative transition, trace, or evaluation conclusion |

If a value has no owning authority, record the gap and route it. Do not make
the configuration authoritative merely because it needs the value.

## Required semantic families

| Family | Minimum content | Fail-closed check |
|---|---|---|
| identity and purpose | event ID, configuration ID/version/status, declared purpose, claim flags | identity is unique; purpose and prohibited claims are explicit |
| semantic inputs | exact accepted Definition, releases, mapping/profile, evidence, and source identities with integrity values | every required identity resolves exactly once and matches bytes |
| execution boundary | eligibility, reason, missing prerequisites, authorization boundary | absent or unbound prerequisites never become defaults |
| clock and order | timezone, start/window/horizon, ordering and tie policy, precision boundary | ordering is replayable and does not invent unsupported time |
| structural baseline | one selection from each required declared domain | no missing, unknown, or extra structural family |
| actor assembly | entity, actor, capability, unit, host, authority graph, and resource owner | uniqueness, capability membership, host scope, and one-owner invariants hold |
| opening records | authority, relationship, resource/condition, information, and business objects needed at opening | every reference resolves; unknown stays explicit; no duplicate owner |
| exogenous inputs | stable ID, activation, targets, effect, visibility, basis, causal limit, sensitivity | no future leakage, hidden outcome forcing, or opening-state contradiction |
| policy selections | required policy ID/version/selection and binding status | all required semantics selected; execution rejects every unbound policy |
| sensitivity overlays | overlay ID and typed exact operations | target kind, target ID, field, and replacement value are valid and unambiguous |
| completion | normal, bounded-incomplete, fail-closed, and carry-forward rules | no unresolved active object disappears at the horizon |
| validation expectations | derived semantic and assembly counts plus required invariants | values derive from pinned authorities rather than copied prose |

## Operationalization rules

- Use qualitative categories, intervals, procedures, or numbers in proportion
  to their identification. Record source class and identification status for
  every material opening value or selection.
- Treat `unknown`, `unavailable`, `disputed`, `not yet delivered`, and
  `unbound` as distinct states.
- Keep participant posture separate from environment-owned resource or
  business truth.
- Keep issue, route, delivery, receipt, admissibility, decision, intent,
  adjudication, result, and later observation separate.
- Keep proposal, reservation, commitment, transfer, effect, and release
  separate for resources.
- A stable residual tie-break may resolve otherwise unordered equal-time
  commits; it may not replace evidenced precedence.
- Synthetic mechanism-coverage choices must be labeled as such and must not be
  described as historical estimates.
- Every exogenous input and structural choice must state whether and how it
  participates in sensitivity analysis.

## Closure record

The closure is derived from exact inputs. It should contain these matrices or
equivalent machine-checkable inventories:

1. **input integrity** — each required authority, identity, integrity value,
   resolution result, and consumed scope;
2. **Definition-family closure** — each Definition configuration family,
   configuration carrier, closure result, and retained boundary;
3. **actor and unit assembly** — entity, actor, capabilities, authority graph,
   resource owner, units, hosts, and uniqueness result;
4. **opening-record closure** — each required state/record family, source,
   identity, owner, visibility, and identification status;
5. **exogenous-input closure** — required family, selected input, target,
   activation, causal limit, and baseline/sensitivity disposition;
6. **policy closure** — required policy family, semantic selection, version,
   implementation-binding status, and execution consequence;
7. **sensitivity closure** — declared uncertainty, baseline selection, exact
   overlay operations, valid target domains, and coupled-change disclosure;
8. **completion and validation closure** — horizon treatment, unresolved-object
   handling, derived counts, and invariants; and
9. **open matters** — owner, blocking class, next legal stage, and prohibited
   local workaround.

A `closed` row means that the configuration represents the accepted meaning
without semantic loss. It does not mean that a policy exists, a carrier has
been projected, the configuration is executable, or a scientific claim has
been validated.

## High-information consistency cases

Use only cases present in the candidate. Prefer checks that jointly exercise:

- one entity composing multiple capabilities without duplicating authority or
  resources;
- one host-scoped population unit and its private-state boundary;
- an opening state later changed by a dated exogenous input;
- a disputed or unavailable value that remains nonnumeric;
- one information item across issue, delivery, freshness, and correction;
- one resource across proposal, commitment, transfer, and result;
- one exact structural overlay and one exact nonstructural overlay; and
- one active object carried explicitly across the analytic horizon.

Do not expand the event merely to populate every example in this list.
