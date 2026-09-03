---
name: benchmark-input-admission
description: Admit exactly the declared H2EPR dataset files and publish a hash-closed Source Profile without Reference or external research.
---

# Benchmark input admission

Read [references/guide.md](references/guide.md) before performing an admission.
It defines the preflight record, direct-path checks, exposure classifications,
worked failures, and the exact handoff evidence. This entry point supplies the
execution order.

## Read first

Read `BENCHMARK_PROTOCOL.md`, `templates/source-profile/README.md`, and
`schemas/source-profile.schema.json`. Receive an exact event ID; do not find
one by browsing protected directories.

## Procedure

1. Record branch, HEAD, tree, worktree, index, unmerged state, event ID, slug,
   exposure mode, and authorized endpoint.
2. Resolve only `event_spec.json`, `frozen_evidence.json`, and `draft_epg.json`
   beneath the declared data root.
3. Reject absolute paths, traversal, symlinks, duplicate logical names, wrong
   event IDs, parse failure, or any additional input.
4. Validate event-spec identity and the exposed Draft's stage, episode,
   participant, action, name, type, role, and timestamp wrappers without
   discovering siblings.
5. Record byte size and SHA-256 before semantic work.
6. State that Draft/frozen records are dataset material, not independently
   verified history. Record known shape or identifier defects without repair.
7. Publish the required discovery policy, dataset limitations, prohibited
   input classes, claim exclusions, and Source Profile self-hash; validate the
   exact three-name sequence against the current schema.

## Stop conditions

Stop on protected exposure, source drift, implicit sibling discovery, an
undeclared file, event mismatch, or a request to search external sources.

## Completion record

Report profile identity, three paths/hashes/sizes, exposure, eligibility,
prohibited inputs, validation, and next legal action.
