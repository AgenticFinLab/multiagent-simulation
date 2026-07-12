# CreditCycle — Shared Changes Required

## AGENT_POOL Changes (written in-place during this polish run)

### Icon PNGs Generated

| # | File | Agent |
|---|---|---|
| 1 | `examples/AGENT_POOL/agent_images/icons/finance-pro-cyclical-lender.png` | pro-cyclical-lender |
| 2 | `examples/AGENT_POOL/agent_images/icons/finance-minsky-borrower.png` | minsky-borrower |
| 3 | `examples/AGENT_POOL/agent_images/icons/finance-counter-cyclical-lender.png` | counter-cyclical-lender |
| 4 | `examples/AGENT_POOL/agent_images/icons/finance-value-investor.png` | value-investor |

### design.md Mapping Rows Added

Rows #54-#57 appended to `examples/AGENT_POOL/agent_images/design.md`:

| # | Agent | Icon | Display Name |
|---|---|---|---|
| 54 | `finance/pro-cyclical-lender.md` | `finance-pro-cyclical-lender.png` | 顺周期贷方 |
| 55 | `finance/minsky-borrower.md` | `finance-minsky-borrower.png` | 明斯基借方 |
| 56 | `finance/counter-cyclical-lender.md` | `finance-counter-cyclical-lender.png` | 逆周期贷方 |
| 57 | `finance/value-investor.md` | `finance-value-investor.png` | 价值型投资者 |

### Pool Profile Status

All 5 CreditCycle archetypes resolved as `reuse` against existing pool profiles:
- `finance/pro-cyclical-lender.md` — stub (expansion deferred, shared-fabric ownership)
- `finance/minsky-borrower.md` — stub (expansion deferred, shared-fabric ownership)
- `finance/counter-cyclical-lender.md` — stub (expansion deferred, shared-fabric ownership)
- `finance/value-investor.md` — stub (expansion deferred, shared-fabric ownership)
- `finance/noise-trader.md` — full profile (no changes needed)

No new AGENT_POOL stub profiles were created. No fork or new outcomes.

## Notes

- The noise-trader pool profile already had a full spec + icon (row #14) from a previous session.
- The 4 stub profiles already had `Icon` rows referencing the expected PNG path; the PNGs were the only missing asset.
- design.md total updated from 53 to 57 rows.
