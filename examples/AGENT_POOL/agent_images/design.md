# Agent Images Design

## Style

All agent icons follow the **icon-focused** style shown in
`icon_focused_contact_sheet.jpg` — circular badges with a flat-design robot
character, domain-specific visual motif, and Chinese label tag. Individual
icon files are stored in `icons/`.

## Mapping: finance/ agents → icons/

The table below maps each agent design spec in `finance/` to its corresponding
icon in `icons/`.

| #  | Agent                                        | Icon                                          | Display Name     | Match Reason                                                         |
|----|----------------------------------------------|-----------------------------------------------|------------------|----------------------------------------------------------------------|
| 1  | `finance/anchored-trader.md`                 | `finance-anchored-trader.png`                 | 固守型投资者     | Anchoring bias → anchor motif                                        |
| 2  | `finance/block-trade-buyer.md`               | `finance-block-trade-buyer.png`               | 信息型投资者     | Opportunistic block buyer → eye motif                                |
| 3  | `finance/concentrated-fund.md`               | `finance-concentrated-fund.png`               | 激进型投资者     | TRS-leveraged fund → lever motif                                     |
| 4  | `finance/contrarian-trader.md`               | `finance-contrarian-trader.png`               | 逆向型投资者     | Mean-reversion contrarian → reverse-arrow motif                      |
| 5  | `finance/disposition-trader.md`              | `finance-disposition-trader.png`              | 保守型投资者     | Disposition effect → loss-curve motif                                |
| 6  | `finance/equity-trader.md`                   | `finance-equity-trader.png`                   | 量化型投资者     | Volatility-managed algo equity → code-grid motif                     |
| 7  | `finance/fundamental-analyst.md`             | `finance-fundamental-analyst.png`             | 研究型投资者     | Conservative analyst → magnifier motif                               |
| 8  | `finance/fundamentalist.md`                  | `finance-fundamentalist.png`                  | 价值型投资者     | Brock-Hommes fundamentalist → diamond motif                          |
| 9  | `finance/historical-anchor.md`               | `finance-historical-anchor.png`               | 历史锚定型投资者 | Historical-price anchoring → anchor+hourglass motif                  |
| 10 | `finance/information-trader.md`              | `finance-information-trader.png`              | 社交型投资者     | Liquidation-signal information → network-chat motif                  |
| 11 | `finance/liquidity-provider.md`              | `finance-liquidity-provider.png`              | 做市型投资者     | Two-sided LP → bid-ask motif                                         |
| 12 | `finance/long-vol-hedger.md`                 | `finance-long-vol-hedger.png`                 | 波动型投资者     | Long-vol crash insurance → wave motif                                |
| 13 | `finance/momentum-trader.md`                 | `finance-momentum-trader.png`                 | 趋势型投资者     | Short-term momentum → trend motif                                    |
| 14 | `finance/noise-trader.md`                    | `finance-noise-trader.png`                    | 随性型投资者     | Random noise → random-dots motif                                     |
| 15 | `finance/prime-broker-delayed-liquidator.md` | `finance-prime-broker-delayed-liquidator.png` | 风控型投资者     | Risk-driven liquidation → gauge motif                                |
| 16 | `finance/prime-broker-first-mover.md`        | `finance-prime-broker-first-mover.png`        | 恐慌型投资者     | First-mover forced selling → down-alert motif                        |
| 17 | `finance/rational-updater.md`                | `finance-rational-updater.png`                | 防御型投资者     | Rational fundamental updater → shield/stability motif                |
| 18 | `finance/short-vol-trader.md`                | `finance-short-vol-trader.png`                | 空头型投资者     | Short-vol carry → short-arrow motif                                  |
| 19 | `finance/slow-adapter.md`                    | `finance-slow-adapter.png`                    | 稳健型投资者     | Slow belief update → pillar/stability motif                          |
| 20 | `finance/trend-follower.md`                  | `finance-trend-follower.png`                  | 跟风型投资者     | CTA/momentum following → nodes/cascade motif                         |
| 21 | `finance/vol-arbitrageur.md`                 | `finance-vol-arbitrageur.png`                 | 套利型投资者     | Volatility mean-reversion arb → scales motif                         |
| 22 | `finance/vol-etn-manager.md`                 | `finance-vol-etn-manager.png`                 | 结构产品型投资者 | Structured product manager → stacked-layers motif                    |
| 23 | `finance/volatility-trader.md`               | `finance-volatility-trader.png`               | 波动管理型投资者 | Vol-targeting/risk-parity → volatility-wave motif                    |
| 24 | `finance/momentum-speculator.md`             | `finance-momentum-speculator.png`             | 追涨型投资者     | Aggressive trend chaser (bubble driver) → rising-arrow trend motif   |
| 25 | `finance/rational-arbitrageur.md`            | `finance-rational-arbitrageur.png`            | 套利修正型投资者 | Value-based short-seller correcting mispricing → balance-scale motif |
| 26 | `finance/fundamental-investor.md`            | `finance-fundamental-investor.png`            | 基本面型投资者   | Slow value anchor → magnifier + diamond motif                        |
| 27 | `finance/leveraged-buyer.md`                 | `finance-leveraged-buyer.png`                 | 杠杆型投资者     | Margin-amplified positions → lever motif                             |
| 28 | `finance/conservative-holder.md`             | `finance-conservative-holder.png`             | 长持型投资者     | Long-term stability holder → pillar/anchor motif                     |
| 29 | `finance/hot-money-funder.md`                | `finance-hot-money-funder.png`                | 热钱型投资者     | Short-term foreign creditor / sudden-stop exit → hot-money / capital-flight motif |
| 30 | `finance/contagion-trader.md`                | `finance-contagion-trader.png`                | 传染型投资者     | Cross-border regional-stress seller → contagion / linked-nodes motif |
| 31 | `finance/imf-rescuer.md`                     | `finance-imf-rescuer.png`                     | 救援型投资者     | Delayed official crisis lender → shield / rescue-flag motif          |
| 32 | `finance/value-contrarian.md`                | `finance-value-contrarian.png`                | 逆向价值型投资者 | Deep-discount patient buyer / crisis contrarian → magnifier + reverse-arrow motif |

## Notes

- Icon file names carry a ``finance-`` domain prefix so the filename encodes
  both the domain (finance) and the agent (e.g. ``finance-anchored-trader.png``).
- Icons are 32 total and map 1:1 to the 32 ``finance/`` agent specs.
- Each ``finance/*.md`` file carries an ``| Icon |`` row in its Design
  Provenance table linking to its icon via relative path.
- 2026-07-05: Icons #9, #22, #23 were regenerated with dedicated motifs
  (previously borrowed from the original taxonomy contact sheet). Old icons
  backed up in the project workspace.
- 2026-07-11: Icons #24–#28 added for the AssetBubble scenario archetypes
  (momentum-speculator, rational-arbitrageur, fundamental-investor,
  leveraged-buyer, conservative-holder) via agent-icon-generation-skill.
  This closes the Step 2 AGENT_POOL icon-resolution gate that the initial
  polish run of `examples/AssetBubble` had missed.
- 2026-07-12: Mapping rows #29–#32 added for the AsianFinancialCrisis
  scenario archetypes (hot-money-funder, contagion-trader, imf-rescuer,
  value-contrarian). Icons were already present in `agent_images/icons/`
  from an earlier session; the mapping-row gap was closed as part of the
  polish-simulation-pipeline Step 2 icon-resolution sub-gate.
- If new agents are added to `finance/`, commission a new icon in the same
  style and name it ``finance-<agent-stem>.png``.
