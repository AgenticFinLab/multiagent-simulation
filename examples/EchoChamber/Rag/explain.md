# Echo Chamber Rag Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | Rag |
| Simulation | Echo Chamber |
| Decision Mechanism | RAG-augmented social-action decisions parsed as {"action": "polarize"|"depolarize"|"hold", "influence_strength": number, "target_group": string, "reasoning": string} |
| Theory Reference | `examples/EchoChamber/simulation-bases.md` |
| Market Broadcast | `configs/EchoChamber/Rag/topology.yml` |

This is a documented special-schema scenario. Decisions operate on opinion through influence_action, not bid_price-based trading orders.

## §2 Theory -> Implementation Mapping

### §2.1 Ideologue (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.1 | `RagLLMIdeologue` in `examples/EchoChamber/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/EchoChamber/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented social-action decisions parsed as {"action": "polarize"|"depolarize"|"hold", "influence_strength": number, "target_group": string, "reasoning": string}. |
### §2.2 Conformist (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.2 | `RagLLMConformist` in `examples/EchoChamber/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/EchoChamber/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented social-action decisions parsed as {"action": "polarize"|"depolarize"|"hold", "influence_strength": number, "target_group": string, "reasoning": string}. |
### §2.3 CriticalThinker (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.3 | `RagLLMCriticalThinker` in `examples/EchoChamber/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/EchoChamber/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented social-action decisions parsed as {"action": "polarize"|"depolarize"|"hold", "influence_strength": number, "target_group": string, "reasoning": string}. |
### §2.4 BridgeBuilder (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.4 | `RagLLMBridgeBuilder` in `examples/EchoChamber/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/EchoChamber/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented social-action decisions parsed as {"action": "polarize"|"depolarize"|"hold", "influence_strength": number, "target_group": string, "reasoning": string}. |
### §2.5 PassiveFollower (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Investor role and activation rule from simulation-bases.md §4.5 | `RagLLMPassiveFollower` in `examples/EchoChamber/Rag/players.py` implements the corresponding retained behavior for this variant. |
| Behavioral parameters from simulation-bases.md §6 | Loaded from `configs/EchoChamber/Rag/players.yml` through `extras`. |
| Variant-specific decision mechanism | RAG-augmented social-action decisions parsed as {"action": "polarize"|"depolarize"|"hold", "influence_strength": number, "target_group": string, "reasoning": string}. |

## §3 Market Mechanism

The coordinator mechanism is the final implementation in `examples/EchoChamber/Rag/players.py` and its configured counterpart in `configs/EchoChamber/Rag/players.yml`. It broadcasts scenario state each round, receives agent decisions, updates state variables, and records the series required by `analysis-bases.md`.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/EchoChamber/Rag/players.py` |
| Prompt module | `examples/EchoChamber/Rag/prompts.py` |
| Inference | Uses the project ARK LLM policy; RAG variants also use the project Hunyuan/LiteLLM embedding policy. |
| Output parsing | Explicit parser contract in players.py and prompts.py |
| Error handling | Deterministic config/schema errors fail fast; stochastic API parse fallback is allowed only when explicit, conservative, logged, and quality-audited. |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/EchoChamber/Rag/simulation.yml` | Full simulation entry point with 200-round full experiment setting. |
| `configs/EchoChamber/Rag/players.yml` | Player class paths, extras, and model or retrieval configuration. |
| `configs/EchoChamber/Rag/topology.yml` | Message routing between coordinator and agents. |
| `configs/EchoChamber/Rag/persona.yml` | Turn recording and persona metadata. |

## §6 Running Instructions

```bash
python examples/EchoChamber/Rag/run_echochamber_rag.py -c configs/EchoChamber/Rag/simulation.yml
```

## §7 Expected Behavior

- The run records the full scenario state path for the configured round count.
- Agent decisions should exercise the mechanism defined in `simulation-bases.md §4`.
- API variants may show greater behavioral dispersion than the deterministic Rule baseline while preserving the same scenario contract.
- A successful full experiment must pass Level-1 execution review and then Level-2 structural quality review.

## §8 References

See `examples/EchoChamber/simulation-bases.md §2` for full DOI citations and mechanism references.

## §9 Variant Comparison

See `examples/EchoChamber/simulation-bases.md §9` for the Rule / LLM / RuleLLM / Rag comparison table.
