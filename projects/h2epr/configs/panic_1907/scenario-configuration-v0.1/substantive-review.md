# H2EPR-0288 Scenario Configuration substantive review

- Review date: `2026-08-23`
- Review mode: independent substantive review
- Candidate: `h2epr.0288.scenario.mechanism-coverage.v0_1`
- Candidate version: `0.1.0-candidate.1`
- Verdict: `PASS_WITH_RECORDED_LIMITATIONS`
- Recommendation: `ACCEPT_FOR_NON_EXECUTABLE_CONFIGURATION_RELEASE`

## 1. Review question

Is the first configuration a small, falsifiable, reviewable instantiation of
the accepted Event Scenario Definition, or does it hide unsupported history,
participant policy, authority, numeric defaults, outcome fitting, or runtime
implementation inside a configuration file?

The review compares the explanatory candidate, machine-readable candidate,
accepted Definition, interface closure, Roster release, consolidated mapping,
mapping profile, evidence ledger, and source register. It does not use
simulation output or the known outcome to tune the candidate.

## 2. Overall judgment

The candidate is fit for owner review as a non-executable mechanism-coverage
configuration. It is correctly narrower than a historical baseline: it fixes
identity, clock, assembly, categorical opening records, bounded external
inputs, conservative structural choices, policy semantics, sensitivities,
termination, and fail-closed expectations while refusing to invent exact
resources, capacities, population shares, service rates, participant policies,
or market allocation.

The candidate exercises all 12 released semantic products with a deliberately
small 16-actor assembly. The three-role KT--NBC--NYCH lineage remains the first
recommended implementation slice; the full assembly is an integration target,
not permission to implement the whole event at once.

There are no open blocking findings. Acceptance would approve configuration
semantics only. It would not make the file executable or authorize policy
code, simulation, Rule v2, LLM/RAG, Contracts mutation, historical validity,
Git publication, or remote operations.

## 3. Findings resolved during review

### `CFG-R01` — opening private need was conflated with dated activation

- Severity before correction: `MAJOR`
- Status: `RESOLVED`

Three depositor units originally carried `private_need = immediate` directly
in their unit records even though the exogenous register said the need would
be activated on 22--23 October. A loader could reasonably interpret the unit
field as opening state and activate those decisions too early.

The candidate now records `opening_private_need = none` for all six depositor
units, gives exactly three units a dated activation reference, and lists those
same three target IDs on the exogenous input. Signal-response units have no
baseline private-need activation.

### `CFG-R02` — sensitivity targets were not machine-unambiguous

- Severity before correction: `MAJOR`
- Status: `RESOLVED`

Several overlays used a bare field name or an actor-qualified name for a
parameter actually owned by one population capability unit. This was unsafe
for the composed bank/lender actor and left the depositor conflict overlay
without a target set.

All overlays now use typed operations with exact target kind, ID, field, and
value. The depositor overlay targets the three signal-response units; the bank,
lender, and broker overlays target their exact capability units.

## 4. Conformance strengths

1. **Scope calibration.** The purpose is explicitly mechanism coverage, with
   no historical calibration, validation, or known-outcome fitting claim.
2. **Input integrity.** Every recorded semantic-input hash matches the current
   accepted byte identity.
3. **Causal ownership.** Exogenous inputs open opportunities or deliver
   records without choosing participant actions or authoritative results.
4. **Assembly integrity.** Actor, entity, artifact, authority, resource-owner,
   host, capability, and unit references are unique and resolvable.
5. **Information discipline.** Issue, routing, delivery, freshness,
   correction, visibility, and version coherence remain separate.
6. **Resource discipline.** Qualitative envelopes are labeled, owner-scoped,
   and forbidden from unsupported arithmetic or automatic allocation.
7. **Sensitivity integrity.** Baseline and alternatives are predeclared;
   alternatives require new exact identities before use.
8. **Execution honesty.** All nine policy implementations are unbound and the
   candidate explicitly requires fail-closed rejection by a runner.

## 5. Recorded limitations

These limitations do not block a non-executable release, but they block any
claim of runtime readiness or scientific validity:

- no configuration schema, loader, canonical serialization rule, or carrier
  projection is accepted yet;
- bounded event windows do not supply invented intraday times; a later
  scheduler must preserve partial order and record any construction choice;
- qualitative resource envelopes cannot support arithmetic until a reviewed
  carrier policy supplies exact semantics or rejects the operation;
- population weights, normalized claims, response profiles, postures, opening
  envelopes, and the 2 November horizon are synthetic or weakly identified;
- the Treasury and alternative-horizon overlays are declarations, not
  executable values, until separately materialized;
- all outcomes were exposed during design, so future work is exploratory
  construction unless a genuinely held-out protocol is established; and
- no simulation, empirical comparison, parameter calibration, or historical
  validation has been performed.

## 6. Owner-decision recommendations

| Decision | Recommendation | Reason |
|---|---|---|
| `OD-CFG-01` purpose and horizon | accept | the mechanism-coverage label and early-November construction horizon are explicit and nonhistorical |
| `OD-CFG-02` assembly | accept | it covers all released products with the smallest practical heterogeneous assembly and preserves entity/resource identity |
| `OD-CFG-03` baseline and sensitivities | accept | conservative structural choices remain fixed; synthetic profiles are exposed and overlays require new identities |
| `OD-CFG-04` non-executable boundary | accept | it prevents backend defaults from converting an incomplete design into an apparently runnable scenario |

## 7. Recommended disposition

Freeze the current candidate as `review_candidate` while the project owner
decides `OD-CFG-01` through `OD-CFG-04`. If accepted, promote it in one short,
atomic configuration-release cycle with an exact manifest and checksum set.
Do not combine that promotion with policy implementation or simulation.

After promotion, the next separately authorized engineering question should
be the smallest configuration loader and KT--NBC--NYCH projection that can
prove identity, observation boundaries, request lineage, typed results,
deterministic replay, and fail-closed behavior. Any broader event execution is
premature.

## 8. Owner decision resolution

On 23 August 2026, the project owner accepted `OD-CFG-01` through
`OD-CFG-04` and authorized their atomic formal promotion. The accepted
resolution preserves the mechanism-coverage purpose, 16-actor / 10-unit
assembly, conservative baseline, exact-identity sensitivity rule, and
non-executable boundary.

The same instruction authorizes this tracked release only. It does not
authorize external publication, policy implementation,
simulation, Rule v2, LLM/RAG, Contracts mutation, historical calibration,
historical validation, or a scientific-validity claim.

## 9. Final disposition

`ACCEPTED_BY_OWNER_FOR_NON_EXECUTABLE_CONFIGURATION_RELEASE`

The candidate review hashes remain recorded in the release manifest. Promotion
changes only release status, version labels, links, and provenance; it does not
change the reviewed configuration semantics or clear any recorded limitation.
