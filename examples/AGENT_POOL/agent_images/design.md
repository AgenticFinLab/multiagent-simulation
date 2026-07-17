# Agent Images Design

## Style

All agent icons follow the **icon-focused** style shown in
`icon_focused_contact_sheet.jpg` — circular badges with a flat-design robot
character, domain-specific visual motif, and Chinese label tag. Individual
icon files are stored in `icons/`.

## Mapping: finance/ & opinion/ agents → icons/

The table below maps each agent design spec in `finance/` and `opinion/` to its
corresponding icon in `icons/`. Rows marked **MISSING** have no icon PNG on disk.

| #  | Agent                                        | Icon                                          | Display Name         | Match Reason                                                                                            |
|----|----------------------------------------------|-----------------------------------------------|----------------------|---------------------------------------------------------------------------------------------------------|
| 1  | `finance/anchored-trader.md`                 | `finance-anchored-trader.png`                 | 固守型投资者         | Anchoring bias → anchor motif                                                                           |
| 2  | `finance/block-trade-buyer.md`               | `finance-block-trade-buyer.png`               | 信息型投资者         | Opportunistic block buyer → eye motif                                                                   |
| 3  | `finance/concentrated-fund.md`               | `finance-concentrated-fund.png`               | 激进型投资者         | TRS-leveraged fund → lever motif                                                                        |
| 4  | `finance/contrarian-trader.md`               | `finance-contrarian-trader.png`               | 逆向型投资者         | Mean-reversion contrarian → reverse-arrow motif                                                         |
| 5  | `finance/disposition-trader.md`              | `finance-disposition-trader.png`              | 保守型投资者         | Disposition effect → loss-curve motif                                                                   |
| 6  | `finance/equity-trader.md`                   | `finance-equity-trader.png`                   | 量化型投资者         | Volatility-managed algo equity → code-grid motif                                                        |
| 7  | `finance/fundamental-analyst.md`             | `finance-fundamental-analyst.png`             | 研究型投资者         | Conservative analyst → magnifier motif                                                                  |
| 8  | `finance/fundamentalist.md`                  | `finance-fundamentalist.png`                  | 价值型投资者         | Brock-Hommes fundamentalist → diamond motif                                                             |
| 9  | `finance/historical-anchor.md`               | `finance-historical-anchor.png`               | 历史锚定型投资者     | Historical-price anchoring → anchor+hourglass motif                                                     |
| 10 | `finance/information-trader.md`              | `finance-information-trader.png`              | 社交型投资者         | Liquidation-signal information → network-chat motif                                                     |
| 11 | `finance/liquidity-provider.md`              | `finance-liquidity-provider.png`              | 做市型投资者         | Two-sided LP → bid-ask motif                                                                            |
| 12 | `finance/long-vol-hedger.md`                 | `finance-long-vol-hedger.png`                 | 波动型投资者         | Long-vol crash insurance → wave motif                                                                   |
| 13 | `finance/momentum-trader.md`                 | `finance-momentum-trader.png`                 | 趋势型投资者         | Short-term momentum → trend motif                                                                       |
| 14 | `finance/noise-trader.md`                    | `finance-noise-trader.png`                    | 随性型投资者         | Random noise → random-dots motif                                                                        |
| 15 | `finance/prime-broker-delayed-liquidator.md` | `finance-prime-broker-delayed-liquidator.png` | 风控型投资者         | Risk-driven liquidation → gauge motif                                                                   |
| 16 | `finance/prime-broker-first-mover.md`        | `finance-prime-broker-first-mover.png`        | 恐慌型投资者         | First-mover forced selling → down-alert motif                                                           |
| 17 | `finance/rational-updater.md`                | `finance-rational-updater.png`                | 防御型投资者         | Rational fundamental updater → shield/stability motif                                                   |
| 18 | `finance/short-vol-trader.md`                | `finance-short-vol-trader.png`                | 空头型投资者         | Short-vol carry → short-arrow motif                                                                     |
| 19 | `finance/slow-adapter.md`                    | `finance-slow-adapter.png`                    | 稳健型投资者         | Slow belief update → pillar/stability motif                                                             |
| 20 | `finance/trend-follower.md`                  | `finance-trend-follower.png`                  | 跟风型投资者         | CTA/momentum following → nodes/cascade motif                                                            |
| 21 | `finance/vol-arbitrageur.md`                 | `finance-vol-arbitrageur.png`                 | 套利型投资者         | Volatility mean-reversion arb → scales motif                                                            |
| 22 | `finance/vol-etn-manager.md`                 | `finance-vol-etn-manager.png`                 | 结构产品型投资者     | Structured product manager → stacked-layers motif                                                       |
| 23 | `finance/volatility-trader.md`               | `finance-volatility-trader.png`               | 波动管理型投资者     | Vol-targeting/risk-parity → volatility-wave motif                                                       |
| 24 | `finance/momentum-speculator.md`             | `finance-momentum-speculator.png`             | 追涨型投资者         | Aggressive trend chaser (bubble driver) → rising-arrow trend motif                                      |
| 25 | `finance/rational-arbitrageur.md`            | `finance-rational-arbitrageur.png`            | 套利修正型投资者     | Value-based short-seller correcting mispricing → balance-scale motif                                    |
| 26 | `finance/fundamental-investor.md`            | `finance-fundamental-investor.png`            | 基本面型投资者       | Slow value anchor → magnifier + diamond motif                                                           |
| 27 | `finance/leveraged-buyer.md`                 | `finance-leveraged-buyer.png`                 | 杠杆型投资者         | Margin-amplified positions → lever motif                                                                |
| 28 | `finance/conservative-holder.md`             | `finance-conservative-holder.png`             | 长持型投资者         | Long-term stability holder → pillar/anchor motif                                                        |
| 29 | `finance/hot-money-funder.md`                | `finance-hot-money-funder.png`                | 热钱型投资者         | Short-term foreign creditor / sudden-stop exit → hot-money / capital-flight motif                       |
| 30 | `finance/contagion-trader.md`                | `finance-contagion-trader.png`                | 传染型投资者         | Cross-border regional-stress seller → contagion / linked-nodes motif                                    |
| 31 | `finance/imf-rescuer.md`                     | `finance-imf-rescuer.png`                     | 救援型投资者         | Delayed official crisis lender → shield / rescue-flag motif                                             |
| 32 | `finance/value-contrarian.md`                | `finance-value-contrarian.png`                | 逆向价值型投资者     | Deep-discount patient buyer / crisis contrarian → magnifier + reverse-arrow motif                       |
| 33 | `finance/recent-event-overweighter.md`       | `finance-recent-event-overweighter.png`       | 近期事件偏好投资者   | Recency salience / overweighted latest bar → dumbbell-on-recent-bar motif                               |
| 34 | `finance/media-influenced-trader.md`         | `finance-media-influenced-trader.png`         | 媒体影响投资者       | Media narrative amplification → megaphone-to-price-arrow motif                                          |
| 35 | `finance/portfolio-insurer.md`               | `finance-portfolio-insurer.png`               | 组合保险型投资者     | Delta-hedged sell-into-decline insurance → descending-staircase + shield motif                          |
| 36 | `finance/index-arbitrageur.md`               | `finance-index-arbitrageur.png`               | 指数套利型投资者     | Futures-cash arbitrage transmission → parallel-lines + double-arrow motif                               |
| 37 | `finance/program-trader.md`                  | `finance-program-trader.png`                  | 程式交易型投资者     | Threshold-based feedback selling with convex amplification → cascade-bars + lightning motif             |
| 38 | `finance/carry-trader.md`                    | `finance-carry-trader.png`                    | 套息型投资者         | Leveraged FX carry accumulator / crash-risk exposure → currency-arrow motif                             |
| 39 | `finance/leveraged-carry-fund.md`            | `finance-leveraged-carry-fund.png`            | 杠杆套息基金型投资者 | Stop-loss-triggered forced-liquidation hedge fund → lever + stop-loss + margin-call bell motif          |
| 40 | `finance/funding-currency-buyer.md`          | `finance-funding-currency-buyer.png`          | 避险货币买入型投资者 | Safe-haven / repatriation JPY-CHF buyer → shield + inward arrows + anchor motif                         |
| 41 | `finance/hedged-carry-trader.md`             | `finance-hedged-carry-trader.png`             | 对冲型套息投资者     | Volatility-managed macro fund with options overlay → carry-arrow + umbrella + volatility waveform motif |
| 42 | `finance/belief-anchor.md`                   | `finance-belief-anchor.png`                   | 信念锚定型投资者     | Belief-state compounding under confirming signals → self-reinforcing "+" motif                          |
| 43 | `finance/selective-scanner.md`               | `finance-selective-scanner.png`               | 选择型投资者         | Selective information search / myside bias → magnifier-with-highlight motif                             |
| 44 | `finance/balanced-analyst.md`                | `finance-balanced-analyst.png`                | 均衡分析型投资者     | Rational Bayesian evidence weighing → equal-armed balance-scale motif                                   |
| 45 | `finance/speculative-attacker.md`            | `finance-speculative-attacker.png`            | 投机攻击型投资者     | Reserve-depletion currency attacker → downward sword + currency motif                                   |
| 46 | `finance/self-fulfilling-trader.md`          | `finance-self-fulfilling-trader.png`          | 自我实现型投资者     | Expectation-coordination herding seller → converging arrows motif                                       |
| 47 | `finance/central-bank-defender.md`           | `finance-central-bank-defender.png`           | 央行防御型投资者     | Reserve-financed peg defender → shield + currency pillar motif                                          |
| 48 | `finance/fundamental-hedger.md`              | `finance-fundamental-hedger.png`              | 基本面对冲型投资者   | Fundamental-value mean-reversion anchor → anchor + balance-scale motif                                  |
| 49 | `finance/new-economy-evangelist.md`          | `finance-new-economy-evangelist.png`          | 新经济布道者         | Narrative tech-belief buyer → laptop/circuit-board motif                                                |
| 50 | `finance/ipo-flipper.md`                     | `finance-ipo-flipper.png`                     | 打新型投资者         | Short-horizon IPO flip trader → coin-flip motif                                                         |
| 51 | `finance/momentum-follower.md`               | `finance-momentum-follower.png`               | 跟风型投资者         | Trend-following amplifier → rising-momentum-arrow motif                                                 |
| 52 | `finance/skeptical-value-investor.md`        | `finance-skeptical-value-investor.png`        | 价值怀疑型投资者     | Cautious fundamental analyst → magnifier + diamond motif                                                |
| 53 | `finance/short-seller.md`                    | `finance-short-seller.png`                    | 做空型投资者         | Bearish arbitrage pressure → descending-arrow motif                                                     |
| 54 | `finance/pro-cyclical-lender.md`             | `finance-pro-cyclical-lender.png`             | 顺周期贷方           | Pro-cyclical credit expansion → upward-arrow + coins motif                                              |
| 55 | `finance/minsky-borrower.md`                 | `finance-minsky-borrower.png`                 | 明斯基借方           | Hedge-speculative-Ponzi fragility → collapsing-staircase motif                                          |
| 56 | `finance/counter-cyclical-lender.md`         | `finance-counter-cyclical-lender.png`         | 逆周期贷方           | Counter-cyclical stabilization → shield + dampened-wave motif                                           |
| 57 | `finance/value-investor.md`                  | `finance-value-investor.png`                  | 价值型投资者         | Fundamental value anchor → magnifier + diamond motif                                                    |

