# Agent Images Design

## Style

All agent icons follow the **icon-focused** style shown in
`icon_focused_contact_sheet.jpg` — circular badges with a flat-design robot
character, domain-specific visual motif, and Chinese label tag. Individual
icon files are stored in `icons/`.

## Mapping: finance/ agents → icons/

The table below maps each agent design spec in `finance/` to its corresponding
icon in `icons/`.

| #  | Agent                                        | Icon                                  | Display Name     | Match Reason                                          |
|----|----------------------------------------------|---------------------------------------|------------------|-------------------------------------------------------|
| 1  | `finance/anchored-trader.md`                 | `anchored-trader.png`                 | 固守型投资者     | Anchoring bias → anchor motif                         |
| 2  | `finance/block-trade-buyer.md`               | `block-trade-buyer.png`               | 信息型投资者     | Opportunistic block buyer → eye motif                 |
| 3  | `finance/concentrated-fund.md`               | `concentrated-fund.png`               | 激进型投资者     | TRS-leveraged fund → lever motif                      |
| 4  | `finance/contrarian-trader.md`               | `contrarian-trader.png`               | 逆向型投资者     | Mean-reversion contrarian → reverse-arrow motif       |
| 5  | `finance/disposition-trader.md`              | `disposition-trader.png`              | 保守型投资者     | Disposition effect → loss-curve motif                 |
| 6  | `finance/equity-trader.md`                   | `equity-trader.png`                   | 量化型投资者     | Volatility-managed algo equity → code-grid motif      |
| 7  | `finance/fundamental-analyst.md`             | `fundamental-analyst.png`             | 研究型投资者     | Conservative analyst → magnifier motif                |
| 8  | `finance/fundamentalist.md`                  | `fundamentalist.png`                  | 价值型投资者     | Brock-Hommes fundamentalist → diamond motif           |
| 9  | `finance/historical-anchor.md`               | `historical-anchor.png`               | 谨慎型投资者     | Historical-price anchoring → ledger motif             |
| 10 | `finance/information-trader.md`              | `information-trader.png`              | 社交型投资者     | Liquidation-signal information → network-chat motif   |
| 11 | `finance/liquidity-provider.md`              | `liquidity-provider.png`              | 做市型投资者     | Two-sided LP → bid-ask motif                          |
| 12 | `finance/long-vol-hedger.md`                 | `long-vol-hedger.png`                 | 波动型投资者     | Long-vol crash insurance → wave motif                 |
| 13 | `finance/momentum-trader.md`                 | `momentum-trader.png`                 | 趋势型投资者     | Short-term momentum → trend motif                     |
| 14 | `finance/noise-trader.md`                    | `noise-trader.png`                    | 随性型投资者     | Random noise → random-dots motif                      |
| 15 | `finance/prime-broker-delayed-liquidator.md` | `prime-broker-delayed-liquidator.png` | 风控型投资者     | Risk-driven liquidation → gauge motif                 |
| 16 | `finance/prime-broker-first-mover.md`        | `prime-broker-first-mover.png`        | 恐慌型投资者     | First-mover forced selling → down-alert motif         |
| 17 | `finance/rational-updater.md`                | `rational-updater.png`                | 防御型投资者     | Rational fundamental updater → shield/stability motif |
| 18 | `finance/short-vol-trader.md`                | `short-vol-trader.png`                | 空头型投资者     | Short-vol carry → short-arrow motif                   |
| 19 | `finance/slow-adapter.md`                    | `slow-adapter.png`                    | 稳健型投资者     | Slow belief update → pillar/stability motif           |
| 20 | `finance/trend-follower.md`                  | `trend-follower.png`                  | 跟风型投资者     | CTA/momentum following → nodes/cascade motif          |
| 21 | `finance/vol-arbitrageur.md`                 | `vol-arbitrageur.png`                 | 套利型投资者     | Volatility mean-reversion arb → scales motif          |
| 22 | `finance/vol-etn-manager.md`                 | `vol-etn-manager.png`                 | 数字资产型投资者 | Structured product manager → hex/structured motif     |
| 23 | `finance/volatility-trader.md`               | `volatility-trader.png`               | 宏观型投资者     | Vol-targeting/risk-parity → globe/macro motif         |

## Unmapped icons (no finance/ agent)

These icons exist in `icons/` but have no corresponding agent spec in `finance/`:

| icons/ file                                   | Display Name | Available for future agents |
|-----------------------------------------------|--------------|-----------------------------|
| BankingCreditAgent.png                        | 信贷型投资者 | Yes                         |
| FramingEffectTrader.png                       | 主题型投资者 | Yes                         |
| OverconfidenceAndRepresentativenessTrader.png | 冒进型投资者 | Yes                         |
| RebalancingStatusQuoInvestor.png              | 平衡型投资者 | Yes                         |
| RetailCoordinatedTrader.png                   | 抱团型投资者 | Yes                         |
| SentimentNarrativeTrader.png                  | 情绪型投资者 | Yes                         |

## Notes

- Icons are 29 total; finance/ agents are 23. The 6 unmapped icons are reserved
  for future agent designs.
- Some mappings are approximate (e.g. #9, #22, #23) because the icon set was
  originally designed for a different agent taxonomy. Visual motifs are
  close-enough for identification purposes.
- If new agents are added to `finance/`, assign them an unmapped icon from the
  table above or commission a new icon in the same style.
