# Angola Yellow Fever Outbreak of 2016 Rule realization

## Identity and semantic parents

Realization `h2epr.0551.rule-realization.v2` attaches the registered declarative Rule backend to configuration `h2epr.0551.rule.v2` and eight exact semantic parents. Four implementation files are hash-pinned in `realization.json`.

## Actor and capability coverage

Every active actor uses `h2epr.backends.rule.DeclarativeRuleBackend` with observation and intent lists equivalent to the participant interface. The realization adds no source participant, route, state field, intent, or hidden fallback. The two world-state source groups receive no backend row.

## Decision production

Rows are considered inside inclusive actor availability windows, ordered by ascending priority and stable rule ID after every state or retained-message guard passes. Accepted rows complete once; rejected rows retry only after observed information changes, and missing information permits waiting. Missing matches produce typed `no_op`. Model and network access are denied. Opaque generated identifiers do not participate in ordering.

## Failure routing

Malformed observations and unavailable implementation IDs fail before or during decision production. Invalid targets, authority, parameters, preconditions, and conflicts become environment-owned rejected dispositions. Transport failure fails the run. Backend substitution and silent repair are forbidden.

## Environment boundary

The realization emits action and message intents only. It cannot write state, declare delivery, validate disease or laboratory truth, allocate vaccine, establish coverage, or claim response effectiveness.

## Verification and verdict

Admission requires actor/intent parity, exact source hashes, configuration receipt equality, package-core invariance after attachment, deterministic A/B output, opaque-ID conformance, replay, graph coverage, and terminal transport. Verdict at semantic release: implemented and eligible for runtime verification; success is not predeclared.
