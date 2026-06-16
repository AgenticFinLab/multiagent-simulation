# LossAversion / Break Even Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LossAversion |
| Agent type | Break Even Trader |
| Canonical class | `BreakEvenTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Operationalises CPT's prediction that investors in a loss position are in the convex (risk-seeking) region of the value function and therefore escalate their position to gamble back to break-even. Activation is triggered by a -5% loss threshold; intensity scales with loss depth.

## Financial Theory / Theoretical Basis

### Rule / `BreakEvenTrader`
- Break-even effect: takes excessive risk to recover losses.
- Theory: simulation-bases.md Section 4.2
- Foundation: Tversky & Kahneman (1992) doi:10.1007/BF00122574;
- Barberis & Xiong (2009) doi:10.1111/j.1540-6261.2009.01448.x
- Formula: risky_qty = min(int(|pnl_pct| x risk_increase_factor x 5000), int(cash/price))

### LLM / `LLMBreakEvenTrader`
- LLM-driven BreakEvenTrader. Theory: simulation-bases.md Section 4.2

### RuleLLM / `RuleLLMBreakEvenTrader`
- Hybrid: BreakEvenTrader rules + LLM reasoning. Theory: simulation-bases.md Section 4.2

### Rag / `RagLLMBreakEvenTrader`
- RAG-augmented: BreakEvenTrader rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.2

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `350`<br>LLM: `350`<br>RuleLLM: `350`<br>Rag: `350` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1200000.0`<br>LLM: `1200000.0`<br>RuleLLM: `1200000.0`<br>Rag: `1200000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LossAversion.LLM.prompts:LLM_BREAK_EVEN_PROMPT', 'user_message': 'examples.LossAversion.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LossAversion.RuleLLM.prompts:RULELLM_BREAK_EVEN_PROMPT', 'user_message': 'examples.LossAversion.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LossAversion.Rag.prompts:RULELLM_BREAK_EVEN_PROMPT', 'user_message': 'examples.LossAversion.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.8, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| risk_increase_factor | Rule: `2.0`<br>LLM: `2.0`<br>RuleLLM: `2.0`<br>Rag: `2.0` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | breakeventrader | BreakEvenTrader | `BreakEvenTrader` | 2 | `examples/LossAversion/Rule/players.py` |
| LLM | breakeventrader | BreakEvenTrader | `LLMBreakEvenTrader` | 2 | `examples/LossAversion/LLM/players.py` |
| RuleLLM | breakeventrader | BreakEvenTrader | `RuleLLMBreakEvenTrader` | 2 | `examples/LossAversion/RuleLLM/players.py` |
| Rag | breakeventrader | BreakEvenTrader | `RagLLMBreakEvenTrader` | 2 | `examples/LossAversion/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.2 BreakEvenTrader

**Summary**: Operationalises CPT's prediction that investors in a loss position are in the convex (risk-seeking) region of the value function and therefore escalate their position to gamble back to break-even. Activation is triggered by a -5% loss threshold; intensity scales with loss depth.

**Foundation**: Tversky, A., & Kahneman, D. (1992). doi:10.1007/BF00122574; Barberis, N., & Xiong, W. (2009). doi:10.1111/j.1540-6261.2009.01448.x

**Design Purpose**: Capture the "doubling down" behaviour that amplifies losses in bear markets and contributes to momentum crashes. The agent's buying pressure at depressed prices creates a temporary floor, but can accelerate losses if the position continues to decline.

**Behavioral Framework**:

| Decision Variable    | Logic                                | Formula                               |
|----------------------|--------------------------------------|---------------------------------------|
| `pnl_pct`            | Floating PnL relative to entry price | `(price - entry_price) / entry_price` |
| Activation threshold | Enters loss-domain convex region     | `pnl_pct < -0.05`                     |
| Risky quantity       | Escalates with loss depth            | `min(int(abs(pnl_pct) x risk_increase_factor x 5000), int(cash / price))` |
| Cash constraint      | Cannot exceed available cash         | `int(cash / price)`                   |

**Decision Walkthrough**:
1. Receive market update; compute `pnl_pct`.
2. If `pnl_pct >= -0.05`: hold -- not yet in the convex loss domain.
3. Else: compute `risky_qty = min(int(|pnl_pct| x 2.0 x 5000), int(cash / price))`.
4. If `risky_qty > 0`: submit buy order to attempt break-even recovery.
5. Escalation ensures deeper losses -> larger buy orders (risk-seeking in losses).

**Worked Example**: entry_price = 100, price = 92, pnl_pct = -0.08. risky_qty = `min(int(0.08 x 2.0 x 5000), cash/92) = min(800, cash_constraint)`. If cash = 50000, max_buy = 543 -> buys 543 shares, deepening exposure.

**References**: simulation-bases.md Section 2 Theory 2 (CPT); doi:10.1007/BF00122574; doi:10.1111/j.1540-6261.2009.01448.x

---

## Source Docstring Excerpts

### Rule / `BreakEvenTrader`

```text
Break-even effect: takes excessive risk to recover losses.

Theory: simulation-bases.md Section 4.2
Foundation: Tversky & Kahneman (1992) doi:10.1007/BF00122574;
            Barberis & Xiong (2009) doi:10.1111/j.1540-6261.2009.01448.x
Activation: pnl_pct < -0.05
Formula: risky_qty = min(int(|pnl_pct| x risk_increase_factor x 5000), int(cash/price))
```

### LLM / `LLMBreakEvenTrader`

```text
LLM-driven BreakEvenTrader. Theory: simulation-bases.md Section 4.2
```

### RuleLLM / `RuleLLMBreakEvenTrader`

```text
Hybrid: BreakEvenTrader rules + LLM reasoning. Theory: simulation-bases.md Section 4.2
```

### Rag / `RagLLMBreakEvenTrader`

```text
RAG-augmented: BreakEvenTrader rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.2
```
