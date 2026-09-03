# Maintained Skills

[benchmark-event-simulation](benchmark-event-simulation/SKILL.md) is the thin
end-to-end orchestrator. Specialized Skills own each admission, construction,
execution, and review boundary.

Each package has a concise `SKILL.md` entry point and a
`references/guide.md` method guide. Read the guide only when that Skill is
selected, then follow its inputs, decision rules, worked failures, completion
evidence, and stop conditions. The split keeps routine orchestration compact
without reducing the method to a checklist.

| Skill | Responsibility |
|---|---|
| [benchmark-input-admission](benchmark-input-admission/SKILL.md) | Closed three-file input and exposure |
| [agent-definition](agent-definition/SKILL.md) | Dataset-bounded named decision interfaces |
| [agent-definition-review](agent-definition-review/SKILL.md) | Substantive and adversarial review |
| [population-model](population-model/SKILL.md) | Aggregate or heterogeneous choice units |
| [event-agent-batch](event-agent-batch/SKILL.md) | Event-wide participant production |
| [roster-mapping-conformance](roster-mapping-conformance/SKILL.md) | Roster, actor map, and registries |
| [event-scenario-design](event-scenario-design/SKILL.md) | World and institutional semantics |
| [scenario-configuration](scenario-configuration/SKILL.md) | Shared/backend selections and provenance admission |
| [backend-realization](backend-realization/SKILL.md) | Rule, LLM, or RuleLLM implementation projection |
| [run-release-verification](run-release-verification/SKILL.md) | Materialization, replay, graph, and release verification |
| [generated-process-analysis](generated-process-analysis/SKILL.md) | Simulation reading and backend comparison |
| [experiment-planning](experiment-planning/SKILL.md) | Matrix parity, scheduling, failure, and analysis admission |

Skills do not override schemas, admitted semantic parents, or the benchmark
protocol. None authorizes external research, Reference access, remote writes,
dependency installation, or an unimplemented backend.

The current procedure requires a machine Scenario Mechanism, exhaustive
configuration provenance, independent admission, trace-complete Generated
EPG, formal custody, deterministic identity perturbation, and independent
publication. Cross-event conformance applies only after at least two distinct
current events exist.

## Quality contract

A Skill guide must name its owning product, accepted parents, direct evidence,
decision rules, at least one failure or falsifier, failure destination, exact
completion record, and what it cannot authorize. Shared changes require an
event-neutral regression case. Event vocabulary and successful trajectories
do not belong in a reusable Skill.
