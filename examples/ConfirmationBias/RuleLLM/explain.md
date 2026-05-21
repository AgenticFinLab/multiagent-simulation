# ConfirmationBias RuleLLM Variant — Design Specification

## §1 Overview

| Item            | Detail                                                                                         |
|-----------------|------------------------------------------------------------------------------------------------|
| **Phenomenon**  | Confirmation bias reproduced by LLM agents guided by explicit numerical decision rules         |
| **Variant**     | RuleLLM — hybrid: LLM inference + rule-structured prompts                                      |
| **Rounds**      | 200 (configurable)                                                                             |
| **Market**      | Identical deterministic Rule-based Market agent                                                |
| **Key Feature** | Dual-section system prompts: `== PERSONA ==` + `== DECISION RULES ==`; measures rule adherence |
| **Target**      | Rule adherence rate ≥ 80% for all agents                                                       |

---

## §2 Theory → Implementation Mapping

| Theoretical Concept                 | Agent / Mechanism                                                      | Code Location                                       |
|-------------------------------------|------------------------------------------------------------------------|-----------------------------------------------------|
| Belief anchoring with explicit rule (`simulation-bases.md §4.1`) | `RuleLLMBeliefAnchor` — persona + rule: buy when deviation confirms belief | `RuleLLM/prompts.py: RULELLM_BELIEF_ANCHOR_SYS`     |
| Selective scanning with threshold (`simulation-bases.md §4.2`)   | `RuleLLMSelectiveScanner` — persona + rule: buy when deviation > 0.02  | `RuleLLM/prompts.py: RULELLM_SELECTIVE_SCANNER_SYS` |
| Rational Bayesian with threshold (`simulation-bases.md §4.3`)    | `RuleLLMBalancedAnalyst` — persona + rule: buy when deviation < -0.05  | `RuleLLM/prompts.py: RULELLM_BALANCED_ANALYST_SYS`  |
| Contrarian with threshold (`simulation-bases.md §4.4`)           | `RuleLLMContrarianTrader` — persona + rule: sell when deviation > 0.05 | `RuleLLM/prompts.py: RULELLM_CONTRARIAN_TRADER_SYS` |
| Noise with probability (`simulation-bases.md §4.5`)              | `RuleLLMNoiseTrader` — persona + rule: random at p=0.30                | `RuleLLM/prompts.py: RULELLM_NOISE_TRADER_SYS`      |

### §2.1 RuleLLMBeliefAnchor (`simulation-bases.md §4.1`)

| Theory Component | Implementation |
|---|---|
| Prior-belief anchoring | `== PERSONA ==` defines conviction; `== DECISION RULES ==` maps confirming deviation to constrained orders. |

### §2.2 RuleLLMSelectiveScanner (`simulation-bases.md §4.2`)

| Theory Component | Implementation |
|---|---|
| Selective search | Persona protects its current view; decision rules use the +0.02/-0.02 asymmetric threshold. |

### §2.3 RuleLLMBalancedAnalyst (`simulation-bases.md §4.3`)

| Theory Component | Implementation |
|---|---|
| Rational benchmark | Persona is objective; decision rules trade symmetrically at the 5% threshold. |

### §2.4 RuleLLMContrarianTrader (`simulation-bases.md §4.4`)

| Theory Component | Implementation |
|---|---|
| Bias correction | Persona is skeptical; decision rules fade deviations larger than 5%. |

### §2.5 RuleLLMNoiseTrader (`simulation-bases.md §4.5`)

| Theory Component | Implementation |
|---|---|
| Noise liquidity | Persona and decision rules produce occasional random buy/sell orders. |

---

## §3 Market Mechanism

Identical to Rule variant. Market broadcasts per round:

```python
{"price": float, "fundamental": float, "deviation": float, "round": int}
```

---

## §4 Variant-Specific Features

### 4.1 Dual-Section System Prompt Structure

```
== PERSONA ==
You are a belief-anchored trader. You form strong prior beliefs and
overweight evidence that confirms your current view. You tend to
continue buying when signals confirm your bullish position.

== DECISION RULES ==
- If deviation > 0.0: BUY {order_size} units
- If deviation < -0.5: consider SELL, quantity = {order_size}
- Otherwise: HOLD

Always output JSON with `action`, `bid_price`, `quantity`, and `reasoning`.
```

