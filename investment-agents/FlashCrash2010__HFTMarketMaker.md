# FlashCrash2010 / HFT Market Maker

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | FlashCrash2010 |
| Agent type | HFT Market Maker |
| Canonical class | `HFTMarketMaker` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Role:** HFT liquidity provider; withdraws under stress -- primary amplification mechanism.

## Financial Theory / Theoretical Basis

### Rule / `HFTMarketMaker`
- Theory: simulation-bases.md Section 4.1 -- HFTMarketMaker
- Theoretical basis: Kirilenko et al. (2017) HFT market maker stress response;

### LLM / `LLMHFTMarketMaker`
- LLM-driven HFT market maker -- liquidity withdrawal under stress via LLM reasoning. Theory: simulation-bases.md Section 4.1.

### RuleLLM / `RuleLLMHFTMarketMaker`
- Hybrid: HFT liquidity withdrawal rules + LLM reasoning. Theory: simulation-bases.md Section 4.1.

### Rag / `RagLLMHFTMarketMaker`
- RAG-augmented HFT market maker -- liquidity withdrawal rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.1.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `40.0`<br>LLM: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0`<br>LLM: `0`<br>RuleLLM: `0`<br>Rag: `0` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `40.0`<br>LLM: `40.0`<br>RuleLLM: `40.0`<br>Rag: `40.0` | LLM, Rag, Rule, RuleLLM |
| inventory_limit | Rule: `1000`<br>LLM: `1000`<br>RuleLLM: `1000`<br>Rag: `1000` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.FlashCrash2010.LLM.prompts:LLM_HFT_MARKET_MAKER_SYS', 'user_message': 'examples.FlashCrash2010.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.FlashCrash2010.RuleLLM.prompts:RULELLM_HFT_MARKET_MAKER_SYS', 'user_message': 'examples.FlashCrash2010.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.FlashCrash2010.Rag.prompts:RAGLLM_HFT_MARKET_MAKER_SYS', 'user_message': 'examples.FlashCrash2010.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}` | LLM, Rag, RuleLLM |
| mm_qty | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| normal_spread | Rule: `0.0001`<br>LLM: `0.0001`<br>RuleLLM: `0.0001`<br>Rag: `0.0001` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| stress_spread | Rule: `0.005`<br>LLM: `0.005`<br>RuleLLM: `0.005`<br>Rag: `0.005` | LLM, Rag, Rule, RuleLLM |
| withdrawal_threshold | Rule: `0.02`<br>LLM: `0.02`<br>RuleLLM: `0.02`<br>Rag: `0.02` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | hftmarketmaker | HFTMarketMaker | `HFTMarketMaker` | 3 | `examples/FlashCrash2010/Rule/players.py` |
| LLM | hftmarketmaker | HFTMarketMaker | `LLMHFTMarketMaker` | 3 | `examples/FlashCrash2010/LLM/players.py` |
| RuleLLM | hftmarketmaker | HFTMarketMaker | `RuleLLMHFTMarketMaker` | 3 | `examples/FlashCrash2010/RuleLLM/players.py` |
| Rag | hftmarketmaker | HFTMarketMaker | `RagLLMHFTMarketMaker` | 3 | `examples/FlashCrash2010/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 HFTMarketMaker

**Role:** HFT liquidity provider; withdraws under stress -- primary amplification mechanism.

**Behavioural model:**
```python
# 5-round velocity computation
velocity = mean(|return_i| for i in last 5 rounds)
stressed = velocity > withdrawal_threshold

if not stressed:
    provides_liquidity = True
    quantity = 500                # normal liquidity provision
    spread = normal_spread
else:
    provides_liquidity = False
    quantity = 0                  # complete withdrawal
    spread = stress_spread
```

**Parameters:** `withdrawal_threshold`, `normal_spread`, `stress_spread`, `inventory_limit`

**Decision rule:** Provides liquidity (500 units) and uses tight spread in normal conditions; completely withdraws when 5-round price velocity exceeds `withdrawal_threshold`.

**Market effect:** Withdrawal increases `hft_participation` denominator drop -> `stress_factor` collapses -> `Depth` shrinks -> price impact amplifies.

**Theory:** Kirilenko et al. (2017) -- HFT stress response; Biais et al. (2015) -- spread widening.

**Diversity:** Varied `withdrawal_threshold` (0.005-0.03) across instances -- staggered withdrawal.

**Distinguishing feature:** `agent_type = "hft"` flag drives the market's depth calculation; withdrawal is the single largest amplifier.

---

## Source Docstring Excerpts

### Rule / `HFTMarketMaker`

```text
HFT market maker with liquidity withdrawal under stress.

Theory: simulation-bases.md Section 4.1 -- HFTMarketMaker
Theoretical basis: Kirilenko et al. (2017) HFT market maker stress response;
rapid spread widening and withdrawal when volatility exceeds threshold
creates a self-reinforcing liquidity vacuum during the 2010 flash crash.
See simulation-bases.md Section 4.1 for mathematical model.

Parameters from config extras:
    - initial_cash, initial_position, normal_spread, stress_spread,
      inventory_limit, withdrawal_threshold, custom_state_hot_limit, record_path
```

### LLM / `LLMHFTMarketMaker`

```text
LLM-driven HFT market maker -- liquidity withdrawal under stress via LLM reasoning. Theory: simulation-bases.md Section 4.1.
```

### RuleLLM / `RuleLLMHFTMarketMaker`

```text
Hybrid: HFT liquidity withdrawal rules + LLM reasoning. Theory: simulation-bases.md Section 4.1.
```

### Rag / `RagLLMHFTMarketMaker`

```text
RAG-augmented HFT market maker -- liquidity withdrawal rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.1.
```
