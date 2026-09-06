# Agent Definition template

Use this template for one named person, organization, office, committee, or
institutional decision interface. Keep the ten modules and their order. Delete
all prompts and placeholder rows before review.

The Definition is the reader-facing semantic authority for participant
identity, information, authority, admissible choice, and limitations.
Registries and backend bindings project it without widening. Exact values,
selection logic, transport, world effects, and successful outcomes belong to
their downstream owners.

For the full method, use the
[agent-definition Skill](../skills/agent-definition/SKILL.md). The
[complete synthetic example](../skills/agent-definition/references/complete-synthetic-example.md)
shows a filled document; its event vocabulary and choices are not defaults.

Copy machine-facing identifiers exactly from their owning artifacts:
`actor_id` and `intent_id` use lowercase snake case, observation IDs use the
maintained `obs.<name>` namespace, state fields use their exact dotted scenario
paths, and semantic parents use the maintained dotted identity. Labels prefixed
with `claim.`, `assumption.`, `decision.`, and `case.` are descriptive
cross-references local to this document. Do not add them to machine artifacts
unless a reviewed schema explicitly adopts them.

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | `<exact lowercase_snake_case actor_id>; <reader-facing name>` |
| Benchmark event and interval | `<event ID, title, and modeled interval>` |
| Represented decision interface | `<one accountable interface and bounded choice family>` |
| Source participant IDs | `<all source participant IDs and Draft appearances>` |
| Primary decision commitments | `<document-local decision.<descriptive_name> labels>` |
| Invocation semantics | `<event-triggered or otherwise bounded; exact cadence owner>` |
| Participant-state authority | `<state the Agent may retain and state it cannot own>` |
| Dataset exposure and scope | `<admitted inputs and explicit exclusions>` |
| Semantic parents | `<Source Profile, roster, registries, and scenario identities>` |
| Definition semantic ID | `<h2epr.<event_number>.agent.<actor_id>.v1 or current maintained form>` |

In one compact paragraph, explain why this participant is an Agent, which
choice remains open to a backend, and which outcomes remain with other
participants or the environment. The paragraph must remain true if the
backend, configuration, and trajectory change.

## 2. Benchmark participant and representation

State the roster disposition and the evidence that the candidate has an
attributable, consequential, observable, and separable choice. Record rejected
alternatives such as Population, context, or institutional process.

For an organization or office, complete the boundary ledger.

| Internal or related unit | Status | Included function | Excluded function | Reason and anchor |
|---|---|---|---|---|
| `<unit>` | included / excluded / context | `<function represented here>` | `<authority or state kept outside>` | `<claim or assumption label>` |

Name:

- the represented decision interface;
- aggregation loss and any suppressed internal conflict;
- authority deliberately not granted;
- overlap checked against other Agents and Populations;
- a condition for narrowing the interface; and
- a condition for splitting it into successor Agents.

Do not retain a participant solely because it is prominent in the event. If
the candidate only undergoes an environment transition, return it to roster or
scenario ownership.

## 3. Dataset basis and provenance

Use only the admitted `event_spec.json`, `frozen_evidence.json`, and
`draft_epg.json`, plus accepted projections of those inputs. Draft material is
benchmark-provided process content, not independently verified history.

### Claim ledger

| Claim label | Claim | Provenance class | Stable anchor or owner | Semantic use | Withdrawal consequence |
|---|---|---|---|---|---|
| `claim.<descriptive_name>` | `<material identity, role, relation, observation, authority, or choice claim>` | dataset / assumption / generated / downstream | `<file and stable ID, JSON Pointer, or owning layer>` | `<modules or identifiers affected>` | `<what must change if withdrawn>` |

### Executable assumption ledger

| Assumption label | Missing dataset detail | Selected structure | Owner | Affected commitments | Alternative and successor condition |
|---|---|---|---|---|---|
| `assumption.<descriptive_name>` | | | Definition / registry / scenario / configuration / backend | | |

Separate:

- dataset material exposed to the author;
- observations the simulated Agent may actually receive;
- generated material unavailable before a run;
- structural assumptions needed for execution; and
- constructs or values selected downstream.

Record conflicts without resolving them through external knowledge. List
event-specific vocabulary visible before its associated result and explain its
admitted treatment. Stop on Reference, held-out, evaluation-only, web, or
remembered-event exposure.

## 4. Event role, relationships, and authority

