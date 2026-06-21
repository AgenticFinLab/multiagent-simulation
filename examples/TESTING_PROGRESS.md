# 场景测试进度

用于登记 `examples/` 下各场景的测试负责人和完成情况。

状态统一填写：`未测`、`进行中`、`通过`、`失败`、`阻塞`。只有完成配置中的全部轮次，并检查运行日志和分析结果后，才标记为 `通过`。

| 场景                   | Rule | LLM    | RuleLLM | Rag    | 测试人      | 完成日期 | 结果路径或备注 |
| ---------------------- | ---- | ------ | ------- | ------ | ----------- | -------- | -------------- |
| AnchoringEffect        | 通过 | 进行中 | 进行中  | 进行中 | Yuxuan Zhao |          |                |
| ArchegosCollapse       | 未测 | 未测   | 未测    | 未测   |             |          |                |
| AsianFinancialCrisis   | 未测 | 未测   | 未测    | 未测   |             |          |                |
| AssetBubble            | 未测 | 未测   | 未测    | 未测   |             |          |                |
| AvailabilityBias       | 未测 | 未测   | 未测    | 未测   |             |          |                |
| BlackMonday1987        | 未测 | 未测   | 未测    | 未测   |             |          |                |
| CarryTradeUnwind       | 未测 | 未测   | 未测    | 未测   |             |          |                |
| ConfirmationBias       | 未测 | 未测   | 未测    | 未测   |             |          |                |
| CreditCycle            | 未测 | 未测   | 未测    | 未测   |             |          |                |
| CurrencyCrisis         | 未测 | 未测   | 未测    | 未测   |             |          |                |
| DispositionEffect      | 未测 | 未测   | 未测    | 未测   |             |          |                |
| DotComBubble           | 未测 | 未测   | 未测    | 未测   |             |          |                |
| EchoChamber            | 未测 | 未测   | 未测    | 未测   |             |          |                |
| EndowmentEffect        | 未测 | 未测   | 未测    | 未测   |             |          |                |
| EquityPremium          | 未测 | 未测   | 未测    | 未测   |             |          |                |
| EuropeanDebtCrisis     | 未测 | 未测   | 未测    | 未测   |             |          |                |
| FlashCrash             | 未测 | 未测   | 未测    | 未测   |             |          |                |
| FlashCrash2010         | 未测 | 未测   | 未测    | 未测   |             |          |                |
| FramingEffect          | 未测 | 未测   | 未测    | 未测   |             |          |                |
| GamblerFallacy         | 未测 | 未测   | 未测    | 未测   |             |          |                |
| GameStopShortSqueeze   | 未测 | 未测   | 未测    | 未测   |             |          |                |
| GFC2008                | 未测 | 未测   | 未测    | 未测   |             |          |                |
| HerdEffect             | 未测 | 未测   | 未测    | 未测   |             |          |                |
| HerdingInformation     | 未测 | 未测   | 未测    | 未测   |             |          |                |
| HindsightBias          | 未测 | 未测   | 未测    | 未测   |             |          |                |
| LiquidityDryup         | 未测 | 未测   | 未测    | 未测   |             |          |                |
| LossAversion           | 未测 | 未测   | 未测    | 未测   |             |          |                |
| LTCMCollapse           | 未测 | 未测   | 未测    | 未测   |             |          |                |
| LUNACollapse           | 未测 | 未测   | 未测    | 未测   |             |          |                |
| MarketCrash            | 未测 | 未测   | 未测    | 未测   |             |          |                |
| MentalAccounting       | 未测 | 未测   | 未测    | 未测   |             |          |                |
| MomentumEffect         | 未测 | 未测   | 未测    | 未测   |             |          |                |
| OverconfidenceBias     | 未测 | 未测   | 未测    | 未测   |             |          |                |
| RepresentativenessBias | 未测 | 未测   | 未测    | 未测   |             |          |                |
| ReversalEffect         | 未测 | 未测   | 未测    | 未测   |             |          |                |
| RumorSpread            | 未测 | 未测   | 未测    | 未测   |             |          |                |
| ShortSqueeze           | 未测 | 未测   | 未测    | 未测   |             |          |                |
| SorosPound             | 未测 | 未测   | 未测    | 未测   |             |          |                |
| SouthSeaBubble         | 未测 | 未测   | 未测    | 未测   |             |          |                |
| StatusQuoBias          | 未测 | 未测   | 未测    | 未测   |             |          |                |
| SunkCostFallacy        | 未测 | 未测   | 未测    | 未测   |             |          |                |
| SVBBankRun             | 未测 | 未测   | 未测    | 未测   |             |          |                |
| TulipMania             | 未测 | 未测   | 未测    | 未测   |             |          |                |
| VolatilityClustering   | 未测 | 未测   | 未测    | 未测   |             |          |                |
| Volmageddon            | 未测 | 未测   | 未测    | 未测   |             |          |                |

## 登记规则

1. 开始测试前填写“测试人”，并将对应机制改为 `进行中`。
2. 测试结束后填写完成日期，格式为 `YYYY-MM-DD`。
3. 在“结果路径或备注”中填写隔离实验目录、报告路径或失败原因。
4. 四种机制全部为 `通过` 时，表示该场景已完整测完。
