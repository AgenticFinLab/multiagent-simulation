# AsianFinancialCrisis Rag — Simulation Documentation

## Overview

| Item                      | Description                                                                                                                                                                       |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**               | Rag                                                                                                                                                                               |
| **Implements**            | `../simulation-bases.md`                                                                                                                                                          |
| **Decision Logic**        | LLM decisions augmented with RAG-retrieved historical crisis knowledge; each agent queries a private knowledge index per round                                                    |
| **Key Difference**        | Agents consult retrieved documents (historical crisis cases, academic papers) before deciding; knowledge-grounded behavioral reasoning rather than pure persona or rule-following |
| **Research Contribution** | Tests whether access to crisis-relevant historical knowledge improves agent decision quality and reduces maladaptive behaviors (panic selling, denial, delayed intervention)      |


## 1. How Theoretical Design Is Implemented

### RagLLMHotMoneyFunder: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.1 — Radelet & Sachs, 1998)*

| Theoretical Design Element         | Implementation                                                                                                        |
|------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Hot money reversal at first stress | RAG retrieves 1997 Thai baht reversal cases; agent prompted: "Based on retrieved knowledge, assess crisis likelihood" |
| No loyalty to market               | Persona preserved: "You have no loyalty to any market" + RAG context provides precedent for exits                     |
| Leveraged — cannot hold drawdowns  | RAG context may retrieve Archegos or LTCM leverage failure cases as crisis analogies                                  |
| Knowledge-enhanced exit timing     | RAG provides historical deviation levels that preceded capitulation; may sharpen or dampen exit threshold             |

### RagLLMContagionTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.2 — Kaminsky & Reinhart, 1999)*

| Theoretical Design Element | Implementation                                                                                                            |
|----------------------------|---------------------------------------------------------------------------------------------------------------------------|
| Dual signal monitoring     | RAG retrieves contagion pattern documents; agent cross-references current signals against historical contagion signatures |
| Front-running contagion    | Retrieved knowledge may identify early contagion indicators the agent uses beyond deviation and price return              |
| Regional crisis awareness  | RAG can retrieve Asian Financial Crisis historical timeline; agent anchors decisions to documented contagion sequences    |
| Knowledge-grounded selling | Agent cites retrieved precedent in reasoning: "Based on historical case X, this signal pattern preceded 30% decline"      |

### RagLLMIMFRescuer: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.3 — Corsetti et al., 1999)*

| Theoretical Design Element     | Implementation                                                                                            |
|--------------------------------|-----------------------------------------------------------------------------------------------------------|
| Patient emergency intervention | RAG retrieves IMF intervention timelines; agent anchors patience to documented intervention precedents    |
| Deep pockets rescue packages   | Prompt context: "$5M rescue fund" + RAG may retrieve historical package sizes (e.g., $17.2B Thai package) |
| Knowledge-calibrated threshold | Historical IMF interventions at specific deviation levels inform agent's own threshold calibration        |
| Market floor signaling         | RAG may retrieve post-intervention price recovery data; agent uses this to justify stabilizing commitment |

### RagLLMValueContrarian: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.4)*

| Theoretical Design Element      | Implementation                                                                                                 |
|---------------------------------|----------------------------------------------------------------------------------------------------------------|
| Mean reversion conviction       | RAG retrieves historical recovery rates after crisis trough; provides empirical base for mean reversion belief |
| Emotionally detached from panic | Retrieved knowledge of similar historical crises that recovered anchors detachment                             |
| Proportional conviction         | RAG context provides historical P/B or deviation-at-trough statistics for sizing calibration                   |
| Buy on panic, sell on euphoria  | Retrieved post-crisis returns inform buy timing; agent may cite "last crisis, recovery was X% in N rounds"     |

### RagLLMNoiseTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.5 — Black, 1986 baseline)*

| Theoretical Design Element | Implementation                                                                                    |
|----------------------------|---------------------------------------------------------------------------------------------------|
| Uninformed random trader   | RAG retrieved — but agent is still uniformed; retrieved knowledge has minimal effect on decisions |
| Small retail participant   | RAG may retrieve retail behavior studies; but trader stays random (persona constraint)            |


