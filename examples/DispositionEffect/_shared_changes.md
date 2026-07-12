# DispositionEffect — Shared Changes Required

## AGENT_POOL Changes (applied in this polish run)

### Icon Generation (Step 2 §6.3 gate)

Five AGENT_POOL profiles used by this scenario had **missing icon PNGs** and
**missing `design.md` mapping rows**:

| Agent Profile | Icon File | design.md Row | Status |
|---|---|---|---|
| `finance/disposition-investor.md` | `finance-disposition-investor.png` | #58 | CREATED (was pointing to wrong file `disposition-trader.png`) |
| `finance/rational-investor.md` | `finance-rational-investor.png` | #59 | CREATED (was pointing to wrong file `rational-updater.png`) |
| `finance/tax-aware-investor.md` | `finance-tax-aware-investor.png` | #60 | CREATED |
| `finance/index-holder.md` | `finance-index-holder.png` | #61 | CREATED |
| `finance/institutional-investor.md` | `finance-institutional-investor.png` | #62 | CREATED |

### Profile Icon Row Corrections

- `disposition-investor.md`: Icon row changed from `finance-disposition-trader.png` to `finance-disposition-investor.png`
- `rational-investor.md`: Icon row changed from `finance-rational-updater.png` to `finance-rational-investor.png`

### design.md Updates

- Mapping rows #58-#62 added
- Total icon count updated: 57 -> 62
- Provenance note added (2026-07-14)

## Three-Stage Match Results

All five archetypes resolve to existing AGENT_POOL profiles via Stage 1
filename scan. Outcome: `reuse` for all five agents. No new pool profiles
or forks were needed.

| §4.N Agent | Pool Profile | Match Outcome |
|---|---|---|
| DispositionInvestor | `finance/disposition-investor.md` | reuse |
| RationalInvestor | `finance/rational-investor.md` | reuse |
| TaxAwareInvestor | `finance/tax-aware-investor.md` | reuse |
| IndexHolder | `finance/index-holder.md` | reuse |
| InstitutionalInvestor | `finance/institutional-investor.md` | reuse |
