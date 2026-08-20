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
