# CurrencyCrisis — Shared Changes Required

This file documents changes to shared/pool artefacts that the CurrencyCrisis polish
run requires but that live outside `examples/CurrencyCrisis/` and
`configs/CurrencyCrisis/`.

## AGENT_POOL design.md Mapping Rows

The following 4 mapping rows were added to
`examples/AGENT_POOL/agent_images/design.md` (rows #45–#48):

| # | Agent | Icon | Display Name | Match Reason |
|---|-------|------|--------------|--------------|
| 45 | `finance/speculative-attacker.md` | `finance-speculative-attacker.png` | 投机攻击型投资者 | Reserve-depletion currency attacker |
| 46 | `finance/self-fulfilling-trader.md` | `finance-self-fulfilling-trader.png` | 自我实现型投资者 | Expectation-coordination herding seller |
| 47 | `finance/central-bank-defender.md` | `finance-central-bank-defender.png` | 央行防御型投资者 | Reserve-financed peg defender |
| 48 | `finance/fundamental-hedger.md` | `finance-fundamental-hedger.png` | 基本面对冲型投资者 | Fundamental-value mean-reversion anchor |

Total design.md mapping rows after this change: **48** (was 44).

## AGENT_POOL Icon PNGs Generated

4 new icon PNGs placed in `examples/AGENT_POOL/agent_images/icons/`:

- `finance-speculative-attacker.png`
- `finance-self-fulfilling-trader.png`
- `finance-central-bank-defender.png`
- `finance-fundamental-hedger.png`

The 5th archetype (`noise-trader`) already had a valid PNG and mapping row (#14).

## AGENT_POOL Pool Profile Icon Rows

All 5 pool profiles already had valid `| Icon |` rows pointing to the correct
PNG paths. No profile edits were needed:

- `examples/AGENT_POOL/finance/speculative-attacker.md` — `| Icon | ![](../agent_images/icons/finance-speculative-attacker.png) |`
- `examples/AGENT_POOL/finance/self-fulfilling-trader.md` — `| Icon | ![](../agent_images/icons/finance-self-fulfilling-trader.png) |`
- `examples/AGENT_POOL/finance/central-bank-defender.md` — `| Icon | ![](../agent_images/icons/finance-central-bank-defender.png) |`
- `examples/AGENT_POOL/finance/fundamental-hedger.md` — `| Icon | ![](../agent_images/icons/finance-fundamental-hedger.png) |`
- `examples/AGENT_POOL/finance/noise-trader.md` — `| Icon | ![](../agent_images/icons/finance-noise-trader.png) |`

## Three-Stage Match Outcome

All 5 archetypes resolve to `reuse` (existing pool profiles, no new stubs needed):

| Agent | Pool File | Outcome |
|-------|-----------|---------|
| speculative-attacker | `examples/AGENT_POOL/finance/speculative-attacker.md` | reuse (stub) |
| self-fulfilling-trader | `examples/AGENT_POOL/finance/self-fulfilling-trader.md` | reuse (stub) |
| central-bank-defender | `examples/AGENT_POOL/finance/central-bank-defender.md` | reuse (stub) |
| fundamental-hedger | `examples/AGENT_POOL/finance/fundamental-hedger.md` | reuse (stub) |
| noise-trader | `examples/AGENT_POOL/finance/noise-trader.md` | reuse (full profile) |

No new pool profiles created. No fork/new outcomes. Rule 4 satisfied.
