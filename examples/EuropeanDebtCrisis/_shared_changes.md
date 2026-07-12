# EuropeanDebtCrisis — Shared Changes Required

## AGENT_POOL design.md Mapping Rows

Added mapping rows #63–#67 to `examples/AGENT_POOL/agent_images/design.md`:

| # | Agent | Icon | Display Name | Match Reason |
|---|---|---|---|---|
| 63 | `finance/periphery-bond-seller.md` | `finance-periphery-bond-seller.png` | 主权债抛售型投资者 | Self-fulfilling sovereign crisis seller |
| 64 | `finance/creditor-panicker.md` | `finance-creditor-panicker.png` | 恐慌撤资型投资者 | Sovereign-bank doom-loop funding withdrawal |
| 65 | `finance/core-bond-buyer.md` | `finance-core-bond-buyer.png` | 核心债避险型投资者 | Flight-to-quality safe-haven buyer |
| 66 | `finance/ecb-intervenor.md` | `finance-ecb-intervenor.png` | 央行干预型投资者 | Central-bank backstop buyer |
| 67 | `finance/hedged-fund.md` | `finance-hedged-fund.png` | 对冲套利型投资者 | Relative-value spread arbitrageur |

## Icon PNGs Added

5 PNGs generated and placed at `examples/AGENT_POOL/agent_images/icons/`:
- `finance-periphery-bond-seller.png`
- `finance-creditor-panicker.png`
- `finance-core-bond-buyer.png`
- `finance-ecb-intervenor.png`
- `finance-hedged-fund.png`

## Pool Profile Icon Rows

All 5 profiles already had `Icon` rows pointing to the correct paths (line 52 in each stub profile). No edits needed to pool profiles themselves.

## Note on Stub Profiles

All 5 pool profiles (`examples/AGENT_POOL/finance/{periphery-bond-seller,creditor-panicker,core-bond-buyer,ecb-intervenor,hedged-fund}.md`) remain as auto-generated stubs. Expanding stubs to full profiles is a shared-fabric task owned by the pool, not by this scenario polish. No new profiles were created (three-stage match = `reuse` for all 5).
