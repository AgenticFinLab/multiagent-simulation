# SingHealth Data Breach Roster Definition release v0.1

- Status: accepted semantic release
- Event: `H2EPR-0616`
- Roster: `v0.2`
- Released: 25 August 2026

This release closes the H2EPR-0616 participant-definition phase. It pins seven
Agent Definitions, two population models, the accepted research roster and
event semantic skeleton, two evidence authorities, and two cross-participant
interface accounts.

## What the release establishes

Every causal row has a reviewed disposition:

- seven office-level Agent Definitions and two responsibility-unit Population
  Models own the causally necessary autonomous choices;
- external attack pressure remains a bounded adversarial process, not an
  attacker Agent or a fixed replay of the historical sequence;
- MOH, MCI, and CSA remain distinct routed institutional processes;
- endpoint users remain initial or exogenous context, while affected patients
  remain a consequence cohort; and
- access control, delivery, adjudication, realized system effects, and later
  investigation remain outside participant policy.

The release is a semantic research input. It contains no executable mapping,
configuration, policy, runtime carrier, parameter set, or simulation. It is
also not a historical calibration or scientific-validity claim.

## Files

- [`manifest.json`](manifest.json) records stable identities, versions,
  repository-relative paths, dispositions, and SHA-256 values.
- [`SHA256SUMS`](SHA256SUMS) verifies the files owned by this release
  directory. The manifest verifies its semantic inputs.
- The [research roster](../../../agents/rosters/singhealth_data_breach.md)
  owns the accepted participant and process dispositions.
- The [event semantic skeleton](../../../scenarios/singhealth_data_breach/semantic-skeleton.md)
  owns the shared event concepts, interaction routes, Scenario responsibilities,
  and structural boundaries.
- The [event coordination entry](../../../events/singhealth_data_breach/README.md)
  owns current authorization and links these stable semantic inputs.
- The [participant evidence](../../../events/singhealth_data_breach/participant-evidence-v0.1.md)
  owns the claim-level basis and participant-time limits.

Verify the release from this directory with:

```bash
sha256sum -c SHA256SUMS
```

## Later event work

A later cycle may separately authorize an Event Scenario Definition and one
consolidated semantic mapping from this exact inventory. That work must retain
the release's information, authority, intent/result, and non-participant
ownership boundaries. This release does not itself authorize either stage or
any implementation or experiment.
