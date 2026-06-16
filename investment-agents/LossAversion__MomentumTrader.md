# LossAversion / Momentum Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LossAversion |
| Agent type | Momentum Trader |
| Canonical class | `MomentumTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Trend follower that buys when price is above fundamental and sells when below, reinforcing existing momentum. Activates at `|deviation| > entry_threshold` and sizes orders proportionally to deviation magnitude.

## Financial Theory / Theoretical Basis

### Rule / `MomentumTrader`
- Theory: simulation-bases.md Section 4.4
- Foundation: Jegadeesh & Titman (1993) doi:10.1111/j.1540-6261.1993.tb04702.x
- Formula: qty = min(500, int(|deviation| x 3000))

### LLM / `LLMMomentumTrader`
- LLM-driven MomentumTrader. Theory: simulation-bases.md Section 4.4

### RuleLLM / `RuleLLMMomentumTrader`
- Hybrid: MomentumTrader rules + LLM reasoning. Theory: simulation-bases.md Section 4.4

### Rag / `RagLLMMomentumTrader`
- RAG-augmented: MomentumTrader rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.4

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| entry_threshold | Rule: `0.03`<br>LLM: `0.03`<br>RuleLLM: `0.03`<br>Rag: `0.03` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LossAversion.LLM.prompts:LLM_MOMENTUM_PROMPT', 'user_message': 'examples.LossAversion.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LossAversion.RuleLLM.prompts:RULELLM_MOMENTUM_PROMPT', 'user_message': 'examples.LossAversion.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LossAversion.Rag.prompts:RULELLM_MOMENTUM_PROMPT', 'user_message': 'examples.LossAversion.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | momentumtrader | MomentumTrader | `MomentumTrader` | 2 | `examples/LossAversion/Rule/players.py` |
| LLM | momentumtrader | MomentumTrader | `LLMMomentumTrader` | 2 | `examples/LossAversion/LLM/players.py` |
| RuleLLM | momentumtrader | MomentumTrader | `RuleLLMMomentumTrader` | 2 | `examples/LossAversion/RuleLLM/players.py` |
| Rag | momentumtrader | MomentumTrader | `RagLLMMomentumTrader` | 2 | `examples/LossAversion/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.4 MomentumTrader

**Summary**: Trend follower that buys when price is above fundamental and sells when below, reinforcing existing momentum. Activates at `|deviation| > entry_threshold` and sizes orders proportionally to deviation magnitude.

**Foundation**: Jegadeesh, N., & Titman, S. (1993). Returns to Buying Winners and Selling Losers. *Journal of Finance*, 48(1), 65-91. doi:[10.1111/j.1540-6261.1993.tb04702.x](https://doi.org/10.1111/j.1540-6261.1993.tb04702.x)

**Design Purpose**: Introduce trend-reinforcing order flow that interacts with the disposition effect. Loss-averse selling of winners creates downward pressure that momentum traders may exacerbate; loss-averse holding of losers starves downtrend momentum.

**Behavioral Framework**:

| Decision Variable | Logic                       | Formula                                     |
|-------------------|-----------------------------|---------------------------------------------|
| Entry threshold   | Minimum trend to follow     | `abs(deviation) > entry_threshold`          |
| Quantity          | Proportional to deviation   | `min(500, int(abs(deviation) x 3000))`      |
| Direction         | Buy uptrend, sell downtrend | `deviation > 0 -> buy; deviation < 0 -> sell` |
| Constraint        | Cash / position bounded     | Standard min caps                           |

**Decision Walkthrough**:
1. Receive market update.
2. If `|deviation| <= entry_threshold`: hold.
3. Else: `qty = min(500, int(|deviation| x 3000))`.
4. `deviation > 0`: buy (price above fundamental -- uptrend).
5. `deviation < 0`: sell (price below fundamental -- downtrend).

**Worked Example**: deviation = +0.04. qty = `min(500, int(0.04 x 3000)) = 120`. Buy 120 shares, amplifying the upward move.

**References**: simulation-bases.md Section 2 Theory 3 (Disposition Effect interaction); doi:10.1111/j.1540-6261.1993.tb04702.x

---

## Source Docstring Excerpts

### Rule / `MomentumTrader`

```text
Momentum: follows price trends.

Theory: simulation-bases.md Section 4.4
Foundation: Jegadeesh & Titman (1993) doi:10.1111/j.1540-6261.1993.tb04702.x
Activation: |deviation| > entry_threshold (0.03)
Formula: qty = min(500, int(|deviation| x 3000))
```

### LLM / `LLMMomentumTrader`

```text
LLM-driven MomentumTrader. Theory: simulation-bases.md Section 4.4
```

### RuleLLM / `RuleLLMMomentumTrader`

```text
Hybrid: MomentumTrader rules + LLM reasoning. Theory: simulation-bases.md Section 4.4
```

### Rag / `RagLLMMomentumTrader`

```text
RAG-augmented: MomentumTrader rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.4
```
