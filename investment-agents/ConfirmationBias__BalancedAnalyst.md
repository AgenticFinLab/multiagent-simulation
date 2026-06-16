# ConfirmationBias / Balanced Analyst

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | ConfirmationBias |
| Agent type | Balanced Analyst |
| Canonical class | `BalancedAnalyst` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The BalancedAnalyst is the rational benchmark -- a fundamental analyst who evaluates all market information objectively, without prior beliefs or position bias. Unlike BeliefAnchor (who amplifies confirming signals) or SelectiveScanner (who responds asymmetrically based on position), the BalancedAnalyst applies the same evidence standard to bullish and bearish signals. It buys when prices are genuinely below fundamental (deviation < -5%) and sells when genuinely above (deviation > +5%), serving as the primary mean-reversion force that limits how far confirmation bias can push prices from intrinsic value.

## Financial Theory / Theoretical Basis

### Rule / `BalancedAnalyst`
- Theory: simulation-bases.md Section 4.3 -- BalancedAnalyst
- Theoretical basis: Bayesian rational updating; processes signals without cognitive

### LLM / `LLMBalancedAnalyst`
- LLM-driven balanced analyst -- Bayesian rational updater, no cognitive bias. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMBalancedAnalyst`
- RuleLLM-driven balanced analyst -- Bayesian rational updater, no cognitive bias. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMBalancedAnalyst`
- RAG-augmented balanced analyst -- Bayesian rational updater, no cognitive bias. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| analysis_threshold | Rule: `0.05` | Rule |
| base_size | Rule: `30.0` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `50000.0`<br>LLM: `50000.0`<br>RuleLLM: `50000.0`<br>Rag: `50000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.ConfirmationBias.LLM.prompts:LLM_BALANCED_ANALYST_SYS', 'user_message': 'examples.ConfirmationBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.ConfirmationBias.RuleLLM.prompts:RULELLM_BALANCED_ANALYST_SYS', 'user_message': 'examples.ConfirmationBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.2, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.ConfirmationBias.Rag.prompts:RAG_BALANCED_ANALYST_SYS', 'user_message': 'examples.ConfirmationBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `400` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| trade_threshold | Rule: `0.03` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | balanced_analyst | Balanced Analyst | `BalancedAnalyst` | 1 | `examples/ConfirmationBias/Rule/players.py` |
| LLM | llm_balanced_analyst | LLM Balanced Analyst | `LLMBalancedAnalyst` | 1 | `examples/ConfirmationBias/LLM/players.py` |
| RuleLLM | rulellm_balanced_analyst | RuleLLM Balanced Analyst | `RuleLLMBalancedAnalyst` | 1 | `examples/ConfirmationBias/RuleLLM/players.py` |
| Rag | ragllm_balanced_analyst | RAG Balanced Analyst | `RagLLMBalancedAnalyst` | 1 | `examples/ConfirmationBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 BalancedAnalyst

#### 4.3.1  Summary

The BalancedAnalyst is the rational benchmark -- a fundamental analyst who evaluates all market information objectively, without prior beliefs or position bias. Unlike BeliefAnchor (who amplifies confirming signals) or SelectiveScanner (who responds asymmetrically based on position), the BalancedAnalyst applies the same evidence standard to bullish and bearish signals. It buys when prices are genuinely below fundamental (deviation < -5%) and sells when genuinely above (deviation > +5%), serving as the primary mean-reversion force that limits how far confirmation bias can push prices from intrinsic value.

#### 4.3.2  Theoretical and Empirical Foundation

**Theory 1: Fundamental Analysis and Rational Information Processing**
- Citation: Fama, E. F. (1970). "Efficient capital markets." *Journal of Finance*, 25(2), 383-417. DOI: 10.2307/2325486. Also: Mullainathan, S. (2002). "A memory-based model of bounded rationality." *Quarterly Journal of Economics*, 117(3), 735-774. DOI: 10.1162/003355302760193887
- Core Insight: Rational fundamental analysts provide the stabilizing force in markets with behavioral biases. Fama (1970)'s efficient market hypothesis requires that some agents process information without bias; Mullainathan (2002) shows the rational case is flat-weighted information processing. BalancedAnalyst implements this: symmetric response to positive and negative deviations, no prior beliefs.
- Mathematical Formulation: Symmetric trigger: buy if δ < -0.05; sell if δ > +0.05. Sizing: Q = min(order_size, position or cash_capacity) = min(400, ...). Unlike BeliefAnchor (where sign(trade) depends on belief), BalancedAnalyst's sign(trade) is always contrarian to deviation.
- Relevance to This Investor: analysis_threshold = 0.05 (5%) is deliberately higher than BeliefAnchor's effective threshold (belief > 0.5 -> 500 shares regardless of deviation magnitude). This means BalancedAnalyst is not always in the market -- it corrects only when deviation is meaningfully large, consistent with rational risk-bearing constraints.

