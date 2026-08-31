# Samsung--regional--outlet--consumer bounded binding v0.1

Status: `PASS_BOUNDED_CONFORMANCE_SCOPE`

This release projects one selected H2EPR-0481 remedy lineage to Contracts V1.
It pins the accepted v0.2 Scenario Configuration and admission receipt, Roster,
consolidated mapping, semantic inventory, four participant products, and five
implementation surfaces.

## Bound lineage

The positive carrier sequence contains seven participant intents:

1. Samsung directs a bounded product-flow posture to its Singapore regional
   unit.
2. Samsung announces a proposed replacement program to the same unit.
3. The regional unit asks one outlet unit to coordinate a local response.
4. The regional unit proposes qualified local remedy terms.
5. The outlet proposes a local product posture; this is an ActionIntent to the
   product-flow process and has no participant MessageIntent.
6. After a separately produced posture result and delivered offer, the consumer
   requests exchange or refund from the outlet.
7. The outlet responds to that exact delivered request without claiming
   eligibility, stock, handoff, payment, or completion.

The three configuration routes become four directed carriers because the
outlet--consumer route is used for both request and response. Reusing a route
does not create another configuration route.

## Scope and files

The binding derives the complete eight-product coverage and verifies all 20
observations exposed by the four selected products. It binds seven of their 20
intent placements. Time, information, route, authority, product, remedy, and
lifecycle policies are available only to this slice; hazard and public-action
policies remain unbound.

- `binding.json` fixes actors, observations, actions, parameters, routes, and
  policy bindings.
- `manifest.json` pins upstream and implementation identities and carries a
  canonical self-hash.
- `src/h2epr/scenarios/samsung_note7_battery_recall/lineage_v0_1/` contains the
  strict loader, projections, participant policies, and bounded environment.
- `tests/agents/test_samsung_note7_lineage_binding.py` owns focused carrier and
  negative-conformance checks.
- `SHA256SUMS` covers the release-owned files.

## Boundary

Ticks zero through fourteen are synthetic, fully exposed conformance
coordinates. They are not historical timing, a complete event execution, a
behavioral calibration, a simulation, or an evaluation. The accepted Scenario
Configuration remains non-executable.

After installing H2EPR, run:

```bash
python -B -m pytest -p no:cacheprovider \
  projects/h2epr/tests/agents/test_samsung_note7_lineage_binding.py
```

The next legal action is bounded deterministic lineage conformance and replay.
