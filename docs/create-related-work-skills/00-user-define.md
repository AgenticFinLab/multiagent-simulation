# Stage 0: User Research Definition

> **Fill this file FIRST.** All subsequent stages — keyword extraction, venue selection, search execution, paper classification, writing, and validation — derive entirely from this table.
> Do NOT change these values mid-session; any change requires re-running the keyword matrix and all search queries.

---

| #  | Field                          | Your Input                                                                                                                                    |
|----|--------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| 1  | **Research Area**              | `[e.g., LLM-based multi-agent simulation of financial markets and social behavior]`                                                           |
| 2  | **Research Target**            | `[e.g., Multi-agent simulation framework where each agent is driven by an LLM with behavioral finance theory]`                                |
| 3  | **Research Direction**         | `[e.g., Replicate historical financial events with LLM agents whose behavioral biases drive emergent market dynamics]`                        |
| 4  | **Main Motivation**            | `[e.g., Rule-based agents cannot capture narrative-driven investor psychology; LLMs enable realistic behavioral modeling]`                    |
| 5  | **Main Idea**                  | `[e.g., LLM-driven agents with behavioral finance theory encoded in system prompts produce emergent market dynamics]`                         |
| 6  | **Key Methods**                | `[e.g., 1) LLM-based multi-agent systems, 2) Behavioral finance theory in prompts, 3) RAG-augmented agents, 4) Rule+LLM hybrid variants]`     |
| 7  | **Comparison Dimensions**      | `[e.g., Simulation realism, Agent behavioral diversity, LLM integration depth, Financial phenomenon coverage, Scalability, Interpretability]` |
| 8  | **Search Scope Summary**       | `[e.g., LLM agents, social simulation, financial market simulation, agent-based modeling, multi-agent systems]`                               |
| 9  | **Primary Research Community** | `[e.g., AI/ML + Multi-Agent Systems + Economics/Finance]`                                                                                     |
| 10 | **Year Range**                 | `[e.g., 2020–2026]`                                                                                                                           |

---

## Field Guide

| Field                          | Purpose                                        | Where It Is Used                                                                   |
|--------------------------------|------------------------------------------------|------------------------------------------------------------------------------------|
| **Research Area**              | Broad domain description                       | Venue taxonomy derivation (`03-search-proactive.md §2`), arXiv category selection  |
| **Research Target**            | Specific system you are building or studying   | "Our Work" column in all comparison tables; `08-quality-standards.md §2`           |
| **Research Direction**         | Specific angle or goal within the area         | Relevance scoring during paper review                                              |
| **Main Motivation**            | Gap or problem being addressed                 | Motivation keywords (G1–Gn) for gap-based search queries                           |
| **Main Idea**                  | Central insight or novel contribution          | Method keywords (M1–Mn) for keyword matrix                                         |
| **Key Methods**                | Named techniques/algorithms/architectures      | Method keywords; taxonomy Category derivation (`04b-paper-classification.md`)      |
| **Comparison Dimensions**      | Evaluation axes for comparison tables          | Rows in every "Relationship to Our Work" table (`01-paper-entry-template.md §2.9`) |
| **Search Scope Summary**       | Broader search direction beyond the core topic | Domain keywords (D1–Dn); seed queries                                              |
| **Primary Research Community** | Academic field(s) that publish this work       | CCF-A venue selection (`03-search-proactive.md §2`)                                |
| **Year Range**                 | Time window for all searches                   | Applied to every venue×year combination in coverage tracker                        |

---

## Auto-Generated: Parsed Search Configuration

After you fill the table above, this section is **auto-generated** by the agent following `03-search-proactive.md §1`. Do not fill it manually — it is written here after derivation.

```
### Research Community Classification
- Primary field:    [auto-derived from Research Community]
- Secondary fields: [auto-derived]
- arXiv categories: [auto-derived]

### Domain Keywords (D1–Dn)
D1: [primary domain term, synonym1, synonym2, abbreviation]
D2: [secondary domain term, synonym1, synonym2, abbreviation]
...

### Method Keywords (M1–Mn)
M1: [primary method term, synonym1, synonym2, abbreviation]
M2: [secondary method term, synonym1, synonym2, abbreviation]
...

### Motivation Keywords (G1–Gn)
G1: [gap/limitation term, related phrase]
G2: [gap/limitation term, related phrase]
...

### Comparison Dimensions (for Relationship tables)
- [Dimension 1 from field 7]
- [Dimension 2 from field 7]
...

### Selected Venues (CCF-A + Recognized Top)
| # | Venue | Tier | Community | Years | Rationale |
|---|-------|------|-----------|-------|-----------|
| 1 | ...   | ...  | ...       | ...   | ...       |
```

---

## Filled Example (LLM Financial Simulation)

| #  | Field                          | Value                                                                                                                                             |
|----|--------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| 1  | **Research Area**              | Simulation of society and financial markets using LLM-based multi-agent systems                                                                   |
| 2  | **Research Target**            | Multi-agent simulation framework where LLM-driven agents with behavioral finance theory replicate historical financial events                     |
| 3  | **Research Direction**         | Replicate historical financial bubbles, crashes, and collusion events with emergent agent behavior matching real-world patterns                   |
| 4  | **Main Motivation**            | Existing rule-based ABMs cannot capture narrative-driven, psychologically complex investor behavior; LLMs offer realistic behavioral modeling     |
| 5  | **Main Idea**                  | LLM agents with behavioral biases (availability heuristic, herding, overconfidence) encoded in system prompts produce emergent market dynamics    |
| 6  | **Key Methods**                | 1) LLM-based multi-agent systems, 2) Behavioral finance theory in prompts, 3) RAG-augmented agents, 4) Rule+LLM hybrid variants, 5) ABM framework |
| 7  | **Comparison Dimensions**      | Simulation realism, Agent behavioral diversity, LLM integration depth (none/surface/deep), Financial phenomenon coverage, Scalability             |
| 8  | **Search Scope Summary**       | LLM agents, social simulation, financial market simulation, agent-based modeling, multi-agent systems, emergent behavior                          |
| 9  | **Primary Research Community** | AI/ML + Multi-Agent Systems + Economics/Finance                                                                                                   |
| 10 | **Year Range**                 | 2020–2026                                                                                                                                         |
