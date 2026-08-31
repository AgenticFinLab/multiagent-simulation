# Samsung Galaxy Note7 Event Scenario Definition v0.1

- Event: `H2EPR-0481`
- Scenario: `h2epr.scenario.0481.samsung_note7_battery_recall@0.1.0`
- Modeled interval: 19 August--15 October 2016
- Purpose: engineering and method mechanism coverage

This package defines the event world shared by the eight released participant
products. It owns causal opportunities, institutions and scoped resource
domains, relationships, product and device state, information delivery,
authority, twelve business lifecycles, adjudication, typed results, structural
variants, termination, and reproducibility obligations.

The package permits trajectories that do not reproduce history. It supports
no defect-cause, liability, calibration, historical-fit, held-out,
policy-effectiveness, predictive, scientific-validity, or universal-
generality claim.

## Files

| File | Responsibility |
|---|---|
| [scenario-definition.md](scenario-definition.md) | publication-facing causal, institutional, informational, lifecycle, result, variant, and claim semantics |
| [interface-closure.md](interface-closure.md) | complete reconciliation of 8 products, 40 observations, 28 private-state placements, 37 intents, and 12 lifecycle families |
| [substantive-review.md](substantive-review.md) | authoring-exposed adversarial review, resolved findings, and limitations |
| [manifest.json](manifest.json) | release identity, exact semantic inputs, coverage, artifacts, decisions, and authorization boundary |
| [SHA256SUMS](SHA256SUMS) | release-directory integrity record |

[ADR-0015](../../../decisions/ADR-0015-note7-event-scenario-definition-boundary.md)
records the accepted authoring-window decisions. January 2017 diagnosis and
remediation remain future-only to every 2016 modeled actor.

Verify this directory with `sha256sum -c SHA256SUMS`. The next responsibility
is one qualitative, non-executable Scenario Configuration and fail-closed
static admission.
