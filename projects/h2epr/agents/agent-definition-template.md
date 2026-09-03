# Agent Definition template

Use this template for one named person, organization, office, committee, or
institutional decision interface. Keep the ten modules in order. The document
is a reader-facing semantic authority; registries and code are projections of
it.

## 1. Model overview

| Field | Account |
|---|---|
| Agent ID and display name | |
| Benchmark event and interval | |
| Represented decision interface | |
| Source participant IDs | |
| Primary decision situations | |
| Decision cadence | |
| State authority | |
| Dataset exposure and scope | |

Summarize the participant's event role, the choice represented, and what is
left to other participants or the environment.

## 2. Benchmark participant and representation

Describe the dataset participant, the represented person or organizational
interface, included and excluded internal actors, aggregation losses, and the
condition that would require splitting or narrowing the Agent.

## 3. Dataset basis and provenance

| Anchor | Available content | Semantic use | Limitation or conflict |
|---|---|---|---|
| `<file and stable record locator>` | | | |

Separate dataset statements, executable assumptions, and later generated
observations. Do not add external research or infer that a Draft statement is
verified history.

## 4. Event role, relationships, and authority

State duties, prohibitions, resources controlled or merely observed, eligible
counterparties, communication routes, and authorization boundaries. Scenario
state owns actual memberships, resources, and relationship status.

## 5. Decision situations, observations, and state

| Observation | Meaning | Producer and availability | Missing/stale rule | Consumers |
|---|---|---|---|---|
| | | | | |

List activation conditions, forbidden information, persistent participant
state, its update events, and its owner. Transient model reasoning is not
persistent state.

## 6. Admissible decision semantics

For each decision situation, define:

- activation and non-applicable cases;
- permitted intents and minimum response class;
- duties, prohibitions, and precedence;
- justified delay or abstention and the reopening event;
- remaining backend choice; and
- a process pattern that would contradict the Definition.

Definitions constrain the choice set. Rule code, an LLM, or RuleLLM admission
selects within that set.

## 7. Intent and environment-result boundary

| Intent | Meaning | Eligible target | Required content/lifecycle | Environment-owned result |
|---|---|---|---|---|
| | | | | |

An Agent emits typed action and message intents. Delivery, authority checks,
resource feasibility, scheduling, execution, and state effects belong to the
environment and reducer.

## 8. Configurable dimensions and uncertainty

| Construct | Meaning/unit | Admissible domain | Configuration owner | Behavioral use |
|---|---|---|---|---|
| | | | | |

Declare dimensions and bounds here. Put selected values in configuration or
backend realization. Mark synthetic, sensitivity, underdetermined, and
dataset-derived values distinctly.

## 9. Worked cases and contract falsification

Cover normal operation, missing information, pending state, authority denial,
adverse environment results, and one meaningful perturbation. Each case names
the decision-time observation, admissible response, forbidden response, and
environment boundary.

## 10. Limitations and source anchors

State representation losses, missing dataset content, unmodeled roles,
structural alternatives, parameter limits, and the exact condition for a
successor. List only dataset anchors and project semantic parents used by this
Definition.
