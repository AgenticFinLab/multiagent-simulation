# SVBBankRun LLM — Implementation Explanation

## §1 Overview

| Item | Description |
|---|---|
| Variant | LLM |
| Implements | `../simulation-bases.md` |
| Decision Logic | Persona-driven LLM decisions over the same proxy-market schema. |
| Key Difference from Other Variants | API agents infer action size from persona and market state. |
| Primary Research Contribution | Tests whether natural-language banking roles alter run timing and support pressure. |
| Files | `players.py`, `prompts.py`, `run_svbbankrun_llm.py`, `analysis.py`, `explain.md`, `analysis.md` |

## §2 Theory To Implementation Mapping

| Theory Component | Implementation |
|---|---|
| Depositor -> `simulation-bases.md §4.1` | `LLMDepositor` uses `LLM_DEPOSITOR_SYS` and emits the proxy withdrawal/support schema. |
| SocialMediaInfluencer -> `simulation-bases.md §4.2` | `LLMSocialMediaInfluencer` uses social-amplifier persona language. |
| BankManager -> `simulation-bases.md §4.3` | `LLMBankManager` represents stabilization and asset-liability reasoning. |
| Regulator -> `simulation-bases.md §4.4` | `LLMRegulator` represents policy intervention reasoning. |
| BondTrader -> `simulation-bases.md §4.5` | `LLMBondTrader` represents rate-sensitive valuation reasoning. |

## §3 Market Mechanism Implementation

The market is imported from `Rule.players:Market`. API agents receive the same
`price`, `fundamental`, and `deviation` broadcast and return `investor_order`
payloads consumed by the Rule market.

## §4 Variant-Specific Features

LLM prompts use role personas and the proxy order contract:
`{"action": "buy|sell|hold", "quantity": integer, "reasoning": string}`.
`examples/SVBBankRun/decision.py` validates this contract. Stochastic parse
failure after retries is recorded as explicit fallback with `llm_fallback` and
`fallback_reason`.

## §5 Architecture Diagram

```text
Market -> state prompt -> LLMInvestor -> parsed proxy order -> Market
```

## §6 Configuration Contract

Each player in `configs/SVBBankRun/LLM/players.yml` defines `llm.sys_message`,
`llm.user_message`, `llm.lm_name`, and `llm.generation_config`, plus the same
cash/position parameters used by the Rule baseline.

## §7 Run Command

```bash
python examples/SVBBankRun/LLM/run_svbbankrun_llm.py -c configs/SVBBankRun/LLM/simulation.yml
```

## §8 Validation Checklist

- Prompt schema matches `parse_svbbankrun_decision()`.
- Any fallback is explicit and auditable.
- Output orders include reasoning and fallback fields.

## §9 Expected Variant Behavior

The LLM variant should preserve the same proxy action schema while allowing
persona-driven discretion in the timing and size of withdrawal, amplification,
support, and bond-trader actions.
