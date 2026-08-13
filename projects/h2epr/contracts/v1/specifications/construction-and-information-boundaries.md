# Construction and information boundaries

## Construction identity

The legal identities are:

| State | Target scope | Builder access | Contamination | Eligibility |
|---|---|---|---|---|
| `architecture_generic` | generic only | full draft for generic interfaces | full-draft exposed | architecture demo only |
| `full_draft_target_demo` | target specific | full target draft | full-draft exposed | architecture demo only |
| `prefix_contaminated_demo` | target specific | prefix after target-suffix exposure | full-draft exposed | architecture demo only |
| `prefix_clean_strict` | target specific | prefix allowlist only | clean prefix only | strict eligible |

The six identity fields are propagated through every parent reference and
protocol context. Descendants retain the root construction artifact ID.
Changing the construction object, ID, kind, content hash, or identity tuple
invalidates the lineage even if all descendants are resealed.

## Evidence representation

Construction artifacts store source pointers, file/content hashes, review
state, and narrowly necessary excerpts. They do not embed unrestricted frozen
evidence or whole drafts by default. Runtime values additionally declare
availability, visibility, consumers, and provenance. A construction-only,
unknown, unavailable, or unreviewed provenance entry cannot be promoted to a
runtime-public value.

For strict construction, event-spec fields are deny-by-default. Descriptors,
keywords, and time hints require explicit field-level adjudication. A source
marked `gold_fallback` is mechanically incompatible with strict continuation.

