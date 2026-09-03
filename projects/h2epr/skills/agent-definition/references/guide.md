# Agent Definition authoring guide

## Product boundary

An Agent Definition is the human semantic authority for one named decision
interface. It states who is represented, what the interface can know and
request, and what would falsify that representation. It does not select policy
thresholds, prompts, decoding settings, world outcomes, or a successful path.

Use the maintained ten-module template without renaming or reordering modules.
Machine registries are projections of the accepted prose and must not widen it.

## Representation decision

| Candidate | Use an Agent when | Route elsewhere when |
|---|---|---|
| person | the dataset exposes a consequential choice attributable to that person | the person is mentioned only as context or an object of action |
| organization | one accountable interface can represent the relevant decision | distinct internal authorities would make one interface misleading |
| committee or office | the collective/office has an identifiable decision boundary | it only announces an environment-owned institutional transition |
| supplier or intermediary | it observes or chooses independently in the window | behavior is fully exogenous or unsupported by the dataset |

Name the aggregation loss and a concrete trigger for splitting the Agent. Do
not preserve a famous participant merely because it seems historically
important.

## Provenance ledger

For every material role, relationship, observation, authority, and choice-set
claim, record one of:

- a dataset anchor with file and stable stage/episode/participant/action ID;
- an executable structural assumption with rationale and owner; or
- a generated observation that can exist only after a run.

Wording such as “would,” “may,” or “likely” is not a provenance class. A Draft
statement remains dataset material and must not be rewritten as independently
verified history.

## Interface construction

1. Define the decision occasion and non-applicable condition.
2. Enumerate visible observations, producer, availability, freshness, missing
   behavior, and consumers.
3. Name persistent state and the event that updates it; leave transient model
   reasoning untracked.
4. Define permitted intents, targets, payload meaning, duties, prohibitions,
   precedence, justified delay, and reopening.
5. For every intent, name the environment-owned admission and result. The
   Agent never asserts delivery, feasibility, allocation, or success.
6. Declare configurable constructs and admissible domains, leaving values to
   shared or backend configuration.
7. State a process pattern that would contradict the Definition.

## Worked cases

Each case states observations available at decision time, an admissible
response class, a forbidden response, and the environment boundary.

| Case | Required demonstration |
|---|---|
| normal | at least one material response remains open to the backend |
| missing information | missing data cannot be silently replaced by future or private state |
| pending lifecycle | the Agent does not treat a request as a completed result |
| authority denial | an admissible request can still be rejected by the environment |
| adverse result | backend intent and world outcome remain distinguishable |
| perturbation | changing a material observation can change the admissible response without changing identity |

An always-no-op interface is incomplete when an activated situation carries a
declared duty or minimum response class.

## Falsifiers and routing

Return to roster ownership when the candidate is a population, process, world
entity, or duplicate interface. Return to scenario ownership for world truth,
routes, resources, or effect semantics. Return to configuration for exact
values and to backend realization for selection logic. Stop for protected
information, external research, future leakage, or invented authority.

## Completion evidence

Record template revision, semantic parent ID, source participant IDs and
anchors, interface IDs used, named assumptions, adversarial cases, limitations,
successor trigger, reviewer disposition, validation results, and content hash.
Acceptance means the event-wide interface can project the Definition without
loss or widening; it does not mean a backend or run succeeds.
