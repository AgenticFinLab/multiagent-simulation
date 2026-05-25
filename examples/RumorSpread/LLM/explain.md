# RumorSpread LLM Variant Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | Persona-only LLM reasoning over environment state |
| Schema | Special `social_action`: `spread`, `ignore`, or `correct` with numeric intensity |
| Files | `players.py`, `prompts.py`, `run_rumor_llm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Role | Theory Component | Implementation |
|---|---|---|
| `LLMGullibleSpreader` | `simulation-bases.md §4.1` | Persona prompt describes high credulity; parser enforces rumor action JSON. |
| `LLMDistortingRelayer` | `simulation-bases.md §4.2` | Persona prompt emphasizes dramatic retelling and simplification. |
| `LLMSkepticalEvaluator` | `simulation-bases.md §4.3` | Persona prompt anchors to evidence and allows correction. |
| `LLMFactChecker` | `simulation-bases.md §4.4` | Persona prompt describes professional verification and debunking. |
| `LLMUninformedBystander` | `simulation-bases.md §4.5` | Persona prompt describes low engagement and mostly ignoring. |

## §3 Environment Mechanism

The environment is the same coordinator as Rule. LLM affects only social-action
selection, not belief or distortion update equations.

## §4 Variant Architecture

`LLMSocialAgent` builds a user prompt from environment state, calls
`LangChainAPIInference.run()`, parses `<analysis>` and `<decision>` through
`parse_rumor_response()`, retries transient API/parse failures, and raises after
three failed attempts.

## §5 Config Reference

`configs/RumorSpread/LLM/players.yml` binds every role class, ARK model policy,
temperature, max tokens, and initial belief parameters.

## §6 Running Instructions

```bash
python examples/RumorSpread/LLM/run_rumor_llm.py -c configs/RumorSpread/LLM/simulation.yml
```

## §7 Expected Behavior

LLM decisions should remain in the rumor schema while producing richer
reasoning traces. Persona-only prompts must not introduce trading orders.

## §8 References

See `simulation-bases.md §2` and `analysis-bases.md §2`.

## §9 Variant Comparison

Compare LLM to Rule to isolate whether persona reasoning alone changes belief
amplification, distortion, or correction lag.
