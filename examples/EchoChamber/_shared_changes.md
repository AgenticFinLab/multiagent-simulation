# EchoChamber — Shared Changes (AGENT_POOL)

Changes made to shared AGENT_POOL assets during polish of `examples/EchoChamber/`.

## design.md mapping rows added

| # | Agent | Icon | Display Name | Match Reason |
|---|-------|------|-------------|--------------|
| 75 | `finance/ideologue.md` | `finance-ideologue.png` | 意见领袖 | Strong opinion holder / in-group amplifier |
| 76 | `finance/conformist.md` | `finance-conformist.png` | 从众型参与者 | Social conformist / group opinion adopter |
| 77 | `finance/critical-thinker.md` | `finance-critical-thinker.png` | 批判型思考者 | Evidence evaluator / group-pressure resister |
| 78 | `finance/bridge-builder.md` | `finance-bridge-builder.png` | 桥梁型参与者 | Cross-group engager / depolarizer |
| 79 | `finance/passive-follower.md` | `finance-passive-follower.png` | 被动型参与者 | Low-engagement drifter / occasional participant |

## Icon PNGs generated

- `examples/AGENT_POOL/agent_images/icons/finance-ideologue.png`
- `examples/AGENT_POOL/agent_images/icons/finance-conformist.png`
- `examples/AGENT_POOL/agent_images/icons/finance-critical-thinker.png`
- `examples/AGENT_POOL/agent_images/icons/finance-bridge-builder.png`
- `examples/AGENT_POOL/agent_images/icons/finance-passive-follower.png`

## Pool profile Icon rows

All 5 profiles already had `| Icon |` rows (placed by batch 3 sub-agents):
- `finance/ideologue.md` — `| Icon | ![](../agent_images/icons/finance-ideologue.png) |`
- `finance/conformist.md` — `| Icon | ![](../agent_images/icons/finance-conformist.png) |`
- `finance/critical-thinker.md` — `| Icon | ![](../agent_images/icons/finance-critical-thinker.png) |`
- `finance/bridge-builder.md` — `| Icon | ![](../agent_images/icons/finance-bridge-builder.png) |`
- `finance/passive-follower.md` — `| Icon | ![](../agent_images/icons/finance-passive-follower.png) |`

## Three-stage match outcome

All 5 EchoChamber archetypes resolve to existing stub profiles under
`examples/AGENT_POOL/finance/` placed by batch 3 sub-agents. Outcome: `reuse`
(stubs exist, Icon rows exist, PNGs now generated, mapping rows added).

## Note on domain placement

EchoChamber is an opinion-dynamics scenario, but batch 3 sub-agents placed
profiles under `finance/` rather than `opinion/`. This is a pre-existing
placement that this polish run preserves (not within polish authority to
relocate cross-domain profiles without user directive).
