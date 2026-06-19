# AssetBubble / Noise Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AssetBubble |
| Agent type | Noise Trader |
| Canonical class | `NoiseTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, RuleLLM, Rag |

## Definition and Goal

- **Citation**: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703-738. https://doi.org/10.1086/261703 - **Core Insight**: Uninformed traders acting on noise (sentiment, rumour, trend extrapolation) create systematic and persistent deviations from fundamental value. Their irrational behaviour introduces a risk that rational arbitrageurs cannot diversify away -- if sentiment becomes more bullish, mispricings can widen, causing rational arbitrageurs to lose money before the eventual correction. This "noise trader risk" is itself a cost that limits arbitrage and sustains bubbles. - **Mathematical Formulation**: ``` total_sentiment(t) = random_noise(t) + herding_weight x price_return(t) x 10 where random_noise ~ N(0, sentiment_volatility²)

## Financial Theory / Theoretical Basis

### Rule / `NoiseTrader`
- Noise trader driven by sentiment and crowd behavior.
- Theory: simulation-bases.md Section 4.3 -- NoiseTrader
- Theory: De Long et al. (1990) - Noise Trader Risk
- Behavior:
- - Trades based on "sentiment" (random with bias)
- - Tends to follow recent price direction (herding)
- - Can amplify bubbles by joining buying frenzy
- - Sentiment can flip, causing sudden selling
- Effect: DESTABILIZING - Amplifies bubbles through herding
- Formula:
- -> simulation-bases.md Section 4.3 -- NoiseTrader (Rule-Based Behavior)

### RuleLLM / `RuleLLMNoiseTrader`
- Hybrid sentiment rules with LLM reasoning. Theory: simulation-bases.md Section 4.3 -- NoiseTrader.

### Rag / `RagLLMNoiseTrader`
- RAG-augmented sentiment rules with retrieved knowledge. Theory: simulation-bases.md Section 4.3 -- NoiseTrader.

## Behavior and Decision Logic

- Key implementation methods: `decide`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_position_size | Rule: `20.0`<br>RuleLLM: `15.0`<br>Rag: `15.0` | Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>RuleLLM: `3`<br>Rag: `3` | Rag, Rule, RuleLLM |
| herding_weight | Rule: `0.6`<br>RuleLLM: `0.7`<br>Rag: `0.7` | Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | Rag, Rule, RuleLLM |
| llm | RuleLLM: `{'sys_message': 'examples.AssetBubble.RuleLLM.prompts:RULELLM_NOISE_SYS', 'user_message': 'examples.AssetBubble.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.AssetBubble.Rag.prompts:RAGLLM_NOISE_SYS', 'user_message': 'examples.AssetBubble.Rag.prompts:RAGLLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.5, 'max_new_tokens': 600}}` | Rag, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| sentiment_volatility | Rule: `0.3`<br>RuleLLM: `0.3`<br>Rag: `0.3` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | noise_trader | Noise Trader | `NoiseTrader` | 2 | `examples/AssetBubble/Rule/players.py` |
| RuleLLM | rulellm_noise | RuleLLM Noise Trader | `RuleLLMNoiseTrader` | 2 | `examples/AssetBubble/RuleLLM/players.py` |
| Rag | ragllm_noise | RAG Noise Trader | `RagLLMNoiseTrader` | 2 | `examples/AssetBubble/Rag/players.py` |

## Scenario-Theory Excerpts

### Theory 3: Noise Trader Risk and Herding

- **Citation**: De Long, J. B., Shleifer, A., Summers, L. H., & Waldmann, R. J. (1990). Noise trader risk in financial markets. *Journal of Political Economy*, 98(4), 703-738. https://doi.org/10.1086/261703
- **Core Insight**: Uninformed traders acting on noise (sentiment, rumour, trend extrapolation) create systematic and persistent deviations from fundamental value. Their irrational behaviour introduces a risk that rational arbitrageurs cannot diversify away -- if sentiment becomes more bullish, mispricings can widen, causing rational arbitrageurs to lose money before the eventual correction. This "noise trader risk" is itself a cost that limits arbitrage and sustains bubbles.
- **Mathematical Formulation**:
  ```
  total_sentiment(t) = random_noise(t) + herding_weight x price_return(t) x 10
  where random_noise ~ N(0, sentiment_volatility²)

  Buy when:  total_sentiment(t) > sentiment_threshold  -> Q = total_sentiment x base_size
  Sell when: total_sentiment(t) < -sentiment_threshold -> Q = total_sentiment x base_size
  ```
- **Empirical Evidence**: De Long et al. (1990) show analytically and empirically that noise trader sentiment follows a random walk with mean reversion, with typical one-period swings of 5-15% of the asset value. Barber & Odean (2008) document that retail investors exhibit strong herding behaviour, buying stocks that attract media attention regardless of fundamentals.
- **Relevance to This Simulation**: `NoiseTrader` agents amplify the bubble through two channels: (1) random sentiment shocks add stochastic demand that can tip the positive-feedback loop, and (2) the herding component (`herding_weight x price_return`) creates momentum-following demand that reinforces price trends.
- **Calibration Implication**: `sentiment_volatility = 0.3` matches De Long et al. (1990)'s assumed noise trader variance; `herding_weight = 0.7` calibrates the herding fraction to produce meaningful but not dominant trend-following demand.

---

## Source Docstring Excerpts

### Rule / `NoiseTrader`

```text
Noise trader driven by sentiment and crowd behavior.
Theory: simulation-bases.md Section 4.3 -- NoiseTrader

Theory: De Long et al. (1990) - Noise Trader Risk
    Uninformed traders who create systematic deviations from fundamental value.
    -> simulation-bases.md Section 2.3

Behavior:
    - Trades based on "sentiment" (random with bias)
    - Tends to follow recent price direction (herding)
    - Can amplify bubbles by joining buying frenzy
    - Sentiment can flip, causing sudden selling

Effect: DESTABILIZING - Amplifies bubbles through herding

Formula:
    total_sentiment = random_sentiment + herding_weight x price_return x 10
    -> simulation-bases.md Section 4.3 -- NoiseTrader (Rule-Based Behavior)

Parameters from config extras:
    - sentiment_volatility, herding_weight, base_position_size
    -> simulation-bases.md Section 6
```

### RuleLLM / `RuleLLMNoiseTrader`

```text
Hybrid sentiment rules with LLM reasoning. Theory: simulation-bases.md Section 4.3 -- NoiseTrader.
```

### Rag / `RagLLMNoiseTrader`

```text
RAG-augmented sentiment rules with retrieved knowledge. Theory: simulation-bases.md Section 4.3 -- NoiseTrader.
```