| 58 | `finance/disposition-investor.md`          | `finance-disposition-investor.png`          | 处置效应型投资者   | Prospect-theory disposition bias → S-curve / loss-curve motif                    |
| 59 | `finance/rational-investor.md`             | `finance-rational-investor.png`             | 理性型投资者       | Expected-utility rebalancer → balanced-scale motif                               |
| 60 | `finance/tax-aware-investor.md`            | `finance-tax-aware-investor.png`            | 税务优化型投资者   | Tax-loss harvester / anti-disposition → tax-receipt motif                         |
| 61 | `finance/index-holder.md`                  | `finance-index-holder.png`                  | 被动指数型投资者   | Passive buy-and-hold baseline → flat-line motif                                  |
| 62 | `finance/institutional-investor.md`        | `finance-institutional-investor.png`        | 机构型投资者       | Professional symmetric discipline → threshold-gauge motif                        |
| 63 | `finance/periphery-bond-seller.md`         | `finance-periphery-bond-seller.png`         | 主权债抛售型投资者 | Self-fulfilling sovereign crisis seller → descending yield-curve + red sell-arrow motif |
| 64 | `finance/creditor-panicker.md`             | `finance-creditor-panicker.png`             | 恐慌撤资型投资者   | Sovereign-bank doom-loop funding withdrawal → breaking-chain + alarm-bell motif  |
| 65 | `finance/core-bond-buyer.md`               | `finance-core-bond-buyer.png`               | 核心债避险型投资者 | Flight-to-quality safe-haven buyer → shield + upward-arrow motif                 |
| 66 | `finance/ecb-intervenor.md`                | `finance-ecb-intervenor.png`                | 央行干预型投资者   | Central-bank backstop buyer → institutional-pillar + euro-shield motif           |
| 67 | `finance/hedged-fund.md`                   | `finance-hedged-fund.png`                   | 对冲套利型投资者   | Relative-value spread arbitrageur → balance-scale + opposing-arrows motif        |
| 68 | `finance/endowed-holder.md`                | `finance-endowed-holder.png`                | 禀赋型投资者       | Ownership-attachment endowment holder → treasure-chest + heart motif             |
| 69 | `finance/status-quo-seller.md`             | `finance-status-quo-seller.png`             | 惯性型投资者       | Status-quo-biased inertia seller → pedestal + pause motif                        |
| 70 | `finance/new-buyer.md`                     | `finance-new-buyer.png`                     | 新进型投资者       | Unbiased new market entrant → cart + sparkle motif                               |
| 71 | `finance/myopic-loss-averse-investor.md`   | `finance-myopic-loss-averse-investor.png`   | 短视损失型投资者   | Myopic loss-averse frequent evaluator → declining-chart + broken-magnifier motif |
| 72 | `finance/long-horizon-investor.md`         | `finance-long-horizon-investor.png`         | 长期型投资者       | Patient long-horizon rational rebalancer → extended-upward-timeline motif        |
| 73 | `finance/risk-neutral-investor.md`         | `finance-risk-neutral-investor.png`         | 风险中性型投资者   | Rational excess-return responder → balanced-scale + equation motif               |
| 74 | `finance/conservative-investor.md`         | `finance-conservative-investor.png`         | 保守型投资者       | Loss-averse bond-preferring saver → shield + lock motif                          |
| 75 | `finance/ideologue.md`                     | `finance-ideologue.png`                     | 意见领袖           | Strong opinion holder / in-group amplifier → megaphone + raised-fist motif       |
| 76 | `finance/conformist.md`                    | `finance-conformist.png`                    | 从众型参与者       | Social conformist / group opinion adopter → following-arrows motif               |
| 77 | `finance/critical-thinker.md`              | `finance-critical-thinker.png`              | 批判型思考者       | Evidence evaluator / group-pressure resister → magnifier + lightbulb motif       |
| 78 | `finance/bridge-builder.md`                | `finance-bridge-builder.png`                | 桥梁型参与者       | Cross-group engager / depolarizer → bridge + handshake motif                     |
| 79 | `finance/passive-follower.md`              | `finance-passive-follower.png`              | 被动型参与者       | Low-engagement drifter / occasional participant → cloud + drift motif            |
| 80 | `finance/gain-frame-follower.md`           | `finance-gain-frame-follower.png`           | 追涨型投资者       | Gain-frame risk-averse buyer → upward gain-arrow motif                           |
| 81 | `finance/loss-frame-reactor.md`            | `finance-loss-frame-reactor.png`            | 恐慌抛售型投资者   | Loss-frame risk-seeking seller → downward loss-arrow motif                       |
| 82 | `finance/frame-invariant-trader.md`        | `finance-frame-invariant-trader.png`        | 理性不变型投资者   | Frame-invariant rational value trader → balanced-scale + lens motif              |
| 83 | `finance/arbitrage-framer.md`              | `finance-arbitrage-framer.png`              | 框架套利型投资者   | Framing-mispricing exploiter → converging-arrows + diamond motif                 |
| 84 | `finance/high-frequency-trader.md`         | `finance-high-frequency-trader.png`         | 高频交易型投资者   | Ultra-fast HFT momentum amplifier → lightning + candlestick motif                |
| 85 | `finance/market-maker.md`                  | `finance-market-maker.png`                  | 做市型投资者       | Liquidity provider / stress-withdrawal → bid-ask motif                           |
| 86 | `finance/algorithmic-trader.md`            | `finance-algorithmic-trader.png`            | 算法趋势型投资者   | Systematic trend-follower → trend-arrow + code-bracket motif                     |
| 87 | `finance/stop-loss-trader.md`              | `finance-stop-loss-trader.png`              | 止损级联型投资者   | Forced cascade seller at stop levels → descending-staircase + stop-sign motif    |
| 88 | `finance/fundamental-trader.md`            | `finance-fundamental-trader.png`            | 基本面交易型投资者 | Value buyer / recovery force → magnifier + recovery-arrow motif                  |
| 89 | `finance/retail-trader.md`                 | `finance-retail-trader.png`                 | 散户型投资者       | Uninformed noise participant → random-dots motif                                 |
| 90 | `finance/hft-market-maker.md`              | `finance-hft-market-maker.png`              | 高频做市型投资者   | Ultra-fast liquidity provider / stress-withdrawal → lightning + order-book motif  |
| 91 | `finance/momentum-chaser.md`               | `finance-momentum-chaser.png`               | 动量追涨型投资者   | Trend-following momentum amplifier → rising-momentum-arrow motif                 |
| 92 | `finance/systematic-analyst.md`            | `finance-systematic-analyst.png`            | 系统分析型投资者  | Rational Bayesian evidence weighting → balance-scale + fundamental-diamond motif |
| 93 | `finance/value-trader.md`                  | `finance-value-trader.png`                  | 价值型投资者      | Margin-of-safety value discipline → magnifier + intrinsic-value diamond motif    |
| 94 | `finance/retail-coordinated.md`            | `finance-retail-coordinated.png`            | 协调散户型投资者  | WSB-style social-coordination buyer → smartphone + crowd motif                   |
| 95 | `finance/short-seller-hf.md`               | `finance-short-seller-hf.png`               | 空头基金型投资者  | Forced-cover short-squeeze victim → down-arrow + squeeze motif                   |
| 96 | `finance/market-maker-gamma.md`            | `finance-market-maker-gamma.png`            | 伽马做市型投资者  | Delta-neutral gamma hedger → gamma-symbol + balance motif                        |
| 97 | `finance/institutional-value.md`           | `finance-institutional-value.png`           | 机构价值型投资者  | Finite-inventory fundamental seller → diamond + institution motif                |
| 98 | `finance/momentum-retail.md`               | `finance-momentum-retail.png`               | 追涨散户型投资者  | FOMO attention-driven late buyer → rocket + notification motif                   |
| 99 | `finance/mbs-originator.md`                | `finance-mbs-originator.png`                | 证券化型投资者    | Fee-income securitization distributor → document + dollar motif                   |
| 100 | `finance/rating-agency.md`                | `finance-rating-agency.png`                | 评级型投资者      | Issuer-pays inflated-rating buyer → AAA + star motif                             |
| 101 | `finance/leveraged-investor.md`           | `finance-leveraged-investor.png`           | 杠杆型投资者      | Margin-spiral fire-sale seller → lever + red-arrow motif                         |
| 102 | `finance/distressed-buyer.md`             | `finance-distressed-buyer.png`             | 抄底型投资者      | Deep-discount distressed capital → cart + cracked-diamond motif                  |
| 103 | `finance/regulator.md`                    | `finance-regulator.png`                    | 监管型投资者      | Probabilistic lender-of-last-resort → pillar + shield motif                     |
| 104 | `finance/streak-reversal-trader.md`       | `finance-streak-reversal-trader.png`       | 反转型投资者      | Gambler's-fallacy reversal belief → U-turn arrow + streak motif                 |
| 105 | `finance/hot-hand-trader.md`              | `finance-hot-hand-trader.png`              | 热手型投资者      | Hot-hand continuation belief → flame + rising-trend motif                       |
| 106 | `finance/independent-assessor.md`         | `finance-independent-assessor.png`         | 独立评估型投资者  | Rational streak-independent assessment → balance-scale + magnifier motif        |
| 107 | `finance/arbitrageur.md`                  | `finance-arbitrageur.png`                  | 套利型投资者      | Streak-mispricing exploiter → converging-lines + balance-scale motif            |
| 108 | `finance/category-overgeneralizer.md` | `finance-category-overgeneralizer.png` | 过度归类型投资者 | Category-based overgeneralization → broad-brush motif |
| 109 | `finance/index-fund.md` | `finance-index-fund.png` | — | — |
| 110 | `finance/index-tracker.md` | `finance-index-tracker.png` | — | — |
| 111 | `finance/overconfident-trader.md` | `finance-overconfident-trader.png` | — | — |
| 112 | `finance/pattern-matcher.md` | `finance-pattern-matcher.png` | 模式识别型投资者 | Illusory pattern detection → connecting-dots motif |
| 113 | `finance/self-attributor.md` | `finance-self-attributor.png` | — | — |
| 114 | `opinion/distorting-relayer.md` | `opinion-distorting-relayer.png` | — | — |
| 115 | `opinion/fact-checker.md` | `opinion-fact-checker.png` | — | — |
| 116 | `opinion/gullible-spreader.md` | `opinion-gullible-spreader.png` | — | — |
| 117 | `opinion/skeptical-evaluator.md` | `opinion-skeptical-evaluator.png` | — | — |
| 118 | `opinion/uninformed-bystander.md` | `opinion-uninformed-bystander.png` | — | — |
| 119 | `finance/active-rebalancer.md` | `finance-active-rebalancer.png` | 平衡型/投资者 | Active portfolio rebalancing → balanced-scale + arrows motif |
| 120 | `finance/aggressive-investor.md` | `finance-aggressive-investor.png` | 激进型投资者 | Aggressive high-risk → lightning motif |
| 121 | `finance/anchor-depositor.md` | `finance-anchor-depositor.png` | 锚定存款者 | Yield protocol depositor → vault+anchor motif |
| 122 | `finance/bank-manager.md` | `finance-bank-manager.png` | 银行型/投资者 | Bank management → bank-facade + vault motif |
| 123 | `finance/bayesian-updater.md` | `finance-bayesian-updater.png` | 贝叶斯型/投资者 | Bayesian probability updating → probability-curve motif |
| 124 | `finance/bond-trader.md` | `finance-bond-trader.png` | 债券型/投资者 | Fixed income trading → bond-certificate motif |
| 125 | `finance/bottom-fisher.md` | `finance-bottom-fisher.png` | 抄底型投资者 | Bottom fishing → hook-at-valley motif |
| 126 | `finance/break-even-trader.md` | `finance-break-even-trader.png` | 保本型投资者 | Break-even reference point → zero-line motif |
| 127 | `finance/calibrated-trader.md` | `finance-calibrated-trader.png` | 校准型投资者 | Well-calibrated trading → precision-dial motif |
| 128 | `finance/cascade-follower.md` | `finance-cascade-follower.png` | 跟风型投资者 | Information cascade follower → dominoes motif |
| 129 | `finance/central-bank.md` | `finance-central-bank.png` | 央行干预者 | Central bank intervention → bank-facade motif |
| 130 | `finance/commitment-escalator.md` | `finance-commitment-escalator.png` | 沉没型/投资者 | Sunk-cost escalation of commitment → descending-staircase motif |
| 131 | `finance/contrarian.md` | `finance-contrarian.png` | 逆势型投资者 | Pure contrarian behavior → opposite-arrow motif |
| 132 | `finance/contrarian-investor.md` | `finance-contrarian-investor.png` | 逆向型投资者 | Contrarian against herd → reverse-arrow motif |
| 133 | `finance/contrarian-skeptic.md` | `finance-contrarian-skeptic.png` | 怀疑型投资者 | Skeptical contrarian thinking → question-mark motif |
| 134 | `finance/contrarian-statistical.md` | `finance-contrarian-statistical.png` | 统计型/投资者 | Statistical mean-reversion contrarian → bell-curve + reverse-arrow motif |
| 135 | `finance/convergence-arbitrageur.md` | `finance-convergence-arbitrageur.png` | 收敛套利型投资者 | LTCM convergence arbitrage → converging-lines motif |
| 136 | `finance/convergence-trader.md` | `finance-convergence-trader.png` | 套利型/投资者 | Convergence spread trading → converging-lines motif |
| 137 | `finance/de-fi-lender.md` | `finance-de-fi-lender.png` | 借贷型投资者 | DeFi lending → chain-links motif |
| 138 | `finance/default-follower.md` | `finance-default-follower.png` | 默认型/投资者 | Default-option bias follower → checkbox + path motif |
| 139 | `finance/depositor.md` | `finance-depositor.png` | 存款型/投资者 | Bank depositor / savings holder → vault + coins motif |
| 140 | `finance/distorting-relayer.md` | MISSING | — | — |
| 141 | `finance/early-exit-trader.md` | `finance-early-exit-trader.png` | 止盈型/投资者 | Early profit-taking exit → exit-door + upward-arrow motif |
| 142 | `finance/fact-checker.md` | MISSING | — | — |
| 143 | `finance/flash-market-maker.md` | MISSING | — | — |
| 144 | `finance/forced-seller.md` | MISSING | — | — |
| 145 | `finance/fundamental-anchor.md` | `finance-fundamental-anchor.png` | 基本面锚定型投资者 | Fundamental anchoring → anchor+diamond motif |
| 146 | `finance/greater-fool-speculator.md` | MISSING | — | — |
| 147 | `finance/gullible-spreader.md` | MISSING | — | — |
| 148 | `finance/hindsight-overconfident.md` | `finance-hindsight-overconfident.png` | 后见之明型投资者 | Hindsight bias overconfidence → rearview motif |
| 149 | `finance/house-money-trader.md` | `finance-house-money-trader.png` | 赌资效应型投资者 | House money effect → stacked-coins motif |
| 150 | `finance/independent-thinker.md` | `finance-independent-thinker.png` | 独立型投资者 | Independent thinking against crowd → lightbulb motif |
| 151 | `finance/inertial-holder.md` | `finance-inertial-holder.png` | 惯性型/投资者 | Status-quo inertia holding → pedestal + pause motif |
| 152 | `finance/information-environment.md` | `finance-information-environment.png` | 信息型/环境 | Network info coordinator for rumor propagation |
| 153 | `finance/insider-advantaged.md` | `finance-insider-advantaged.png` | 信息型/投资者 | Information-advantaged insider → eye + key motif |
| 154 | `finance/institutional-holder.md` | `finance-institutional-holder.png` | 机构型/投资者 | Institutional long-term holder → institution-pillar motif |
| 155 | `finance/intrinsic-value-trader.md` | `finance-intrinsic-value-trader.png` | 价值型/投资者 | Intrinsic-value fundamental trading → diamond + magnifier motif |
| 156 | `finance/leverage-trader.md` | `finance-leverage-trader.png` | 杠杆型投资者 | Leveraged trading → lever/fulcrum motif |
| 157 | `finance/leveraged-fund.md` | MISSING | — | — |
| 158 | `finance/leveraged-hedge-fund.md` | `finance-leveraged-hedge-fund.png` | 杠杆基金型投资者 | Leveraged hedge fund → lever+gauge motif |
| 159 | `finance/leveraged-speculator.md` | MISSING | — | — |
| 160 | `finance/liquidity-demander.md` | MISSING | — | — |
| 161 | `finance/liquidity-seeker.md` | `finance-liquidity-seeker.png` | 流动性需求型投资者 | Liquidity seeking → water-droplet motif |
| 162 | `finance/long-term-investor.md` | MISSING | — | — |
| 163 | `finance/loss-averse.md` | `finance-loss-averse.png` | 损失型/投资者 | Myopic loss aversion drives premature exits |
| 164 | `finance/loss-averse-investor.md` | `finance-loss-averse-investor.png` | 损失厌恶型投资者 | Prospect theory loss aversion → loss-curve motif |
| 165 | `finance/macro-hedge-fund.md` | `finance-macro-hedge-fund.png` | 宏观型/投资者 | Macro hedge fund strategy → globe + trend-arrow motif |
| 166 | `finance/mental-accountant.md` | `finance-mental-accountant.png` | 心理账户型投资者 | Mental accounting → compartment-boxes motif |
| 167 | `finance/momentum-buyer.md` | `finance-momentum-buyer.png` | 动量型/投资者 | Momentum-driven buying → rising-arrow motif |
| 168 | `finance/momentum-investor.md` | `finance-momentum-investor.png` | 动量型投资者 | Herd momentum following → trend+crowd motif |
| 169 | `finance/myopic-loss-averse.md` | MISSING | — | — |
| 170 | `finance/narrative-believer.md` | `finance-narrative-believer.png` | 叙事型/投资者 | Narrative-driven belief → story-book + speech-bubble motif |
| 171 | `finance/opinion-environment.md` | MISSING | — | — |
| 172 | `finance/opportunistic-trader.md` | `finance-opportunistic-trader.png` | 机会型/投资者 | Opportunistic trading → eye + lightning motif |
| 173 | `finance/opportunity-cost-trader.md` | `finance-opportunity-cost-trader.png` | 机会型/投资者 | Opportunity-cost aware switching → forked-path motif |
| 174 | `finance/outcome-learner.md` | `finance-outcome-learner.png` | 结果导向型投资者 | Outcome-based learning → checkmark-chart motif |
| 175 | `finance/panic-seller.md` | `finance-panic-seller.png` | 恐慌抛售型投资者 | Panic selling → down-arrow+alert motif |
| 176 | `finance/passive-bystander.md` | MISSING | — | — |
| 177 | `finance/passive-investor.md` | `finance-passive-investor.png` | 被动型投资者 | Passive buy-and-hold → flat-line+clock motif |
| 178 | `finance/peg-defender.md` | `finance-peg-defender.png` | 防御型/投资者 | Currency peg defense → shield + currency-pillar motif |
| 179 | `finance/process-evaluator.md` | `finance-process-evaluator.png` | 过程评估型投资者 | Process evaluation → flowchart motif |
| 180 | `finance/rational-cutter.md` | `finance-rational-cutter.png` | 理性型/投资者 | Rational loss-cutting discipline → scissors + red-line motif |
| 181 | `finance/rational-optimizer.md` | MISSING | — | — |
| 182 | `finance/rational-portfolio-manager.md` | `finance-rational-portfolio-manager.png` | 理性组合管理者 | Rational diversification → pie-chart+checkmark motif |
| 183 | `finance/rational-trader.md` | `finance-rational-trader.png` | 理性型投资者 | Rational utility maximization → balance-scale motif |
| 184 | `finance/reputation-herder.md` | `finance-reputation-herder.png` | 声誉跟随型投资者 | Reputation-driven herding → star+crowd motif |
| 185 | `finance/retail-coordinator.md` | MISSING | — | — |
| 186 | `finance/risk-averse-investor.md` | `finance-risk-averse-investor.png` | 风险规避型投资者 | Risk-averse cautious investor → shield motif |
| 187 | `finance/risk-averse-saver.md` | MISSING | — | — |
| 188 | `finance/risk-manager.md` | `finance-risk-manager.png` | 风控型投资者 | Risk management → gauge+shield motif |
| 189 | `finance/risk-parity-fund.md` | `finance-risk-parity-fund.png` | 风险平价型投资者 | Risk parity allocation → equal-pie motif |
| 190 | `finance/sentiment-trader.md` | MISSING | — | — |
| 191 | `finance/skeptical-analyst.md` | `finance-skeptical-analyst.png` | 研究型/投资者 | Skeptical analytical research → magnifier + question-mark motif |
| 192 | `finance/skeptical-evaluator.md` | MISSING | — | — |
| 193 | `finance/social-media-influencer.md` | `finance-social-media-influencer.png` | 传播型/投资者 | Social media influence amplification → megaphone + smartphone motif |
| 194 | `finance/social-proof-follower.md` | `finance-social-proof-follower.png` | 跟风型/投资者 | Social proof herd following → crowd + thumbs-up motif |
| 195 | `finance/stablecoin-holder.md` | `finance-stablecoin-holder.png` | 稳定币持有者 | Stablecoin holder → coin+flat-line motif |
| 196 | `finance/sunk-cost-holder.md` | `finance-sunk-cost-holder.png` | 沉没成本型投资者 | Sunk cost fallacy → anchor-chain motif |
| 197 | `finance/technical-trader.md` | `finance-technical-trader.png` | 技术分析型投资者 | Technical analysis → candlestick-chart motif |
| 198 | `finance/trend-chaser.md` | `finance-trend-chaser.png` | 趋势型/投资者 | Trend-chasing momentum buyer → rising-trend + runner motif |
| 199 | `finance/uninformed-bystander.md` | MISSING | — | — |
| 200 | `finance/value-buyer.md` | `finance-value-buyer.png` | 价值抄底型投资者 | Value buying at lows → diamond+discount motif |

