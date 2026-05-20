# MentalAccounting Simulation

## §1 Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | Mental accounting causes investors to treat money differently based on its source or intended use |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Mental accounting simulation showing how portfolio segregation leads to suboptimal decisions |
| **Academic Value** | Understanding mental accounting causes investors to treat money differently based on its source or intended use through multi-agent simulation |

## §2 Theoretical Foundation

- Thaler (1999): Mental Accounting Matters
- Thaler (1985): Mental accounting and consumer choice
- Barberis & Huang (2001): Mental accounting, loss aversion, and individual stock returns

## §6 Configuration Reference

The RuleLLM variant uses `configs/MentalAccounting/RuleLLM/simulation.yml`, `players.yml`, `topology.yml`, and `persona.yml`. System prompts provide persona and rule guidance while model settings are loaded from `players.yml`.

## §7 Runtime Outputs

A full RuleLLM run should produce 200 rounds, valid order payloads, and model reasoning traces that remain compatible with the rule-guided decision contract.

## §8 Validation Checklist

- `players.py`, `prompts.py`, and `analysis.py` compile.
- Prompt refs load and preserve the canonical decision schema.
- Dry-run discovers `MentalAccounting__RuleLLM`.
- Existing full sample can be inherited because this pass does not change prompt or player runtime semantics.

## §9 Cross-Variant Comparison Notes

RuleLLM is compared against Rule to isolate language-reasoning effects when rule guidance is present, and against LLM to assess whether explicit rules reduce behavioral drift.

## §3 Agent Descriptions

### MentalAccountant
**Theoretical Basis**: Mental accounting (Thaler, 1999)
**Market Role**: destabilizing
**Description**: Segregates portfolio into separate accounts, doesn't net gains/losses
**Parameters**: num_accounts=3, loss_aversion_per_account=2.25, no_cross_subsidy=True

### HouseMoneyTrader
**Theoretical Basis**: House money effect (Thaler & Johnson, 1990)
**Market Role**: destabilizing
**Description**: Takes more risk with recent gains
**Parameters**: gain_risk_multiplier=1.5, loss_risk_multiplier=0.5, reset_period=20

### RationalPortfolioManager
**Theoretical Basis**: Mean-variance optimization (Markowitz, 1952)
**Market Role**: stabilizing
**Description**: Optimizes entire portfolio without mental accounting
**Parameters**: risk_aversion=0.5, correlation_aware=True

### SunkCostHolder
**Theoretical Basis**: Sunk cost fallacy (Arkes & Blumer, 1985)
**Market Role**: destabilizing
**Description**: Holds losing positions due to already invested capital
**Parameters**: sunk_cost_weight=0.6, aversion_to_realize=high

### NoiseTrader
**Theoretical Basis**: Black (1986)
**Market Role**: neutral
**Description**: Random uninformed trader
**Parameters**: trade_probability=0.05, min_order=100, max_order=500


## §4 Usage

### Rule Variant
```bash
python examples/MentalAccounting/Rule/run_mentalaccounting.py \
    -c configs/MentalAccounting/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/MentalAccounting/LLM/run_mentalaccounting_llm.py \
    -c configs/MentalAccounting/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/MentalAccounting/RuleLLM/run_mentalaccounting_rulellm.py \
    -c configs/MentalAccounting/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/MentalAccounting/Rag/run_mentalaccounting_rag.py \
    -c configs/MentalAccounting/Rag/simulation.yml
```

## §5 References

- Thaler (1999): Mental Accounting Matters
- Thaler (1985): Mental accounting and consumer choice
- Barberis & Huang (2001): Mental accounting, loss aversion, and individual stock returns
