# EndowmentEffect / Rational Arbitrageur

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EndowmentEffect |
| Agent type | Rational Arbitrageur |
| Canonical class | `RationalArbitrageur` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

A fully rational investor who trades at fundamental value with no ownership bias, providing the corrective force that drives prices back toward fair value. Embodies the rational expectations benchmark.

## Financial Theory / Theoretical Basis

### Rule / `RationalArbitrageur`
- Theory: simulation-bases.md Section 4.3 -- RationalArbitrageur
- Theoretical basis: Shleifer & Vishny (1997) limits to arbitrage; exploits

### LLM / `LLMRationalArbitrageur`
- LLM-driven rational arbitrageur -- exploits endowment-bias gap via fundamental analysis. Theory: simulation-bases.md Section 4.3.

### RuleLLM / `RuleLLMRationalArbitrageur`
- RuleLLM rational arbitrageur -- exploits endowment-bias gap with explicit arbitrage rules. Theory: simulation-bases.md Section 4.3.

### Rag / `RagLLMRationalArbitrageur`
- RAG-augmented rational arbitrageur -- fundamental gap trading with arbitrage limit literature. Theory: simulation-bases.md Section 4.3.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| arb_threshold | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.EndowmentEffect.LLM.prompts:LLM_RATIONAL_ARBITRAGEUR_SYS', 'user_message': 'examples.EndowmentEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.EndowmentEffect.RuleLLM.prompts:RULELLM_RATIONAL_ARBITRAGEUR_SYS', 'user_message': 'examples.EndowmentEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.EndowmentEffect.Rag.prompts:RAG_RATIONAL_ARBITRAGEUR_SYS', 'user_message': 'examples.EndowmentEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | rationalarbitrageur | RationalArbitrageur | `RationalArbitrageur` | 2 | `examples/EndowmentEffect/Rule/players.py` |
| LLM | rationalarbitrageur | RationalArbitrageur | `LLMRationalArbitrageur` | 2 | `examples/EndowmentEffect/LLM/players.py` |
| RuleLLM | rationalarbitrageur | RationalArbitrageur | `RuleLLMRationalArbitrageur` | 2 | `examples/EndowmentEffect/RuleLLM/players.py` |
| Rag | rationalarbitrageur | RationalArbitrageur | `RagLLMRationalArbitrageur` | 2 | `examples/EndowmentEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 RationalArbitrageur

#### 4.3.1 Summary

A fully rational investor who trades at fundamental value with no ownership bias, providing the corrective force that drives prices back toward fair value. Embodies the rational expectations benchmark.

#### 4.3.2 Theoretical and Empirical Foundation

- **Muth (1961)**: Rational expectations -- agents incorporate all available information into price. DOI: `10.2307/1905537`.
- **Fama (1970)**: Efficient market hypothesis -- rational arbitrage eliminates systematic mispricings. DOI: `10.2307/2325486`.

#### 4.3.3 Design Purpose and Activation Scenarios

- **Activates when**: `|deviation| > rational_threshold`
- **Role in phenomenon**: Stabilizing -- corrects overvaluation by selling overpriced assets; partially offsets endowment resistance
- **Interaction effects**: Provides downward pressure against EndowedHolder and StatusQuoSeller; insufficient alone to fully correct due to numerical resistance

#### 4.3.4 Behavioral Framework

**Information set**: price, fundamental, deviation

**Mechanism narrative**: RationalArbitrageur computes the pure deviation from fundamental and acts proportionally. No ownership premium -- applies symmetric buy/sell logic.

**Mathematical model**:
```
deviation = (price - fundamental) / fundamental
if deviation > rational_threshold:
    sell(min(order_size x deviation, position))
elif deviation < -rational_threshold:
    buy(min(order_size x |deviation|, affordable))
else: hold()
```

**Behavioral properties**: Fully rational, no cognitive bias, symmetric response, proportional order sizing

#### 4.3.5 Decision Process Walkthrough

1. Compute deviation from fundamental
2. Compare magnitude to rational_threshold
3. Submit proportional sell or buy order

#### 4.3.6 Worked Numerical Example

Given: price = 105, fundamental = 100, rational_threshold = 0.02, order_size = 1000

- deviation = 0.05 > 0.02 -> **sell** min(1000 x 0.05, position) = 50 shares

#### 4.3.7 Academic References

- Muth, J. F. (1961). Rational expectations. *Econometrica*, 29(3), 315-335. DOI: 10.2307/1905537
- Fama, E. F. (1970). Efficient capital markets. *Journal of Finance*, 25(2), 383-417. DOI: 10.2307/2325486

---

## Source Docstring Excerpts

### Rule / `RationalArbitrageur`

```text
Exploits the gap between subjective and objective valuations.

Theory: simulation-bases.md Section 4.3 -- RationalArbitrageur
Theoretical basis: Shleifer & Vishny (1997) limits to arbitrage; exploits
the price gap created by endowment bias, pushing prices toward fundamental.
See simulation-bases.md Section 4.3 for mathematical model.
```

### LLM / `LLMRationalArbitrageur`

```text
LLM-driven rational arbitrageur -- exploits endowment-bias gap via fundamental analysis. Theory: simulation-bases.md Section 4.3.
```

### RuleLLM / `RuleLLMRationalArbitrageur`

```text
RuleLLM rational arbitrageur -- exploits endowment-bias gap with explicit arbitrage rules. Theory: simulation-bases.md Section 4.3.
```

### Rag / `RagLLMRationalArbitrageur`

```text
RAG-augmented rational arbitrageur -- fundamental gap trading with arbitrage limit literature. Theory: simulation-bases.md Section 4.3.
```