## Notes

- Icon file names carry a domain prefix so the filename encodes both the
  domain and the agent (e.g. ``finance-anchored-trader.png``,
  ``opinion-distorting-relayer.png``).
- Rows 1–118: icon exists on disk (118 total: 113 finance + 5 opinion).
- Rows 119–200: icon **MISSING** (82 agents, all stubs awaiting authoring).
- Total agent .md files: 200 (195 finance + 5 opinion).
- Each authored ``finance/*.md`` or ``opinion/*.md`` file carries an
  ``| Icon |`` row in its Design Provenance table linking to its icon via
  relative path.
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
- 2026-07-12: Mapping rows #33–#34 added for the AvailabilityBias scenario
  archetypes (recent-event-overweighter, media-influenced-trader). PNGs
  generated fresh via ImageGen; mapping-row gap closed as part of the
  polish-simulation-pipeline Step 2 icon-resolution sub-gate.
- 2026-07-12: Mapping rows #35–#37 added for the BlackMonday1987 scenario
  archetypes (portfolio-insurer, index-arbitrageur, program-trader). PNGs
  generated via agent-icon-generation-skill; profile Icon rows and design.md
  mapping were the missing links.
- 2026-07-12: Mapping rows #38–#41 added for the CarryTradeUnwind scenario
  archetypes (carry-trader, leveraged-carry-fund, funding-currency-buyer,
  hedged-carry-trader). Icons generated in-session via ImageGen; mapping-row
  and profile-Icon-row gaps closed together.
- 2026-07-12: Mapping rows #42–#44 added for the ConfirmationBias scenario
  archetypes (belief-anchor, selective-scanner, balanced-analyst). PNGs
  generated fresh; mapping-row gap closed as part of the
  polish-simulation-pipeline Step 2 icon-resolution sub-gate.
- 2026-07-13: Mapping rows #45–#48 added for the CurrencyCrisis scenario
  archetypes (speculative-attacker, self-fulfilling-trader, central-bank-defender,
  fundamental-hedger). PNGs generated via ImageGen; mapping-row and
  profile-Icon-row gaps closed as part of the polish-simulation-pipeline
  Step 2 icon-resolution sub-gate.
- 2026-07-13: Mapping rows #49–#53 added for the DotComBubble scenario
  archetypes (new-economy-evangelist, ipo-flipper, momentum-follower,
  skeptical-value-investor, short-seller). PNGs generated via ImageGen;
  mapping-row gaps closed as part of the polish-simulation-pipeline
  Step 2 icon-resolution sub-gate.
- 2026-07-13: Mapping rows #54–#57 added for the CreditCycle scenario
  archetypes (pro-cyclical-lender, minsky-borrower, counter-cyclical-lender,
  value-investor). PNGs generated via ImageGen; mapping-row and
  profile-Icon-row gaps closed as part of the polish-simulation-pipeline
  Step 2 icon-resolution sub-gate.
- 2026-07-14: Mapping rows #58–#62 added for the DispositionEffect scenario
  archetypes (disposition-investor, rational-investor, tax-aware-investor,
  index-holder, institutional-investor). PNGs generated via ImageGen;
  disposition-investor and rational-investor profile Icon rows corrected
  (previously pointed to wrong filenames disposition-trader.png and
  rational-updater.png respectively). Mapping-row and profile-Icon-row
  gaps closed as part of the polish-simulation-pipeline Step 2
  icon-resolution sub-gate.
- 2026-07-15: Mapping rows #63–#67 added for the EuropeanDebtCrisis scenario
  archetypes (periphery-bond-seller, creditor-panicker, core-bond-buyer,
  ecb-intervenor, hedged-fund). PNGs generated via ImageGen; mapping-row
  gaps closed as part of the polish-simulation-pipeline Step 2
  icon-resolution sub-gate.
- 2026-07-15: Mapping rows #68–#70 added for the EndowmentEffect scenario
  archetypes (endowed-holder, status-quo-seller, new-buyer). PNGs generated
  via ImageGen; mapping-row and profile-Icon-row gaps closed as part of the
  polish-simulation-pipeline Step 2 icon-resolution sub-gate.
- 2026-07-16: Mapping rows #71–#74 added for the EquityPremium scenario
  archetypes (myopic-loss-averse-investor, long-horizon-investor,
  risk-neutral-investor, conservative-investor). PNGs generated via ImageGen;
  mapping-row gaps closed as part of the polish-simulation-pipeline Step 2
  icon-resolution sub-gate.
- 2026-07-16: Mapping rows #75–#79 added for the EchoChamber scenario
  archetypes (ideologue, conformist, critical-thinker, bridge-builder,
  passive-follower). PNGs generated via ImageGen; mapping-row gaps closed
  as part of the polish-simulation-pipeline Step 2 icon-resolution sub-gate.
- 2026-07-17: Mapping rows #80–#83 added for the FramingEffect scenario
  archetypes (gain-frame-follower, loss-frame-reactor, frame-invariant-trader,
  arbitrage-framer). PNGs generated via ImageGen; mapping-row and
  profile-Icon-row gaps closed as part of the polish-simulation-pipeline
  Step 2 icon-resolution sub-gate.
- 2025-07-18: Mapping rows #84–#89 added for the FlashCrash scenario
  archetypes (high-frequency-trader, market-maker, algorithmic-trader,
  stop-loss-trader, fundamental-trader, retail-trader). PNGs generated via
  ImageGen (market-maker already existed); mapping-row gaps closed as part
  of the polish-simulation-pipeline Step 2 icon-resolution sub-gate.
- 2025-07-18: Mapping rows #90–#91 added for the FlashCrash2010 scenario
  archetypes (hft-market-maker, momentum-chaser). PNGs generated via ImageGen;
  fundamental-trader and stop-loss-trader already covered by rows #87–#88;
  noise-trader already covered by row #14. Mapping-row gaps closed as part
  of the polish-simulation-pipeline Step 2 icon-resolution sub-gate.
- 2026-07-13: Mapping row #92 added for the systematic-analyst archetype.
  PNG generated via ImageGen from `finance/systematic-analyst.md`; mapping-row
  gap closed as part of the polish-simulation-pipeline Step 2
  icon-resolution sub-gate.
- 2026-07-13: Mapping row #93 added for the value-trader archetype.
  PNG generated via ImageGen from `finance/value-trader.md`; missing PNG and
  mapping-row gaps closed as part of the polish-simulation-pipeline Step 2
  icon-resolution sub-gate.
- 2026-07-20: Mapping rows #94–#98 added for the GameStopShortSqueeze scenario
  archetypes (retail-coordinated, short-seller-hf, market-maker-gamma,
  institutional-value, momentum-retail). PNGs generated via ImageGen;
  mapping-row gaps closed as part of the polish-simulation-pipeline Step 2
  icon-resolution sub-gate.
- 2026-07-21: Mapping rows #99–#103 added for the GFC2008 scenario archetypes
  (mbs-originator, rating-agency, leveraged-investor, distressed-buyer,
  regulator). PNGs generated via ImageGen; mapping-row gaps closed as part
  of the polish-simulation-pipeline Step 2 icon-resolution sub-gate.
- 2026-07-22: Mapping rows #104–#107 added for the GamblerFallacy scenario
  archetypes (streak-reversal-trader, hot-hand-trader, independent-assessor,
  arbitrageur). PNGs generated via ImageGen; noise-trader already covered by
  row #14. Mapping-row gaps closed as part of the polish-simulation-pipeline
  Step 2 icon-resolution sub-gate.
- 2026-07-15: Mapping rows updated for H-O scenario archetypes (momentum-investor,
  contrarian-investor, risk-averse-investor, aggressive-investor, cascade-follower,
  reputation-herder, independent-thinker, contrarian, hindsight-overconfident,
  outcome-learner, process-evaluator, contrarian-skeptic, convergence-arbitrageur,
  leverage-trader, risk-manager, central-bank, stablecoin-holder, de-fi-lender,
  anchor-depositor, value-buyer, liquidity-seeker, loss-averse-investor,
  break-even-trader, rational-trader, risk-parity-fund, leveraged-hedge-fund,
  passive-investor, panic-seller, bottom-fisher, mental-accountant,
  house-money-trader, rational-portfolio-manager, sunk-cost-holder,
  technical-trader, fundamental-anchor, calibrated-trader). PNGs generated via
  ImageGen; mapping-row gaps closed as part of the polish-simulation-pipeline
  Step 2 icon-resolution sub-gate.
- If new agents are added to `finance/`, commission a new icon in the same
  style and name it ``finance-<agent-stem>.png``.

## Mapping: market/ coordinators → icons/market/

Market coordinators live under `examples/AGENT_POOL/market/{market-type}-{stem}.md`
and their icons under `agent_images/icons/market/{market-type}-{stem}.png`.
They follow the same overall visual shell as participant icons, with three
coordinator-specific overrides declared in `masim/skills/market-icon-generation-skill.md`:
(1) a small hub / broadcast-dish / network accent floating above the robot head
signalling *"I coordinate"*, (2) a **compound lower motif** combining the
Market-Type element with the mechanism motif, and (3) a Chinese label tag
ending in `协调器 / 场 / 系统` (never `投资者`).

| # | Coordinator                                          | Icon                                              | Display Label       | Match Reason                                                                                                                                             |
|---|------------------------------------------------------|---------------------------------------------------|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | `market/stock-standard-price-impact.md`              | `market/stock-standard-price-impact.png`          | 股票市场 / 协调器    | Stock (candlestick chart) + Standard price-impact + mean-reversion (anchor motif); blue-cyan palette; label uses 协调器 for matching-engine-like clearing |
| 2 | `market/opinion-echo-chamber-clustering.md`          | `market/opinion-echo-chamber-clustering.png`      | 舆论场 / 回声室型    | Opinion (diverging speech bubbles) + Echo-chamber clustering (converging within-cluster arrows on two clusters); violet-cyan palette; label uses 场 for diffuse environmental field |
| 3 | `market/information-sis-contagion.md`                | `market/information-sis-contagion.png`            | 信息场 / 谣言传播型  | Information (megaphone + propagation-node network) + SIS-style contagion (central node with radiating wave arcs); coral-cyan palette; label uses 场       |
