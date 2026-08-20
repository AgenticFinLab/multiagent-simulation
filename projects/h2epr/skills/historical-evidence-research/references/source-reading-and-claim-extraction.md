# Source reading and claim extraction

Read sources to establish bounded propositions. Keep discovery metadata,
source interpretation, atomic claims, and model use distinct.

## Source record

For every adopted source, record:

| Field | Content |
|---|---|
| Source ID | Stable local identifier. |
| Research status | Adopted, consulted-not-adopted, locator-only, inaccessible, or excluded, with a reason. |
| Full citation | Author or institution, title, date, publication or archive. |
| Source class | Institutional/legal, contemporaneous observation, participant account, quantitative record, retrospective scholarship, theory, analogy, or another explicit class. |
| Locator | Stable URL, archive identifier, volume/issue, page, section, image, table, or file path. |
| Original date | When the source was created or published. |
| Retrieval date | When the H2EPR research process accessed it. |
| Custody or reproduction | Original, official scan, critical edition, faithful transcription, repository copy, or derived capture. |
| Authorship and audience | Who produced it and for whom. |
| Coverage | Event period, institutions, subjects, and evidence base. |
| Limitations | Missing pages, OCR quality, retrospective bias, advocacy, reporting lag, unverified upstream claims, or other constraints. |
| Upstream dependency | Earlier account, dataset, interview, archive item, or citation on which this source relies for the adopted claim. |
| Archive identity | Local filename and content hash when archived. |
| Adoption reason | Which research question or claim family the source changes. |

Do not label a source “primary” without naming the proposition for which it is
primary. A later official report can be a primary source for the report's own
institutional finding and a retrospective source for an earlier private
conversation.

Project decisions and architecture documents may appear in a research brief as
scope constraints. Keep them outside the historical source register and do not
use them to support event facts or participant behavior.

## Reading sequence

1. Confirm title, author or institution, date, edition, and completeness.
2. Read the surrounding section, not only the keyword hit.
3. Identify what the author directly observed, recorded, inferred, or repeated.
4. Locate definitions, exceptions, amendments, dates, and scope conditions.
5. Note whether the source describes formal authority, actual practice,
   contemporaneous belief, later interpretation, or outcome.
6. Inspect cited upstream sources for behaviorally material claims.
7. Search within the source for language that contradicts the initial model.
8. Extract atomic claims with precise locators.

For critical sources, verify OCR against the page image when wording, dates,
names, numbers, negatives, or exceptions matter.

## Atomic claim record

Each record should express one proposition that can be supported, withdrawn,
or disputed independently.

| Field | Content |
|---|---|
| Claim ID | Stable identifier. |
| Proposition | One declarative statement with entity, relation/action, object, and applicable time. |
| Claim family | Identity, membership, governance, authority, information, resource, relation, action, result, mechanism, parameter, or interpretation. |
| Subject and scope | Entity, organizational level, counterpart, jurisdiction, and event interval. |
| Source support | Source ID plus page, section, table, image, or paragraph locator. |
| Source relation | Directly states, records, measures, estimates, infers, repeats, contradicts, or contextualizes. |
| Event time | When the described condition or action held. |
| Participant availability | Who could know the claim, through which channel, and by when. |
| Research availability | When the material became available to the current research process. |
| Epistemic status | Direct support, bounded inference, estimate, disputed, contradicted, unresolved, or unavailable. |
| Use class | Construction, mechanism selection, parameter bounding, scenario, worked case, falsification, or future evaluation. |
| Exposure | Unseen candidate, locally known, full-draft exposed, evaluation-exposed, or another explicit project class. |
| Modeling consequence | Which representation, observation, mechanism, action, parameter, scenario, or falsifier changes. |
| Competing claims | IDs of mutually inconsistent or alternative propositions. |
| Withdrawal consequence | What must be removed, revised, branched, or marked unknown if this claim fails. |

The ledger can encode these fields in the project's chosen format. Field names
are illustrative semantics, not a machine schema mandated by this reference.

## Claim-writing rules

### Keep propositions atomic

Split:

> The institution was not a member, was ineligible for every facility, and was
> rejected because it was insolvent.

into separate claims about membership, each facility or route, the recorded
decision, the stated reason, and solvency. One source may support only some of
them.

### Separate source statement from model interpretation

Record:

1. what the source says;
2. what can be inferred within stated bounds;
3. how H2EPR proposes to use it.

Do not rewrite an observed outcome as a general decision rule.

### Preserve historical terminology

Store the source's original term and the normalized H2EPR concept when they
differ. Explain partial equivalence. Terms such as trust company, clearing
agent, member bank, certificate, loan, assistance, suspension, and solvency may
carry historically specific meanings.

### Treat absence carefully

Failure to find a record is not proof that an action, authority, or discussion
did not exist. Negative claims require an appropriate complete record set,
explicit prohibition, competent testimony, or a clearly bounded formulation.

### Keep quotations short and purposeful

Use a short excerpt when exact wording matters, with a precise locator. Prefer
accurate paraphrase for the research record and retain the original source for
context. Do not build the dossier by copying long passages.

## Source-to-claim cross-check

Before adoption, verify:

- every claim locator resolves inside the source;
- dates and entity names match the relevant edition and event interval;
- quoted numbers and units are transcribed correctly;
- a later source is not described as contemporaneous evidence;
- a source that repeats another account is not counted as independent
  corroboration without qualification;
- advisory or derived synthesis is not used in place of the original theory or
  empirical source for a publication-facing claim;
- the claim scope is no broader than the source;
- source limitations appear in the adjudication.
