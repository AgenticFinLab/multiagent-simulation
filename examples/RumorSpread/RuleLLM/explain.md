# RumorSpread RuleLLM Variant Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | LLM persona plus explicit rumor-action decision rules |
| Schema | Special `social_action`; no trading fields |
| Files | `players.py`, `prompts.py`, `run_rumor_rulellm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Role | Theory Component | Implementation |
|---|---|---|
| `RuleLLMGullibleSpreader` | `simulation-bases.md §4.1` | Prompt has `== PERSONA ==` and `== DECISION RULES ==` mirroring gullible spread formulas. |
| `RuleLLMDistortingRelayer` | `simulation-bases.md §4.2` | Prompt embeds sharpening, leveling, and relay threshold rules. |
| `RuleLLMSkepticalEvaluator` | `simulation-bases.md §4.3` | Prompt embeds truth-pull and correction-threshold rules. |
| `RuleLLMFactChecker` | `simulation-bases.md §4.4` | Prompt embeds fact-check strength, distortion bonus, and credibility discount. |
| `RuleLLMUninformedBystander` | `simulation-bases.md §4.5` | Prompt embeds low-engagement heuristic for stochastic participation. |

## §3 Environment Mechanism

The coordinator remains the RumorSpread environment from `simulation-bases.md
§3`; RuleLLM modifies only agent reasoning before emitting social actions.

## §4 Variant Architecture

`RuleLLMSocialAgent` calls the configured ARK model, validates the special JSON
contract through `parse_rumor_response()`, retries parse or transient provider
errors, and raises after three failed attempts.

## §5 Config Reference

`configs/RumorSpread/RuleLLM/players.yml` binds class paths, model settings, and
initial state parameters. Prompt constants live in `prompts.py`.

## §6 Running Instructions

```bash
python examples/RumorSpread/RuleLLM/run_rumor_rulellm.py -c configs/RumorSpread/RuleLLM/simulation.yml
```

## §7 Expected Behavior

RuleLLM should preserve the sign and scale of Rule behavior while allowing
language reasoning to adjust intensity within the prompt-specified bounds.

## §8 References

See `simulation-bases.md §2` and `analysis-bases.md §2`.

## §9 Variant Comparison

Compare RuleLLM against Rule and LLM to isolate the effect of explicit rule
guidance inside model reasoning.