Describe the participant's bounded role without writing an organizational
biography. Use directional, typed relationships.

| Counterparty or process | Direction | Eligible observation, request, or message | Agent authority | Environment or counterparty boundary |
|---|---|---|---|---|
| `<registered participant/process>` | receive / send / bidirectional | `<semantic ID or kind>` | `<decide, communicate, request, observe>` | `<admission, delivery, execution, or response not owned>` |

Separate authority dimensions.

| Dimension | Boundary and provenance |
|---|---|
| decide | `<choices attributable to this interface>` |
| authorize | `<what it may authorize; what remains institutional>` |
| communicate | `<eligible message kinds and target classes>` |
| allocate | `<resources controlled, requestable, observed, or unavailable>` |
| execute | `<participant execution, if any; otherwise environment-owned>` |
| verify | `<classifications it may make and those it may not>` |
| observe | `<registered delivered information only>` |

Scenario state owns actual memberships, routes, resources, authorization, and
relationship status at runtime. An admissible intent does not prove that any of
them are available.

## 5. Decision situations, observations, and state

### Observation inventory

| Observation ID | Meaning | Producer and delivery route | Availability and freshness | Missing/stale behavior | Visibility | Consuming decisions | Provenance |
|---|---|---|---|---|---|---|---|
| `obs.<descriptive_name>` | | | | | public / addressed / role-scoped / own-private | `<decision.* labels>` | dataset / assumption / generated |

For each observation, distinguish world truth, emission, admission, delivery,
participant receipt, retention, and supersession. A later Draft statement may
name a possible observation type but cannot become earlier Agent knowledge.

### Persistent state surface

| Exact state-field path | Meaning and initial condition | Update event | Update owner | Visibility | Retention/supersession | Consuming decisions |
|---|---|---|---|---|---|---|
| `entities.<entity_id>.<field_name>` | | | shared handler / runtime / reducer | | | `<decision.* labels>` |

Use the exact fields projected through `persistent_state_fields`. Own prior
action dispositions, delivered messages, and outgoing pending lifecycles
normally arrive through the maintained observation contract rather than new
state aliases. The state surface must not expose another Agent's private
choice, undelivered messages, future results, evaluator labels, or transient
model reasoning.

### Decision-situation index

| Decision label | Situation | Activation observation/state | Non-applicable condition | Reopening event |
|---|---|---|---|---|
| `decision.<descriptive_name>` | | | | |

List forbidden information explicitly. Explain what the Agent knows after a
request is pending, rejected, expired, delivered, or superseded. Exact polling
and retry cadence belong to configuration/backend realization.

## 6. Admissible decision semantics

Create one subsection per commitment using a stable document-local label.

### `decision.<descriptive_name>` — `<bounded decision situation>`

| Field | Contract |
|---|---|
| situation | `<choice being represented>` |
| activation | `<observable condition that opens it>` |
| non-applicable | `<condition under which there is no choice>` |
| usable observations/state | `<exact observation IDs and state-field paths>` |
| admissible alternatives | `<semantic response classes, not a decision tree>` |
| minimum response | `<duty, or why explicit no-op is admissible>` |
| prohibitions | `<responses never allowed>` |
| precedence/concurrency | `<relationship to other active commitments>` |
| delay or abstention | `<when permitted and what it cannot imply>` |
| reopening | `<new observation or lifecycle event>` |
| permitted intents | `<exact intent_id values>` |
| environment boundary | `<admission/result the Agent cannot assert>` |
| falsifier | `<observable trace or state pattern that contradicts the contract>` |

Classify each apparent prerequisite as:

- world feasibility, enforced by the environment;
- mandatory actor information, enforced consistently by the shared interface;
  or
- policy selection, left to the backend.

Definitions constrain the choice set. Rule code, an LLM, or RuleLLM admission
selects within that set. At least one executable case should preserve
meaningful backend choice. If the Definition fixes thresholds, priorities,
prompts, a decision tree, or the expected historical response, move that
content downstream.

## 7. Intent and environment-result boundary

| Exact registry `intent_id` | Permitting decisions | Meaning | Eligible target | Required semantic content | Lifecycle and visible receipts | Environment-owned result |
|---|---|---|---|---|---|---|
| `<lowercase_verb_object>` | `<decision.* labels>` | | `<registered target class>` | `<fields, not backend serialization>` | proposed → emitted → admitted/rejected → delivered/acted on/expired as applicable | `<authorization, allocation, delivery, execution, or world effect>` |

