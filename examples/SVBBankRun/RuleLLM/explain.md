# SVBBankRun RuleLLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | RuleLLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | Persona plus explicit decision rules in LLM prompts. |
| Key Difference from Other Variants | LLM agents receive the deterministic Rule logic as natural-language rules. |
| Primary Research Contribution | Tests whether rule-anchored language reasoning stays aligned with the Rule baseline. |
| Files | `players.py`, `prompts.py`, `run_svbbankrun_rulellm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Theory Component | Implementation |
|---|---|
| Depositor -> `simulation-bases.md §4.1` | `RULELLM_DEPOSITOR_SYS` includes withdrawal threshold logic. |
| SocialMediaInfluencer -> `simulation-bases.md §4.2` | `RULELLM_SOCIAL_MEDIA_INFLUENCER_SYS` embeds the amplification formula. |
| BankManager -> `simulation-bases.md §4.3` | `RULELLM_BANK_MANAGER_SYS` embeds the support-buy rule. |
| Regulator -> `simulation-bases.md §4.4` | `RULELLM_REGULATOR_SYS` embeds threshold and probability intervention. |
| BondTrader -> `simulation-bases.md §4.5` | `RULELLM_BOND_TRADER_SYS` embeds the deviation-sensitive rates rule. |

## §3 Market Mechanism Implementation

The market is imported from `Rule.players:Market`. RuleLLM agents use the same
proxy order contract and the same market broadcast as the Rule variant.

## §4 Variant-Specific Features

Every system prompt has `== PERSONA ==` and `== DECISION RULES ==`. The decision
JSON is `action`, `quantity`, and `reasoning`; `bid_price` is intentionally not
part of the SVBBankRun proxy market.

## §5 Architecture Diagram

```text
Market -> state prompt -> RuleLLMInvestor(persona + rules) -> proxy order -> Market
```

## §6 Configuration Contract

`configs/SVBBankRun/RuleLLM/players.yml` binds each investor to its prompt
constant and LLM model. Cash, position, and role-specific parameters mirror the
Rule baseline.

## §7 Run Command

```bash
python examples/SVBBankRun/RuleLLM/run_svbbankrun_rulellm.py -c configs/SVBBankRun/RuleLLM/simulation.yml
```

## §8 Validation Checklist

- Prompt sections use exact `== PERSONA ==` and `== DECISION RULES ==` labels.
- Parser contract matches the proxy market fields.
- Fallback is explicit and recorded if stochastic API output remains invalid.

## §9 Expected Variant Behavior

The RuleLLM variant should stay directionally close to the Rule baseline because
the prompt contains explicit decision rules, while still allowing natural-language
reasoning to modulate action size.
