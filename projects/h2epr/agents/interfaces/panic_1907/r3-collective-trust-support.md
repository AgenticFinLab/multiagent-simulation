# R3 collective-trust-support interface

| Item | Value |
|---|---|
| Status | accepted Roster-production preflight |
| Event | `H2EPR-0288` |
| Roster | `v0.3` |
| Semantic skeleton | `v0.1` |
| Products | committee Agent `0.1.0`; bank resource-decision population `0.1.0` |

## Purpose

This preflight checks whether the two R3 research products expose a coherent
later mapping surface and whether Contracts V1 presents a concrete carrier
counterexample. It does not choose fields, add registry entries, define an
executable participant or modify a contract.

## Cross-role causal chain

```text
applicant or Morgan sends a request/proposal
→ committee receives a case, requests information and reports advice
→ authorized coordinator or committee solicits specific institutions
→ each bank resource-decision unit reviews and independently responds
→ committee/Morgan assembles only delivered offers or commitments
→ environment validates, schedules and executes resources
→ dispositions/results return to their actual owners
```

Every arrow is a separate action, message, lifecycle transition or result.
Neither the committee nor the bank population owns the whole chain.

Morgan and the committee expose overlapping coordination capabilities, but not
shared plan authority. Every plan version has exactly one declared owner.
Cooperation allows one actor to deliver advice, information or a proposal to
the other; it does not permit both to issue the same plan or silently merge
equivalent solicitations.

## Committee semantic surface

### Observations and state

- committee mandate, membership and competent recipient forum;
- referred application identity and lifecycle;
- dated information packages and delivered examination reports;
- case information requirements, conflict and limitation state;
- reporting opportunities and separately demonstrated coordination authority;
- institution-specific solicitations, replies and commitments; and
- delivered dispositions/results.

### Outputs

- open/refer a case;
- request information or a scoped examination;
- issue and report a qualified recommendation;
- solicit an independent contribution under authority;
- assemble or revise a versioned plan from delivered replies; and
- await a named case/plan result.

### Scenario ownership

Appointment/membership facts, delivery, examiner work, presidents' meeting,
contributor authority/resources, plan admissibility, transfer and effects
remain outside the Agent.

## Bank resource-decision population surface

### Choice-unit observations and state

- institution, NYCH membership, capability and relationship identity;
- own decision authority and qualitative/bounded resource envelope;
- delivered proposal, applicant information, terms and expiry;
- own commitment and certificate-application lifecycle;
- delivered facility/eligibility information and controlled-collateral
  projection; and
- own delivered disposition/result.

### Outputs

- request missing proposal information;
- refer or decline with a typed reason;
- make a conditional offer or commit an owned resource;
- revise or cancel through a supported lifecycle;
- apply for a member certificate or submit controlled collateral; and
- await a named result.

### Scenario ownership

Population composition, roles/postures, actual resources, facility rules,
eligibility, collateral truth/value, aggregation, transfer, certificate issue
and realized effects remain outside the population.

## Skeleton compatibility

- Committee, clearing-house and member-bank identities remain distinct.
- Morgan coordination does not create committee findings or bank commitments.
- The population preserves resource ownership and disagreement rather than
  creating a sector-level wallet.
- Requests, advice, offers, commitments, scheduling and realized transfer are
  causally separate.
- Later NYCH certificate rules are not back-projected to the October 23 trust
  committee.
- The products add no call-money, NYSE, later-depositor or Treasury policy.

No conflict with the accepted Roster or semantic skeleton was found.

The current NYCH Definition deliberately excludes the later October 26
certificate program from its October 21 behavior. R3 therefore treats facility
availability/rules as a dated scenario-owned institutional input and models
only member-bank demand. If the released event model must endogenize NYCH
authorization, collateral review or issuance, the Roster Definition release
must separately review the NYCH Definition/scenario boundary. R3 does not
silently extend NYCH `0.2.1`.

## Contracts V1 carrier re-check

| Interface family | Classification | Consolidated-release work |
|---|---|---|
| committee participant identity | `KNOWN_FIT` at participant-contract level | choose the semantic-to-V1 representation mapping for an aggregate procedural committee; no new representation class is presently required |
| bank resource-decision population | `KNOWN_FIT` at participant-contract level | V1 already permits `aggregate_population_agent`; mapping must preserve institution-level unit identity/composition rather than one anonymous wallet |
| information boundary and delivered observations | `KNOWN_FIT` at contract level | add event semantic domains and registry entries only after release; retain source/as-of/freshness/conflict semantics |
| case, review, recommendation and plan state | `MAPPING_EXTENSION_EXPECTED` | choose one authoritative projection using existing profile/state/environment-process carriers; no duplicate backend ledger |
| participation posture and unit capability | `MAPPING_EXTENSION_EXPECTED` | bind exposed posture/capability identity into participant/profile state without name-based policy |
| action/message intents | `KNOWN_FIT` at contract level | `ActionIntent`/`MessageIntent` already carry targets, parameters, claimed authority, resource offer/request, time, observations, decision and idempotency; R3 semantic types require later registry definitions |
| independent resource ownership | `KNOWN_FIT` at contract level | bind each offer/commitment to its institution/resource owner and reject coordinator-created commitments through cross-object validation |
| recommendation/commitment/transfer distinction | `KNOWN_FIT` at authority-flow level | later lifecycle mapping must keep advice, offer, commitment, scheduling, execution and effect distinct |
| certificate application/collateral review/issue | `MAPPING_EXTENSION_EXPECTED` | define the business lifecycle and cross-object checks for membership, facility, controlled collateral, review and issue; do not assume a new Contract yet |
| multi-target solicitation | `KNOWN_FIT_WITH_FAN_OUT` | V1's deterministic single-recipient fan-out can preserve one independent solicitation/reply lifecycle per institution |
| partial, delayed, failed and expired outcomes | `KNOWN_FIT` at disposition level | exact business reason mappings remain a consolidated-release task |
| trace and replay | `KNOWN_FIT` at contract level | later mapping must retain case/plan/unit identities, observation refs, decision refs, prior versions and causal parents |

## Required later cross-object checks

1. a committee case and recommendation cite a valid mandate and delivered
   application/information identities;
2. a committee solicitation cannot create or mutate the target's commitment;
3. every plan version has exactly one Morgan-or-committee owner, and equivalent
   cross-plan solicitations receive an explicit overlap/duplicate decision;
4. every offer/commitment identifies its institution and controlled resource;
5. a plan aggregates only delivered, nonexpired replies with their conditions;
6. certificate application requires member identity, active facility,
   authority and controlled-collateral reference;
7. collateral review and certificate issue cannot be emitted by the applicant;
8. partial or failed execution updates only the realized component; and
9. later behavior reads only delivered results, never an inferred pool total.

## Preflight conclusion

`NO_CONCRETE_V1_CARRIER_COUNTEREXAMPLE`

R3 adds substantial mapping work—committee case/recommendation state,
institution-preserving population composition, independent commitments and a
member-certificate lifecycle—but the current V1 participant, profile,
information, intent/message, resource, disposition and trace surfaces provide
plausible carriers. No successor seam is justified before the consolidated
Roster Definition release.
