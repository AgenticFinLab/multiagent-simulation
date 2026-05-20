# LUNACollapse Simulation

## §1 Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | May 2022 Terra/LUNA crash - $40B wiped out in algorithmic stablecoin death spiral |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Terra/LUNA collapse simulation with algorithmic stablecoin death spiral and DeFi contagion |
| **Academic Value** | Understanding may 2022 terra/luna crash - $40b wiped out in algorithmic stablecoin death spiral through multi-agent simulation |

## §2 Theoretical Foundation

- Algorithmic stablecoin mechanism design (Klages-Mundt et al., 2020)
- Death spiral dynamics (Levy, 2022)
- DeFi contagion (Werner et al., 2022)

## §3 Agent Descriptions

### StablecoinHolder
**Theoretical Basis**: Stablecoin redemption pressure
**Market Role**: destabilizing
**Description**: Redeems UST for LUNA, creating selling pressure on LUNA
**Parameters**: holdings=100000, redemption_threshold=0.98, panic_speed=fast

### Arbitrageur
**Theoretical Basis**: UST-LUNA arbitrage
**Market Role**: destabilizing
**Description**: Arbitrage between UST and LUNA amplifies death spiral
**Parameters**: arb_threshold=0.01, position_size=50000, speed=HFT

### DeFiLender
**Theoretical Basis**: DeFi liquidation cascade
**Market Role**: destabilizing
**Description**: Forced liquidations create additional selling pressure
**Parameters**: liquidation_threshold=0.8, cascade_speed=fast

### AnchorDepositor
**Theoretical Basis**: Yield farming exit
**Market Role**: destabilizing
**Description**: Withdraws from Anchor protocol when confidence drops
**Parameters**: deposit_amount=500000, yield_threshold=0.15, exit_speed=moderate

### ValueBuyer
**Theoretical Basis**: Contrarian buying
**Market Role**: stabilizing
**Description**: Attempts to buy at deep discount but gets overwhelmed
**Parameters**: discount_threshold=0.5, position_limit=100000


## §4 Usage

### Rule Variant
```bash
python examples/LUNACollapse/Rule/run_lunacollapse.py \
    -c configs/LUNACollapse/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/LUNACollapse/LLM/run_lunacollapse_llm.py \
    -c configs/LUNACollapse/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/LUNACollapse/RuleLLM/run_lunacollapse_rulellm.py \
    -c configs/LUNACollapse/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/LUNACollapse/Rag/run_lunacollapse_rag.py \
    -c configs/LUNACollapse/Rag/simulation.yml
```

## §5 References

- Algorithmic stablecoin mechanism design (Klages-Mundt et al., 2020)
- Death spiral dynamics (Levy, 2022)
- DeFi contagion (Werner et al., 2022)
