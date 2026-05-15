# LiquidityDryup — Rag Variant Explanation

## §1 Overview

| Item               | Description                                                                                                                   |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Liquidity dry-up with retrieval-augmented generation — agents consult historical crisis episodes before withdrawal decisions  |
| **Variant**        | Rag: rule threshold triggers; LLM + knowledge base of historical dry-up episodes informs withdrawal depth and recovery timing |
| **Investor Count** | 5 RAG-augmented classes; MarketMaker may moderate withdrawal when KB provides historical recovery evidence                    |
| **Key Feature**    | Historical crisis KB enables agents to contextualise current stress within known dry-up patterns; may moderate spiral         |
| **Academic Value** | Tests whether retrieval of historical precedent reduces liquidity spiral severity and shortens recovery duration              |

---

## §2 Theory → Implementation Mapping

### §2.1 Rag MarketMaker (simulation-bases.md §4.1)

| Theory Element       | Rag Implementation                                                             |
|----------------------|--------------------------------------------------------------------------------|
| Withdrawal trigger   | Rule `                                                                         |
| KB moderation        | If KB shows "spiral reversed after 5 rounds" → LLM may stay partially active   |
| Historical precedent | Episodes: 1987 Black Monday, 1998 LTCM, 2008 GFC, 2010 Flash Crash, 2020 COVID |
| Withdrawal depth     | LLM calibrated by KB evidence about typical spiral depths                      |

### §2.2 Rag LiquiditySeeker (simulation-bases.md §4.2)

| Theory Element       | Rag Implementation                                                                       |
|----------------------|------------------------------------------------------------------------------------------|
| Execution adjustment | KB retrieves historical execution costs during dry-ups; LLM adjusts order more precisely |
| Crisis awareness     | Agent may pause entirely when KB confirms full-scale dry-up                              |

### §2.3 Rag ValueTrader (simulation-bases.md §4.3)

| Theory Element      | Rag Implementation                                                                  |
|---------------------|-------------------------------------------------------------------------------------|
| Crisis entry        | KB retrieves post-crisis recovery data; LLM identifies optimal entry point          |
| Liquidity provision | Historical evidence of crisis reversals accelerates ValueTrader entry → shorter LPD |

### §2.4 Rag MomentumTrader (simulation-bases.md §4.4)

| Theory Element     | Rag Implementation                                                     |
|--------------------|------------------------------------------------------------------------|
| Trend assessment   | KB may retrieve evidence that momentum during dry-ups reverses sharply |
| Cascade moderation | LLM may reduce momentum qty when KB shows high crash-reversal risk     |

### §2.5 Rag NoiseTrader (simulation-bases.md §4.5)

| Theory Element | Rag Implementation                                               |
|----------------|------------------------------------------------------------------|
| Random orders  | KB provides context; LLM may reduce noise during extreme dry-ups |

---

## §3 Market Mechanism

Same rule-based `Market` with liquidity-dependent price impact:

```
P(t+1) = P(t) + (λ × NetDemand × liquidity_factor) + γ × (F − P(t)) + ε(t)
liquidity_factor = 100 / max(total_liquidity, 10)
```

Rag agent flow per round:
1. Market broadcasts data.
2. Rule layer computes preliminary signal.
3. RAG retrieves top-3 most similar historical dry-up episodes by current `|return|` and `LRI`.
4. Retrieved episodes prepended to LLM prompt as "Historical Precedent".
5. LLM calibrates withdrawal depth / recovery timing using historical evidence.
6. `provides_liquidity` feeds back to `total_liquidity`.

---

## §4 Variant Architecture

```
Rag Variant Architecture
─────────────────────────
Knowledge Base (historical dry-up episodes)
  ↓ (top-3 retrieval when |return| > threshold OR LRI < 0.5)
Market (rule-based, liquidity-dependent pricing)
  │  broadcast {price, return%, liquidity, fundamental}
  ├─ Rag MarketMaker     │ rule signal + KB[1987,LTCM,GFC,...] → LLM
  ├─ Rag LiquiditySeeker │ rule scale + KB[execution costs] → LLM
  ├─ Rag ValueTrader     │ rule gate + KB[recovery timelines] → LLM
  ├─ Rag MomentumTrader  │ rule gate + KB[reversal risk] → LLM
  └─ Rag NoiseTrader     │ rule baseline + KB[crisis noise] → LLM
