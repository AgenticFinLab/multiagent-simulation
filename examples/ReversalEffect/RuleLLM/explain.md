# ReversalEffect RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Mechanism | Explicit reversal and overreaction rules embedded in LLM prompts |
| Market | Same rule-based market as Rule |
| Agents | RuleLLM contrarian, overconfident, value, momentum, and noise agents |
| Runtime Change | Documentation-only backfill; no code/config change |

## §2 Theory → Implementation Mapping

### §2.1 RuleLLMContrarianInvestor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.1` | Prompt states contrarian reversal rule |
| Runtime path | LLM decision is parsed and constrained before order |

### §2.2 RuleLLMOverconfidentTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.3` | Prompt states overreaction behavior |
| Runtime path | LLM emits structured decision and reasoning |

### §2.3 RuleLLMValueInvestor

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.5` | Prompt states fundamental-value correction |
| Runtime path | Cash/position constraints cap trades |

### §2.4 RuleLLMMomentumChaser

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.2` | Prompt states continuation behavior |
| Runtime path | Direction should follow recent trend until reversal |

### §2.5 RuleLLMNoiseTrader

| Theory Component | Implementation |
|---|---|
| `simulation-bases.md §4.4` | Prompt expresses random/noisy participation |
| Runtime path | Random-like LLM decisions still use canonical order schema |

## §3 Market Mechanism Implementation

Market mechanics are unchanged from Rule. RuleLLM changes only decision
generation.

## §4 Variant-Specific Features

RuleLLM tests whether LLM reasoning preserves explicit reversal, value, and
overconfidence rules.

## §5 Architecture Diagram

```text
Market update -> rule prompt + context -> LLM JSON decision -> order -> Market
```

## §6 Configuration Reference

Primary config: `configs/ReversalEffect/RuleLLM/players.yml`.

## §7 Running Instructions

```bash
python examples/ReversalEffect/RuleLLM/run_reversaleffect_rulellm.py \
  -c configs/ReversalEffect/RuleLLM/simulation.yml
```

## §8 Expected Behavior Patterns

RuleLLM should show the same overshoot/correction pattern as Rule with some
variation in timing and quantity.

## §9 References

See `../simulation-bases.md §4` and `../analysis-bases.md §2`.
