# Contributing to H2EPR

## Before changing the tree

State the requested outcome and owning layer. Inspect branch, HEAD, tree,
worktree, index, and unmerged entries. Preserve unrelated user changes. Do not
fetch, merge, publish, install dependencies, read protected inputs, or launch a
simulation unless the task authorizes it.

For event work, record the exact event ID and endpoint. For framework work,
use synthetic fixtures before relying on a current event. Do not make a past
event the implicit template for a general contract.

## Change discipline

- Keep MASim changes in separately scoped base-framework work.
- Keep event vocabulary out of `src/h2epr/`.
- Change the authority layer, then rebuild dependent projections.
- Preserve accepted raw custody and failed attempts.
- Keep one current path per responsibility; use Git for replaced tracked
  bytes and `.local-runtime/` for process records.
- Never hand-edit compiled packages, run output, receipts, or checksum
  inventories to make validation pass.
- Use templates for product shape and Skills for task procedure.
- Add a negative test for each new admission or integrity rule.

## Documentation standard

Reader-facing assets should be usable as a paper appendix. State scope,
authority, inputs, outputs, method, assumptions, limitations, falsification,
failure routing, successor condition, and validation. Write for a new
collaborator who has the repository but not the development conversation.

Prefer direct, natural prose. Avoid build diaries, repeated disclaimers,
generic advice, and defensive “not X but Y” constructions. Boundary language
is still required where it prevents a false scientific or authority claim.

Machine documents require stable IDs, schema versions, canonical self-hashes
where specified, safe relative paths, and exact checksums. Human and machine
assets must refer to the same actor, intent, state, lifecycle, and release
universe.

## Validation sequence

Run the narrowest affected tests first, then:

```bash
PYTHONPATH=projects/h2epr/src python -B -m unittest discover \
  -s projects/h2epr/tests -t projects/h2epr/tests -p 'test_*.py' -v
```

Also check Python compilation, strict JSON, local Markdown links, schema
catalog completeness, Skill package validation, release inventories, and
`git diff --check`. Do not install missing tools merely to broaden validation;
report unavailable optional checks.

For a real Rule event, tests alone are insufficient. Compile twice, run fresh
A/B and identity-probe materializations, verify replay and graph coverage,
publish through the independent verifier, and read the complete output.

## Commit and handoff

Use a small number of coherent commits. Follow the repository convention
`<type>: <lowercase verb subject>`. A commit should leave the tree in a
reviewable state and explain the durable outcome, not the conversation or
temporary phase number.

The handoff records exact Git identity, changed responsibilities, validation,
unavailable checks, current registry state, claim boundary, and next legal
action. Remote synchronization requires separate authorization.
