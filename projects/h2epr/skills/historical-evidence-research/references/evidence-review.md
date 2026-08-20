# Evidence review

Review the evidence set as a scientific input to modeling. Structural
completeness, source count, and valid links are useful checks; they do not by
themselves establish that the evidence supports the proposed model use.

## Review dimensions

### Research question and scope

- Is the question bounded enough to adjudicate?
- Does each adopted source affect the stated model question?
- Did the search expand to another participant, event, mechanism, or use
  without renewed scope?
- Are the stop conditions and access boundary recorded?

### Source identity and fit

- Is each source's author or institution, title, date, edition, locator, and
  custody clear?
- Is the source competent for the proposition assigned to it?
- Are official, contemporaneous, retrospective, theoretical, and analogical
  roles distinguished?
- Are project decisions kept as scope constraints rather than event evidence?
- Were important OCR passages checked against page images?
- Are repeated accounts recognized as dependent rather than independent
  corroboration?
- For theory entering the Definition, was the cited original work checked
  rather than relying only on an advisory synthesis?

### Claim quality

- Is each claim atomic and falsifiable independently?
- Does the proposition include its entity, scope, relation or action, and time?
- Does the locator directly support the recorded source relation?
- Are direct statement, inference, estimate, interpretation, and assumption
  separated?
- Is a negative claim supported by an appropriate record boundary?

### Temporal admissibility

- Are event time, participant-available time, source-production time, and
  research-available time distinguished where material?
- Does every proposed observation have a plausible authorized channel?
- Have later outcomes or later institutional mechanisms leaked backward?
- Are uncertain dates represented as intervals or alternatives?

### Evidence use and exposure

- Is every claim assigned a specific use or context-only status?
- Is the proposed use no broader than the source support?
- Are construction, mechanism selection, parameter bounding, worked case, and
  evaluation roles separated?
- Is already exposed evidence excluded from claims of independent held-out
  validation?
- Would withdrawing a claim have a recorded consequence for the model?

### Conflict and uncertainty

- Were disconfirming sources and alternative interpretations sought?
- Are material contradictions preserved rather than averaged into a score?
- Does the record distinguish `unknown`, `not found within scope`, and
  `evidence of absence`?
- Are formal prohibition and discretionary policy modeled as different
  structures when the evidence does not resolve them?

### Model translation

- Does the evidence constrain a representation, observation, authority,
  resource, mechanism, action, parameter, scenario rule, case, or falsifier?
- Has a recorded historical outcome been mistaken for a general decision rule?
- Has theory been mistaken for evidence that the named historical actor used
  that mechanism?
- Would the resulting model still expose its assumptions and limitations to a
  reader who does not inspect runtime code?

## Closure verdicts

### `RESOLVED_FOR_STATED_USE`

Use when appropriate sources support one proposition strongly enough for the
declared model use, material alternatives have been examined, and temporal and
exposure boundaries are clear. State the use explicitly; resolution for
participant identity does not automatically resolve behavior or parameters.

### `BOUNDED_UNRESOLVED`

Use when the search establishes important constraints but cannot distinguish
between model-relevant alternatives. Record:

- what is supported;
- what remains unknown;
- which source classes were searched;
- which model structures remain possible;
- what new evidence could resolve the question;
- how the current model will preserve the uncertainty.

### `INSUFFICIENT_EVIDENCE`

Use when the available sources do not support the proposed claim or model use.
The model must remove the claim, downgrade it to an explicit assumption, narrow
its scope, or defer the affected behavior.

### `EVIDENCE_UNAVAILABLE_WITHIN_AUTHORIZED_SCOPE`

Use when potentially decisive material exists or is plausibly referenced but
cannot be accessed under the current permission, archive, cost, credential, or
time boundary. Do not convert this verdict into a substantive historical
claim.

## Review record

A concise review should state:

```text
research_question=
authorized_scope=
sources_considered=
sources_adopted=
claim_families=
temporal_boundary=
exposure_boundary=
verdict=
supported_for=
not_supported_for=
unresolved_alternatives=
modeling_consequence=
next_evidence_if_any=
```

Use counts for inventory control, not as proof of rigor. The substantive review
must explain why the adopted evidence fits the claim and use.

## Archive review

When adopted sources are archived, verify:

- every archived item was actually used;
- every adopted local file appears in the source register;
- raw source and derived notes are clearly separated;
- locators, retrieval dates, filenames, media types, and hashes are recorded;
- no credentials, secrets, private records, or unauthorized held-out assets
  entered the archive;
- the archive can be read without changing the source bytes.
