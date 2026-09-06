# Worked cases and contract falsification

## Why cases are part of the Definition

Worked cases are adversarial probes of the semantic contract. They show that
identity, information, duties, choice, and environment ownership remain
coherent under more than the expected path.

They are not forecasts, unit-test transcripts, historical reconstructions, or
instructions for a backend to reproduce a preferred result.

## Case record

Use one record per case.

| Field | Required account |
|---|---|
| case label | stable Definition-local `case.<descriptive_name>` label |
| commitments under test | exact document-local `decision.*` labels |
| opening participant state | only persistent state visible to the Agent |
| delivered observations | IDs, values, freshness, and missing markers |
| active/non-applicable reasoning | semantic activation, not backend chain-of-thought |
| admissible response classes | at least one option where choice remains |
| forbidden response | concrete contract violation |
| emitted intent possibility | typed intent, if any |
| environment branch | admission, rejection, delay, delivery, or adverse effect |
| expected invariant | what must remain true for every backend |
| falsifier | observable output or trace pattern that disproves the contract |

Keep the reasoning short and inspectable. Do not include private model
chain-of-thought.

## Minimum portfolio

Every Definition needs cases proportional to its risk. Cover these six unless
the case is structurally impossible and the Definition explains why.

### Normal open-choice case

Activate a material commitment with all mandatory information available. Show
at least two admissible response classes when the participant truly has
discretion. The case fails if the Definition secretly forces the observed Draft
response.

### Missing or stale information

Remove or stale one observation used by a decision. Show whether the situation
becomes non-applicable, requires a query, permits delay, or still permits a
bounded conservative response. The case fails if hidden future or world state
fills the gap.

### Pending lifecycle

Give the Agent evidence that an intent was emitted but no final disposition has
arrived. The case fails if it treats the request as accepted, delivered,
executed, or effective.

### Authority denial

Allow an admissible request and have the environment reject it for authority,
route, or target reasons. The Agent's choice may remain valid even though the
world does not change. The case fails if intent validity depends on success.

### Adverse or partial result

Admit an intent but produce a delayed, partial, or adverse environment result.
The case fails if the Agent wrote the desired outcome directly or if later
reconsideration uses an undelivered result.

### Meaningful perturbation

Change one material observation, state item, or structural assumption while
holding identity and backend type fixed. Show how the admissible set,
activation, or reopening status changes. A perturbation that merely changes the
backend's preferred option does not test the semantic contract.

## Additional high-risk cases

Add these when relevant:

- two commitments activate concurrently;
- duplicated or superseded messages arrive;
- an addressed notice reaches the wrong or ineligible target;
- the Agent attempts an intent after its situation closed;
- an organizational split trigger is reached;
- vocabulary becomes visible before its enabling transition;
- an Agent receives its own rejected intent as if it were another actor's
  message; or
- configuration selects an edge value in the declared domain.

## Invariant versus expected response

Write invariants about legality and ownership:

- no backend may use `obs.authority_notice` before delivery;
- every emitted `request_resource` must be permitted by
  `decision.resource_request`;
- rejection must not mutate the requested world state; or
- receipt of a superseding notice must mark the older notice stale.

Do not write expected responses as if they were invariants:

- the Agent should choose the historically observed act;
- the LLM should be cautious;
- the Rule backend should produce the final Draft state; or
- the request should succeed.

Those may be downstream hypotheses, not Definition truth.

## Falsifier design

A falsifier must be observable in an artifact available to review. Good
falsifiers name:

- a trace record that should never exist;
- a missing trace record required by a duty;
- an out-of-contract intent;
- an unavailable observation in backend context;
- an environment mutation without admission;
- a lifecycle jump;
- a participant-state update with no owned updater; or
- a representation conflict exposed by two independent choices.

“The simulation seems unrealistic” is not a contract falsifier. It does not
locate the violated authority or evidence.

## Structural alternatives

When the dataset underdetermines the interface, cases may compare alternative
structures without claiming which is historically true. Examples:

- one organization Agent versus two office Agents;
- addressed notice versus public observation;
- explicit unknown versus absent observation;
- persistent request state versus stateless reconsideration; or
- action request versus message-only communication.

Record the selected structure as an assumption and the alternative as a
successor trigger. Do not embed both simultaneously unless the scenario
explicitly models the distinction.

## Case adequacy review

The case portfolio is adequate when:

- every material commitment appears in at least one normal and one adverse or
  boundary case;
- every intent appears in a lifecycle or rejection case;
- every mandatory observation is absent or stale in at least one case;
- environment ownership is exercised rather than merely stated;
- at least one perturbation can change admissibility; and
- every falsifier maps to a trace, state, or validation observation.

Case counts are not a substitute for risk coverage. A simple interface may need
six compact cases; an aggregated authority with several commitments may need
more.

## Failure routing

If a case cannot be expressed because an observation or intent kind is missing,
return to shared registries. If the world cannot admit, reject, or apply the
branch, return to scenario/mechanism. If exact selection is missing, route to
configuration or backend. If the case reveals duplicate authority or
aggregation loss, return to roster and representation.

## Completion evidence

Record the case portfolio, commitment and intent coverage, each expected
invariant, each falsifier, the owner of every environment branch, and unresolved
structural alternatives. A reviewer must be able to reproduce the semantic
judgment without choosing the same backend response.
