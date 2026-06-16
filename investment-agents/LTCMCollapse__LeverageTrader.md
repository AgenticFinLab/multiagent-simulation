# LTCMCollapse / Leverage Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LTCMCollapse |
| Agent type | Leverage Trader |
| Canonical class | `LeverageTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The `LeverageTrader` represents balance-sheet-constrained investors whose actions are dominated by leverage and margin pressure. Under normal undervaluation the trader may buy; under equity erosion it must deleverage.

## Financial Theory / Theoretical Basis

### Rule / `LeverageTrader`
- Theory: simulation-bases.md Section 4.2 -- LeverageTrader
- Theoretical basis: Geanakoplos (2010) leverage cycle.

### LLM / `LLMLeverageTrader`
- Theory: simulation-bases.md Section 4.2 -- LeverageTrader.

### RuleLLM / `RuleLLMLeverageTrader`
- Theory: simulation-bases.md Section 4.2 -- LeverageTrader.

### Rag / `RagLLMLeverageTrader`
- RAG margin-pressure deleveraging trader. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `3000000.0`<br>LLM: `3000000.0`<br>RuleLLM: `3000000.0`<br>Rag: `3000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| leverage_ratio | Rule: `25`<br>LLM: `25`<br>RuleLLM: `25`<br>Rag: `25` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LTCMCollapse.LLM.prompts:LLM_LEVERAGETRADER_PROMPT', 'user_message': 'examples.LTCMCollapse.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LTCMCollapse.RuleLLM.prompts:RULELLM_LEVERAGETRADER_PROMPT', 'user_message': 'examples.LTCMCollapse.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LTCMCollapse.Rag.prompts:RAG_LEVERAGETRADER_PROMPT', 'user_message': 'examples.LTCMCollapse.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| margin_call_threshold | Rule: `0.04`<br>LLM: `0.04`<br>RuleLLM: `0.04`<br>Rag: `0.04` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | leveragetrader | LeverageTrader | `LeverageTrader` | 2 | `examples/LTCMCollapse/Rule/players.py` |
| LLM | leveragetrader | LeverageTrader | `LLMLeverageTrader` | 2 | `examples/LTCMCollapse/LLM/players.py` |
| RuleLLM | leveragetrader | LeverageTrader | `RuleLLMLeverageTrader` | 2 | `examples/LTCMCollapse/RuleLLM/players.py` |
| Rag | leveragetrader | LeverageTrader | `RagLLMLeverageTrader` | 2 | `examples/LTCMCollapse/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 LeverageTrader

#### Section 4.2.1 Summary

The `LeverageTrader` represents balance-sheet-constrained investors whose actions are dominated by leverage and margin pressure. Under normal undervaluation the trader may buy; under equity erosion it must deleverage.

This investor produces forced selling pressure after losses accumulate, capturing the leverage-cycle channel of the LTCM crisis.

#### Section 4.2.2 Theoretical and Empirical Foundation

The primary basis is the leverage cycle (Section 2.2). The code computes equity from portfolio value and leverage exposure, then triggers a 30% deleveraging order when equity falls below a margin-call threshold.

#### Section 4.2.3 Design Purpose and Activation Scenarios

| Market Condition | Response | Economic Effect | Theory |
|---|---|---|---|
| Equity below margin threshold | Deleverage 30% of absolute position | Fire-sale pressure or short covering | Section 2.2 |
| `deviation < -0.03` and no margin breach | Buy with leveraged capacity | Adds convergence exposure | Section 2.1, Section 2.2 |
| Otherwise | Hold | No new pressure | Section 2.2 |

#### Section 4.2.4 Behavioral Framework

Trigger:

```
equity(t) < margin_call_threshold * |position(t) * P(t)|
```

Sizing:

```
Q_delever(t) = floor(0.30 * |position(t)|)
```

The agent tracks cash and position and reacts to price through current portfolio value.

#### Section 4.2.5 Decision Process Walkthrough

When losses reduce equity below the margin-call threshold, the trader sells if long and buys if short. If no margin call is active and the asset is undervalued by more than 3%, the trader adds a leveraged long.

#### Section 4.2.6 Worked Numerical Example

If position is 500 shares, the forced deleveraging quantity is:

```
Q = floor(0.30 * 500) = 150
```

#### Section 4.2.7 Academic References

Geanakoplos (2010); Brunnermeier & Pedersen (2009); Jorion (2000).

## Source Docstring Excerpts

### Rule / `LeverageTrader`

```text
Highly leveraged trader forced to deleverage when losses mount.

Theory: simulation-bases.md Section 4.2 -- LeverageTrader
Theoretical basis: Geanakoplos (2010) leverage cycle.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMLeverageTrader`

```text
LLM-driven margin-pressure deleveraging trader.

Theory: simulation-bases.md Section 4.2 -- LeverageTrader.
```

### RuleLLM / `RuleLLMLeverageTrader`

```text
RuleLLM margin-pressure deleveraging trader.

Theory: simulation-bases.md Section 4.2 -- LeverageTrader.
```

### Rag / `RagLLMLeverageTrader`

```text
RAG margin-pressure deleveraging trader. Theory: simulation-bases.md Section 4.2.
```
