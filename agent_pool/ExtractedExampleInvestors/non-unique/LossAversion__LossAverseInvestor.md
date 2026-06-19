# LossAversion / Loss Averse Investor

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | LossAversion |
| Agent type | Loss Averse Investor |
| Canonical class | `LossAverseInvestor` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

**Summary**: Implements Kahneman & Tversky's (1979) loss-aversion coefficient lambda = 2.25 in position-management decisions. Sells winners quickly at a small gain threshold and clings to losers far longer due to the asymmetric loss-pain multiplier.

## Financial Theory / Theoretical Basis

### Rule / `LossAverseInvestor`
- Loss averse: values losses 2.25x more than gains (prospect theory).
- Theory: simulation-bases.md Section 4.1
- Foundation: Kahneman & Tversky (1979) doi:10.2307/1914185;
- Odean (1998) doi:10.1111/0022-1082.00072
- Formula (gain): sell_qty = min(position, int(position x 0.7))
- Formula (loss): sell_qty = min(position, int(position x 0.2))

### LLM / `LLMLossAverseInvestor`
- LLM-driven LossAverseInvestor. Theory: simulation-bases.md Section 4.1

### RuleLLM / `RuleLLMLossAverseInvestor`
- Hybrid: LossAverseInvestor rules + LLM reasoning. Theory: simulation-bases.md Section 4.1

### Rag / `RagLLMLossAverseInvestor`
- RAG-augmented: LossAverseInvestor rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.1

## Behavior and Decision Logic

- Key implementation methods: `_make_decision`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `400`<br>LLM: `400`<br>RuleLLM: `400`<br>Rag: `400` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1000000.0`<br>LLM: `1000000.0`<br>RuleLLM: `1000000.0`<br>Rag: `1000000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.LossAversion.LLM.prompts:LLM_LOSS_AVERSE_PROMPT', 'user_message': 'examples.LossAversion.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}`<br>RuleLLM: `{'sys_message': 'examples.LossAversion.RuleLLM.prompts:RULELLM_LOSS_AVERSE_PROMPT', 'user_message': 'examples.LossAversion.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}`<br>Rag: `{'sys_message': 'examples.LossAversion.Rag.prompts:RULELLM_LOSS_AVERSE_PROMPT', 'user_message': 'examples.LossAversion.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.7, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| loss_aversion_lambda | Rule: `2.25`<br>LLM: `2.25`<br>RuleLLM: `2.25`<br>Rag: `2.25` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| sell_gain_threshold | Rule: `0.05`<br>LLM: `0.05`<br>RuleLLM: `0.05`<br>Rag: `0.05` | LLM, Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | lossaverseinvestor | LossAverseInvestor | `LossAverseInvestor` | 3 | `examples/LossAversion/Rule/players.py` |
| LLM | lossaverseinvestor | LossAverseInvestor | `LLMLossAverseInvestor` | 3 | `examples/LossAversion/LLM/players.py` |
| RuleLLM | lossaverseinvestor | LossAverseInvestor | `RuleLLMLossAverseInvestor` | 3 | `examples/LossAversion/RuleLLM/players.py` |
| Rag | lossaverseinvestor | LossAverseInvestor | `RagLLMLossAverseInvestor` | 3 | `examples/LossAversion/Rag/players.py` |

## Scenario-Theory Excerpts

### Section 4.1 LossAverseInvestor

**Summary**: Implements Kahneman & Tversky's (1979) loss-aversion coefficient lambda = 2.25 in position-management decisions. Sells winners quickly at a small gain threshold and clings to losers far longer due to the asymmetric loss-pain multiplier.

**Foundation**: Kahneman, D., & Tversky, A. (1979). doi:10.2307/1914185; Odean, T. (1998). doi:10.1111/0022-1082.00072

**Design Purpose**: Encode the disposition effect -- PGR > PLR -- so that the simulation produces the asymmetric realisation rates documented in brokerage data. The agent's reluctance to sell losers maintains downward price pressure; its eagerness to sell winners caps upside moves.

**Behavioral Framework**:

| Decision Variable    | Logic                                | Formula                                          |
|----------------------|--------------------------------------|--------------------------------------------------|
| `pnl_pct`            | Floating PnL relative to entry price | `(price - entry_price) / entry_price`            |
| Sell-winner trigger  | Realise gain above small threshold   | `pnl_pct > sell_gain_threshold (0.05)`           |
| Sell-winner quantity | 70% liquidation                      | `min(position, int(position x 0.7))`             |
| Hold-loser threshold | Much more negative, scaled by lambda      | `pnl_pct < -sell_gain x loss_lambda (≈ -0.1125)` |
| Sell-loser quantity  | Minimal 20% liquidation              | `min(position, int(position x 0.2))`             |

**Decision Walkthrough**:
1. Receive market update; compute `pnl_pct = (price - entry_price) / entry_price`.
2. If `pnl_pct > 0.05`: realise gain -- sell 70% of position (winner sold too early).
3. Else if `pnl_pct < -0.1125` (`-0.05 x 2.25`): acknowledge loss -- sell only 20% (loser held too long).
4. Otherwise: hold -- neither gain nor loss threshold crossed.
5. Update `entry_price` only when a new purchase occurs.

**Worked Example**: entry_price = 100, current price = 106, pnl_pct = +0.06 > 0.05 -> sell `int(500 x 0.7) = 350` shares. If price = 88, pnl_pct = -0.12 < -0.1125 -> sell only `int(500 x 0.2) = 100` shares. The 3.5x asymmetry in sell quantity mirrors the disposition effect.

**References**: simulation-bases.md Section 2 Theory 1 (Prospect Theory); doi:10.2307/1914185; doi:10.1111/0022-1082.00072

---

## Source Docstring Excerpts

### Rule / `LossAverseInvestor`

```text
Loss averse: values losses 2.25x more than gains (prospect theory).

Sells winners too early and holds losers too long.

Theory: simulation-bases.md Section 4.1
Foundation: Kahneman & Tversky (1979) doi:10.2307/1914185;
            Odean (1998) doi:10.1111/0022-1082.00072
Activation: pnl_pct > sell_gain_threshold (gain) or
            pnl_pct < -sell_gain x loss_aversion_lambda (loss)
Formula (gain): sell_qty = min(position, int(position x 0.7))
Formula (loss): sell_qty = min(position, int(position x 0.2))
```

### LLM / `LLMLossAverseInvestor`

```text
LLM-driven LossAverseInvestor. Theory: simulation-bases.md Section 4.1
```

### RuleLLM / `RuleLLMLossAverseInvestor`

```text
Hybrid: LossAverseInvestor rules + LLM reasoning. Theory: simulation-bases.md Section 4.1
```

### Rag / `RagLLMLossAverseInvestor`

```text
RAG-augmented: LossAverseInvestor rules + LLM + retrieved knowledge. Theory: simulation-bases.md Section 4.1
```
