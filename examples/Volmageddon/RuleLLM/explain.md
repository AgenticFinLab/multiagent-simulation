# Volmageddon Simulation

## §1 Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | February 5, 2018 - VIX spiked 115%, XIV ETN lost 90%+ in after-hours trading |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | Volmageddon simulation with VIX ETN blowup, short volatility crowd, and reverse feedback loop |
| **Academic Value** | Understanding february 5, 2018 - vix spiked 115%, xiv etn lost 90%+ in after-hours trading through multi-agent simulation |

## §2 Theoretical Foundation

- Volatility product feedback (Bergsma & Jiang, 2022)
- Short volatility crowding (Culp et al., 2018)
- Inverse VIX ETN dynamics

## §3 Agent Descriptions

### ShortVolTrader
**Theoretical Basis**: Short volatility strategy
**Market Role**: destabilizing
**Description**: Sells VIX futures/ETNs, profits from contango but faces tail risk
**Parameters**: short_size=10000, stop_loss=0.5, rebalance_frequency=daily

### VolETNManager
**Theoretical Basis**: Inverse ETN rebalancing mechanics
**Market Role**: destabilizing
**Description**: Must buy VIX futures when VIX rises, creating positive feedback
**Parameters**: leverage=-1.0, rebalance_threshold=0.05, rebalance_size=50000

### LongVolHedger
**Theoretical Basis**: Portfolio insurance via volatility
**Market Role**: stabilizing
**Description**: Holds long VIX positions as portfolio hedge
**Parameters**: hedge_ratio=0.1, target_vol=0.15

### VolArbitrageur
**Theoretical Basis**: VIX futures term structure arbitrage
**Market Role**: neutral
**Description**: Trades VIX term structure dislocations
**Parameters**: entry_threshold=0.02, position_size=5000

### EquityTrader
**Theoretical Basis**: Equity market participant
**Market Role**: neutral
**Description**: Trades equities, affected by volatility spike
**Parameters**: position_size=1000, risk_limit=0.02


## §4 Usage

### Rule Variant
```bash
python examples/Volmageddon/Rule/run_volmageddon.py \
    -c configs/Volmageddon/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/Volmageddon/LLM/run_volmageddon_llm.py \
    -c configs/Volmageddon/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/Volmageddon/RuleLLM/run_volmageddon_rulellm.py \
    -c configs/Volmageddon/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/Volmageddon/Rag/run_volmageddon_rag.py \
    -c configs/Volmageddon/Rag/simulation.yml
```

## §5 References

- Volatility product feedback (Bergsma & Jiang, 2022)
- Short volatility crowding (Culp et al., 2018)
- Inverse VIX ETN dynamics
