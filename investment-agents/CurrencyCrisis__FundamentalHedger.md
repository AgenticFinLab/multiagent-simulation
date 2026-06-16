# CurrencyCrisis / Fundamental Hedger

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CurrencyCrisis |
| Agent type | Fundamental Hedger |
| Canonical class | `FundamentalHedger` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**4.4.1 Economic Role**: Hedger who trades based on fundamental value, not speculative expectations.

## Financial Theory / Theoretical Basis

### Rule / `FundamentalHedger`
- Theory: simulation-bases.md Section 4.4 -- FundamentalHedger
- Theoretical basis: Morris & Shin (1998) global games; fundamental analysis anchors

### LLM / `LLMFundamentalHedger`
- LLM-driven fundamental hedger -- trades on fundamental value, not speculation. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMFundamentalHedger`
- RuleLLM-driven fundamental hedger -- trades on fundamental value, not speculation. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMFundamentalHedger`
- RAG-augmented fundamental hedger -- trades on fundamental value, not speculation. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| hedge_ratio | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `2000`<br>LLM: `2000`<br>RuleLLM: `2000`<br>Rag: `2000` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.CurrencyCrisis.LLM.prompts:LLM_FUNDAMENTAL_HEDGER_SYS', 'user_message': 'examples.CurrencyCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CurrencyCrisis.RuleLLM.prompts:RULELLM_FUNDAMENTAL_HEDGER_SYS', 'user_message': 'examples.CurrencyCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CurrencyCrisis.Rag.prompts:RAG_FUNDAMENTAL_HEDGER_SYS', 'user_message': 'examples.CurrencyCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `400` | Rule |
| position_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | fundamentalhedger | FundamentalHedger | `FundamentalHedger` | 1 | `examples/CurrencyCrisis/Rule/players.py` |
| LLM | fundamentalhedger | FundamentalHedger | `LLMFundamentalHedger` | 1 | `examples/CurrencyCrisis/LLM/players.py` |
| RuleLLM | fundamentalhedger | FundamentalHedger | `RuleLLMFundamentalHedger` | 1 | `examples/CurrencyCrisis/RuleLLM/players.py` |
| Rag | fundamentalhedger | FundamentalHedger | `RagLLMFundamentalHedger` | 1 | `examples/CurrencyCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 FundamentalHedger

**4.4.1 Economic Role**: Hedger who trades based on fundamental value, not speculative expectations.

**4.4.2 Destabilizing/Stabilizing**: Stabilizing -- buys at deep discounts to fundamental; sells at premiums; provides mean-reversion anchor.

**4.4.3 Mathematical Model**:

```
qty(t) = order_size   if deviation < -hedge_ratio   [buy]
qty(t) = order_size   if deviation > hedge_ratio    [sell]
qty(t) = 0            otherwise
```

Parameters: `hedge_ratio` = 0.05, `order_size` = 400, `initial_position` = 2000.

**4.4.4 Calibration Targets**: Activates at ±5% deviation from peg; provides stabilizing flow without reserve constraints.

**4.4.5 Historical Analogue**: Long-term institutional investors using purchasing-power-parity models; exporters hedging FX exposure.

**4.4.6 Interaction Pattern**: Provides supplementary floor below CentralBankDefender; activates at deeper discount than Defender.

**4.4.7 Diversity Contribution**: Models the fundamental-anchoring channel (Morris & Shin, 1998) that can prevent self-fulfilling attacks if fundamental value is sound.

---

## Source Docstring Excerpts

### Rule / `FundamentalHedger`

```text
Hedges based on fundamental analysis rather than speculative expectations.

Theory: simulation-bases.md Section 4.4 -- FundamentalHedger
Theoretical basis: Morris & Shin (1998) global games; fundamental analysis anchors
against self-fulfilling crises when underlying value is sound.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMFundamentalHedger`

```text
LLM-driven fundamental hedger -- trades on fundamental value, not speculation. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMFundamentalHedger`

```text
RuleLLM-driven fundamental hedger -- trades on fundamental value, not speculation. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMFundamentalHedger`

```text
RAG-augmented fundamental hedger -- trades on fundamental value, not speculation. Theory: simulation-bases.md Section 4.4.
```
