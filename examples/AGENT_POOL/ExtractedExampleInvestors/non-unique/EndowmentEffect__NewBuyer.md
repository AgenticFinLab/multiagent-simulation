# EndowmentEffect / New Buyer

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EndowmentEffect |
| Agent type | New Buyer |
| Canonical class | `NewBuyer` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

A new entrant who evaluates assets purely at market value with no ownership bias, representing the rational WTP side of the endowment gap. Provides corrective buying when prices are below or at fundamental.

## Financial Theory / Theoretical Basis

### Rule / `NewBuyer`
- Theory: simulation-bases.md Section 4.4 -- NewBuyer
- Theoretical basis: Kahneman et al. (1990) -- buyers unaffected by endowment effect;

### LLM / `LLMNewBuyer`
- LLM-driven unbiased new buyer -- evaluates assets at market price, no ownership distortion. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMNewBuyer`
- RuleLLM unbiased new buyer -- fundamental evaluation rules, no ownership bias. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMNewBuyer`
- RAG-augmented new buyer -- unbiased fundamental evaluation with buyer behavior literature. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| buy_threshold | Rule: `0.03`<br>LLM: `0.03`<br>RuleLLM: `0.03`<br>Rag: `0.03` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.EndowmentEffect.LLM.prompts:LLM_NEW_BUYER_SYS', 'user_message': 'examples.EndowmentEffect.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.EndowmentEffect.RuleLLM.prompts:RULELLM_NEW_BUYER_SYS', 'user_message': 'examples.EndowmentEffect.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.EndowmentEffect.Rag.prompts:RAG_NEW_BUYER_SYS', 'user_message': 'examples.EndowmentEffect.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | newbuyer | NewBuyer | `NewBuyer` | 2 | `examples/EndowmentEffect/Rule/players.py` |
| LLM | newbuyer | NewBuyer | `LLMNewBuyer` | 2 | `examples/EndowmentEffect/LLM/players.py` |
| RuleLLM | newbuyer | NewBuyer | `RuleLLMNewBuyer` | 2 | `examples/EndowmentEffect/RuleLLM/players.py` |
| Rag | newbuyer | NewBuyer | `RagLLMNewBuyer` | 2 | `examples/EndowmentEffect/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 NewBuyer

#### 4.4.1 Summary

A new entrant who evaluates assets purely at market value with no ownership bias, representing the rational WTP side of the endowment gap. Provides corrective buying when prices are below or at fundamental.

#### 4.4.2 Theoretical and Empirical Foundation

- **Kahneman, Knetsch & Thaler (1990)**: Buyers unaffected by endowment effect -- WTP equals rational valuation. DOI: `10.1086/261737`.
- **Plott & Zeiler (2005)**: Without ownership priming, subjects exhibit no WTA/WTP gap. DOI: `10.1257/aer.95.3.530`.

#### 4.4.3 Design Purpose and Activation Scenarios

- **Activates when**: `deviation < buy_threshold` (buys at or below fundamental); `deviation > 0.10` (sells overvalued)
- **Role in phenomenon**: Stabilizing -- buys when EndowedHolder refuses to sell; partially fills volume gap
- **Interaction effects**: Provides demand-side correction; acts as the rational WTP counterpart to EndowedHolder's inflated WTA

#### 4.4.4 Behavioral Framework

**Information set**: price, fundamental, deviation

**Mechanism narrative**: NewBuyer has no ownership attachment and applies pure value-investing logic. Buys at or below fundamental; sells above 10% premium.

**Mathematical model**:
```
if deviation < buy_threshold:
    buy(min(500, int(cash / price)))
elif deviation > 0.10:
    sell(min(400, position))
else: hold()
```

**Behavioral properties**: Rational WTP, unbiased, contrarian relative to endowed sellers

#### 4.4.5 Decision Process Walkthrough

1. Observe deviation from market broadcast
2. If deviation < buy_threshold -> buy up to 500 shares
3. If deviation > 0.10 -> sell up to 400 shares
4. Otherwise -> hold

#### 4.4.6 Worked Numerical Example

Given: deviation = -0.03, buy_threshold = 0.0

- -0.03 < 0.0 -> **buy** min(500, int(cash / price)) shares

#### 4.4.7 Academic References

- Kahneman, D. et al. (1990). *Journal of Political Economy*, 98(6). DOI: 10.1086/261737
- Plott, C. R., & Zeiler, K. (2005). *American Economic Review*, 95(3). DOI: 10.1257/aer.95.3.530

---

## Source Docstring Excerpts

### Rule / `NewBuyer`

```text
Evaluates assets at market price without ownership bias.

Theory: simulation-bases.md Section 4.4 -- NewBuyer
Theoretical basis: Kahneman et al. (1990) -- buyers unaffected by endowment effect;
provides rational price discovery and stabilizes the market from the buy side.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMNewBuyer`

```text
LLM-driven unbiased new buyer -- evaluates assets at market price, no ownership distortion. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMNewBuyer`

```text
RuleLLM unbiased new buyer -- fundamental evaluation rules, no ownership bias. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMNewBuyer`

```text
RAG-augmented new buyer -- unbiased fundamental evaluation with buyer behavior literature. Theory: simulation-bases.md Section 4.4.
```
