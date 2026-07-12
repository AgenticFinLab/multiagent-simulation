# BlackMonday1987 — Shared-File Change Handoff

This file records changes that need to be applied to files OUTSIDE
`examples/BlackMonday1987/` and `configs/BlackMonday1987/` as part of the
2026-07-12 polish-simulation-pipeline run. Per the concurrency-safety rule,
the polish sub-agent commits only files inside its two scenario roots plus
the three pool profiles it updated in-place under
`examples/AGENT_POOL/finance/`. The main coordinator session is expected to
merge the mapping rows below into
`examples/AGENT_POOL/agent_images/design.md`.

## Pending merge: `examples/AGENT_POOL/agent_images/design.md`

Append the following three rows to the "Mapping: finance/ agents → icons/"
table (after row #32 `value-contrarian`; assign row numbers #33, #34, #35 —
adjust if concurrent merges have taken those slots):

```
| 33 | `finance/portfolio-insurer.md`               | `finance-portfolio-insurer.png`               | 组合保险型投资者 | Delta-hedged sell-into-decline insurance → descending-staircase + shield motif |
| 34 | `finance/index-arbitrageur.md`               | `finance-index-arbitrageur.png`               | 指数套利型投资者 | Futures-cash arbitrage transmission → parallel-lines + double-arrow motif      |
| 35 | `finance/program-trader.md`                  | `finance-program-trader.png`                  | 程式交易型投资者 | Threshold-based feedback selling with convex amplification → cascade-bars + lightning motif |
```

Also append the following bullet to the "Notes" section (keep chronology):

```
- 2026-07-12: Mapping rows #33–#35 added for the BlackMonday1987 scenario
  archetypes (portfolio-insurer, index-arbitrageur, program-trader). Icons
  were generated via agent-icon-generation-skill as part of the
  polish-simulation-pipeline Step 2 icon-completeness HARD GATE. All three
  pool profiles now carry a matching `| Icon |` row in their Design
  Provenance table.
```

## Files installed inside `examples/AGENT_POOL/`

The polish sub-agent has already written the following files inside the
shared pool root because they are logically owned by the BlackMonday1987
polish run and are the counterpart to the mapping rows above. If a merge
conflict arises with concurrent polish runs, these three profiles + three
icons should be preserved:

- `examples/AGENT_POOL/finance/portfolio-insurer.md` — added `| Icon |` row
- `examples/AGENT_POOL/finance/index-arbitrageur.md` — added `| Icon |` row
- `examples/AGENT_POOL/finance/program-trader.md`   — added `| Icon |` row
- `examples/AGENT_POOL/agent_images/icons/finance-portfolio-insurer.png`
- `examples/AGENT_POOL/agent_images/icons/finance-index-arbitrageur.png`
- `examples/AGENT_POOL/agent_images/icons/finance-program-trader.png`

## Verification checklist for the main-session merge

- [ ] Three rows appended to `design.md` mapping table, row numbers
      contiguous with the last existing row.
- [ ] Notes chronology bullet appended.
- [ ] `ls examples/AGENT_POOL/agent_images/icons/finance-{portfolio-insurer,index-arbitrageur,program-trader}.png` returns three files.
- [ ] `grep -l '| Icon |' examples/AGENT_POOL/finance/{portfolio-insurer,index-arbitrageur,program-trader}.md` returns three files.
