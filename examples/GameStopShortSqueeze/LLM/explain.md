# GameStopShortSqueeze — LLM Variant

## §1 Overview

The LLM variant implements the short squeeze simulation via LLM persona reasoning. Each agent's persona encodes its role in the squeeze: retail coordination enthusiasm (§4.1), short-seller anxiety (§4.2), mechanical hedging urgency (§4.3), institutional value conviction (§4.4), and FOMO excitement (§4.5). LLM agents may exhibit more contextual behavior than Rule: e.g., §4.2 may delay covering based on LLM "conviction" reasoning, or §4.1 may buy more aggressively when LLM context shows social momentum.

| Aspect             | Detail                                       |
|--------------------|----------------------------------------------|
| Variant            | LLM                                          |
| Simulation         | GameStopShortSqueeze                         |
| Decision Mechanism | LLM persona reasoning via system prompt      |
| Theory Reference   | `simulation-bases.md §4.1–§4.5`              |
| Market Broadcast   | `price`, `fundamental`, `deviation`, `round` |

---

## §2 Theory → Implementation Mapping

### §2.1 LLMRetailCoordinated (`simulation-bases.md §4.1`)
| Theory Component                          | Implementation                                                                                              |
|-------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| Social coordination (Barber et al., 2022) | System prompt: "you are a Reddit retail investor coordinating to squeeze short sellers; buy and hold"       |
| FOMO/diamond hands persona                | LLM may buy more aggressively when price is rising; "diamond hands" prompt may prevent selling even on loss |

### §2.2 LLMShortSellerHF (`simulation-bases.md §4.2`)
| Theory Component                           | Implementation                                                                                           |
|--------------------------------------------|----------------------------------------------------------------------------------------------------------|
| Short squeeze (Diamond & Verrecchia, 1987) | System prompt: "you are a hedge fund with massive short position, losing money; decide whether to cover" |
| Emotional covering decision                | LLM may delay covering (stubbornness) or panic-cover faster than Rule's 50%/round                        |

### §2.3 LLMMarketMakerGamma (`simulation-bases.md §4.3`)
| Theory Component                  | Implementation                                                                                 |
|-----------------------------------|------------------------------------------------------------------------------------------------|
| Gamma hedging (Jarrow & Li, 2021) | System prompt: "you are a market maker managing delta hedge; buy when options go in-the-money" |
| Mechanical mandate                | Prompt encodes obligation to hedge; LLM may reason about hedge timing                          |

### §2.4 LLMInstitutionalValue (`simulation-bases.md §4.4`)
| Theory Component  | Implementation                                                                      |
|-------------------|-------------------------------------------------------------------------------------|
| Fundamental value | System prompt: "you are a value investor; sell when price is far above fundamental" |
| LLM conviction    | May hold longer than Rule threshold based on narrative reasoning                    |

### §2.5 LLMMomentumRetail (`simulation-bases.md §4.5`)
| Theory Component           | Implementation                                                                      |
|----------------------------|-------------------------------------------------------------------------------------|
| FOMO (Lyocsa et al., 2022) | System prompt: "you buy when you see a big move upward; FOMO drives your decisions" |

---

## §3 LLM-Specific Notes

- **ShortSellerHF variability**: Key LLM effect — §4.2 may delay covering (narrative conviction), extending squeeze duration vs. Rule.
- **IEP delayed**: LLM §4.4 may hold conviction longer than Rule threshold, delaying institutional exit.
- **SQI amplification**: If §4.1 FOMO is more aggressive, LLM SQI may exceed Rule baseline.

---

## §4 Expected Ranges (LLM Variant vs. Rule Baseline)

| Metric | LLM Expected Range | Rule Baseline | Direction                            |
|--------|--------------------|---------------|--------------------------------------|
| SQI    | 0.8–6.0            | 1.0–5.0       | More variable                        |
| PAR    | 0.15–1.2           | 0.2–1.0       | More variable                        |
| SCD    | 2–12 rounds        | 2–8           | Longer (LLM §4.2 may delay covering) |
| IEP    | Rounds 2–15        | 3–10          | More variable                        |
| WTI    | 0.08–0.45          | 0.10–0.40     | More variable                        |

## §5 References and Quality Review

This variant traces to `../simulation-bases.md §4` for investor design and
`../analysis-bases.md §2` for metric definitions. Post-run review should verify
full round count, order schema completeness, price and portfolio sanity, LLM
parse/retry logs, and squeeze-phase patterns.

## §6 Running Instructions

```bash
python examples/GameStopShortSqueeze/LLM/run_gamestopshortsqueeze_llm.py \
  -c configs/GameStopShortSqueeze/LLM/simulation.yml
```

## §7 Expected Behavior

LLM agents should preserve the five investor archetypes while allowing more
variation in timing and quantity than the deterministic Rule baseline. The
short-seller and institutional-value agents are expected to create the largest
behavioral variation because their prompts emphasize conviction under pressure.

## §8 Cross-Variant Role

The LLM variant tests whether persona-only language reasoning can reproduce the
short-squeeze mechanism without embedded numerical rules.

## §9 Implementation Traceability

System prompts in `prompts.py` define persona behavior, while `players.py`
parses the canonical `<analysis>` and `<decision>` response. Accepted decisions
must contain `action`, positive `bid_price`, `quantity`, and non-empty
`reasoning`; deterministic parser or provider failures fail fast after bounded
retries. The user prompt injects the agent's configured decision parameters so
threshold references resolve to the same runtime values used by configs.
