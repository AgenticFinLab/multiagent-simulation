# EndowmentEffect / Endowed Holder

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EndowmentEffect |
| Agent type | Endowed Holder |
| Canonical class | `EndowedHolder` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

A heavily endowed investor who values owned shares far above market price due to maximum ownership attachment. Sells only when price exceeds a large endowment premium threshold; creates persistent upward price pressure and suppresses trading volume. Embodies the strongest form of the endowment effect.

## Financial Theory / Theoretical Basis

### Rule / `EndowedHolder`
- Theory: simulation-bases.md Section 4.1 -- EndowedHolder
- Theoretical basis: Kahneman, Knetsch & Thaler (1990) endowment effect; ownership

### LLM / `LLMEndowedHolder`
- LLM-driven endowed holder -- attachment bias suppresses selling via LLM reasoning. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMEndowedHolder`
- RuleLLM endowed holder -- ownership premium suppresses selling below threshold. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMEndowedHolder`
- RAG-augmented endowed holder -- ownership premium with historical ownership bias literature. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| endowment_premium | Rule: `0.15`<br>LLM: `0.15`<br>RuleLLM: `0.15`<br>Rag: `0.15` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `800000.0`<br>LLM: `800000.0`<br>RuleLLM: `800000.0`<br>Rag: `800000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.EndowmentEffect.LLM.prompts:LLM_ENDOWED_HOLDER_SYS', 'user_message': 'examples.EndowmentEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.EndowmentEffect.RuleLLM.prompts:RULELLM_ENDOWED_HOLDER_SYS', 'user_message': 'examples.EndowmentEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.EndowmentEffect.Rag.prompts:RAG_ENDOWED_HOLDER_SYS', 'user_message': 'examples.EndowmentEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.6, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| sell_reluctance | Rule: `0.3` | Rule |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | endowedholder | EndowedHolder | `EndowedHolder` | 2 | `examples/EndowmentEffect/Rule/players.py` |
| LLM | endowedholder | EndowedHolder | `LLMEndowedHolder` | 2 | `examples/EndowmentEffect/LLM/players.py` |
| RuleLLM | endowedholder | EndowedHolder | `RuleLLMEndowedHolder` | 2 | `examples/EndowmentEffect/RuleLLM/players.py` |
| Rag | endowedholder | EndowedHolder | `RagLLMEndowedHolder` | 2 | `examples/EndowmentEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 EndowedHolder

#### 4.1.1 Summary

A heavily endowed investor who values owned shares far above market price due to maximum ownership attachment. Sells only when price exceeds a large endowment premium threshold; creates persistent upward price pressure and suppresses trading volume. Embodies the strongest form of the endowment effect.

#### 4.1.2 Theoretical and Empirical Foundation

- **Kahneman, Knetsch & Thaler (1990)**: Endowment effect; WTA/WTP ratio of 2-7 for identical objects. DOI: `10.1086/261737`. Mechanism: ownership frames selling as a loss; loss aversion coefficient lambda ≈ 2.25 drives WTA > market price.
- **Shefrin & Statman (1985)**: Disposition effect; extreme reluctance to realize losses combines with endowment attachment to suppress selling. DOI: `10.1111/j.1540-6261.1985.tb05002.x`.

#### 4.1.3 Design Purpose and Activation Scenarios

- **Activates when**: Price exceeds `fundamental x (1 + endowment_premium)` -> sells; price falls below `fundamental x (1 - 0.05)` -> buys
- **Role in phenomenon**: Destabilizing -- suppresses selling below the endowment threshold, keeping prices above fundamental
- **Interaction effects**: Resists RationalArbitrageur sell pressure; amplifies StatusQuoSeller resistance layer

#### 4.1.4 Behavioral Framework

**Information set**: current price, fundamental value, deviation, personal `endowment_premium` and `sell_reluctance` parameters

**Mechanism narrative**: EndowedHolder adds a large ownership premium to their minimum acceptable sale price. They will only sell if price exceeds `fundamental x (1 + endowment_premium)`. Below this threshold they hold regardless of market conditions, creating a persistent volume suppression. When selling, they sell only `position x sell_reluctance` shares, reflecting reluctance to liquidate fully.

**Mathematical model**:
```
threshold = fundamental x (1 + endowment_premium)
if price > threshold:
    sell_q = min(int(position x sell_reluctance), position)
    sell(sell_q)
elif deviation < -0.05:
    buy_q = min(500, int(cash / price))
    buy(buy_q)
else: hold()
```

**Behavioral properties**: Strong loss aversion (lambda ≈ 2.25), high ownership attachment, low trading frequency, asymmetric buy/sell thresholds

#### 4.1.5 Decision Process Walkthrough

1. Receive market broadcast: extract price, fundamental, deviation
2. Compute endowment threshold = fundamental x (1 + endowment_premium)
3. If price > threshold -> sell `position x sell_reluctance` shares (reluctant partial sell)
4. Else if deviation < -0.05 -> buy up to 500 shares (buys undervalued)
5. Otherwise -> hold

#### 4.1.6 Worked Numerical Example

Given: price = 112, fundamental = 100, endowment_premium = 0.15, position = 1000, sell_reluctance = 0.30

- Endowment threshold = 100 x 1.15 = 115; price (112) < 115 -> do NOT sell
- deviation = (112 - 100)/100 = 0.12 > -0.05 -> do NOT buy
- Decision: **hold**

Given: price = 120, fundamental = 100, endowment_premium = 0.15, position = 1000, sell_reluctance = 0.30

- Endowment threshold = 115; price (120) > 115 -> sell 1000 x 0.30 = **300 shares**

#### 4.1.7 Academic References

- Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1990). Experimental tests of the endowment effect. *Journal of Political Economy*, 98(6), 1325-1348. DOI: 10.1086/261737
- Shefrin, H., & Statman, M. (1985). The disposition to sell winners too early. *Journal of Finance*, 40(3), 777-790. DOI: 10.1111/j.1540-6261.1985.tb05002.x

---

## Source Docstring Excerpts

### Rule / `EndowedHolder`

```text
Values owned assets above market price, reluctant to sell at fair value.

Theory: simulation-bases.md Section 4.1 -- EndowedHolder
Theoretical basis: Kahneman, Knetsch & Thaler (1990) endowment effect; ownership
increases subjective value above market price, suppressing rational selling.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMEndowedHolder`

```text
LLM-driven endowed holder -- attachment bias suppresses selling via LLM reasoning. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMEndowedHolder`

```text
RuleLLM endowed holder -- ownership premium suppresses selling below threshold. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMEndowedHolder`

```text
RAG-augmented endowed holder -- ownership premium with historical ownership bias literature. Theory: simulation-bases.md Section 4.1.
```
