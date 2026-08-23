---
name: h2epr-scenario-configuration
description: Design, revise, review, or promote a versioned H2EPR Scenario Configuration from an accepted Event Scenario Definition and consolidated mapping. Use to pin a declared purpose, semantic inputs, execution boundary, clock, structural selections, actor and unit assembly, opening records, exogenous inputs, policy selections, sensitivity overlays, completion, and validation expectations; do not use to invent participant behavior, define a machine schema, implement policies, project carriers, or run a simulation.
---

# Scenario Configuration

> Method status: working candidate extracted from the accepted H2EPR-0288
> Scenario Configuration. It has passed retrospective conformance against that
> case and should be forward-tested when a second event reaches this stage.

Use this Skill after both the Event Scenario Definition and the consolidated
mapping have been accepted. It turns their semantic possibilities into one
versioned, declared-purpose configuration while preserving a normally
non-executable boundary.

Read the public
[Scenario Configuration template](../../configs/scenario-configuration-template.md)
and [configuration content and closure](references/configuration-content-and-closure.md)
before authoring. Read
[configuration review and promotion](references/configuration-review-and-promotion.md)
before issuing a verdict or performing an authorized promotion. Read
[bounded engineering preflight](references/bounded-engineering-preflight.md)
only when preparing or reviewing the later E5 configuration-admission step.

This Skill has three modes:

- **Design mode** creates or revises a mutable semantic candidate and its
  Definition-closure record.
- **Review mode** independently tests the candidate and routes findings to the
  correct authority.
- **Promotion mode** records an explicit owner decision and promotes an
  unchanged reviewed semantic payload as one integrity package.

Keep the transition explicit:

```text
mutable configuration candidate
  -> independent substantive review
  -> owner decision
  -> separately authorized atomic promotion
  -> separately authorized bounded configuration admission
```

No earlier transition silently authorizes the next one.

## Required inputs

Confirm:

- event identity, modeled interval, declared configuration purpose, and claim
  boundary;
- exact accepted Event Scenario Definition identity and integrity record;
- exact accepted roster release, consolidated mapping, mapping profile,
  evidence ledger, and source-register identities required by the Definition;
- accepted owner decisions and unresolved structural or evidence questions;
- the complete actor, unit, relationship, resource, information, lifecycle,
  exogenous-input, policy, and sensitivity inventory owned by the scenario;
- candidate location, configuration ID, version rule, review audience, and
  intended status;
- whether the task permits evidence revision, schema or loader work, policy
  implementation, carrier projection, simulation, or only configuration work;
  and
- the exact stopping point and prohibited claims.

Stop before authoring if either semantic authority is mutable, inconsistent,
or not byte-identifiable. A configuration cannot stabilize a moving Definition
or mapping.

## Design mode

### 1. Fix purpose and claim boundary

Name exactly one primary purpose, such as mechanism coverage, a structural
sensitivity, or a later explicitly authorized empirical purpose. State
whether historical calibration, historical validation, and known-outcome
fitting are permitted. Default all three to false unless the task explicitly
authorizes and supports them.

State what the configuration can establish. A mechanism-coverage
configuration selects inspectable cases; it is not a historical baseline or a
scientific-validity claim.

### 2. Pin semantic inputs

Record stable identities and exact integrity values for every accepted input.
Resolve paths from one declared project root during verification, but keep
portable semantic identities in the configuration.

Do not copy a current working file where a release or manifest is the
authority. Do not let a frozen engineering canary supply defaults to the
configuration.

### 3. Derive the configuration inventory

Derive required families and coverage from the accepted Definition and
mapping before choosing values. Reconcile:

- clock, ordering, phases, horizon, and completion;
- structural variants and exogenous inputs;
- named actors, population actors, capability units, hosts, authority graphs,
  and resource owners;
- opening authority, relationship, resource, condition, information, and
  business-object records;
- policy semantics and implementation-binding status;
- exact sensitivity targets and operations; and
- validation expectations derived from the accepted semantic inventory.

The configuration selects scenario-owned alternatives and assembles released
semantics. It may not add a new participant choice, observation, authority,
resource, lifecycle meaning, or result.

### 4. Declare the execution boundary first

State whether the candidate is execution eligible. A normally accepted
configuration remains non-executable until exact identity, required policy
implementations, validated carrier projection, fail-closed loading, and the
authorized execution slice all exist.

