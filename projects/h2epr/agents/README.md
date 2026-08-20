# H2EPR Agents

This directory is the mutable, tracked research surface for H2EPR Agent
Definitions and their derived executable mappings. It borrows MASim's useful
separation between Markdown definitions and Python implementations, while
keeping the H2EPR profiles event-bound until reuse is demonstrated.

The pilot tests whether role, legal information, persistent state, authority,
procedure, and intent/result separation can drive auditable behavior. It does
not claim historical calibration, cross-event reuse, LLM readiness, or a
complete reconstruction of the Panic of 1907.

## Authority map

| Asset | Owns | Does not own |
|---|---|---|
| Agent Definition Markdown | representation, legal information semantics, decision commitments, intent meaning, assumptions, falsifiers | source status, actual world values, wire schemas, adjudicated results |
| `evidence-ledger.md` | adopted source locator/hash, claim status, exposure and allowed use | behavior rules or runtime values |
| `micro-situation.md` | pilot boundary, institutional facts, observation delivery, business-process and adjudication assumptions | participant decision policy |
| `defines/<event>/binding-catalog.json` | derived, executable mapping of Definition identity, observation domains, commitment-specific inputs, intent parameters, and intent envelopes | independent behavior semantics |
| machine contracts | encoding, type, shape, serialization and versioning | historical or behavioral claims |
| environment/reducer | authoritative business state, admissibility, effects and results | participant intent |

The Markdown Definitions are canonical for this pilot. `binding-catalog.json`
must match their content SHA-256 values, declared commitment IDs, semantic
observation/intent contracts, and commitment mappings. A binding is invalid
after the Markdown changes until it is regenerated and reviewed.

## Layout and naming

```text
agents/
├── README.md
├── agent-definition-template.md
└── defines/
    └── panic_1907/
        ├── knickerbocker-trust.md
        ├── new-york-clearing-house.md
        ├── evidence-ledger.md
        ├── micro-situation.md
        └── binding-catalog.json
```

- Definition filenames are lowercase kebab-case, matching the MASim profile
  convention. Python modules remain snake_case under `src/h2epr/agents/`.
- The event directory follows the existing `configs/panic_1907/` identifier.
- Only the role Markdown files are Agent Definitions. The evidence ledger,
  micro-situation, and binding catalog are adjacent event support assets with
  separate authority.
- H2EPR framework Skills are flat Markdown files under `skills/` unless a
  genuinely multi-file workflow later justifies a directory.

## Current assets

- [`agent-definition-template.md`](agent-definition-template.md): provisional
  method, not a stable schema.
- [`defines/panic_1907/evidence-ledger.md`](defines/panic_1907/evidence-ledger.md): adopted evidence and
  bounded unresolved gaps.
- [`defines/panic_1907/micro-situation.md`](defines/panic_1907/micro-situation.md): shared
  three-step pilot boundary.
- [`defines/panic_1907/knickerbocker-trust.md`](defines/panic_1907/knickerbocker-trust.md) and
  [`defines/panic_1907/new-york-clearing-house.md`](defines/panic_1907/new-york-clearing-house.md):
  the two mutable candidate Definitions.

All historical outcomes used here are already exposed. This iteration is
construction and semantic falsification work, not held-out validation.

## Lightweight iteration lifecycle

The tracked paths above contain only the current accepted candidate. Do not add
`-v2`, `-old`, date-suffixed copies, or an archive directory beside them.

1. Explore and review drafts below the ignored `.local-runtime/h2epr-simulation/working/`
   area. Store adopted raw sources and sealed evidence in its evidence area.
2. Form an immutable local review snapshot with source hashes, candidate hashes,
   test results, and unresolved questions. Rejected alternatives remain local.
3. Promote one accepted candidate atomically to the stable tracked paths; update
   Definition identity/version, binding hashes, code, tests, and concise current
   documentation together.
4. Commit that coherent state. Git history is the authoritative history of
   accepted repository versions; `.local-runtime` preserves richer research and
   review history that should not burden the public tree.

Contract successors or intentionally supported public release lines may coexist
when compatibility requires it. Mutable Agent drafts do not receive that
exception merely to retain history.
