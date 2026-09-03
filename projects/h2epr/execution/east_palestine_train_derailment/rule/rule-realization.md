# East Palestine Train Derailment Rule realization

## Identity and semantic parents

Realization `h2epr.0196.rule-realization.v1` attaches the registered declarative Rule backend to configuration `h2epr.0196.rule.v1` and the seven exact semantic parents. Four implementation files are hash-pinned in `realization.json`.

## Actor and capability coverage

Every current actor uses `h2epr.backends.rule.DeclarativeRuleBackend` with observation and intent lists byte-equivalent to the participant interface. The realization adds no event actor, intent, route, state field, or fallback.

## Decision production

Rules are selected by actor, coordinate, ascending priority, and stable rule ID after all state or delivered-message guards pass. A missing match produces typed `no_op`. Model and network access are denied. Opaque generated identifiers do not participate in semantic ordering.

## Failure routing

Malformed observations and unavailable implementation IDs fail before or during decision production. Invalid targets, authority, parameters, preconditions, and conflicts become environment-owned rejected dispositions. Transport failure fails the run. Backend substitution and silent repair are forbidden.

## Environment boundary

The realization emits action and message intents only. It cannot write world state, declare delivery, decide legal or scientific validity, or claim that a cleanup or settlement announcement was implemented.

## Verification and verdict

Admission requires actor/intent parity, exact implementation hashes, configuration receipt equality, package-core invariance after attachment, deterministic A/B output, opaque-ID perturbation conformance, replay, trace-derived graph coverage, and terminal transport. Verdict at semantic release: implemented and eligible for runtime verification; runtime success is not predeclared.
