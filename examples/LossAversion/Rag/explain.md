# LossAversion — Rag Variant Explanation

## §1 Overview

| Item               | Description                                                                                                                 |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------|
| **Phenomenon**     | Prospect-theory loss aversion with retrieval-augmented generation providing behavioural-finance knowledge                   |
| **Variant**        | Rag: rule thresholds trigger signal; LLM + knowledge base of loss-aversion literature enables bias self-recognition         |
| **Investor Count** | 5 RAG-augmented classes mirroring Rule logic with KB-enhanced LLM reasoning                                                 |
| **Key Feature**    | Agents retrieve relevant Prospect Theory and Disposition Effect papers before trading; may recognise and correct own biases |
| **Academic Value** | Tests whether knowledge-retrieval enables genuine debiasing vs. Rule or LLM variants                                        |

---

## §2 Theory → Implementation Mapping

### §2.1 Rag LossAverseInvestor (simulation-bases.md §4.1)

| Theory Element            | Rag Implementation                                                                                     |
|---------------------------|--------------------------------------------------------------------------------------------------------|
| Loss-aversion λ = 2.25    | Rule threshold computes gain/loss triggers; KB papers (Kahneman & Tversky 1979) retrieved when `       |
| Disposition effect        | KB retrieval may surface Odean (1998) PGR/PLR findings; LLM may use this to moderate sell fraction     |
| Self-correction potential | If retrieved paper explicitly documents disposition-effect cost, LLM may decide to sell more of losers |

### §2.2 Rag BreakEvenTrader (simulation-bases.md §4.2)

| Theory Element        | Rag Implementation                                                                                     |
|-----------------------|--------------------------------------------------------------------------------------------------------|
| Break-even escalation | Rule activates at `pnl_pct < −0.05`; KB retrieves Barberis & Xiong (2009) documenting break-even costs |
| Risk reduction        | If KB paper retrieved warns that escalation deepens losses, LLM may reduce `risky_qty`                 |

### §2.3 Rag RationalTrader (simulation-bases.md §4.3)

| Theory Element   | Rag Implementation                                                                    |
|------------------|---------------------------------------------------------------------------------------|
| Expected utility | Rule threshold + KB confirms deviation is significant via fundamental analysis papers |
| KB enhancement   | Glosten & Milgrom (1985) retrieved to confirm arbitrage direction                     |

### §2.4 Rag MomentumTrader (simulation-bases.md §4.4)

| Theory Element   | Rag Implementation                                                                  |
|------------------|-------------------------------------------------------------------------------------|
| Trend following  | Rule threshold; KB retrieves Jegadeesh & Titman (1993) to confirm momentum validity |
| Trend assessment | LLM uses retrieved evidence to determine trend persistence and appropriate quantity |

### §2.5 Rag MarketMaker (simulation-bases.md §4.5)

| Theory Element         | Rag Implementation                                                                              |
|------------------------|-------------------------------------------------------------------------------------------------|
| Liquidity provision    | Rule inventory gate; KB retrieves Ho & Stoll (1981) for optimal spread pricing context          |
| Quantity determination | LLM adjusts size based on retrieved evidence about optimal market-making in volatile conditions |

---

## §3 Market Mechanism

Same rule-based `Market` as all variants. Price formation:

```
P(t+1) = P(t) + λ × NetDemand(t) + γ × (F − P(t)) + ε(t)
```

Rag agent flow per round:
1. Market broadcasts `{price, fundamental, deviation}`.
2. Rule layer computes preliminary action direction and baseline quantity.
3. RAG system retrieves top-3 relevant knowledge base documents based on agent type + current PnL/deviation context.
4. Retrieved documents prepended to LLM prompt as "Research Context".
5. LLM reasons over `{preliminary_signal, retrieved_papers, price_context}`.
6. Hard constraints enforced post-LLM.
7. Orders aggregated; Market updates price.

---

## §4 Variant Architecture

```
Rag Variant Architecture
─────────────────────────
Knowledge Base (behavioural finance papers)
  ↓ (top-3 retrieval when |pnl_pct| > 0.03 OR round triggers)
Market (rule-based)
  │  broadcast {price, fundamental, deviation}
  ├─ Rag LossAverseInvestor  │ rule signal + KB[Kahneman,Odean,...] → LLM
  ├─ Rag BreakEvenTrader     │ rule signal + KB[Barberis,Thaler,...] → LLM
  ├─ Rag RationalTrader      │ rule signal + KB[Glosten,Shleifer,...] → LLM
  ├─ Rag MomentumTrader      │ rule signal + KB[Jegadeesh,...] → LLM
  └─ Rag MarketMaker         │ rule signal + KB[Ho,Stoll,...] → LLM