## 2. Market Mechanism Implementation

Market mechanism is **identical** to Rule variant — only investor decision logic changes.

*(Full formula: simulation-bases.md §3.1 — P(t+1) = P(t) + 0.04·D + 0.02·(F−P) + ε)*

### RAG System Architecture

Each agent builds or loads a private RAG index on initialization:

```
Agent Init:
  1. ResourceManager resolves knowledge sources (global + local documents)
  2. KnowledgeStore built from MinerU-processed documents
  3. Per-round: KnowledgeQuery(text=market_context, top_k=3)
  4. Retrieved passages injected into user prompt as {rag_context}
```

### Rag User Prompt Variables

| Variable            | Source                  | Format  | Notes                                                        |
|---------------------|-------------------------|---------|--------------------------------------------------------------|
| `{round}`           | market_data.round       | integer | Current simulation round                                     |
| `{price}`           | market_data.price       | float   | Current price                                                |
| `{prev_price}`      | market_data.prev_price  | float   | Previous round price for momentum calculation                |
| `{deviation}`       | market_data.deviation   | `+.2%`  | Primary signal: deviation from fundamental                   |
| `{fundamental}`     | market_data.fundamental | float   | Fundamental value reference                                  |
| `{cash}`            | agent state             | float   | Available cash                                               |
| `{position}`        | agent state             | float   | Current position (shares)                                    |
| `{portfolio_value}` | cash + pos × price      | float   | Total portfolio value                                        |
| `{rag_context}`     | KnowledgeStore.query()  | string  | Top-3 retrieved passages; "(No relevant knowledge)" if empty |

### RAG Query Logic

Per-round query constructed in `_build_prompt()`:
```python
query = KnowledgeQuery(
    text=f"forced liquidation cascade strategy when: "
         f"price={price:.2f}, deviation={deviation:+.2%}",
    top_k=3,
    round_num=round_num,
    agent_id=self.config.identity,
)
```

Query is scenario-specific: deviation magnitude and price level drive which crisis documents are retrieved.

### Response Format

LLM must output canonical JSON inside `<decision>` tags:
```json
{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": "string"}
```

Parsed by `parse_llm_response_with_thinking()` from `examples/llm_utils.py`.


## 3. Variant-Specific Features

- **Per-agent private knowledge index**: Each agent initializes its own `KnowledgeStore` — allows agent-specific document collections (e.g., IMFRescuer gets IMF papers, ContagionTrader gets contagion literature)
- **Shared index fallback**: If local index absent, copies from shared RAG index; if shared absent, builds from `MinerU_processed` documents
- **RAG context quality dependency**: If document sources contain 1997 Asian crisis materials, agent decisions become historically grounded; poor documents → RAG behaves like LLM
- **Knowledge-augmented crisis awareness**: Agents may cite historical crises ("similar to the Thai baht 1997") in reasoning field — validates knowledge retrieval quality
- **Max retries = 3**: If LLM parse fails, agent holds position; ensures simulation completion


## 4. Architecture Diagram

```
Round t:
  ┌─────────────────────────────────────────┐
  │  Market (Rule — identical to Rule)      │
  │  P(t+1) = P(t) + 0.04·D + 0.02·(F−P) + ε │
  │  Broadcasts: {price, prev_price,        │
  │               fundamental, deviation}   │
  └─────────────────┬───────────────────────┘
                    │ market_data
        ┌───────────┼───────────────────────┐
        ▼           ▼           ▼           ▼
  ┌───────────────┐ ┌────────────────┐ ┌───────────────┐ ┌──────────────────┐
  │RagLLMHotMoney │ │RagLLMContagion │ │RagLLMIMF      │ │RagLLMValue       │
  │Funder×2       │ │Trader×2        │ │Rescuer         │ │Contrarian×2      │
  │+ RAG context  │ │+ RAG context   │ │+ RAG context   │ │+ RAG context     │
  │  (crisis exit │ │  (contagion    │ │  (intervention │ │  (recovery data) │
  │   precedents) │ │   patterns)    │ │   timelines)   │ │                  │
  └──────┬────────┘ └──────┬─────────┘ └──────┬────────┘ └─────────┬────────┘
         │                 │                  │                     │
         └─────────────────┴──────────────────┴─────────────────────┘
                           │ investor_bid orders
                           ▼
                   Market aggregates
                   RagLLMNoise×3 also contributes
                   (KnowledgeStore initialized but low impact on noise)
```


