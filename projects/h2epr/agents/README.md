# H2EPR Agents

This directory is the mutable, tracked research surface for H2EPR Agent
Definitions and their supporting evidence. It borrows MASim's useful
separation between Markdown definitions and Python implementations, while
keeping H2EPR profiles event-bound until reuse is demonstrated.

The current two-role study examines whether institutional role,
participant-available information, persistent state, authority, procedure, and
intent/result separation can support auditable behavior. Its scope is the
exploratory reconstruction of a bounded Panic of 1907 situation; calibration,
cross-event reuse, and additional execution approaches require separate work.

## Authority map

| Asset | Owns | Does not own |
|---|---|---|
| Agent Definition Markdown | representation, participant-available information semantics, decision commitments, intent meaning, assumptions, falsifiers | source status, actual world values, wire schemas, adjudicated results |
| `source-register.md` | adopted source identity, locator, byte hash, cited passages and source limitations | claim adjudication or behavior rules |
| `evidence-ledger.md` | claim status, participant availability, exposure, allowed use and withdrawal consequence | behavior rules or runtime values |
| `decision-situations.md` | shared research situations and perturbations | participant policy or executable scenario state |
| accepted binding specification | derived mapping of Definition identity, observations, commitments and intents | independent behavior semantics or executable conformance |
| machine contracts | encoding, type, shape, serialization and versioning | historical or behavioral claims |
| environment/reducer | authoritative business state, admissibility, effects and results | participant intent |

The Markdown Definitions are canonical for participant behavior. A binding is
valid only for the exact Definition hashes, commitment inventory, observation
and intent semantics it was reviewed against. The current `0.2.1` Definitions
have an accepted, non-executable V1 mapping specification; an executable
binding remains future work.

## Layout and naming

```text
agents/
├── README.md
├── agent-definition-template.md
├── bindings/
│   └── panic_1907/
└── defines/
    └── panic_1907/
        ├── README.md
        ├── decision-situations.md
        ├── evidence-ledger.md
        ├── knickerbocker-trust.md
        ├── new-york-clearing-house.md
        └── source-register.md
```

- Definition filenames are lowercase kebab-case, matching the MASim profile
  convention. Python modules remain snake_case under `src/h2epr/agents/`.
- The event directory follows the existing `configs/panic_1907/` identifier.
- Only the role Markdown files are Agent Definitions. The source register,
  evidence ledger, and decision-situation portfolio are adjacent research
  assets with separate authority.
- H2EPR framework Skills use one directory per workflow. `SKILL.md` is the
  entry point; detailed research and review guidance lives in `references/`.
  The current catalog is documented in [`../skills/README.md`](../skills/README.md).

## Current assets

- [`agent-definition-template.md`](agent-definition-template.md): ten-module
  working template for event-bound scholarly and behavioral Definitions.
- [`defines/panic_1907/README.md`](defines/panic_1907/README.md): current event assets,
  authority boundaries, and implementation status.
- [`defines/panic_1907/source-register.md`](defines/panic_1907/source-register.md) and
  [`defines/panic_1907/evidence-ledger.md`](defines/panic_1907/evidence-ledger.md): adopted sources,
  claim adjudication, exposure, and bounded unresolved gaps.
- [`defines/panic_1907/decision-situations.md`](defines/panic_1907/decision-situations.md): shared role-comparison
  situations and falsification perturbations.
- [`defines/panic_1907/knickerbocker-trust.md`](defines/panic_1907/knickerbocker-trust.md) and
  [`defines/panic_1907/new-york-clearing-house.md`](defines/panic_1907/new-york-clearing-house.md):
  the current `0.2.1` reference Definitions.
- [`bindings/panic_1907/`](bindings/panic_1907/): the accepted, non-executable
  Definition-to-V1 mapping, scenario/lifecycle specification, 21-intent
  registry, and cross-object conformance rules.

All historical outcomes used here are already exposed. This iteration is
construction and semantic falsification work, not held-out validation.

## Lightweight iteration lifecycle

The tracked paths above contain only the current accepted candidate. Do not add
`-v2`, `-old`, date-suffixed copies, or an archive directory beside them.

1. Explore and review drafts below the ignored `.local-runtime/h2epr-simulation/working/`
   area. Store adopted raw sources and sealed evidence in its evidence area.
2. Form an immutable local review snapshot with source hashes, candidate hashes,
   test results, and unresolved questions. Rejected alternatives remain local.
3. Perform a Definition-to-binding impact review before promotion. Update an
   actually conforming mapping atomically, or explicitly retire/freeze an old
   mapping rather than relabeling it as current.
4. Commit that coherent state. Git history is the authoritative history of
   accepted repository versions; `.local-runtime` preserves richer research and
   review history that should not burden the public tree.

Contract successors or intentionally supported public release lines may coexist
when compatibility requires it. Mutable Agent drafts do not receive that
exception merely to retain history.

The `0.1.0-dev` three-tick path is retained under
[`tests/fixtures/agents/panic_1907/minimal_binding_v0_1/`](../tests/fixtures/agents/panic_1907/minimal_binding_v0_1/)
as a frozen engineering fixture. It is not a current Definition line and cannot
be cited as conformance evidence for version `0.2.1`.