```

**RAG Architecture**:

| Component          | Details                                                                                                                                                                                 |
|--------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Knowledge Base     | Behavioural finance papers: Kahneman & Tversky (1979), Tversky & Kahneman (1992), Odean (1998), Barberis & Xiong (2009), Shefrin & Statman (1985), Barber & Odean (2000), Thaler (1999) |
| Embedding Model    | Text embedding of paper abstracts and key empirical findings                                                                                                                            |
| Retrieval Strategy | Top-3 most relevant papers by agent type, current PnL% magnitude, and deviation                                                                                                         |
| Injection Format   | Prepended as "Research Context" section in system prompt                                                                                                                                |
| Trigger Condition  | Retrieve when `                                                                                                                                                                         |

---

## §5 Config Reference

Configuration file: `configs/LossAversion/Rag/simulation.yml` → `players.yml`

| Parameter              | Agent              | Default      | Description                     |
|------------------------|--------------------|--------------|---------------------------------|
| `loss_aversion_lambda` | LossAverseInvestor | 2.25         | Rule-layer threshold multiplier |
| `sell_gain_threshold`  | LossAverseInvestor | 0.05         | Rule gain trigger               |
| `risk_increase_factor` | BreakEvenTrader    | 2.0          | Rule escalation factor          |
| `llm.model`            | All RAG agents     | (configured) | LLM model identifier            |
| `llm.temperature`      | All RAG agents     | 0.3          | Sampling temperature            |
| `rag.kb_path`          | All RAG agents     | (configured) | Knowledge base directory        |
| `rag.top_k`            | All RAG agents     | 3            | Number of retrieved documents   |
| `rag.trigger_pnl`      | All RAG agents     | 0.03         | PnL threshold for KB retrieval  |
| `initial_cash`         | All investors      | 100000       | Starting cash                   |
| `initial_position`     | All investors      | 500          | Starting shares                 |

---

## §6 Running Instructions

```bash
# Run Rag variant
python examples/LossAversion/Rag/run_lossaversion_rag.py \
    -c configs/LossAversion/Rag/simulation.yml

# Run with higher retrieval sensitivity
python examples/LossAversion/Rag/run_lossaversion_rag.py \
    -c configs/LossAversion/Rag/simulation.yml \
    --extras rag.trigger_pnl=0.02
```

Output files written to `records/LossAversion/Rag/`.

---

## §7 Expected Behavior

| Metric | Expected Range | Rationale                                                                                        |
|--------|----------------|--------------------------------------------------------------------------------------------------|
| LAI    | 1.4–2.0        | Lowest across variants — KB retrieval surfaces bias documentation, enabling self-correction      |
| DEI    | 1.0–1.8        | Agents may sell more losers when KB confirms the cost of the disposition effect                  |
| BER    | 1.0–2.0        | BreakEvenTrader retrieves Barberis & Xiong; may reduce escalation                                |
| VAF    | 1.2–1.8        | Lowest volatility amplification — KB reduces both disposition selling caps and break-even buying |
| WPI    | 0.85–0.95      | Highest WPI (lowest wealth penalty) — bias reduction leads to better portfolio outcomes          |
| NCE    | 0.30–0.60      | Largest correction — KB enables genuine bias recognition, not just narrative prompting           |

The Rag variant is expected to produce the most debiased behaviour. The critical insight is that `LossAverseInvestor` agents may retrieve the Odean (1998) paper documenting the *cost* of the disposition effect and adjust their own sell fractions accordingly.

---

## §8 References

- Kahneman, D., & Tversky, A. (1979). doi:[10.2307/1914185](https://doi.org/10.2307/1914285)
- Odean, T. (1998). doi:[10.1111/0022-1082.00072](https://doi.org/10.1111/0022-1082.00072)
- Barberis, N., & Xiong, W. (2009). doi:[10.1111/j.1540-6261.2009.01448.x](https://doi.org/10.1111/j.1540-6261.2009.01448.x)
- Shefrin, H., & Statman, M. (1985). doi:[10.1111/j.1540-6261.1985.tb05002.x](https://doi.org/10.1111/j.1540-6261.1985.tb05002.x)
- simulation-bases.md §4.1–§4.5 (Investor Taxonomy)

---

## §9 Variant Comparison

| Dimension              | Rule            | LLM          | RuleLLM    | Rag                                  |
|------------------------|-----------------|--------------|------------|--------------------------------------|
| Loss-aversion encoding | Deterministic λ | Narrative    | Rule + LLM | Rule + KB papers                     |
| Break-even effect      | Fixed formula   | LLM moderate | Rule + LLM | RAG may reduce significantly         |
| Expected LAI           | 2.0–2.8         | 1.6–2.4      | 1.8–2.5    | **1.4–2.0** (lowest)                 |
| Expected WPI           | 0.75–0.90       | 0.80–0.93    | 0.78–0.92  | **0.85–0.95** (highest)              |
| NCE vs. Rule           | —               | 0.15–0.40    | 0.10–0.30  | **0.30–0.60** (strongest)            |
| KB self-correction     | No              | No           | Partial    | Yes — bias documentation retrievable |
