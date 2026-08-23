# Event Scenario Configuration — semantic design template

Use this template for the publication-facing design companion to one H2EPR
Scenario Configuration. It defines the minimum semantic account independently
of JSON/YAML layout. An accepted machine schema, when one exists, is a separate
engineering authority.

Delete instructional text when instantiating the template. Do not copy values
from a frozen canary or another event as defaults.

## Configuration identity

| Field | Value |
|---|---|
| Event ID | |
| Configuration ID | |
| Version and status | |
| Primary declared purpose | |
| Modeled interval and analytic horizon | |
| Historical calibration | `false` unless explicitly authorized and supported |
| Historical validation | `false` unless explicitly authorized and supported |
| Known-outcome fitting | `false` unless explicitly authorized and supported |
| Machine-document path and format identity | |
| Review and owner-decision records | |

## 1. Purpose and claim boundary

State the single primary purpose, the mechanism or comparison it must expose,
and what accepting the configuration would establish. List claims it cannot
support, including any excluded calibration, historical-baseline, prediction,
or validity claim.

Explain why this configuration is needed in addition to the accepted Event
Scenario Definition: identify the choices or instances it selects without
redefining scenario or participant meaning.

## 2. Pinned semantic inputs

| Input authority | Stable identity/version | Integrity value | Consumed scope | Verification root/rule |
|---|---|---|---|---|
| Event Scenario Definition and release manifest | | | | |
| Roster Definition release | | | | |
| Consolidated mapping and mapping profile | | | | |
| Evidence ledger and source register | | | | |
| Accepted owner decisions | | | | |

List every input needed to interpret the candidate. Do not replace an accepted
identity with an unpinned working path.

## 3. Execution boundary

| Question | Declaration |
|---|---|
| Execution eligible? | |
| Reason | |
| Missing prerequisites | |
| Selected-policy binding status | |
| Separately required authorization | |

Parsing, schema validation, or configuration admission must not change this
boundary. State explicitly how unbound policies fail closed.

## 4. Clock and structural baseline

### Clock and order

Record timezone, start, primary window, analytic horizon, event/phase ordering,
same-time precedence, tie-breaking, and forbidden precision. Explain the
evidence or construction basis for each material temporal choice.

### Structural selections

| Structural ID | Allowed domain | Baseline selection | Basis/identification | Causal limit | Sensitivity disposition |
|---|---|---|---|---|---|
| | | | | | |

Select exactly one allowed baseline for every structural family required by
the Definition.

## 5. Actor and unit assembly

### Named and population actors

| Entity ID | Actor ID | Participant product | Capabilities | Authority graph | Resource owner | Status/source |
|---|---|---|---|---|---|---|
| | | | | | | |

### Population capability units

| Unit ID | Actor ID | Capability | Host/institution | Weight and status | Private-state/profile selections | Resource scope |
|---|---|---|---|---|---|---|
| | | | | | | |

Reconcile one actor, authority graph, relationship set, and resource owner per
entity. Explain every deliberate multi-capability composition.

## 6. Opening records and exogenous inputs

### Opening records

| Record ID | Family | Owner/parties | Typed concept and value | Identification | Visibility | Source class |
|---|---|---|---|---|---|---|
| | | | | | | |

Cover the required authority, relationship, resource/condition, information,
and business-object families. Preserve unknown, unavailable, disputed, and
not-yet-delivered states without numerical repair.

### Exogenous inputs

| Input ID | Activation/time | Exact target | Typed effect | Visibility/delivery | Basis | Causal limit | Sensitivity | Outcome forcing? |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

Check opening state against later activation and distinguish issue from
delivery and receipt.

## 7. Policy semantics

| Policy ID | Semantic version | Selected alternative | Definition family closed | Implementation binding | Execution consequence |
|---|---|---|---|---|---|
| | | | | | |

Select semantic alternatives only. Policy algorithms, numeric calibration,
and runtime class references do not belong in this design.

## 8. Sensitivity overlays

| Overlay ID | Uncertainty addressed | Target kind | Exact target ID | Field | Replacement value | Coupled operations disclosed? |
|---|---|---|---|---|---|---|
| | | | | | | |

Every operation must be exact and type-checkable. Separate structural
uncertainty from input/parameter uncertainty, and do not introduce a semantic
family absent from the accepted Definition.

## 9. Completion and validation expectations

Define:

- normal completion;
- bounded-incomplete completion;
- fail-closed conditions;
- unresolved active-object carry-forward; and
- seal or later evaluation eligibility, if relevant to the accepted
  Definition but not yet authorized.

| Derived expectation or invariant | Expected value | Derivation authority | Verification method |
|---|---|---|---|
| | | | |

Counts are integrity expectations. They do not prove behavioral, historical,
or scientific validity.

## 10. Definition closure, review, and promotion

Summarize the adjacent closure record:

| Definition/configuration family | Configuration carrier | Closure | Retained boundary or routed gap |
|---|---|---|---|
| | | | |

Record substantive-review verdict, finding dispositions, owner-decision IDs,
limitations, and the next legal stage. If atomic promotion is authorized,
identify the final README, manifest, checksum inventory, and verification
rule. Promotion must not introduce semantic changes.

## Package checklist

- [ ] machine-readable Scenario Configuration candidate;
- [ ] this publication-facing configuration design;
- [ ] Definition-to-configuration closure record;
- [ ] separate substantive review;
- [ ] explicit owner-decision record when needed; and
- [ ] README, manifest, and checksum inventory only after authorized
  promotion.

The package remains non-executable until every separately governed
prerequisite and authorization is satisfied.
