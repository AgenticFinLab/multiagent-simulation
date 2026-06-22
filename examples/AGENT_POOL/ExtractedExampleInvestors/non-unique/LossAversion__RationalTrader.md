# LossAversion / Rational Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LossAversion |
| Agent type | Rational Trader |
| Canonical class | `RationalTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Expected-utility maximiser that corrects mispricings when deviation exceeds 3%. Provides a rational-agent baseline against which loss-aversion wealth penalties are benchmarked. Capacity capped at 500 shares to reflect practical limits to arbitrage.

## Financial Theory / Theoretical Basis

### Rule / `RationalTrader`
- Theory: simulation-bases.md Section 4.3
- Foundation: Glosten & Milgrom (1985) doi:10.1016/0304-405X(85)90044-3
- Formula: qty = min(500, int(|deviation| x risk_aversion x 3000))

### LLM / `LLMRationalTrader`
- LLM-driven RationalTrader. Theory: simulation-bases.md Section 4.3

### RuleLLM / `RuleLLMRationalTrader`
- Hybrid: RationalTrader rules + LLM reasoning. Theory: simulation-bases.md Section 4.3

### Rag / `RagLLMRationalTrader`
- RAG-augmented: RationalTrader rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.3

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `300`<br>LLM: `300`<br>RuleLLM: `300`<br>Rag: `300` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1500000.0`<br>LLM: `1500000.0`<br>RuleLLM: `1500000.0`<br>Rag: `1500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LossAversion.LLM.prompts:LLM_RATIONAL_PROMPT', 'user_message': 'examples.LossAversion.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LossAversion.RuleLLM.prompts:RULELLM_RATIONAL_PROMPT', 'user_message': 'examples.LossAversion.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LossAversion.Rag.prompts:RULELLM_RATIONAL_PROMPT', 'user_message': 'examples.LossAversion.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| risk_aversion | Rule: `0.7`<br>LLM: `0.7`<br>RuleLLM: `0.7`<br>Rag: `0.7` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | rationaltrader | RationalTrader | `RationalTrader` | 2 | `examples/LossAversion/Rule/players.py` |
| LLM | rationaltrader | RationalTrader | `LLMRationalTrader` | 2 | `examples/LossAversion/LLM/players.py` |
| RuleLLM | rationaltrader | RationalTrader | `RuleLLMRationalTrader` | 2 | `examples/LossAversion/RuleLLM/players.py` |
| Rag | rationaltrader | RationalTrader | `RagLLMRationalTrader` | 2 | `examples/LossAversion/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.3 RationalTrader

**Summary**: Expected-utility maximiser that corrects mispricings when deviation exceeds 3%. Provides a rational-agent baseline against which loss-aversion wealth penalties are benchmarked. Capacity capped at 500 shares to reflect practical limits to arbitrage.

**Foundation**: Glosten, L. R., & Milgrom, P. R. (1985). doi:10.1016/0304-405X(85)90044-3; Shleifer, A. (2000). *Inefficient Markets*. Oxford University Press.

**Design Purpose**: Encode the force that prevents loss-aversion distortions from becoming infinite -- rational arbitrageurs trade against mispricing but are size-constrained. Their wealth accumulation relative to biased agents measures the cost of behavioural biases.

**Behavioral Framework**:

| Decision Variable          | Logic                            | Formula                                     |
|----------------------------|----------------------------------|---------------------------------------------|
| Deviation threshold        | Minimum mispricing to act        | `abs(deviation) > 0.03`                     |
| Quantity                   | Proportional to mispricing       | `min(500, int(abs(deviation) x risk_aversion x 3000))` |
| Direction                  | Buy underpriced, sell overpriced | `deviation < 0 -> buy; deviation > 0 -> sell` |
| Cash / position constraint | Cannot exceed holdings           | Standard min caps                           |

**Decision Walkthrough**:
1. Receive market update with `deviation`.
2. If `|deviation| <= 0.03`: hold -- noise level; no signal.
3. Else: `qty = min(500, int(|deviation| x 0.5 x 3000))`.
4. `deviation < 0`: buy up to `int(cash / price)` shares.
5. `deviation > 0`: sell up to current position.

**Worked Example**: deviation = -0.06. qty = `min(500, int(0.06 x 0.5 x 3000)) = min(500, 90) = 90`. Buy 90 shares, pushing price toward fundamental.

**References**: simulation-bases.md Section 2 Theory 5 (Market Making); doi:10.1016/0304-405X(85)90044-3

---

## Source Docstring Excerpts

### Rule / `RationalTrader`

```text
Rational: makes decisions based on expected utility, no bias.

Theory: simulation-bases.md Section 4.3
Foundation: Glosten & Milgrom (1985) doi:10.1016/0304-405X(85)90044-3
Activation: |deviation| > 0.03
Formula: qty = min(500, int(|deviation| x risk_aversion x 3000))
```

### LLM / `LLMRationalTrader`

```text
LLM-driven RationalTrader. Theory: simulation-bases.md Section 4.3
```

### RuleLLM / `RuleLLMRationalTrader`

```text
Hybrid: RationalTrader rules + LLM reasoning. Theory: simulation-bases.md Section 4.3
```

### Rag / `RagLLMRationalTrader`

```text
RAG-augmented: RationalTrader rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.3
```
