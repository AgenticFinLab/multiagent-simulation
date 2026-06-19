# HindsightBias / Hindsight Overconfident

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | HindsightBias |
| Agent type | Hindsight Overconfident |
| Canonical class | `HindsightOverconfident` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements Fischhoff (1975) hindsight bias -- the agent interprets price moves as "obviously" predictable in retrospect, amplifying momentum by buying when deviation > 0.02 and selling when deviation < -0.02.

## Financial Theory / Theoretical Basis

### Rule / `HindsightOverconfident`
- Theory: simulation-bases.md Section 4.1 -- HindsightOverconfident
- Theoretical basis: Knew-it-all-along effect (Fischhoff, 1975).

### LLM / `LLMHindsightOverconfident`
- LLM-driven HindsightOverconfident: excessive confidence from hindsight reasoning. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMHindsightOverconfident`
- RuleLLM HindsightOverconfident: excessive confidence from hindsight reasoning. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMHindsightOverconfident`
- RAG HindsightOverconfident: excessive confidence from hindsight reasoning. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`, `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| activation_threshold | Rule: `0.02` | Rule |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| hindsight_inflation | Rule: `1.5`<br>LLM: `1.5`<br>RuleLLM: `1.5`<br>Rag: `1.5` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.HindsightBias.LLM.prompts:LLM_HINDSIGHTOVERCONFIDENT_PROMPT', 'user_message': 'examples.HindsightBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.HindsightBias.RuleLLM.prompts:RULELLM_HINDSIGHTOVERCONFIDENT_PROMPT', 'user_message': 'examples.HindsightBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.HindsightBias.Rag.prompts:RAG_HINDSIGHTOVERCONFIDENT_PROMPT', 'user_message': 'examples.HindsightBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.9, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `800`<br>LLM: `800`<br>RuleLLM: `800`<br>Rag: `800` | LLM, Rag, Rule, RuleLLM |
| prediction_overweight | Rule: `1.0` | Rule |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| quantity_scale | Rule: `5000` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | hindsightoverconfident | HindsightOverconfident | `HindsightOverconfident` | 3 | `examples/HindsightBias/Rule/players.py` |
| LLM | hindsightoverconfident | HindsightOverconfident | `LLMHindsightOverconfident` | 3 | `examples/HindsightBias/LLM/players.py` |
| RuleLLM | hindsightoverconfident | HindsightOverconfident | `RuleLLMHindsightOverconfident` | 3 | `examples/HindsightBias/RuleLLM/players.py` |
| Rag | hindsightoverconfident | HindsightOverconfident | `RagLLMHindsightOverconfident` | 3 | `examples/HindsightBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 HindsightOverconfident

**Summary**: Implements Fischhoff (1975) hindsight bias -- the agent interprets price moves as "obviously" predictable in retrospect, amplifying momentum by buying when deviation > 0.02 and selling when deviation < -0.02.

**Theoretical and Empirical Basis**: Fischhoff, B. (1975). "Hindsight ≠ Foresight." *JEP:HPP*, 1(3), 288-299. `doi:10.1037/0096-1523.1.3.288`; Daniel, Hirshleifer & Subrahmanyam (1998). `doi:10.1111/0022-1082.00077`

**Design Purpose**: Encode the "knew-it-all-along" effect in position sizing -- each perceived success inflates confidence via `hindsight_inflation` and `prediction_overweight`, creating a momentum amplifier that drives price away from fundamental.

**Behavioral Framework**:

| Decision Variable   | Logic                                                             | Formula                                                                        |
|---------------------|-------------------------------------------------------------------|--------------------------------------------------------------------------------|
| Activation          | Trades when deviation large enough to trigger hindsight certainty | `abs(deviation) > 0.02`                                                        |
| Direction           | Follows deviation direction (momentum-following)                  | buy if dev > 0; sell if dev < 0                                                |
| Quantity            | Scaled by deviation magnitude x inflation parameters              | `min(800, int(abs(dev) x 5000 x hindsight_inflation x prediction_overweight))` |
| Cash constraint     | Cannot buy more than cash allows                                  | `buy_qty = min(qty, int(cash / price))`                                        |
| Position constraint | Cannot sell more than held                                        | `sell_qty = min(qty, max(position, 0))`                                        |

**Decision Process**:
1. Receive market broadcast: `{price, fundamental, deviation, round}`
2. Check `abs(deviation) > 0.02` -- if not, hold
3. If deviation > 0: bias triggers "this move was obvious" -> buy order
4. If deviation < 0: bias triggers "this decline was obvious" -> sell order
5. Quantity = `min(800, int(abs(dev) x 5000 x hindsight_inflation x prediction_overweight))`

**Worked Example**: fundamental = 100, price = 103.5, deviation = +0.035, hindsight_inflation = 1.2, prediction_overweight = 1.0 -> qty = min(800, int(0.035 x 5000 x 1.2 x 1.0)) = min(800, 210) = 210 shares buy order.

**Academic References**: `simulation-bases.md Section 2 Theory 1`; `doi:10.1037/0096-1523.1.3.288`; `doi:10.1111/0022-1082.00077`

## Source Docstring Excerpts

### Rule / `HindsightOverconfident`

```text
Theory: simulation-bases.md Section 4.1 -- HindsightOverconfident

Theoretical basis: Knew-it-all-along effect (Fischhoff, 1975).
Believes past outcomes were obvious, leading to excessive confidence in predictions.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMHindsightOverconfident`

```text
LLM-driven HindsightOverconfident: excessive confidence from hindsight reasoning. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMHindsightOverconfident`

```text
RuleLLM HindsightOverconfident: excessive confidence from hindsight reasoning. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMHindsightOverconfident`

```text
RAG HindsightOverconfident: excessive confidence from hindsight reasoning. Theory: simulation-bases.md Section 4.1.
```