```

**RAG Architecture**:

| Component          | Details                                                                                                                                  |
|--------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| Knowledge Base     | Historical dry-up episodes: 1929 crash, 1987 Black Monday, 1998 LTCM, 2008 GFC (Lehman), 2010 Flash Crash, 2020 COVID-19 liquidity shock |
| Embedding Model    | Text embedding of episode summaries: trigger, depth, duration, recovery mechanism                                                        |
| Retrieval Strategy | Top-3 episodes by similarity to current `                                                                                                |
| Injection Format   | Prepended as "Historical Precedent" in system prompt                                                                                     |
| Trigger Condition  | Retrieve when `                                                                                                                          |

---

## §5 Config Reference

| Parameter              | Agent       | Default      | Description                    |
|------------------------|-------------|--------------|--------------------------------|
| `volatility_threshold` | MarketMaker | 0.03         | Rule trigger                   |
| `base_liquidity`       | MarketMaker | 30           | Maximum normal liquidity       |
| `llm.model`            | All RAG     | (configured) | LLM model                      |
| `llm.temperature`      | All RAG     | 0.3          | Sampling temperature           |
| `rag.kb_path`          | All RAG     | (configured) | Historical episodes KB         |
| `rag.top_k`            | All RAG     | 3            | Retrieved episodes             |
| `rag.trigger_return`   | All RAG     | 0.03         | Return threshold for retrieval |
| `fundamental_value`    | Market      | 100          | Fundamental anchor             |
| `price_impact`         | Market      | 0.001        | Base λ                         |

---

## §6 Running Instructions

```bash
# Run Rag variant
python examples/LiquidityDryup/Rag/run_liquidity_dryup_ragllm.py \
    -c configs/LiquidityDryup/Rag/simulation.yml
```

Output written to `records/LiquidityDryup/Rag/`.

---

## §7 Expected Behavior

| Metric      | Expected Range | Rationale                                                              |
|-------------|----------------|------------------------------------------------------------------------|
| LRI minimum | 0.10–0.30      | Highest among variants — KB moderates withdrawal depth                 |
| MWF maximum | 0.4–0.8        | Partial withdrawal — historical evidence of recovery reduces full exit |
| PAD         | 0.07–0.18      | Smallest dislocation — knowledge-informed position management          |
| LPD         | 6–15 rounds    | Shortest — ValueTrader KB retrieval accelerates crisis-entry timing    |
| WDI         | 0.18–0.35      | Lowest redistribution — less extreme spiral                            |

The Rag variant is expected to produce the shortest dry-up (LPD) and highest minimum liquidity (LRI). The key mechanism: `ValueTrader` agents retrieve post-crisis recovery timelines from the KB and enter the market sooner, providing liquidity that arrests the spiral. `MarketMaker` agents that retrieve Black Monday or Flash Crash data showing swift reversals may stay partially active rather than fully withdrawing.

---

## §8 References

- Brunnermeier, M. K., & Pedersen, L. H. (2009). doi:[10.1093/rfs/hhn098](https://doi.org/10.1093/rfs/hhn098)
- Grossman, S. J., & Miller, M. H. (1988). doi:[10.1111/j.1540-6261.1988.tb04594.x](https://doi.org/10.1111/j.1540-6261.1988.tb04594.x)
- Amihud, Y. (2002). doi:[10.1016/S1386-4181(01)00024-6](https://doi.org/10.1016/S1386-4181(01)00024-6)
- simulation-bases.md §4.1–§4.5 (Investor Taxonomy); §8 Historical Case Studies

---

## §9 Variant Comparison

| Dimension          | Rule                  | LLM             | RuleLLM          | Rag                                      |
|--------------------|-----------------------|-----------------|------------------|------------------------------------------|
| MM withdrawal      | Formula               | LLM social      | Rule + LLM depth | Rule + KB precedent                      |
| Recovery mechanism | ValueTrader threshold | LLM opportunism | Rule + LLM       | KB-informed early entry                  |
| Expected LRI min   | 0.05–0.20             | 0.05–0.30       | 0.05–0.25        | **0.10–0.30** (highest)                  |
| Expected LPD       | 10–25                 | 8–20            | 9–22             | **6–15** (shortest)                      |
| KB role            | None                  | None            | Partial          | Full — crisis precedents guide decisions |