**Theory 2: Contrarian Value Investing and the Rational Correction Force**
- Citation: De Bondt, W. F. M., & Thaler, R. H. (1985). "Does the stock market overreacttheta" *Journal of Finance*, 40(3), 793-805. DOI: 10.2307/2327804
- Core Insight: De Bondt & Thaler (1985) provide the empirical evidence that rational correction (reversals following overreaction) exists but is incomplete. BalancedAnalyst's bounded correction capacity (400 shares) models this partial correction.
- Relevance to This Investor: analysis_threshold = 0.05 calibrated to the threshold below which rational correction begins dominating; order_size = 400 is intentionally smaller than BeliefAnchor (500) + SelectiveScanner (600) combined.

#### 4.3.3  Design Purpose and Activation Scenarios

**Purpose**: Provide rational mean-reversion correction that limits (but cannot fully prevent) confirmation-bias-driven mispricing.

**Activation Scenarios**:
- Scenario A (|deviation| < 5%): Hold -- within rational tolerance; not enough mispricing to justify correction costs.
- Scenario B (Undervaluation, deviation < -5%): Buy -- rational fundamental buying.
- Scenario C (Overvaluation, deviation > +5%): Sell -- rational fundamental selling.

**Market Contribution**: Stabilizing -- partial correction; combined with ContrarianTrader provides 900 units of stabilizing capacity vs. biased agents' 1100.

#### 4.3.4  Behavioral Framework

**4.3.4.1  Decision Information Set**
- `deviation`: Sole signal; symmetric treatment -- no prior beliefs.

**4.3.4.2  Core Behavioral Mechanism**
1. If deviation < -analysis_threshold (-0.05): buy order_size = 400.
2. If deviation > +analysis_threshold (+0.05): sell order_size = 400.
3. Hold if |deviation| <= 0.05.

**4.3.4.3  Mathematical Model**
- Trigger: buy if δ < -0.05; sell if δ > +0.05
- Sizing: Q = min(400, floor(cash / price)) or min(400, position)

| Parameter          | Value | Meaning                                        | Config Path                                            | Source                                |
|--------------------|-------|------------------------------------------------|--------------------------------------------------------|---------------------------------------|
| analysis_threshold | 0.05  | Minimum deviation to trigger rational trading  | `ConfirmationBias/Rule/config.yaml -> balanced_analyst` | Fama (1970); De Bondt & Thaler (1985) |
| order_size         | 400   | Fixed trade size (slightly below BeliefAnchor) | `ConfirmationBias/Rule/config.yaml -> balanced_analyst` | Normalization                         |

**4.3.4.4  Behavioral Properties**: Rational, objective, symmetric, unbiased.

#### 4.3.5  Decision Process Walkthrough

Given: deviation = +0.06, position = 1000

Trigger: 0.06 > 0.05 -> sell. Q = 400. Order: sell 400.

#### 4.3.6  Worked Numerical Example

Market state: price = 93.5, deviation = -0.065. Trigger: -0.065 < -0.05 -> buy 400.

#### 4.3.7  Academic References

| # | Citation                                                                                                                                  | Notes                                                       |
|---|-------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| 1 | Fama, E. F. (1970). "Efficient capital markets." *Journal of Finance*, 25(2), 383-417. DOI: 10.2307/2325486                               | Rational information processing baseline                    |
| 2 | De Bondt, W. F. M., & Thaler, R. H. (1985). "Does the stock market overreacttheta" *Journal of Finance*, 40(3), 793-805. DOI: 10.2307/2327804 | Partial correction evidence; analysis_threshold calibration |


---

## Source Docstring Excerpts

### Rule / `BalancedAnalyst`

```text
Evaluates all evidence equally regardless of prior beliefs.

Theory: simulation-bases.md Section 4.3 -- BalancedAnalyst
Theoretical basis: Bayesian rational updating; processes signals without cognitive
bias, providing mean-reversion force that stabilizes price around fundamentals.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMBalancedAnalyst`

```text
LLM-driven balanced analyst -- Bayesian rational updater, no cognitive bias. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMBalancedAnalyst`

```text
RuleLLM-driven balanced analyst -- Bayesian rational updater, no cognitive bias. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMBalancedAnalyst`

```text
RAG-augmented balanced analyst -- Bayesian rational updater, no cognitive bias. Theory: simulation-bases.md Section 4.3.
```
