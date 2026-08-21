# Panic of 1907 two-role conformance slice

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
