# Publication-facing research artifacts

H2EPR keeps its research account separate from the records used to manage and
verify the repository. Every tracked document should be intelligible to an
external reader, while Agent Definitions, population models, and evidence
syntheses should also be suitable for use as paper appendices or supplementary
methods.

## Artifact responsibilities

| Artifact | Primary reader and responsibility | Project metadata |
|---|---|---|
| Agent Definition or population model | Explains a participant, its evidence, information, state, mechanisms, choices, and limitations | Stable IDs, versions, review states, Git identities, and file hashes belong in a release manifest or other project record |
| Evidence synthesis or source register | States the claims, source locations, temporal availability, interpretation, and withdrawal consequences | Source identifiers and evidence classes may be retained when they improve scholarly traceability |
| Cross-participant interface account | Explains information routes, authority, lifecycles, and ownership across models | Mapping readiness and implementation decisions belong in the batch or release record |
| Roster, event entry, release, mapping, configuration, receipt, or test record | Coordinates scope or verifies an exact repository object | May retain the minimum IDs, versions, statuses, paths, and hashes needed for that responsibility |

Project metadata must not be copied into a research artifact merely to show
that a workflow step occurred. Conversely, a manifest or integrity record
should not be rewritten as narrative prose when exact machine identity is its
purpose.

When a release first needs a machine identity, new participant records use
`h2epr.agent-definition.<event_namespace>.<role-slug>` for Agent Definitions
and `h2epr.population-model.<event_namespace>.<role-slug>` for population
models. The release record assigns that identity once; the public title and
body do not repeat it. Existing released identities remain stable compatibility
identifiers rather than being renamed for appearance.

## Admission standard for research artifacts

A new or changed publication-facing artifact should satisfy six questions:

1. **Scholarly account.** Does it explain the event-bound representation and
   causal model in domain language that can be read without repository context?
2. **Evidence and limits.** Are evidence use, hindsight, uncertainty,
   calibration, and explanatory limits stated directly and without repeated
   disclaimer language?
3. **Clean public surface.** Are Git commits, file hashes, local paths, owner
   decision codes, workflow states, production profiles, semantic versions,
   release readiness labels, and implementation authorization notes absent?
4. **Lifecycle memory.** If a sent request, direction, investigation, control,
   or message can be delayed, rejected, fail, expire, or be superseded, does
   declared persistent state let later behavior distinguish those outcomes
   from an intent that was never issued?
5. **Claim precision.** Is a claim split when its parts have different model
   owners, evidence relations, or withdrawal consequences? Claims need not be
   reduced to sentence fragments when those responsibilities remain the same.
6. **Falsifiability.** Do the high-information cases include at least one
   controlled change and the corresponding change, or invariance, in predicted
   behavior?

These are content responsibilities, not six new documents or approvals. A
standard participant row normally closes them in its Definition or population
model, shared evidence record, concise review, and existing interface account.

## Repository check

The Agent Definition profile checker also screens canonical Agent Definitions
and population models for project-only metadata. It is a small admission aid,
not a substitute for evidence, historical, behavioral, or publication review.
Release manifests and other integrity records remain outside this check because
their purpose is to retain exact project identity.
