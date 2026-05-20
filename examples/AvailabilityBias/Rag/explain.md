# AvailabilityBias Rag — Simulation Documentation

## §1 Overview

| Item                      | Description                                                                                                                                                                            |
|---------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Variant**               | Rag                                                                                                                                                                                    |
| **Implements**            | `../simulation-bases.md`                                                                                                                                                               |
| **Decision Logic**        | LLM decisions augmented with RAG-retrieved behavioral finance and availability bias literature; each agent queries a private knowledge index per round                                 |
| **Key Difference**        | Agents consult retrieved research on availability heuristic, media effects, and systematic analysis before deciding; knowledge-grounded behavioral reasoning                           |
| **Research Contribution** | Tests whether access to behavioral finance literature on cognitive biases improves or degrades agent decision quality — does knowing about availability bias reduce its manifestation? |


## §2 How Theoretical Design Is Implemented

### RagLLMRecentEventOverweighter: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.1 — Tversky & Kahneman, 1973)*

| Theoretical Design Element   | Implementation                                                                                                   |
|------------------------------|------------------------------------------------------------------------------------------------------------------|
| RAG-informed recency bias    | Retrieved documents may include Tversky & Kahneman papers; agent may cite experimental evidence for recency bias |
| Persona preserved            | Core availability bias persona maintained; RAG context adds historical/experimental grounding                    |
| Knowledge may reinforce bias | If retrieved documents describe availability bias in detail, agent may apply it more precisely                   |
| Historical event parallels   | RAG can retrieve past market crash/bubble events; agent anchors overreaction to historical precedents            |

### RagLLMMediaInfluencedTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.2 — Tetlock, 2007)*

| Theoretical Design Element      | Implementation                                                                                                      |
|---------------------------------|---------------------------------------------------------------------------------------------------------------------|
| Media effect grounding          | RAG may retrieve Tetlock (2007) media sentiment studies; agent applies empirically documented amplification factors |
| Social amplification literature | Retrieved Kasperson (1988) social amplification studies anchor amplification factor in reasoning                    |

### RagLLMSystematicAnalyst: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.3 — Mullainathan, 2002)*

| Theoretical Design Element   | Implementation                                                                                         |
|------------------------------|--------------------------------------------------------------------------------------------------------|
| Behavioral finance debiasing | RAG may retrieve debiasing literature; systematic analyst armed with research on bias recognition      |
| Anti-contamination research  | Retrieved papers on bounded rationality may help SystematicAnalyst resist availability bias in context |

### RagLLMValueTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.4 — Graham, 1949)*

| Theoretical Design Element     | Implementation                                                                                    |
|--------------------------------|---------------------------------------------------------------------------------------------------|
| Value investing literature     | RAG may retrieve Graham (1949) or Buffett references; deepens commitment to fundamental valuation |
| Historical value recovery data | Retrieved post-crash recovery statistics anchor conviction in mean reversion                      |

### RagLLMNoiseTrader: Theory → Implementation Mapping

*(Theory defined in simulation-bases.md §4.5 — Black, 1986)*

| Theoretical Design Element | Implementation                                                              |
|----------------------------|-----------------------------------------------------------------------------|
| Random with knowledge      | RAG retrieved but noise trader remains random; knowledge has minimal effect |


## §3 Market Mechanism Implementation

*(Full formula: simulation-bases.md §3.1 — P(t+1) = P(t) + 0.01·D + 0.02·(F−P) + ε)*

### RAG System Architecture

Each agent builds or loads a private `KnowledgeStore`:
1. Documents from `examples/document-sources/` (behavioral finance papers)
2. Per-round query: text includes `return_pct` and `deviation` context
3. Top-3 passages injected into `{rag_context}` slot in user prompt

### Rag User Prompt Variables

Same as LLM variant with addition of `{rag_context}`:

