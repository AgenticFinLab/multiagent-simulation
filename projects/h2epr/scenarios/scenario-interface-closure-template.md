# Scenario Interface Closure template

## Closure identity

Record the exact roster, Agent Definitions, Population Models, registries,
Scenario Definition, and configuration profile reviewed.

## Participant and capability assembly

For every runtime actor, resolve its semantic product, observations, persistent
state, action intents, message intents, targets, and required lifecycle.

## Observation production and delivery

For every observation, resolve producer, source state, projection, route,
availability time, missing behavior, and consumers. Reject hidden or future
inputs.

## Intent, communication, adjudication, and result

For every intent, resolve authority, payload, route, environment handler,
result lifecycle, failure codes, and state deltas. Agents never author their
own success.

## State, institutions, and resources

Confirm one owner for every field and resource; conservation and concurrency
rules; replay application; and no duplicate private copy of institutional
truth.

## Structural identity and representative cases

Check actor closure, name erasure, role swap, invalid target, missing route,
delayed delivery, partial allocation, and termination.

## Gaps and verdict

Route each unresolved item to roster, Definition, Population Model, Scenario,
Configuration, backend realization, or runtime. Use `complete`, `complete with
recorded limitations`, or `return to owning layer`.
