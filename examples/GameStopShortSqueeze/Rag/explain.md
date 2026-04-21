# GameStopShortSqueeze Simulation

## Overview

| Item | Description |
|------|-------------|
| **Phenomenon** | January 2021 GameStop short squeeze - Reddit coordination drove 1,700% price increase |
| **Model** | Rule-based / LLM / RuleLLM / RAG |
| **Key Feature** | GameStop short squeeze simulation with retail coordination, gamma exposure, and social media-driven trading |
| **Academic Value** | Understanding january 2021 gamestop short squeeze - reddit coordination drove 1,700% price increase through multi-agent simulation |

## Theoretical Foundation

- Gamma squeeze dynamics (Jarrow & Li, 2021)
- Social media and retail coordination (Lyocsa et al., 2022)
- Short sale constraints (Jones & Lamont, 2002)

## Agent Descriptions

### RetailCoordinated
**Theoretical Basis**: Social media coordination
**Market Role**: destabilizing
**Description**: Retail traders coordinating via social media to buy and hold
**Parameters**: diamond_hands=True, buy_pressure=0.8, coordination_strength=0.6

### ShortSellerHF
**Theoretical Basis**: Short selling and squeeze dynamics
**Market Role**: destabilizing
**Description**: Heavily short hedge fund forced to cover at higher prices
**Parameters**: short_interest=1.4, margin_requirement=0.5, cover_threshold=0.3

### MarketMakerGamma
**Theoretical Basis**: Delta hedging and gamma exposure
**Market Role**: neutral
**Description**: Market maker hedging options exposure creates buying pressure
**Parameters**: gamma_exposure=0.3, hedge_frequency=continuous

### InstitutionalValue
**Theoretical Basis**: Fundamental analysis
**Market Role**: stabilizing
**Description**: Values company based on fundamentals, sees extreme overvaluation
**Parameters**: fundamental_value=20.0, sell_threshold=3.0, patience=high

### MomentumRetail
**Theoretical Basis**: FOMO trading
**Market Role**: neutral
**Description**: Retail momentum trader driven by fear of missing out
**Parameters**: fomo_threshold=0.1, position_size=50, attention_span=short


## Usage

### Rule Variant
```bash
python examples/GameStopShortSqueeze/Rule/run_gamestopshortsqueeze.py \
    -c configs/GameStopShortSqueeze/Rule/simulation.yml
```

### LLM Variant
```bash
python examples/GameStopShortSqueeze/LLM/run_gamestopshortsqueeze_llm.py \
    -c configs/GameStopShortSqueeze/LLM/simulation.yml
```

### RuleLLM Variant
```bash
python examples/GameStopShortSqueeze/RuleLLM/run_gamestopshortsqueeze_rulellm.py \
    -c configs/GameStopShortSqueeze/RuleLLM/simulation.yml
```

### RAG Variant
```bash
python examples/GameStopShortSqueeze/Rag/run_gamestopshortsqueeze_rag.py \
    -c configs/GameStopShortSqueeze/Rag/simulation.yml
```

## References

- Gamma squeeze dynamics (Jarrow & Li, 2021)
- Social media and retail coordination (Lyocsa et al., 2022)
- Short sale constraints (Jones & Lamont, 2002)
