# New event playbook

This is the thin entry point for adding one H2EPR benchmark event. Detailed
requirements remain in the linked standards, templates, Skills, and tests.

1. Read [BENCHMARK_PROTOCOL.md](BENCHMARK_PROTOCOL.md),
   [WORKFLOW.md](WORKFLOW.md), [PUBLICATION_STANDARD.md](PUBLICATION_STANDARD.md),
   and the [event-package template](templates/event-package/README.md).
2. Follow the
   [benchmark-event-simulation Skill](skills/benchmark-event-simulation/SKILL.md).
3. Publish a Source Profile for exactly `event_spec.json`,
   `frozen_evidence.json`, and `draft_epg.json`. Declare full exposure and the
   claim boundary. Do not begin with a research question or external research.
4. Close every Draft participant through the roster and actor map. Write the
   required Agent Definitions and Population Models, then publish the
   participant semantic index and observation, intent, and lifecycle
   registries.
5. Publish the Scenario Definition, Scenario Mechanism, Interface Closure, and
   admitted shared configuration. Keep event-specific state, routes,
   coordinates, messages, effects, and annotations in these assets.
6. Publish an admitted Rule configuration and one Backend Realization. Compile
   the backend-neutral event package, attach Rule through the registry, and
   prove that attachment leaves `package_sha256` unchanged. Leave `llm` and
   `rulellm` planned until their real implementations exist.
7. Add semantic, package, backend, environment, negative-boundary, runtime,
   replay, graph-coverage, determinism, identity-perturbation, checksum,
   publication, and cross-event tests. Common Python must not gain an event ID,
   slug, participant, or domain branch.
8. Materialize canonical, repeat, and generated-identity probe runs in fresh
   ignored custody. Publish the compact Rule release only after independent
   reproduction and verification succeeds.
9. Read the complete trace and Generated EPG. Publish one simulation-only
   reading that separates generated facts, mechanism attribution,
   interpretation, open state, and limitations.
10. Add one row to [events/current-events.json](events/current-events.json)
    only after all current paths and identities close and cross-event
    conformance succeeds.

For multiple events, backends, or seeds, insert the
[experiment-planning Skill](skills/experiment-planning/SKILL.md) before
materialization. Admission fixes the intended denominator and failure policy;
it does not launch runs or replace per-run verification.

Panic, SingHealth, and Note7 demonstrate the expected repository shape across
three domains. Reuse their structure and the common compiler/runtime, but
derive all event vocabulary from the selected benchmark package.
