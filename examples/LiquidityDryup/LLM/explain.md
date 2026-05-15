# LiquidityDryup — LLM Variant Explanation

## §1 Overview

| Item               | Description                                                                                                               |
|--------------------|---------------------------------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Liquidity dry-up with LLM-driven market maker withdrawal — agents reason about stress signals and decide when to withdraw |
| **Variant**        | LLM-based: all 5 investor classes use language model reasoning with persona-specific system prompts                       |
| **Investor Count** | 5 LLM classes: LLMMarketMaker, LLMLiquiditySeeker, LLMValueTrader, LLMMomentumTrader, LLMNoiseTrader (approx.)            |
| **Key Feature**    | Emergent market maker withdrawal coordination — LLMs observe liquidity levels and may follow others' withdrawal           |
| **Academic Value** | Tests whether LLM agents reproduce Brunnermeier–Pedersen liquidity spirals through narrative reasoning                    |

---

## §2 Theory → Implementation Mapping

### §2.1 LLM MarketMaker (simulation-bases.md §4.1)

| Theory Element           | LLM Implementation                                                                   |
|--------------------------|--------------------------------------------------------------------------------------|
| Inventory risk threshold | System prompt describes withdrawal conditions: "liquidity < 50" or "volatility > 2%" |
| Emergent coordination    | LLM observes total liquidity in user message — may follow peers' withdrawal signal   |
| Social observation       | Prompt: "others are withdrawing" context provided when liquidity falls               |
| Quantity                 | LLM determines inventory adjustment; hard constraints enforced post-LLM              |

### §2.2 LLM LiquiditySeeker (simulation-bases.md §4.2)

| Theory Element       | LLM Implementation                                                      |
|----------------------|-------------------------------------------------------------------------|
| Random trade need    | LLM reasons about urgency of trade given liquidity conditions           |
| Execution constraint | Prompt frames liquidity as a cost — LLM may reduce quantity voluntarily |
| Narrative framing    | "You must trade, but liquidity is low — adjust accordingly"             |

### §2.3 LLM ValueTrader (simulation-bases.md §4.3)

| Theory Element                 | LLM Implementation                                                                 |
|--------------------------------|------------------------------------------------------------------------------------|
| Crisis opportunity recognition | Prompt frames low-liquidity, high-deviation periods as buying opportunities        |
| Fundamental anchoring          | LLM receives `{price, fundamental, deviation%}` and decides if "prime opportunity" |
| Liquidity provision            | Prompt instructs: "provide liquidity when others flee"                             |

### §2.4 LLM MomentumTrader (simulation-bases.md §4.4)

| Theory Element        | LLM Implementation                                                  |
|-----------------------|---------------------------------------------------------------------|
| Trend following       | Prompt describes momentum strategy: follow return direction         |
| Cascade amplification | LLM may amplify momentum when liquidity is low (higher price moves) |

### §2.5 LLM NoiseTrader (simulation-bases.md §4.5)

| Theory Element    | LLM Implementation                                       |
|-------------------|----------------------------------------------------------|
| Random order flow | Prompt produces uncertain, context-aware random trading  |
| Low coherence     | LLM may occasionally deviate from expected noise pattern |

---

## §3 Market Mechanism

Same rule-based `Market` as Rule variant. Price formation:

```
P(t+1) = P(t) + (λ × NetDemand × liquidity_factor) + γ × (F − P(t)) + ε(t)
liquidity_factor = 100 / max(total_liquidity, 10)
```

LLM agent flow per round:
1. Market broadcasts `{price, return, liquidity, fundamental}`.
2. Each LLM agent constructs user message with full market context.
3. LLM called; response parsed for `{quantity, provides_liquidity, reasoning}`.
4. Hard constraints enforced (cash/position limits).
5. `provides_liquidity` from LLM directly influences `total_liquidity`.

Key LLM dynamic: if MarketMaker LLMs observe `liquidity < threshold` in user message, they may coordinate withdrawal even without an explicit formula trigger.

---