List every missing prerequisite. Never interpret an absent or unbound policy
as a default implementation, and never let successful parsing change
execution eligibility.

### 5. Select time and structural baseline

Choose one clock, temporal-ordering policy, analytic horizon, and baseline
selection for every required structural variant. Preserve bounded dates and
partial order when evidence does not support invented intraday precision.

Every structural selection needs a stable identity, allowed domain, source or
construction basis, causal limit, and sensitivity disposition.

### 6. Assemble actors, units, and opening records

Preserve the accepted entity-to-actor-to-capability assembly. One entity keeps
one canonical actor interface, authority graph, relationship set, and resource
owner across composed capabilities. Population units retain their own host,
identity, weight status, private state, and resource scope.

Give every opening record a stable identity, owner, typed concept, value or
explicit unknown, identification status, visibility, and source class as
applicable. Unknown is not zero, unlimited, false, or an invitation to invent
a numeric default.

### 7. Select exogenous inputs and policy semantics

For each exogenous input, declare identity, time or activation condition,
target, typed effect, visibility/delivery, basis, causal limit, and
outcome-forcing status. A dated activation must agree with opening state.

For each policy family required by the Definition, select a semantic version
and named alternative and record implementation-binding status separately.
The configuration defines policy meaning, not policy code.

### 8. Define sensitivities and completion

Represent each sensitivity as typed operations against exact target kind,
target identity, field, and replacement value. Reject free-text targets,
ambiguous labels, hidden coupled changes, and overlays that introduce a new
semantic family.

Define normal completion, bounded incomplete completion, fail-closed
conditions, pending-object handling, and validation expectations. Derived
counts are integrity expectations, not evidence of correctness by themselves.

### 9. Close the Definition and review

Complete a family-by-family closure from the accepted Definition and mapping
to the candidate. Reconcile actor assembly, opening state, exogenous inputs,
policy coverage, sensitivities, causal ownership, and execution boundary.

Then enter review mode using the linked rubric. Do not use policy code,
runtime output, or private authoring notes to excuse a semantic gap.

## Review and promotion modes

Review mode produces a separate, finding-ranked report and no promotion. A
reviewer may require revision, return a problem to the Definition or mapping,
or identify an owner decision; review acceptance does not resolve that owner
decision.

Promotion mode begins only after the owner records explicit dispositions for
all blocking decisions. Revalidate the reviewed candidate, limit changes to
promotion metadata and integrity packaging, and verify the resulting bytes as
one package. Any substantive semantic edit returns to review.

After promotion, use the bounded-preflight reference to define the later E5
admission scope. Do not create a schema, loader, error-code vocabulary,
carrier projection, policy binding, or runtime as part of configuration
promotion.

## Outputs

A complete design and review cycle produces:

1. one machine-readable, versioned Scenario Configuration candidate with a
   declared format identity and explicit execution boundary;
2. one publication-facing configuration design using the public template;
3. one Definition-to-configuration closure record;
4. one independent substantive-review report with routed findings and owner
   decisions; and
5. one concise list of prerequisites for bounded configuration admission.

When separately authorized, atomic promotion additionally produces or
finalizes:

1. `README.md` with identity, scope, files, verification, and next legal stage;
2. `manifest.json` with pinned inputs, artifacts, owner decisions, claim and
   execution boundaries, and artifact hashes; and
3. `SHA256SUMS` covering the promoted payload and decision record.

Until an accepted machine schema exists, the candidate's serialization is
provisional and must remain non-executable. Do not invent an event-local schema
inside this Skill.

## Stop conditions

Stop and request direction when:

- the event question, purpose, horizon, roster, or accepted structural owner
  would change;
- an input identity or integrity value cannot be verified;
- a required value needs unauthorized evidence, held-out access, calibration,
  or known-outcome fitting;
- configuration work would add participant behavior or duplicate scenario,
  mapping, contract, or reducer authority;
- an unknown or disputed value is being replaced with an unsupported numeric
  or categorical default;
- one entity would acquire duplicate actors, authority graphs, relationships,
  private state, or resource owners;
- a sensitivity target is not exact and type-checkable;
- a selected policy is unbound but execution is being authorized;
- a semantic change is proposed during promotion; or
- schema, loader, carrier, policy, runtime, evaluation, or validity work lies
  outside the authorized stage.
