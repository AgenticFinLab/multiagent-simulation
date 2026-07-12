# DotComBubble — Shared Changes Required

## AGENT_POOL `design.md` Mapping Rows

The DotComBubble polish run added 5 mapping rows to
`examples/AGENT_POOL/agent_images/design.md` (rows #49–#53), bringing the total
from 48 to 53.

| Row | Agent Profile | Icon File | Display Name |
|-----|---------------|-----------|--------------|
| 49 | `finance/new-economy-evangelist.md` | `finance-new-economy-evangelist.png` | 新经济布道者 |
| 50 | `finance/ipo-flipper.md` | `finance-ipo-flipper.png` | 打新型投资者 |
| 51 | `finance/momentum-follower.md` | `finance-momentum-follower.png` | 跟风型投资者 |
| 52 | `finance/skeptical-value-investor.md` | `finance-skeptical-value-investor.png` | 价值怀疑型投资者 |
| 53 | `finance/short-seller.md` | `finance-short-seller.png` | 做空型投资者 |

## Icon PNGs Added

5 PNG files placed in `examples/AGENT_POOL/agent_images/icons/`:
- `finance-new-economy-evangelist.png`
- `finance-ipo-flipper.png`
- `finance-momentum-follower.png`
- `finance-skeptical-value-investor.png`
- `finance-short-seller.png`

## Pool Profile Status

All 5 pool profiles already exist as stubs with `Icon` rows pointing to the
correct filenames. No new pool profiles were created (rule 4 respected). The
stubs remain owned by the shared pool fabric — expanding them is out of
DotComBubble polish scope.

## Three-Stage Match Outcome

All 5 DotComBubble archetypes resolve to `reuse` against existing stub profiles
in `examples/AGENT_POOL/finance/`:
- `new-economy-evangelist.md` → reuse (stub)
- `ipo-flipper.md` → reuse (stub)
- `momentum-follower.md` → reuse (stub)
- `skeptical-value-investor.md` → reuse (stub)
- `short-seller.md` → reuse (stub)

No `new` or `fork` outcomes — no halt required per rule 4.