The registry `intent_id` becomes `action_type` in a participant decision. Each
runtime emission receives a separate generated `ActionIntent.intent_id`; do not
use a `decision.*` label or registry action type as that instance identity.

### Message output surface

| Exact scenario `message_type` | Permitting decision/action type | Eligible recipients | Required payload semantics | Transport lifecycle and environment boundary |
|---|---|---|---|---|
| `<lowercase_descriptive_name>` | `<decision.* label and registry intent_id>` | `<registered recipient IDs or class>` | `<closed fields, not prompt serialization>` | `<pending, delivered, expired, rejected, duplicate, or failed; emission does not prove delivery>` |

Each emitted message receives a generated `message_intent_id` distinct from its
`message_type` and source `ActionIntent.intent_id`. State duplicate,
withdrawal, expiration, and supersession semantics where they matter. Prefer
request names over success names: `request_restriction`, not
`restriction_completed`.

The Agent may select a typed action and attach zero or more typed messages.
Action admission, message transport, target eligibility, delivery, authority,
resources, scheduling, execution, state mutation, and causal effects belong to
the environment and reducer.

## 8. Configurable dimensions and uncertainty

Declare a construct only when a worked case or planned backend comparison
depends on it. A Definition does not need personality parameters merely to
appear complete.

| Construct | Meaning and unit | Admissible domain | Provenance class | Configuration owner | Behavioral use |
|---|---|---|---|---|---|
| `<construct ID>` | | `<bounded categorical, ordinal, or numeric domain>` | dataset-derived / synthetic / underdetermined | shared / Rule / LLM / RuleLLM | `<which commitment it may affect>` |

Put exact selected values, seeds, thresholds, retry schedules, prompt settings,
and fallback algorithms in configuration or backend realization. If the
dataset cannot justify numerical precision, use a labeled categorical or
structural alternative. State which dimensions require sensitivity analysis
before a scientific claim.

## 9. Worked cases and contract falsification

Use one table or subsection per case. Cover normal choice, missing or stale
information, pending lifecycle, authority denial, adverse or partial result,
and a meaningful perturbation unless a category is structurally impossible.

| Field | Case account |
|---|---|
| case label | `case.<descriptive_name>` |
| decisions under test | `<decision.* labels>` |
| opening participant state | `<exact state-field paths, memory, and lifecycle values visible to the Agent>` |
| delivered observations | `<exact observation IDs, values, freshness, and missing markers>` |
| activation/non-applicable result | `<semantic result without private model reasoning>` |
| admissible response classes | `<at least one; preserve choice where intended>` |
| forbidden response | `<concrete violation>` |
| possible intent | `<exact intent_id, if any>` |
| environment branch | `<admit, reject, delay, deliver, partially apply, or adverse result>` |
| invariant | `<what every backend must preserve>` |
| falsifier | `<observable trace/state pattern that disproves the contract>` |

Case coverage must exercise every commitment, intent lifecycle, mandatory
observation, and material environment boundary. Cases test legality and
ownership; they do not require the Draft trajectory or a successful outcome.

## 10. Limitations and source anchors

State concrete limitations and consequences:

- representation and aggregation losses;
- missing or conflicting dataset content;
- omitted roles, routes, resources, or internal distinctions;
- executable assumptions and viable structural alternatives;
- parameter or configuration uncertainty;
- semantics not exercised by current backends;
- exact condition for a successor, split, narrowing, or scenario revision; and
- scientific questions deferred to later evaluation.

Close with:

### Source-anchor index

| Anchor | Claims supported |
|---|---|
| `<stable admitted locator>` | `<claim.* labels>` |

### Semantic-parent and publication handoff

| Field | Record |
|---|---|
| template revision | `<current template identity>` |
| Source Profile and roster | `<paths and content identities>` |
| shared registries and scenario | `<paths and content identities>` |
| Definition semantic ID | `<stable ID used by participant-interface projections>` |
| External content identity record | `<participant semantic index or release receipt; never a self-embedded file digest>` |
| commitment/observation/state/intent/case counts | `<counts>` |
| validation | `<structural, semantic, and event-wide checks>` |
| review record | `<authoritative external disposition, reviewer, and date>` |
| unresolved findings | `<specific findings or none>` |
| next legal action | `<independent review, projection, revision, or successor>` |
