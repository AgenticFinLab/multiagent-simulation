# ArchegosCollapse / Block Trade Buyer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ArchegosCollapse |
| Agent type | Block Trade Buyer |
| Canonical class | `BlockTradeBuyer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

`BlockTradeBuyer` represents the opportunistic institutional buyer who absorbs forced supply at fire-sale discounts. In the Archegos event, several hedge funds and asset managers purchased blocks of ViacomCBS and Discovery at 50-60% discounts from peak prices. This investor is the primary stabilizing force: once prices fall far enough below fundamental value (beyond the discount_threshold), it deploys cash to buy. Its presence creates a price floor -- without it, prices could cascade to near-zero in extreme scenarios. BlockTradeBuyer is distinguished by large cash reserves, patient capital, and willingness to absorb illiquid supply when others are forced to sell.

## Financial Theory / Theoretical Basis

### Rule / `BlockTradeBuyer`
- Theory: simulation-bases.md Section 4.4 -- BlockTradeBuyer
- Theoretical basis: Fire-Sale Arbitrage / Liquidity Provider (Shleifer & Vishny, 1992).

### LLM / `LLMBlockTradeBuyer`
- LLM-driven block trade buyer -- opportunistic discount buyer. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMBlockTradeBuyer`
- RuleLLM block trade buyer -- opportunistic discount buyer. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMBlockTradeBuyer`
- RAG-augmented block trade buyer -- opportunistic discount buyer. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| buy_ratio | Rule: `0.3` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| discount_threshold | Rule: `-0.1` | Rule |
| fundamental_value | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| initial_price | RuleLLM: `100.0`<br>Rag: `100.0` | Rag, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ArchegosCollapse.LLM.prompts:LLM_BLOCK_TRADE_BUYER_SYS', 'user_message': 'examples.ArchegosCollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.ArchegosCollapse.RuleLLM.prompts:RULELLM_BLOCK_TRADE_BUYER_SYS', 'user_message': 'examples.ArchegosCollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.ArchegosCollapse.Rag.prompts:RAG_BLOCK_TRADE_BUYER_SYS', 'user_message': 'examples.ArchegosCollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | block_trade_buyer | Block Trade Buyer | `BlockTradeBuyer` | 1 | `examples/ArchegosCollapse/Rule/players.py` |
| LLM | block_trade_buyer | Block Trade Buyer | `LLMBlockTradeBuyer` | 1 | `examples/ArchegosCollapse/LLM/players.py` |
| RuleLLM | block_trade_buyer | Block Trade Buyer | `RuleLLMBlockTradeBuyer` | 1 | `examples/ArchegosCollapse/RuleLLM/players.py` |
| Rag | ragllm_block_trade_buyer | RAG Block Trade Buyer | `RagLLMBlockTradeBuyer` | 1 | `examples/ArchegosCollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 BlockTradeBuyer

#### 4.4.1 Summary

`BlockTradeBuyer` represents the opportunistic institutional buyer who absorbs forced supply at fire-sale discounts. In the Archegos event, several hedge funds and asset managers purchased blocks of ViacomCBS and Discovery at 50-60% discounts from peak prices. This investor is the primary stabilizing force: once prices fall far enough below fundamental value (beyond the discount_threshold), it deploys cash to buy. Its presence creates a price floor -- without it, prices could cascade to near-zero in extreme scenarios. BlockTradeBuyer is distinguished by large cash reserves, patient capital, and willingness to absorb illiquid supply when others are forced to sell.

#### 4.4.2 Theoretical and Empirical Foundation

**Theory/Study 1: Block Trading and Liquidity Provision in Stressed Markets**

- Citation: Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617-637. https://doi.org/10.1111/j.1540-6261.1988.tb04591.x
- Core Insight: Block trade buyers provide liquidity by holding inventory at a discount. They only absorb supply when prices are low enough to compensate for the risk of further price decline (inventory risk). The minimum discount required equals the expected holding cost plus a risk premium for uncertainty about when prices will recover.
- Mathematical Formulation: `Activation condition: (F - P(t)) / F > discount_threshold`, equivalent to `deviation(t) < -discount_threshold`. `Purchase quantity: Q_buy = alpha x cash / P(t)` where alpha is the capital deployment fraction.
- Empirical Evidence: Grossman & Miller (1988) estimate normal block trade discounts of 1.5-3.0%. In distressed markets, block trade discounts of 5-15% are documented (Mitchell & Pulvino, 2012, *Review of Financial Studies*, 25(7), 2235-2274). The 10% threshold (discount_threshold = 0.10) is calibrated to this distressed range.
- Relevance to This Investor: BlockTradeBuyer's 10% discount threshold models institutional buyers who require compensation for holding risk during the Archegos-scale cascade.
- Parameter Calibration: discount_threshold = 0.10; cash_deployment = 0.30 (30% of available cash per activation round).

**Theory/Study 2: Value Investing and Margin of Safety**

