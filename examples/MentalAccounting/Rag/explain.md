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

The RAG variant uses `configs/MentalAccounting/Rag/simulation.yml`, `players.yml`, `topology.yml`, and `persona.yml`. It adds knowledge and embedding configuration to the LLM-style investor setup while preserving the same market topology.

## §7 Runtime Outputs

A full RAG run should produce 200 rounds, valid order payloads, parseable LLM decisions, and retrieval context sufficient for quality review of knowledge-augmented decisions.

## §8 Validation Checklist

- `players.py`, `prompts.py`, and `analysis.py` compile.
- RAG embedding config resolves and prompt templates inject `{rag_context}`.
- Dry-run discovers `MentalAccounting__Rag`.
- Full runs should complete 200 rounds with valid decision JSON and auditable retrieval context.

## §9 Cross-Variant Comparison Notes

RAG is compared primarily against RuleLLM to isolate whether retrieved financial-behavioral knowledge changes mental-accounting intensity, house-money risk taking, or sunk-cost persistence.

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
