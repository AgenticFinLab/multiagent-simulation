# RumorSpread Rag — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | Rag |
| Mechanism | Rumor-action LLM decisions augmented with retrieved information/misinformation context |
| Environment | InformationEnvironment |
| Knowledge Sources | Shared document corpus and RAG index |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 Rag Spreaders And Relayers

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` and `§4.3` | Retrieved rumor/misinformation context is added to prompt |
| Effect | May change spread or distortion intensity |

### §2.2 Rag Skeptics And Fact Checkers

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` and `§4.5` | Retrieved correction/evidence context informs evaluation |
| Effect | May strengthen correction |

### §2.3 Rag Bystanders

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.6` | Low-engagement behavior remains scenario-specific |
| Effect | Should preserve special information-action schema |

## §3 Market Mechanism Implementation

Rag keeps RumorSpread's information environment and special action schema.
Retrieved context changes reasoning, not schema.

## §4 Variant-Specific Features

Rag quality review should check retrieval relevance and whether retrieved
evidence improves correction or reduces distortion.

## §5 Architecture Diagram

```text
Rumor state -> retrieve context -> LLM information action -> environment update
```

## §6 Configuration Reference

Primary config: `configs/RumorSpread/Rag/players.yml`.

## §7 Running Instructions

```bash
python examples/RumorSpread/Rag/run_rumorspread_rag.py \
  -c configs/RumorSpread/Rag/simulation.yml
```

## §8 Expected Behavior Patterns

Rag may slow false rumor spread if retrieval supplies corrective evidence, or
may amplify spread if retrieved context makes the rumor more salient.

## §9 References

See `../simulation-bases.md §2`, `../simulation-bases.md §4`, and
`../analysis-bases.md §2`.