- Citation: Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers. (Revised edition 2006, Collins Business.)
- Core Insight: Value investors require a "margin of safety" -- a sufficient discount to fundamental value -- before committing capital. This provides protection against estimation error and further price decline. The margin of safety principle produces natural price-floor behavior: value capital is deployed when discounts exceed the safety threshold.
- Empirical Evidence: Academic research on value investing documents that deep-value purchases (at discounts of 30%+ to book value or intrinsic value) have historically generated 5-10% annual alpha (Lakonishok, Shleifer & Vishny, 1994, *Journal of Finance*, 49(5), 1541-1578), consistent with the block trade buying strategy.
- Relevance to This Investor: BlockTradeBuyer's activation at -10% deviation represents a conservative margin of safety, deployed by patient capital willing to accept short-term mark-to-market losses in exchange for long-term value recovery.

#### 4.4.3 Design Purpose and Activation Scenarios

**Purpose**: Provide a price floor that eventually halts the cascade and begins the recovery phase.

| Market Condition  | BlockTradeBuyer Response          | Economic Effect                                                              | Theory                                           |
|-------------------|-----------------------------------|------------------------------------------------------------------------------|--------------------------------------------------|
| deviation >= -0.10 | Hold; no action                   | No stabilization needed at normal prices                                     | Below discount threshold                         |
| deviation < -0.10 | Buy: `0.30 x cash / price` shares | Positive demand shock; partially offsets broker selling; creates price floor | Section 4.4.2 Theory 1: block trade liquidity provision |

**Market Contribution**: Stabilizing. Provides positive demand offset during and after cascade. The recovery phase begins when BlockTradeBuyer's purchases (combined with mean reversion) exceed the remaining selling pressure from brokers.

#### 4.4.4 Behavioral Framework

##### 4.4.4.1 Mathematical Model

**Trigger Function**:
```
Trigger when: δ(t) < -theta_discount   where theta_discount = 0.10
```

**Sizing Function**:
```
Q_buy = floor(alpha x cash / P(t))
where alpha = cash_deployment = 0.30
Constraint: Q_buy x P(t) <= cash   [cannot spend more than available]
```

**State Variables**:
| Variable | Type  | Update Rule                         |
|----------|-------|-------------------------------------|
| cash     | float | cash -= Q_buy x P(t) each buy round |
| position | int   | position += Q_buy each buy round    |

#### 4.4.5 Decision Process Walkthrough

At cascade trough (price ≈ $33, deviation ≈ -0.67):
- BlockTradeBuyer observes deviation = -0.67 < -0.10 -> trigger
- Q_buy = floor(0.30 x 100,000 / 33.0) = floor(909) = 909 shares
- Submit: buy 909 shares at $33.00
- Market impact: DeltaP ≈ 0.03 x 909 = +$27.27; P rises toward $60.27
- Cascade begins to reverse as BlockTradeBuyer continues buying in subsequent rounds

#### 4.4.6 Worked Numerical Example

```
P(t) = 33.20, δ = -0.668, cash = 100,000, alpha = 0.30, theta = 0.10
Step 1: -0.668 < -0.10 -> True
Step 2: Q_buy = floor(0.30 x 100,000 / 33.20) = floor(30,000 / 33.20) = 903 shares
Step 3: Buy 903 @ $33.20; cash -> 100,000 - 903x33.20 = $70,020
Market impact: DeltaP ≈ 0.03 x 903 = $27.09; P(t+1) ≈ 33.20 + 27.09 + 0.668 = $60.96
Recovery begins.
```

#### 4.4.7 Academic References

| # | Full Citation                                                                                                                                                                                    | Contribution                                                         |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------|
| 1 | Grossman, S. J., & Miller, M. H. (1988). Liquidity and market structure. *Journal of Finance*, 43(3), 617-637. https://doi.org/10.1111/j.1540-6261.1988.tb04591.x                                | Block trade discount threshold; liquidity provision mechanism        |
| 2 | Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers (rev. ed. 2006, Collins Business).                                                                                              | Margin of safety principle; value buyer activation at deep discounts |
| 3 | Lakonishok, J., Shleifer, A., & Vishny, R. W. (1994). Contrarian investment, extrapolation, and risk. *Journal of Finance*, 49(5), 1541-1578. https://doi.org/10.1111/j.1540-6261.1994.tb04772.x | Empirical returns to deep-value block buying strategy                |

---

## Source Docstring Excerpts

### Rule / `BlockTradeBuyer`

```text
Opportunistic block trade buyer purchasing at fire-sale discount.

Theory: simulation-bases.md Section 4.4 -- BlockTradeBuyer
Theoretical basis: Fire-Sale Arbitrage / Liquidity Provider (Shleifer & Vishny, 1992).
Buys when price drops below discount_threshold (relative to fundamental).
Deploys buy_ratio of available cash per round.
See simulation-bases.md Section 4.4.4.3 for mathematical model.
```

### LLM / `LLMBlockTradeBuyer`

```text
LLM-driven block trade buyer -- opportunistic discount buyer. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMBlockTradeBuyer`

```text
RuleLLM block trade buyer -- opportunistic discount buyer. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMBlockTradeBuyer`

```text
RAG-augmented block trade buyer -- opportunistic discount buyer. Theory: simulation-bases.md Section 4.4.
```
