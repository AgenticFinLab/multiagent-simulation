# Scenario Configuration guide

## Configuration ownership

Shared configuration selects event-world values that must remain equal across
backends. Backend configuration selects decision-production values that may be
the experimental treatment. Run-local values such as seed and custody locator
belong to the run manifest or experiment plan.

| Setting | Owner |
|---|---|
| timeline coordinates, initial state, routes, exogenous schedule | shared configuration |
| Rule thresholds/order, prompt/model/decoding, repair policy | backend configuration |
| state field types, legal effects, authority | Scenario Mechanism |
| seed, identity variant, custody path | run/experiment layer |

A value appearing in the wrong layer is a contract failure even when it is
schema-valid.

## Provenance classes

Each selected value has exactly one JSON Pointer and one basis:

- `dataset_derived`: directly selected from an admitted dataset anchor;
- `structural`: necessary to instantiate the declared mechanism;
- `synthetic`: intentionally chosen without dataset support;
- `sensitivity`: varied across a declared comparison;
- `model`: fixed by an implemented model backend;
- `run_local`: prohibited in a reusable configuration and routed to a run.

Describe unit, transformation, and limitation. A citation to an entire file is
not sufficient when a stable stage, episode, participant, action, or setting
anchor exists.

## Exhaustive pointer coverage

Enumerate every direct child of `/settings`. Each appears exactly once in
`value_provenance` or in a typed coverage exemption with reviewer, rationale,
and successor trigger. Validate that every pointer exists, traverses no scalar,
resolves uniquely, and refers to the value represented by the provenance row.
Recompute the coverage receipt independently; do not trust a producer boolean.

## Admission cases

Reject a missing or duplicated pointer, pointer outside `/settings`, unknown
actor or route, undeclared state field, out-of-domain value, backend value in
shared configuration, run-local value in either release, parent/hash drift,
unsafe path, self-hash mismatch, or a receipt copied from another event.

Test one synthetic value explicitly: admission may pass while the resulting
run remains unsuitable for historical or calibrated claims. Provenance states
where a value came from, not whether it is scientifically valid.

## Release and handoff

Publish design prose, selected JSON, independently derived admission receipt,
provenance coverage, manifest, and checksum inventory. Record all parent
identities, settings/pointer/exemption counts, provenance-class counts,
validation command, negative cases, limitations, reviewer disposition, and
next legal action. A configuration is promotable only when the compiler can
rederive every admission check from authoritative parents.