## §4 Variant Architecture

```
LLM Variant Architecture
─────────────────────────
Market (rule-based, liquidity-dependent pricing)
  │  broadcast {price, return%, liquidity, fundamental}
  ├─ LLM MarketMaker     │ [withdrawal system prompt] → LLM → provides_liquidity
  ├─ LLM LiquiditySeeker │ [execution prompt] → LLM → quantity
  ├─ LLM ValueTrader     │ [crisis-opportunity prompt] → LLM → value buy
  ├─ LLM MomentumTrader  │ [momentum prompt] → LLM → trend quantity
  └─ LLM NoiseTrader     │ [noise prompt] → LLM → random-ish quantity
```

Prompts defined in `examples/LiquidityDryup/LLM/prompts.py`.

---

## §5 Config Reference

| Parameter           | Agent         | Default      | Description               |
|---------------------|---------------|--------------|---------------------------|
| `llm.model`         | All LLM       | (configured) | LLM model identifier      |
| `llm.temperature`   | All LLM       | 0.3          | Sampling temperature      |
| `base_liquidity`    | Market        | 30           | Reference liquidity level |
| `fundamental_value` | Market        | 100          | Fundamental anchor        |
| `price_impact`      | Market        | 0.001        | Base λ                    |
| `mean_reversion`    | Market        | 0.05         | γ                         |
| `initial_cash`      | All investors | 100000       | Starting cash             |

---

## §6 Running Instructions

```bash
# Run LLM variant
python examples/LiquidityDryup/LLM/run_llm.py \
    -c configs/LiquidityDryup/LLM/simulation.yml

# Run with lower temperature for consistency
python examples/LiquidityDryup/LLM/run_llm.py \
    -c configs/LiquidityDryup/LLM/simulation.yml \
    --extras llm.temperature=0.1
```

Output written to `records/LiquidityDryup/LLM/`.

---

## §7 Expected Behavior

| Metric            | Expected Range | Rationale                                                                 |
|-------------------|----------------|---------------------------------------------------------------------------|
| LRI minimum       | 0.05–0.30      | LLM coordination may be slower or faster than rule threshold              |
| MWF maximum       | 0.5–1.0        | Emergent LLM withdrawal — may not be simultaneous                         |
| PAD               | 0.08–0.20      | Slightly lower dislocation — LLM may provide more nuanced crisis response |
| LPD               | 8–20 rounds    | LLM may recover faster if ValueTrader prompt is opportunistic             |
| WDI               | 0.20–0.40      | Moderate redistribution                                                   |
| LPI (MarketMaker) | 0.30–0.70      | LLM MMs may partially withdraw (not binary)                               |

LLM variant introduces variance — some runs may show no dry-up (LLM resists withdrawal), others may show faster cascades (LLM coordinates).

---

## §8 References

- Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:[10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098)
- Grossman, S. J., & Miller, M. H. (1988). doi:[10.1111/j.1540-6261.1988.tb04594.x](https://doi.org/10.1111/j.1540-6261.1988.tb04594.x)
- Kyle, A. S. (1985). doi:[10.2307/1913210](https://doi.org/10.2307/1913210)
- simulation-bases.md §4.1–§4.5 (Investor Taxonomy)
- examples/LiquidityDryup/LLM/prompts.py (System prompt definitions)

---

## §9 Variant Comparison

| Dimension        | Rule               | LLM                    | RuleLLM           | Rag                   |
|------------------|--------------------|------------------------|-------------------|-----------------------|
| MM withdrawal    | Volatility formula | LLM social observation | Rule + LLM timing | Rule + KB crisis data |
| Cascade speed    | Deterministic      | Variable               | Rule-anchored     | RAG may slow onset    |
| Expected LRI min | 0.05–0.20          | 0.05–0.30              | 0.05–0.25         | 0.10–0.30             |
| Expected LPD     | 10–25              | 8–20                   | 9–22              | 6–15 (shortest)       |
| Run variance     | Low                | High                   | Moderate          | Moderate              |
