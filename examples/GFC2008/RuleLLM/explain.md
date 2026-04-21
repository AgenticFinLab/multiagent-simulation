# GFC2008 Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | 2007-2009 financial crisis - Housing bubble burst triggered global recession |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | 2008 Global Financial Crisis simulation with mortgage-backed securities, rating agency failures, and systemic contagion |
| **Academic Value** | Understanding 2007-2009 financial crisis - housing bubble burst triggered global recession through multi-agent simulation |

## Theoretical Foundation

- Gorton (2010): Securitized banking and the run on repo
- Brunnermeier (2009): Deciphering the liquidity and credit crunch
- Acharya & Richardson (2009): Restoring financial stability

## Agent Descriptions

### MBSOriginator
**Theoretical Basis**: Originate-to-distribute model (Keys et al., 2010)
**Market Role**: destabilizing
**Description**: Creates mortgage-backed securities with lax screening
**Parameters**: origination_rate=0.8, screening_quality=0.3, securitization_speed=fast

### RatingAgency
**Theoretical Basis**: Rating agency conflict of interest (Bolton et al., 2012)
**Market Role**: destabilizing
**Description**: Overrates securities due to issuer-pays model
**Parameters**: overrating_bias=0.3, competition_pressure=0.5

### LeveragedInvestor
**Theoretical Basis**: Leverage cycle (Adrian & Shin, 2010)
**Market Role**: destabilizing
**Description**: Uses high leverage, forced to sell in downturn
**Parameters**: leverage=30, margin_call_trigger=0.05, fire_sale_discount=0.2

### DistressedBuyer
**Theoretical Basis**: Distressed debt investing
**Market Role**: stabilizing
**Description**: Buys assets at deep discount during panic
**Parameters**: discount_threshold=0.4, investment_horizon=long, patience=high

### Regulator
**Theoretical Basis**: Macroprudential regulation
**Market Role**: stabilizing
**Description**: Monitors systemic risk and may intervene
**Parameters**: intervention_threshold=0.15, rescue_probability=0.6


## Usage

### Rule Variant
```bash
python examples/GFC2008/Rule/run_gfc2008.py \
    -c configs/GFC2008/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/GFC2008/LLM/run_gfc2008_llm.py \
    -c configs/GFC2008/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/GFC2008/RuleLLM/run_gfc2008_rulellm.py \
    -c configs/GFC2008/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/GFC2008/Rag/run_gfc2008_rag.py \
    -c configs/GFC2008/Rag/simulation.yml
```

## References

- Gorton (2010): Securitized banking and the run on repo
- Brunnermeier (2009): Deciphering the liquidity and credit crunch
- Acharya & Richardson (2009): Restoring financial stability
