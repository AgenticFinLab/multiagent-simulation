# Dataset provenance and exposure

## Closed input boundary

Agent Definition authoring may use only the admitted event package:

- `event_spec.json`;
- `frozen_evidence.json`; and
- `draft_epg.json`.

The accepted Source Profile, roster, and shared registries are permitted
projections of those inputs. They do not create new historical evidence.
Reference EPG, held-out records, evaluation-only material, external research,
web search, and remembered facts about the event remain outside the authoring
boundary.

## Four provenance classes

Classify each material statement before using it.

| Class | Meaning | Where it may appear |
|---|---|---|
| dataset material | directly exposed by an admitted record | provenance ledger and semantic prose |
| executable structural assumption | needed to make an underspecified interface runnable | assumption ledger, limitations, later configuration when valued |
| generated run material | created only by admitted execution | never as authoring-time knowledge; only as a possible observation kind |
| downstream selection | exact value or choice made by configuration/backend | domain declaration only in the Definition |

Grammar such as “may,” “would,” “typically,” or “likely” is not a provenance
class. If the author cannot classify a claim, remove it or stop for review.

## Stable anchors

Use locators that survive prose movement and are resolvable from the admitted
JSON. Prefer:

- event ID plus stable stage or episode ID;
- participant ID;
- action, message, edge, or process ID;
- frozen-evidence record ID; and
- a JSON Pointer when no stable record ID exists.

An anchor identifies the exposed dataset statement. It does not certify that
the statement is complete, historically verified, causal, or suitable for
calibration.

## Claim ledger

Create one row for each claim that changes representation or executable
semantics.

| Claim label | Claim | Class | Anchor or owner | Use | Withdrawal consequence |
|---|---|---|---|---|---|
| `claim.<descriptive_name>` | | dataset / assumption / generated / downstream | | | |

Material claims include:

- participant identity and role;
- communication or reporting relationships;
- observation availability;
- authority and prohibitions;
- action or message alternatives;
- ordering and lifecycle constraints;
- persistent state transitions; and
- scope exclusions.

Several sentences may share an anchor, but one broad citation must not conceal
different provenance classes.

## Draft and frozen evidence

Treat Draft EPG content as benchmark-provided process material. Preserve its
identity and uncertainty; do not rewrite it as independently verified history.
Treat frozen evidence according to its own exposed fields and status. Neither
source authorizes inference about an internal motive, private knowledge,
institutional rule, or causal mechanism that is not represented in the bytes.

When two admitted records conflict:

1. preserve both anchors;
2. state the conflict;
3. avoid resolving it through external knowledge;
4. choose an executable treatment only as a labeled assumption; and
5. describe the alternative treatment and successor condition.

## Full-Draft exposure

Authoring may need every appearance of the candidate across the exposed Draft.
That does not make every later stage available to the simulated Agent.

Separate:

- author exposure: records the Definition author may inspect;
- interface exposure: observations the simulated Agent may receive at a
  particular decision time; and
- backend context: the serialized subset delivered to Rule, LLM, or RuleLLM.

A later Draft result may justify defining a possible lifecycle state, but it
must not be placed in the Agent's earlier observation inventory unless a
scenario route can produce and deliver it.

## Vocabulary exposure

Even a field name can leak future information. Record event-specific vocabulary
that exists in schemas, intent alternatives, message kinds, or enumerations
before its associated event occurs.

Acceptable treatments include:

- use a domain-neutral term;
- expose the term only after a scenario transition;
- declare that vocabulary exposure is an intentional structural assumption;
  or
- create a successor interface whose vocabulary becomes available later.

Leaving a value blank does not hide the meaning of a revealing field.

## Structural assumptions

An assumption must be executable and contestable.

| Field | Required account |
|---|---|
| assumption label | stable document-local `assumption.<descriptive_name>` label |
| missing dataset fact | what the admitted package does not specify |
| selected structure | what is introduced so execution is possible |
| owner | Definition, scenario, configuration, or backend |
| affected commitments | exact `decision.*` labels and observation IDs |
| alternative | at least one plausible structural treatment |
| sensitivity or successor | what change requires reevaluation |

Do not use an assumption to manufacture historical accuracy. A Definition may
declare a route possible; it cannot claim that the route existed historically
unless the dataset exposes that claim.

## Generated material

Generated messages, admissions, rejections, allocations, and effects may be
named as observation types. Their values are unavailable until the
authoritative environment produces them in a run.

Bad:

> The Agent observes that its request will be approved.

Good:

> After the environment delivers a typed disposition, the Agent may observe
> `request_disposition` with an admitted, rejected, or pending state.

## Downstream selections

The Definition may declare a construct such as response urgency, confidence
class, or reconsideration window only when the construct changes admissible
behavior. It records meaning, unit if any, and domain. Configuration selects
values; backend realization selects among admissible responses.

Avoid invented precision. If the dataset does not support a numerical domain,
use an explicit ordered or categorical construct and record its synthetic
status.

## Leakage review

Before publication, inspect for:

- later-stage facts presented as current observations;
- results embedded in intent names;
- another Agent's private state;
- evaluator labels or Reference structure;
- historical facts recalled but absent from admitted inputs;
- exact values copied from a previous event;
- vocabulary that reveals an unreached state; and
- prose implying that the Draft has been externally verified.

Any protected-content exposure is a stop condition. Record it; do not
paraphrase the exposed fact into the Definition.

## Falsification and withdrawal

For each assumption and high-impact dataset claim, state what changes if it is
withdrawn. A useful Definition does not merely cite support; it shows which
interface commitments depend on that support.

If removing one anchor invalidates identity, return to roster. If it invalidates
a route or world result, return to scenario. If it affects only an exact
selection, route it to configuration or backend.

## Completion evidence

Completion requires a resolvable claim ledger, a separate assumption ledger,
an author/interface exposure distinction, future-information and vocabulary
reviews, conflicts left visible, and withdrawal consequences for material
claims. The ledger must be understandable without external browsing.
