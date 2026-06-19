# EuropeanDebtCrisis / ECB Intervenor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | EuropeanDebtCrisis |
| Agent type | ECB Intervenor |
| Canonical class | `ECBIntervenor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The `ECBIntervenor` represents credible central-bank backstop purchases. It is the main crisis-resolution force when peripheral bond prices fall far below fundamental value.

## Financial Theory / Theoretical Basis

### Rule / `ECBIntervenor`
- Theory: simulation-bases.md Section 4.4 -- ECBIntervenor
- Theoretical basis: Draghi (2012) 'whatever it takes' backstop mechanism; credible

### LLM / `LLMECBIntervenor`
- LLM-driven ECB intervenor -- whatever-it-takes backstop logic via LLM reasoning. Theory: simulation-bases.md Section 4.4.

### RuleLLM / `RuleLLMECBIntervenor`
- RuleLLM ECB intervenor -- backstop threshold rules with LLM policy reasoning. Theory: simulation-bases.md Section 4.4.

### Rag / `RagLLMECBIntervenor`
- RAG-augmented ECB intervenor -- backstop purchases with monetary policy literature. Theory: simulation-bases.md Section 4.4.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| core_price | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| ecb_threshold | LLM: `8.0`<br>RuleLLM: `8.0`<br>Rag: `8.0` | LLM, Rag, RuleLLM |
| fundamental_value | LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, RuleLLM |
| initial_cash | Rule: `5000000.0`<br>LLM: `5000000.0`<br>RuleLLM: `5000000.0`<br>Rag: `5000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | LLM: `95.0`<br>RuleLLM: `95.0`<br>Rag: `95.0` | LLM, Rag, RuleLLM |
| intervention_size | Rule: `600`<br>LLM: `600`<br>RuleLLM: `600`<br>Rag: `600` | LLM, Rag, Rule, RuleLLM |
| intervention_threshold | Rule: `-0.2` | Rule |
| llm | LLM: `{'sys_message': 'examples.EuropeanDebtCrisis.LLM.prompts:LLM_ECB_INTERVENOR_SYS', 'user_message': 'examples.EuropeanDebtCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_ECB_INTERVENOR_SYS', 'user_message': 'examples.EuropeanDebtCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.EuropeanDebtCrisis.Rag.prompts:RAG_ECB_INTERVENOR_SYS', 'user_message': 'examples.EuropeanDebtCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | ecbintervenor | ECBIntervenor | `ECBIntervenor` | 1 | `examples/EuropeanDebtCrisis/Rule/players.py` |
| LLM | ecbintervenor | ECBIntervenor | `LLMECBIntervenor` | 1 | `examples/EuropeanDebtCrisis/LLM/players.py` |
| RuleLLM | ecbintervenor | ECBIntervenor | `RuleLLMECBIntervenor` | 1 | `examples/EuropeanDebtCrisis/RuleLLM/players.py` |
| Rag | ecbintervenor | ECBIntervenor | `RagLLMECBIntervenor` | 1 | `examples/EuropeanDebtCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 ECBIntervenor

#### Section 4.4.1 Summary

The `ECBIntervenor` represents credible central-bank backstop purchases. It is the main crisis-resolution force when peripheral bond prices fall far below fundamental value.

#### Section 4.4.2 Theoretical and Empirical Foundation

The basis is Draghi's 2012 commitment and De Grauwe's lender-of-last-resort argument (Section 2.4). The agent is intentionally asymmetric: it buys more aggressively in crisis than it sells after recovery.

#### Section 4.4.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| `deviation < intervention_threshold` | buy | stops the self-fulfilling spiral | Section 2.4 |
| `deviation > 0.05` | sell | normalizes balance sheet after stress | Section 2.4 |

#### Section 4.4.4 Behavioral Framework

```
if deviation < intervention_threshold: buy min(800, cash / price)
elif deviation > 0.05: sell min(500, position)
else: hold
```

#### Section 4.4.5 Decision Process Walkthrough

At deviation -25% with intervention threshold -20%, the ECB proxy buys because the crisis has reached systemic stress.

#### Section 4.4.6 Worked Numerical Example

With cash 5,000,000 and price 75, affordable quantity is above 800, so the intervention order is 800.

#### Section 4.4.7 Academic References

Draghi (2012); De Grauwe (2011).

## Source Docstring Excerpts

### Rule / `ECBIntervenor`

```text
Provides liquidity support and bond purchases to stabilize spreads.

Theory: simulation-bases.md Section 4.4 -- ECBIntervenor
Theoretical basis: Draghi (2012) 'whatever it takes' backstop mechanism; credible
central bank commitment halts self-fulfilling crisis spiral.
See simulation-bases.md Section 4.4 for mathematical model.
```

### LLM / `LLMECBIntervenor`

```text
LLM-driven ECB intervenor -- whatever-it-takes backstop logic via LLM reasoning. Theory: simulation-bases.md Section 4.4.
```

### RuleLLM / `RuleLLMECBIntervenor`

```text
RuleLLM ECB intervenor -- backstop threshold rules with LLM policy reasoning. Theory: simulation-bases.md Section 4.4.
```

### Rag / `RagLLMECBIntervenor`

```text
RAG-augmented ECB intervenor -- backstop purchases with monetary policy literature. Theory: simulation-bases.md Section 4.4.
```
