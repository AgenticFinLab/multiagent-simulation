# CurrencyCrisis / Speculative Attacker

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | CurrencyCrisis |
| Agent type | Speculative Attacker |
| Canonical class | `SpeculativeAttacker` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**4.1.1 Economic Role**: Short-seller of the vulnerable currency; profits from forced devaluation.

## Financial Theory / Theoretical Basis

### Rule / `SpeculativeAttacker`
- Theory: simulation-bases.md Section 4.1 -- SpeculativeAttacker
- Theoretical basis: Krugman (1979) first-generation crisis model; speculators attack

### LLM / `LLMSpeculativeAttacker`
- LLM-driven speculative attacker -- shorts vulnerable currency on reserve weakness. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMSpeculativeAttacker`
- RuleLLM-driven speculative attacker -- shorts vulnerable currency on reserve weakness. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMSpeculativeAttacker`
- RAG-augmented speculative attacker -- shorts vulnerable currency on reserve weakness. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| attack_threshold | Rule: `0.03`<br>LLM: `0.03`<br>RuleLLM: `0.03`<br>Rag: `0.03` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `5000`<br>LLM: `5000`<br>RuleLLM: `5000`<br>Rag: `5000` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.CurrencyCrisis.LLM.prompts:LLM_SPECULATIVE_ATTACKER_SYS', 'user_message': 'examples.CurrencyCrisis.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.CurrencyCrisis.RuleLLM.prompts:RULELLM_SPECULATIVE_ATTACKER_SYS', 'user_message': 'examples.CurrencyCrisis.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.CurrencyCrisis.Rag.prompts:RAG_SPECULATIVE_ATTACKER_SYS', 'user_message': 'examples.CurrencyCrisis.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| order_size | Rule: `600` | Rule |
| position_size | Rule: `800`<br>LLM: `800`<br>RuleLLM: `800`<br>Rag: `800` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | speculativeattacker | SpeculativeAttacker | `SpeculativeAttacker` | 2 | `examples/CurrencyCrisis/Rule/players.py` |
| LLM | speculativeattacker | SpeculativeAttacker | `LLMSpeculativeAttacker` | 2 | `examples/CurrencyCrisis/LLM/players.py` |
| RuleLLM | speculativeattacker | SpeculativeAttacker | `RuleLLMSpeculativeAttacker` | 2 | `examples/CurrencyCrisis/RuleLLM/players.py` |
| Rag | speculativeattacker | SpeculativeAttacker | `RagLLMSpeculativeAttacker` | 2 | `examples/CurrencyCrisis/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 SpeculativeAttacker

**4.1.1 Economic Role**: Short-seller of the vulnerable currency; profits from forced devaluation.

**4.1.2 Destabilizing/Stabilizing**: Destabilizing -- large sell orders accelerate currency depreciation; rational when reserve depletion appears likely.

**4.1.3 Mathematical Model**:

```
qty(t) = order_size   if deviation < -attack_threshold  [sell]
qty(t) = order_size   if deviation > +attack_threshold  [buy/cover]
qty(t) = 0            otherwise
```

Parameters: `attack_threshold` = 0.03, `order_size` = 600, `initial_position` = 5000.

**4.1.4 Calibration Targets**: Attack volume activates once the peg is visibly weak; two attacker instances can contribute up to 1,200 units of sell pressure per round.

**4.1.5 Historical Analogue**: George Soros / Quantum Fund during EMS crisis (1992); LTCM/others during Asian crisis (1997).

**4.1.6 Interaction Pattern**: Competes with CentralBankDefender buying; synchronizes with SelfFulfillingTrader selling; destabilizes FundamentalHedger's anchor.

**4.1.7 Diversity Contribution**: Provides the initial attack momentum; distinguishes first-mover speculative aggression from herd behavior.

---

## Source Docstring Excerpts

### Rule / `SpeculativeAttacker`

```text
Builds short positions in vulnerable currency, profiting from forced devaluation.

Theory: simulation-bases.md Section 4.1 -- SpeculativeAttacker
Theoretical basis: Krugman (1979) first-generation crisis model; speculators attack
when reserves appear insufficient; attack size scales with deviation severity.
See simulation-bases.md Section 4.1 for mathematical model.
```

### LLM / `LLMSpeculativeAttacker`

```text
LLM-driven speculative attacker -- shorts vulnerable currency on reserve weakness. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMSpeculativeAttacker`

```text
RuleLLM-driven speculative attacker -- shorts vulnerable currency on reserve weakness. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMSpeculativeAttacker`

```text
RAG-augmented speculative attacker -- shorts vulnerable currency on reserve weakness. Theory: simulation-bases.md Section 4.1.
```
