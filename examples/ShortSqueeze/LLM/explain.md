# Short Squeeze LLM Variant Explanation

## §1 Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Simulation | ShortSqueeze |
| Decision Mechanism | Persona-driven API trading orders |
| Theory Reference | `examples/ShortSqueeze/simulation-bases.md` |
| Market Broadcast | `configs/ShortSqueeze/LLM/topology.yml` |

The LLM variant keeps the Rule market structure and five role families but
replaces deterministic formulas with persona prompts and structured JSON
decisions.

## §2 Theory -> Implementation Mapping

### §2.1 ShortSeller (simulation-bases.md §4.1)

| Theory Component | Implementation |
|---|---|
| Forced covering | `LLMShortSeller` interprets short-position risk and may mark buy orders as `is_short_cover=true`. |
| API contract | Emits `action`, `bid_price`, `quantity`, optional `is_short_cover`, and `reasoning`. |

### §2.2 MomentumBuyer (simulation-bases.md §4.2)

| Theory Component | Implementation |
|---|---|
| Positive-feedback demand | `LLMMomentumBuyer` follows price trends through prompt reasoning. |
| API contract | Parser validates canonical trading fields and records analysis text. |

### §2.3 RetailCoordinator (simulation-bases.md §4.3)

| Theory Component | Implementation |
|---|---|
| Attention-driven bullish flow | `LLMRetailCoordinator` represents bullish retail coordination. |
| API contract | Stochastic parse fallback is explicit, conservative, logged, and quality-auditable. |

### §2.4 ValueInvestor (simulation-bases.md §4.4)

| Theory Component | Implementation |
|---|---|
| Fundamental resistance | `LLMValueInvestor` compares price against fundamental value. |
| API contract | Reasoning is retained for Level-2 review. |

### §2.5 InstitutionalHolder (simulation-bases.md §4.5)

| Theory Component | Implementation |
|---|---|
| Float scarcity | `LLMInstitutionalHolder` models sticky long supply and possible profit-taking. |
| API contract | Structured JSON is parsed into signed market orders. |

## §3 Market Mechanism

`Market` in `examples/ShortSqueeze/LLM/players.py` consumes the same signed
order schema as Rule and treats `is_short_cover` as the forced-covering marker.

## §4 Variant Architecture

| Component | Implementation |
|---|---|
| Player classes | `examples/ShortSqueeze/LLM/players.py` |
| Prompt module | `examples/ShortSqueeze/LLM/prompts.py` |
| Inference | ARK API model configured in `players.yml` |
| Output parsing | `_parse_response` validates required fields |
| Error handling | Bounded retry; conservative logged hold only after stochastic parse failure |

## §5 Config Reference

| Config | Purpose |
|---|---|
| `configs/ShortSqueeze/LLM/simulation.yml` | Full simulation entry point |
| `configs/ShortSqueeze/LLM/players.yml` | LLM investor set and model config |
| `configs/ShortSqueeze/LLM/topology.yml` | Message routing |
| `configs/ShortSqueeze/LLM/persona.yml` | Recording/persona metadata |

## §6 Running Instructions

```bash
python examples/ShortSqueeze/LLM/run_short_squeeze_llm.py -c configs/ShortSqueeze/LLM/simulation.yml
```

## §7 Expected Behavior

LLM should preserve the short-squeeze mechanism while allowing variable
narrative-driven timing in covering, retail demand, and profit-taking.

## §8 References

See `examples/ShortSqueeze/simulation-bases.md §2` and
`examples/ShortSqueeze/analysis-bases.md §2`.

## §9 Variant Comparison

Compare LLM against Rule to isolate persona-driven variation and against
RuleLLM to measure the value of explicit rules.