## 5. Configuration Reference

| Config Path                                  | Key Parameter   | Value                      | Notes                                           |
|----------------------------------------------|-----------------|----------------------------|-------------------------------------------------|
| `*.extras.llm.sys_message`                   | System prompt   | per agent                  | Behavioral persona; no explicit numerical rules |
| `*.extras.llm.user_message`                  | User template   | `RAG_USER_TEMPLATE`        | Includes `{rag_context}` slot                   |
| `*.extras.knowledge.global_uri`              | Document source | path to docs dir           | Contains crisis research papers                 |
| `*.extras.knowledge.rag.output_position`     | RAG index dir   | `rag_index/`               | Persisted per agent                             |
| `*.extras.private_knowledge.rag.top_k`       | Retrieval k     | 3                          | Top passages retrieved per round                |
| `*.extras.private_knowledge.rag.embed_model` | Embedding model | `openai/hunyuan-embedding` | LiteLLM-compatible embedding                    |

Full config: `configs/AsianFinancialCrisis/Rag/players.yml`


## 6. Running Instructions

```bash
# From project root (requires HUNYUAN_API_KEY or ARK_API_KEY in .env):
python examples/AsianFinancialCrisis/Rag/run_asianfinancialcrisis_rag.py \
    -c configs/AsianFinancialCrisis/Rag/simulation.yml

# Run analysis (uses Rule analysis functions):
python examples/AsianFinancialCrisis/Rule/analysis.py \
    -c configs/AsianFinancialCrisis/Rag/simulation.yml
```

Output: `EXPERIMENT/AsianFinancialCrisis/Rag/records/`

**Prerequisites:**
1. Documents in `examples/document-sources/` (or configured `global_uri`)
2. MinerU preprocessing completed: `MinerU_processed/` directory populated
3. `ARK_API_KEY` and `HUNYUAN_API_KEY` set in `.env`


## 7. Expected Behavior Patterns

| Phase              | Deviation Range | Rag-Specific Behavior                                                                                      |
|--------------------|-----------------|------------------------------------------------------------------------------------------------------------|
| **Stable**         | [−2%, +2%]      | RAG retrieves stable-market precedents; agents hold; retrieved knowledge confirms stability                |
| **Hot Money Exit** | [−5%, −2%]      | RagHotMoneyFunder retrieves pre-crisis signals; may exit slightly before −2% with historical justification |
| **Contagion**      | [−10%, −5%]     | RagContagionTrader retrieves contagion propagation patterns; acts with historical rationale                |
| **Crisis Peak**    | [−30% to −60%]  | RagIMFRescuer retrieves intervention case studies; timing informed by historical packages                  |
| **Recovery**       | Stabilizing     | RagValueContrarian retrieves post-crisis recovery data; commits to recovery with precedent                 |


## 8. References

*(Theory sections from simulation-bases.md — cross-reference only)*

- `../simulation-bases.md §4` — Investor archetype specifications (all 5 types)
- `../simulation-bases.md §5` — Rag variant column in agent diversity table
- `../analysis-bases.md §6` — Expected Rag result ranges (improved intervention timing)
- `players.py → RagLLMInvestor._build_prompt()` — RAG context injection logic
- `players.py → RagLLMInvestor._initialize_rag()` — KnowledgeStore initialization
- `prompts.py → RAG_*_SYS` — Behavioral persona prompts with RAG context slot
