# Panic of 1907 scenario

## Accepted Event Scenario Definition

The [Event Scenario Definition v0.1](definition-v0.1/) is the accepted semantic
authority for the full H2EPR-0288 Roster. It defines the modeled interval,
causal ownership, institutions, relationships, resources, information
delivery, shared lifecycles, adjudication, structural variants, termination,
and reproducibility boundary. Its interface companion closes all 12 released
products, 115 observation placements, 107 intent placements, 13 lifecycle
families, and 34 cross-object rules.

The Definition is not an executable configuration. Those choices are now
instantiated by the accepted
[Scenario Configuration v0.1](../../configs/panic_1907/scenario-configuration-v0.1/),
which remains non-executable. Its fail-closed admission and separate exact
KT--NBC--NYCH binding and its
[lineage conformance closeout v0.1](lineage-conformance-v0.1/) are now complete
through E7. This engineering closeout is not permission for a full-event run.

## Semantic precursor

The event-level [semantic skeleton](semantic-skeleton.md) defines the shared
v0.1 vocabulary, interaction routes, ownership boundaries, structural
variants, and interface-preflight questions used during Roster production. It
is retained as release provenance and does not compete with the accepted
Definition.

## Current three-role bounded slice

The new [three-role bounded binding](../../agents/bindings/panic_1907/kt-nbc-nych-v0.1/)
and `lineage_v0_1/` package preserve KT-to-NBC and NBC-to-NYCH as distinct
messages and deliveries. They implement only four positive semantic actions
and six lineage-only environment policies. `lineage_conformance_v0_1.py` adds
the fixed five-tick cross-hop validator and deterministic trace/replay used by
the E7 receipt. The accepted full configuration is not made executable.

## Frozen two-role reference slice

This package connects the accepted Knickerbocker Trust and New York Clearing
House Definitions to the machine mapping in `agents/bindings/panic_1907/`.

The conservative path covers:

1. a bounded Knickerbocker support request;
2. NYCH case registration and classification;
3. a request for case information and its delivered response;
4. collecting and examining review states;
5. a member-facility-scoped decline;
6. delivery of that disposition; and
7. Knickerbocker contingency preparation without automatic suspension.

The runner uses synthetic conformance inputs, starts no simulator or Ray
process, and makes no historical-validity claim. Its purpose is to test that
the Definition identity, legal observations, decision commitments, typed
intents, messages, reducer-owned state transitions, trace and replay form one
closed path.

`feedback.py` adds a deterministic 22-case policy-and-binding matrix. It
varies information freshness, authority, channel status, request lifecycle,
review state, scoped disposition and communication outcome. Twenty reachable
cases validate response selection and semantic intent projection. Two
proposal/result states that are unreachable in the conservative structural
variant must be rejected before policy selection. The matrix does not claim
that every selected intent already has an end-to-end reducer path. The fixed
runner remains the bounded end-to-end slice described above.

Out-of-domain observations are not delivered: the runner records a safe
payload hash and failed field identity as an invariant violation. A
schema-valid action whose authority record has the wrong owner, capability,
scope, target, or effective interval receives a rejected ActionDisposition,
creates no message or state delta, and remains in the trace for review.
Target grants use exact set equality, so an empty target list is a genuine
no-external-target grant rather than a wildcard. NYCH may seek a procedural
forum only when the delivered authority observation names that forum.

NYCH's `request_authorization_evidence` is derived only from material delivered
into its case dossier. Knickerbocker's internal authorization state is not a
NYCH observation. With no delivered request the evidence is absent; request
delivery marks it incomplete, and only an explicit information response
containing the authorization reference makes it sufficient.
