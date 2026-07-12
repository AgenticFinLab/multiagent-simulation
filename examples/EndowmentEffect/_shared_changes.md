# EndowmentEffect — Shared Changes Required

This file documents changes to shared AGENT_POOL artefacts made during the
EndowmentEffect polish run that affect the broader repository.

## AGENT_POOL design.md Mapping Rows

Added mapping rows #68-70 to `examples/AGENT_POOL/agent_images/design.md`:

| # | Agent | Icon | Display Name | Match Reason |
|---|-------|------|--------------|--------------|
| 68 | `finance/endowed-holder.md` | `finance-endowed-holder.png` | 禀赋型投资者 | Ownership-attachment endowment holder |
| 69 | `finance/status-quo-seller.md` | `finance-status-quo-seller.png` | 惯性型投资者 | Status-quo-biased inertia seller |
| 70 | `finance/new-buyer.md` | `finance-new-buyer.png` | 新进型投资者 | Unbiased new market entrant |

## Icon PNGs Generated

- `examples/AGENT_POOL/agent_images/icons/finance-endowed-holder.png` — NEW
- `examples/AGENT_POOL/agent_images/icons/finance-status-quo-seller.png` — NEW
- `examples/AGENT_POOL/agent_images/icons/finance-new-buyer.png` — NEW

## Pool Profile Changes

Pool profiles `finance/endowed-holder.md`, `finance/status-quo-seller.md`, and
`finance/new-buyer.md` already had correct `Icon` rows prior to this polish run.
No changes to pool profile content were required (profiles remain in `stub` status —
shared-fabric ownership, not expanded during this scenario polish).

## design.md Total Count

Previous: 67 mapping rows.
After: 70 mapping rows.
