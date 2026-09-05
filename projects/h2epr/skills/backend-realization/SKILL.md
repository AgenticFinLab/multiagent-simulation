---
name: backend-realization
description: Project accepted participant and scenario semantics into one implemented Rule, LLM, or RuleLLM backend with complete actor coverage and typed failure routing.
---

# Backend realization

Read [references/guide.md](references/guide.md) for backend-specific ownership,
coverage matrices, Rule/LLM/RuleLLM failure contracts, adversarial cases, and
attachment evidence.

## Procedure

1. Pin package, participant/scenario parents, shared configuration, backend
   configuration, decision contract, and backend type.
2. Map every active actor, decision situation, observation, state, permitted
   intent, message, and lifecycle to one implementation entry.
3. Keep environment admission and effects outside the backend.
4. For Rule, use the generic declarative implementation, close every non-no-op
   intent with at least one decision row, use a typed no-op default, keep
   semantic actor prefixes stable under opaque ID perturbation, and deny model
   and network access.
   Use bounded activation windows for reopenable decisions. Test prior receipt
   memory, changed-information retry, acceptance without duplicate submission,
   and expiry; reserve an exact coordinate for a justified time-fixed choice.
5. For LLM, close prompt projection, structured output, parser, retry,
   unavailability, timeout, malformed output, and provenance.
6. For RuleLLM, close proposal, hard constraints, bounded repair, rejection,
   and declared safe fallback without hidden backend substitution.
7. Run backend-interface, actor/action parity, non-no-op coverage, negative
   payload, authority, lifecycle, generated-ID, and implementation-source hash
   tests. Package admission, not backend setup alone, verifies source bytes.
8. Publish realization manifest and binding only after implementation exists.

Stop on missing coverage, silent fallback, model/network use in Rule, world
mutation by a backend, or any change to the shared package needed only for one
backend.
