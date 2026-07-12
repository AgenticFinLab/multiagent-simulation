# EquityPremium — Shared Changes (AGENT_POOL)

This file documents changes made to shared artefacts outside `examples/EquityPremium/`
and `configs/EquityPremium/` during the EquityPremium polish run.

## AGENT_POOL `agent_images/design.md`

- **Rows added**: #71–#74 (4 new mapping rows)
- **Total row count**: 70 → 74
- **Agents mapped**:
  - `finance/myopic-loss-averse-investor.md` → `finance-myopic-loss-averse-investor.png` (短视损失型投资者)
  - `finance/long-horizon-investor.md` → `finance-long-horizon-investor.png` (长期型投资者)
  - `finance/risk-neutral-investor.md` → `finance-risk-neutral-investor.png` (风险中性型投资者)
  - `finance/conservative-investor.md` → `finance-conservative-investor.png` (保守型投资者)
- **Provenance note** added to Notes section (2026-07-16 entry)

## AGENT_POOL `agent_images/icons/`

- **PNGs added** (4 files):
  - `finance-myopic-loss-averse-investor.png`
  - `finance-long-horizon-investor.png`
  - `finance-risk-neutral-investor.png`
  - `finance-conservative-investor.png`

## AGENT_POOL `finance/*.md` Pool Profiles

- No new profiles created (all 5 existed as stubs).
- No profile content was edited (stubs are shared-fabric artefacts; expanding them
  is out of scope for this scenario polish and deferred).
- All 5 profiles already had `Icon` rows pointing to the correct PNG filenames.

## Notes

- `noise-trader.md` already had a full profile and icon (design.md row #14).
- The 4 newly-generated pool profiles remain stubs (`Status: stub` banner).
  Expanding stubs is a shared-fabric task, not a per-scenario polish action.
- Three-stage match outcome for all 5 archetypes: `reuse`.
