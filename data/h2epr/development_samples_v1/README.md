# H2EPR Cross-Domain Development Samples v1

This fixture contains eight bounded events for early H2EPR-to-MASim design and
testing. Selection favored authentic FinMycelium drafts with useful temporal
coverage, nontrivial participant interaction, manageable file size, and
different simulation patterns across all six H2EPR domains.

The fixture is a development sample, not a benchmark split and not a quality
ranking of H2EPR events.

## Files Per Event

- `event_spec.json`: public event identity, domain, category, and scope.
- `frozen_evidence.json`: the evidence context used by H2EPR reconstruction.
- `draft_epg.json`: byte-identical FinMycelium `FinalEventCascade` output.
- `reference_epg.json`: byte-identical Formal Gold v2 graph, for evaluation
  only.

`sample_manifest.csv` records the selection rationale and structural counts.
`SHA256SUMS` binds every copied JSON and the manifest. The hash file excludes
itself.

## Safety Rules

1. Do not mutate these fixtures in place.
2. Do not expose `reference_epg.json` to simulated agents.
3. Do not treat draft claims as verified facts merely because they occur in a
   FinMycelium output; preserve their evidence and provenance.
4. Write generated scenarios and runtime results outside this directory.
5. Add or replace events only through a new versioned fixture and focused
   commit.
