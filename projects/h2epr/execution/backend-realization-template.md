# Backend Realization template

## Identity and semantic parents

Pin package, configuration, roster, interfaces, scenario, backend, decision
contract, implementation sources, and version.

## Actor and capability coverage

For every actor, resolve its Definition or Population Model, decision
situations, observations, state, permitted intents, and implementation entry.

## Decision production

Describe Rule evaluation, LLM prompt/parser, or RuleLLM proposal/admission.
State ordering, determinism, model access, generated-ID independence, and
remaining choice. Name the registered implementation ID; package attachment
must fail before setup if that exact factory is unavailable.

## Failure routing

Define malformed observation, invalid output, unavailable model, timeout,
retry, repair, rejection, and no-op behavior. Do not silently substitute a
different backend.

## Environment boundary

Confirm the realization emits intents only and cannot commit world state or
declare delivery, feasibility, allocation, or success.

## Verification and verdict

Cover actor parity, intent parity, negative payloads, authority denial,
lifecycle handling, reducer-order and opaque-ID perturbation, deterministic or
recorded model provenance, attachment-invariant package core, and release
identity.
