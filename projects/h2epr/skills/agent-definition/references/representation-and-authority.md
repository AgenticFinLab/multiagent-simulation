# Representation and authority

## Question owned by this reference

This reference decides whether one roster candidate should become a named
Agent and, if so, the exact decision interface represented. It does not decide
how that Agent selects an option or whether an attempted action succeeds.

An Agent exists because the benchmark exposes a consequential, attributable
choice. Fame, causal importance, frequency of mention, and organizational size
are not sufficient reasons.

## Disposition test

Apply every test before drafting behavior.

| Test | Evidence of an Agent | Route elsewhere |
|---|---|---|
| attribution | a choice can be attributed to the candidate or a bounded office | the record describes only an event, condition, or result |
| autonomy | more than one admissible response can remain at a decision point | behavior is fully fixed by the environment |
| observability | the interface has a describable information boundary | it would require omniscient access to world state |
| consequence | an intent can enter an event process or communication route | the candidate is merely named or affected |
| separability | its decisions and state can be distinguished from other units | it is a cohort response or an unresolvable organization aggregate |

A candidate may pass some tests and still be represented as context,
Population, institutional process, or exogenous state. Record the rejected
alternative; do not leave disposition reasoning implicit.

## Interface statement

Write the representation as one sentence:

> `<Agent ID>` represents `<accountable person, office, or organizational
> interface>` only when deciding `<bounded choice family>` during `<event
> interval>`.

The sentence should still be true if the backend, parameter values, and run
trajectory change. If it names a particular response, threshold, or achieved
result, the boundary is too narrow or already scripts behavior.

## People, offices, and organizations

### Named person

Represent a person when the dataset attributes the decision to that person and
the event model needs that personal interface. State whether organizational
staff, advisers, and delegates are included as information channels or
excluded. Do not give the person every observation held anywhere in the
organization.

### Office or committee

Represent an office when the relevant choice belongs to the office across
possible officeholders. Identify quorum, approval, or delegation only if the
admitted data supports it or the model declares a structural assumption.
Meeting, vote, and announcement processes may still belong to the scenario.

### Organization

An organization Agent is a deliberate aggregation. State:

- the operational interface being aggregated;
- internal roles included only for this choice family;
- internal roles expressly excluded;
- information lost through aggregation;
- conflicts suppressed by aggregation; and
- the observation or behavior that would require a split.

“The organization decides” is not a representation boundary. A regulator's
warning office, enforcement office, and adjudication process, for example,
must not be collapsed unless their choice and authority can be represented
without granting one interface powers held by another.

## Inclusion and exclusion ledger

Use a ledger rather than an unbounded narrative.

| Internal or related unit | Status | Included function | Excluded function | Reason and anchor |
|---|---|---|---|---|
| `<unit>` | included / excluded / context | | | |

Inclusion authorizes only the named function. It does not merge private state,
resources, or authority by default.

## Authority dimensions

Separate the following dimensions. A participant may hold one without the
others.

| Dimension | Question |
|---|---|
| decide | May the interface choose or request the act? |
| authorize | May it make the act institutionally admissible? |
| communicate | May it issue the relevant message or notice? |
| allocate | May it commit a resource? |
| execute | May it physically or procedurally carry out the act? |
| verify | May it classify evidence or declare a condition satisfied? |
| observe | May it receive the relevant state or report? |

The Agent Definition owns the participant-side boundary. Scenario and
mechanism assets own whether authorization, routes, resources, and execution
are actually available at a particular run state.

## Relationships are scoped

Name relationships by function and direction:

- may send `<message kind>` to `<eligible target class>`;
- may receive `<observation kind>` from `<producer class>`;
- may request `<intent kind>` through `<route>`;
- may not observe another participant's private disposition; and
- does not control `<environment-owned resource or process>`.

Avoid general statements such as “coordinates with all stakeholders.” They
cannot be projected into a bounded interface and usually conceal unsupported
communication access.

## Resource boundary

For each material resource, record one of:

- controlled by the Agent;
- requestable by the Agent but allocated by the environment;
- observable but not controllable;
- external and unavailable; or
- omitted from the modeled world.

An intent to allocate is not proof that the resource exists, is free, reaches
the target, or has the intended effect.

## Split and narrowing triggers

Every organizational representation needs at least one testable successor
condition. Common triggers include:

- two internal units receive different observations;
- two units have incompatible duties or independent vetoes;
- the Draft attributes separate choices to them;
- a future backend needs private state that cannot be shared honestly;
- one interface can act while another only announces or executes; or
- aggregate behavior hides a causal mechanism required by the experiment.

Narrow the interface when unsupported authority can simply be removed. Split
it when two autonomous choice boundaries remain. Route a repeated homogeneous
response to a Population Model.

## Worked classification

Suppose a synthetic benchmark names a harbor authority, its response office,
shipping firms, and affected residents. The Draft attributes closure requests
and cleanup coordination to the response office.

- The response office is an Agent candidate because it receives reports and
  makes attributable requests.
- Shipping firms may be Agents or a Population depending on whether distinct
  choices matter.
- Residents are a Population if only aggregate compliance is represented.
- Harbor closure status is scenario state, not an Agent.
- Cleanup progress is an environment result, not a separate decision maker.

This classification would change if the admitted data attributed an
independent veto to another harbor unit. That is a split trigger, not a reason
to grant the response office the veto.

## Falsifiers

The representation fails if any accepted parent or executable case shows that:

- the Agent requires a choice owned by an excluded unit;
- two supposedly aggregated units need incompatible private state;
- the interface observes a result before a valid delivery path exists;
- it asserts authority that belongs to scenario admission;
- its only behavior is an environment transition; or
- another accepted Agent already owns the same choice and state.

Route roster failures to roster review, semantic-route failures to shared
registries, and world authority failures to scenario design. Do not repair
them by widening the Definition.

## Completion evidence

Record the chosen disposition, rejected alternatives, representation
sentence, inclusion/exclusion ledger, authority dimensions, resource
classification, aggregation loss, split/narrowing conditions, and anchors.
Independent review must be able to disagree with the representation using
these records.