| Variable                     | Source                 | Notes                                                        |
|------------------------------|------------------------|--------------------------------------------------------------|
| `{return_pct}`               | market_data.return_pct | Recent return — key availability bias signal                 |
| `{deviation}`                | market_data.deviation  | Fundamental deviation                                        |
| `{rag_context}`              | KnowledgeStore.query() | Top-3 retrieved passages; "(No relevant knowledge)" if empty |
| *(other standard variables)* | —                      | Same as Rule/LLM variants                                    |


## §4 Variant-Specific Features

- **Knowledge may reduce bias**: If retrieved papers describe availability bias as a cognitive error, SystematicAnalyst may use this to resist bias influence; RecencyOverweighter may paradoxically apply bias more accurately
- **Unique research question**: Does meta-knowledge about availability bias (retrieved from papers) reduce its expression in agent behavior?
- **Per-agent private index**: Each agent can have agent-specific documents (RecencyOverweighter: behavioral papers; SystematicAnalyst: debiasing literature)
- **Document source dependency**: Rag advantage contingent on availability bias literature quality in document sources


## §5 Architecture Diagram

```
Round t:
  ┌──────────────────────────────────────────────────────────┐
  │  Market (Rule — identical to Rule)                       │
  │  Broadcasts: {price, prev_price, fundamental,            │
  │               deviation, return_pct, round}              │
  └─────────────────┬────────────────────────────────────────┘
                    │ market_data
        ┌───────────┼──────────────────────────┐
        ▼           ▼           ▼              ▼
  ┌────────────────┐ ┌──────────────────┐ ┌────────────────┐ ┌────────────────┐
  │RagLLMRecent    │ │RagLLMMedia       │ │RagLLMSystem    │ │RagLLMValue     │
  │EventOverweight │ │InfluencedTrader  │ │aticAnalyst     │ │Trader          │
  │+ RAG context   │ │+ RAG context     │ │+ debiasing     │ │+ value         │
  │ (bias research)│ │ (media research) │ │  literature    │ │  literature    │
  └────────────────┘ └──────────────────┘ └────────────────┘ └────────────────┘
```


## §6 Configuration Reference

| Config Path                            | Key Parameter   | Notes                                       |
|----------------------------------------|-----------------|---------------------------------------------|
| `*.extras.llm.sys_message`             | System prompt   | Behavioral persona with RAG context slot    |
| `*.extras.llm.user_message`            | User template   | Includes `{return_pct}` and `{rag_context}` |
| `*.extras.knowledge.global_uri`        | Document source | Behavioral finance papers                   |
| `*.extras.private_knowledge.rag.top_k` | Retrieval k     | 3                                           |

Full config: `configs/AvailabilityBias/Rag/players.yml`


## §7 Running Instructions

```bash
# From project root (requires HUNYUAN_API_KEY or ARK_API_KEY):
python examples/AvailabilityBias/Rag/run_availabilitybias_rag.py \
    -c configs/AvailabilityBias/Rag/simulation.yml
```

Output: `EXPERIMENT/AvailabilityBias/Rag/records/`


## §8 Expected Behavior Patterns

| Phase             | Deviation Range  | Rag-Specific Behavior                                                                                |
|-------------------|------------------|------------------------------------------------------------------------------------------------------|
| **Pre-Event**     | [−2%, +2%]       | Knowledge of stability periods may reinforce holding                                                 |
| **Event Trigger** | First large move | RecencyOverweighter cites retrieved bias research when overreacting; more articulate bias expression |
| **Bias Peak**     | [3%–12%]         | Possibly intermediate; depends on whether retrieved knowledge reinforces or dampens bias             |
| **Correction**    | Declining        | SystematicAnalyst may use debiasing literature to resist availability contamination                  |
| **Stabilization** | Near 0%          | Variable; knowledge quality determines outcome                                                       |


## §9 References

- `../simulation-bases.md §4.1–§4.5` — Investor archetype specifications
- `../simulation-bases.md §5` — Rag variant description
- `../analysis-bases.md §6` — Expected Rag result ranges
- `players.py → RagLLMInvestor._build_prompt()` — RAG context injection logic
