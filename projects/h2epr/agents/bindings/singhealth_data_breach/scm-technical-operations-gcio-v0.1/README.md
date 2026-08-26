# SCM technical--operations--GCIO bounded binding v0.1

This release projects one selected H2EPR-0616 lineage to Contracts V1. It
identifies the exact Scenario Configuration, admission receipt, Roster release,
consolidated mapping, three participant products, and implementation surfaces
used by the projection.

## Bound lineage

The carrier sequence contains four participant intents:

1. the SCM application/database technical unit shares a source-preserving
   technical finding with the application/SCM operational unit;
2. the operational unit requests a named fact verification from that technical
   unit;
3. after a separately produced and delivered verification result, the
   operational unit escalates a qualified account to the SingHealth GCIO; and
4. the GCIO, acting in the IHiS service-lead capacity, requests a scoped
   clarification from the operational unit.

The accepted configuration supplies two bidirectional exact-address routes.
The binding projects them into four directed message carriers so each sender,
recipient, capacity, and delivery history remains explicit. A directed carrier
does not create another configuration route.

## Semantic and causal boundary

The release derives the complete nine-product catalog from the exact Roster
release and checks it against the accepted semantic inventory before selecting
the three capabilities. It binds all 17 observations exposed by those products
and only four of their 16 semantic intents.

Time, information, technical verification, route, authority, and lifecycle
policies are implemented only where the four-intent lineage requires them.
Coordination, incident, and notification policies remain outside this binding.
Message issue, delivery, acknowledgement, verification request, verification
result, escalation, recipient interpretation, and later response remain
different objects or stages.

The fixed ticks zero through eight form a synthetic positive conformance case.
They are not a historical schedule, parameter fit, complete event execution,
or evaluation result. The accepted Scenario Configuration continues to list
all nine policy selections as unbound and remains non-executable.

## Integrity and files

`manifest.json` records the binding, implementation surfaces, and upstream
identities. Its `manifest_sha256` is a canonical self-hash; consumers also
provide the expected raw manifest hash. `SHA256SUMS` covers the files owned by
this release directory.

- `binding.json` declares the selected actors, capacities, observations,
  actions, directed carriers, and policy bindings.
- `manifest.json` fixes implementation and upstream identities.
- `src/h2epr/scenarios/singhealth_data_breach/lineage_v0_1/` contains the
  strict loader, carrier projection, participant policies, and bounded
  environment policies.
- `tests/agents/test_singhealth_data_breach_lineage_binding.py` checks loading,
  Contracts V1 projection, causal separation, and focused rejection cases.

From the repository root, run:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/agents/test_singhealth_data_breach_lineage_binding.py

cd projects/h2epr/agents/bindings/singhealth_data_breach/scm-technical-operations-gcio-v0.1
sha256sum --check SHA256SUMS
```