The `== DECISION RULES ==` section provides the LLM with explicit
numerical thresholds, bridging the gap between LLM reasoning and
deterministic Rule behavior.

### 4.2 Embedded Rules as Investor Characterization

The `== DECISION RULES ==` section provides the LLM with explicit
numerical thresholds that define the investor's knowledge and habitual
decision-making framework. The LLM uses these rules as guidance
alongside its persona to make intelligent, context-aware decisions.

Low-quality reasoning for a specific agent → review that agent's `== DECISION RULES ==` section
in `RuleLLM/prompts.py`.

### 4.3 Key Difference: BeliefAnchor

Rule BeliefAnchor has internal `belief` state (not accessible to LLM).
RuleLLM substitutes this with a simplified deviation-based rule:
```
IF deviation > 0 → BUY (simulating locked bullish belief)
IF deviation < -0.05 → SELL (simulating belief flip)
```

This simplification reduces the bias strength vs Rule but maintains
the directional behavior. Expect RuleLLM `bias_amplitude_pct` between
Rule and LLM.

---

## §5 Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│                  Market (Rule)                        │
│  P(t+1) = P(t) + λ·D + γ·(F−P) + ε                  │
└──────────────────────┬───────────────────────────────┘
                       │
   ┌────────────┬───────┼────────────┬────────────┐
   │            │       │            │            │
┌──▼───────┐ ┌──▼──────┐ ┌──▼──────┐ ┌──▼──────┐ ┌──▼──────┐
│RuleLLM   │ │RuleLLM  │ │RuleLLM  │ │RuleLLM  │ │RuleLLM  │
│Belief    │ │Selective│ │Balanced │ │Contrarian│ │Noise    │
│Anchor    │ │Scanner  │ │Analyst  │ │Trader    │ │Trader   │
│PERSONA + │ │PERSONA +│ │PERSONA +│ │PERSONA + │ │PERSONA +│
│DEC.RULES │ │DEC.RULES│ │DEC.RULES│ │DEC.RULES │ │DEC.RULES│
└──────────┘ └─────────┘ └─────────┘ └──────────┘ └─────────┘
                  │  LLM + rules → JSON → Market
              ┌───▼──────────────────────────────┐
              │    LangChainAPIInference           │
              └───────────────────────────────────┘
```

---

## §6 Configuration Reference

Config: `configs/ConfirmationBias/RuleLLM/simulation.yml`

| Parameter          | Value                   | Description             |
|--------------------|-------------------------|-------------------------|
| `llm.model`        | `ark/doubao-seed-2-0-mini-260428` | LLM model name          |
| `llm.temperature`  | 0.2–0.9 by agent        | Decision randomness     |
| `llm.max_tokens`   | 512                     | Max response length     |
| `initial_cash`     | 50000 for core agents; 20000 for noise traders | Starting cash per agent |
| `initial_position` | 0                       | Starting holdings       |

---

## §7 Running Instructions

```bash
python examples/ConfirmationBias/RuleLLM/run_confirmationbias_rulellm.py \
    -c configs/ConfirmationBias/RuleLLM/simulation.yml

python examples/ConfirmationBias/RuleLLM/analysis.py \
    -c configs/ConfirmationBias/RuleLLM/simulation.yml
```

---

## §8 Expected Behavior

- All agents should achieve ≥ 80% rule adherence if prompts are well-designed
- `bias_amplitude_pct` between Rule (highest) and LLM (lowest)
- `bias_persistence_rounds` close to Rule variant
- Low adherence agents: check `== DECISION RULES ==` section clarity and threshold values
- Rule adherence bars in analysis chart: green = meets target, red = needs improvement

---

## §9 References

*Do not repeat citations from simulation-bases.md §2. Cross-references only:*

- Confirmation bias theory → `../simulation-bases.md §2, §4 — BeliefAnchor, SelectiveScanner`
- Chain-of-thought prompting → Wei, J., et al. (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS*.
