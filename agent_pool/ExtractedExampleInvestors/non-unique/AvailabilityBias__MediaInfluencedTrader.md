# AvailabilityBias / Media Influenced Trader

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | AvailabilityBias |
| Agent type | Media Influenced Trader |
| Canonical class | `MediaInfluencedTrader` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

The MediaInfluencedTrader is an investor whose perceptions of market conditions are shaped by media framing and social signal amplification rather than direct observation of price-fundamental relationships. When the media covers a market event intensively (proxied by the deviation signal being amplified by media_weight x social_amplification), this investor perceives the event as more significant than it is. This investor does not overweight recent returns (unlike RecentEventOverweighter) but instead overweights the magnitude of any current deviation -- treating deviation as a media-salient signal with 1.2x perceived intensity. This creates a distinct channel: availability through media salience rather than temporal recency.

## Financial Theory / Theoretical Basis

### Rule / `MediaInfluencedTrader`
- Theory: simulation-bases.md Section 4.2 -- MediaInfluencedTrader
- Theoretical basis: Schwarz et al. (1991); Tetlock (2007) -- Media-driven availability channel.

### LLM / `LLMMediaInfluencedTrader`
- LLM-driven trader influenced by media coverage and social signals. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMMediaInfluencedTrader`
- RuleLLM -- influenced by media coverage and social signals. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMMediaInfluencedTrader`
- RAG-augmented -- influenced by media coverage and social signals. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `10000.0`<br>LLM: `10000.0`<br>RuleLLM: `10000.0`<br>Rag: `10000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `0.0`<br>LLM: `0.0`<br>RuleLLM: `0.0`<br>Rag: `0.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.AvailabilityBias.LLM.prompts:LLM_MEDIA_INFLUENCED_TRADER_SYS', 'user_message': 'examples.AvailabilityBias.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 500}}`<br>RuleLLM: `{'sys_message': 'examples.AvailabilityBias.RuleLLM.prompts:RULELLM_MEDIA_INFLUENCED_TRADER_SYS', 'user_message': 'examples.AvailabilityBias.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_new_tokens': 500}}`<br>Rag: `{'sys_message': 'examples.AvailabilityBias.Rag.prompts:RAG_MEDIA_INFLUENCED_TRADER_SYS', 'user_message': 'examples.AvailabilityBias.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_new_tokens': 600}}` | LLM, Rag, RuleLLM |
| max_order | Rule: `300.0` | Rule |
| media_threshold | Rule: `0.03` | Rule |
| media_weight | Rule: `0.8`<br>RuleLLM: `0.8`<br>Rag: `0.8` | Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |
| quantity_scale | Rule: `5000.0` | Rule |
| social_amplification | Rule: `1.5`<br>RuleLLM: `1.5`<br>Rag: `1.5` | Rag, Rule, RuleLLM |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | media_influenced_trader | Media Influenced Trader | `MediaInfluencedTrader` | 2 | `examples/AvailabilityBias/Rule/players.py` |
| LLM | llm_media_influenced_trader | LLM Media Influenced Trader | `LLMMediaInfluencedTrader` | 2 | `examples/AvailabilityBias/LLM/players.py` |
| RuleLLM | rulellm_media_influenced_trader | RuleLLM Media Influenced Trader | `RuleLLMMediaInfluencedTrader` | 2 | `examples/AvailabilityBias/RuleLLM/players.py` |
| Rag | ragllm_media_influenced_trader | RAG Media Influenced Trader | `RagLLMMediaInfluencedTrader` | 2 | `examples/AvailabilityBias/Rag/players.py` |

## Scenario-Theory Excerpts

### Investor: MediaInfluencedTrader

#### 4.2.1  Summary

The MediaInfluencedTrader is an investor whose perceptions of market conditions are shaped by media framing and social signal amplification rather than direct observation of price-fundamental relationships. When the media covers a market event intensively (proxied by the deviation signal being amplified by media_weight x social_amplification), this investor perceives the event as more significant than it is. This investor does not overweight recent returns (unlike RecentEventOverweighter) but instead overweights the magnitude of any current deviation -- treating deviation as a media-salient signal with 1.2x perceived intensity. This creates a distinct channel: availability through media salience rather than temporal recency.

#### 4.2.2  Theoretical and Empirical Foundation

**Theory 1: Media Influence on Asset Prices (Tetlock)**
- Theory / Study: Media coverage as a driver of investor sentiment and return predictability
- Citation: Tetlock, P. C. (2007). "Giving content to investor sentiment: The role of media in the stock market." *Journal of Finance*, 62(3), 1139-1168. DOI: 10.1111/j.1540-6261.2007.01232.x
- Core Insight: Tetlock (2007) finds that media pessimism (negative language in Wall Street Journal columns) predicts downward pressure on Dow Jones next day and subsequent reversal within 1-2 weeks. The initial price impact is driven by sentiment-influenced retail investors (the MediaInfluencedTrader archetype); the subsequent reversal reflects rational correction. The effect is linear in media intensity.
- Mathematical Formulation: Tetlock (2007) estimates a 1 standard deviation increase in media pessimism predicts a -0.5% market return, with reversal within 3-5 days. Extrapolated to simulation: media_weight x deviation x social_amplification = 0.80 x deviation x 1.50 = 1.20 x deviation.
- Empirical Evidence: Tetlock (2007) Table 2 shows that media pessimism explains 11-18% of next-day return variance for high-coverage stocks. Amplification consistent with social_amplification = 1.5 (50% additional amplification from social/network effects beyond direct media).
- Relevance to This Investor: amplified_signal = 0.80 x deviation x 1.50 = 1.20 x deviation. The signal threshold of 0.03 means the MediaInfluencedTrader activates at |deviation| > 0.025.

**Theory 2: Social Amplification of Risk (Schwarz et al.; Kasperson et al.)**
- Theory / Study: Social amplification creating cascade effects in perceived risk
- Citation: Schwarz, N., et al. (1991). "Ease of retrieval as information." *Journal of Personality and Social Psychology*, 61(2), 195-202. DOI: 10.1037/0022-3514.61.2.195. Also: Kasperson, R. E., et al. (1988). "The social amplification of risk: A conceptual framework." *Risk Analysis*, 8(2), 177-187. DOI: 10.1111/j.1539-6924.1988.tb01168.x
- Core Insight: Schwarz et al. (1991) show that information delivered through high-profile channels (more "available" due to broadcast intensity) is perceived as more important even when the underlying content is identical to less-publicized information. Kasperson et al. (1988) develop the Social Amplification of Risk Framework (SARF) showing how social networks multiply the perceived importance of risk signals. Applied to markets: social_amplification captures the multiplicative effect of network-based information spread.
- Empirical Evidence: Kasperson et al.'s SARF documents amplification factors of 1.5-3.0 across different risk domains; social_amplification = 1.5 is at the conservative end of this range, consistent with mature financial markets with professional investor participation.
- Relevance to This Investor: social_amplification = 1.5 is the network amplification factor applied on top of the direct media weight; the two combined (media_weight x social_amplification = 1.20) represent the total perceived signal inflation from media coverage.

#### 4.2.3  Design Purpose and Activation Scenarios

**Purpose**: Model the media-salience channel of availability bias -- where the *intensity of coverage* (not the recency of an event) amplifies the perceived importance of fundamental signals. Creates overreaction to current fundamental deviations that are heavily covered.

**Activation Scenarios**:
- Scenario A (Small deviation, |deviation| < 0.025): |amplified_signal| < 0.03 -> hold. Even media amplification is insufficient to trigger trading.
- Scenario B (Moderate deviation, 0.025 < |deviation| < 0.05): |amplified_signal| = 0.03-0.06 -> trade proportionally. Media is covering the deviation intensively; investor reacts more strongly than objective analysis alone would justify.
- Scenario C (Large deviation, |deviation| > 0.05): |amplified_signal| > 0.06 -> trade with larger proportional size. Intensive media coverage of a significant fundamental gap triggers stronger activation.

**Market Contribution**: Destabilizing -- amplifies fundamental deviations into larger price moves than rational analysis would produce. Unlike RecentEventOverweighter (which amplifies momentum), MediaInfluencedTrader amplifies level-based deviations -- a different and potentially complementary destabilizing mechanism.

**Interaction with other agents**: Amplifies the same deviations that SystematicAnalyst is correcting (both respond to deviation, but MediaInfluencedTrader overreacts); may amplify the same direction as RecentEventOverweighter when a large deviation was preceded by a dramatic return.

#### 4.2.4  Behavioral Framework

**4.2.4.1  Decision Information Set**
- `deviation`: Primary signal -- multiplied by media_weight x social_amplification to produce the amplified_signal. This represents media coverage intensity as a function of current mispricing.
- `price`: Used for order submission and cash constraint calculation.
- Does NOT use `return_pct` -- the MediaInfluencedTrader responds to media framing of *current state* (deviation level), not recent event salience. This is distinct from RecentEventOverweighter.

**4.2.4.2  Core Behavioral Mechanism**
1. Each round, observe `deviation` from market broadcast.
2. Compute: amplified_signal = media_weight x deviation x social_amplification = 0.80 x deviation x 1.50 = 1.20 x deviation.
3. If |amplified_signal| > 0.03: trade. (Equivalent to |deviation| > 0.025.)
4. If amplified_signal > 0 (market above fundamental; media narrative amplifies optimism): buy. Quantity = min(300, amplified_signal x 5000). Cash-constrained.
5. If amplified_signal < 0 (market below fundamental; media narrative amplifies pessimism): sell. Quantity = min(300, |amplified_signal| x 5000). Position-constrained.
6. Hold if |amplified_signal| <= 0.03.
7. The media-amplified signal is directional with respect to deviation: it buys into positive media salience and sells into negative media salience, making the reaction destabilizing when media framing reinforces the current mispricing.

**4.2.4.3  Mathematical Model**
- Decision variable: Q*(t) in shares
- Amplified signal: ã(t) = m_w x δ(t) x s_a, where m_w = media_weight = 0.80, s_a = social_amplification = 1.50, δ = deviation
- Trigger: trade if |ã(t)| > 0.03 (implicitly, |δ| > 0.025)
- Sizing: Q*(t) = min(Q_max, |ã(t)| x 5000), where Q_max = 300
- Direction: buy if ã(t) > 0; sell if ã(t) < 0
- State variables: cash, position

| Parameter            | Value | Meaning                                           | Config Path                                                   | Source                  |
|----------------------|-------|---------------------------------------------------|---------------------------------------------------------------|-------------------------|
| media_weight         | 0.80  | Media intensity amplification of deviation signal | `configs/AvailabilityBias/Rule/players.yml -> media_influenced_trader` | Tetlock (2007)          |
| social_amplification | 1.5   | Social network additional amplification factor    | `configs/AvailabilityBias/Rule/players.yml -> media_influenced_trader` | Kasperson et al. (1988) |
| initial_cash         | 10000 | Starting cash reserves                            | `configs/AvailabilityBias/Rule/players.yml -> media_influenced_trader` | Normalization           |
| initial_position     | 0     | Starting share position                           | `configs/AvailabilityBias/Rule/players.yml -> media_influenced_trader` | Normalization           |

**4.2.4.4  Behavioral Properties**
- Time horizon: Short-to-medium term -- responds to current deviation level; position held until deviation corrects
- Risk tolerance: Medium -- overreacts to media signals but with appropriate direction (contrarian to deviation); less momentum-driven than RecentEventOverweighter
- Information asymmetry: None -- responds to publicly broadcast deviation, but with distorted magnitude perception
- Psychological profile: Media-driven, social-signal-dependent. Treats media consensus as a signal multiplier. In LLM variants, the persona references news headlines and social chatter as primary inputs.

#### 4.2.5  Decision Process Walkthrough

Given: price = 103.0, fundamental = 100.0, deviation = +0.03, media_weight = 0.80, social_amplification = 1.50, cash = 10000

Step 1: Compute amplified_signal = 0.80 x 0.03 x 1.50 = 0.036.
Step 2: |0.036| > 0.03theta YES -> trade (buy, since positive media salience reinforces optimism).
Step 3: Quantity = min(300, 0.036 x 5000) = 180 shares, then cash-constrained to 97.09 shares at price 103.
Step 4: Send order: action=buy, quantity≈97.09, bid_price=103.
Result: media-driven buying amplifies a positive deviation and pushes price further above fundamental.

#### 4.2.6  Worked Numerical Example

Market state: price = 97.0, fundamental = 100.0, deviation = -0.03, media_weight = 0.80, social_amplification = 1.50, position = 200

Amplified signal: ã = 0.80 x (-0.03) x 1.50 = -0.036.
|-0.036| > 0.03 -> sell (negative media salience reinforces pessimism).
Quantity: min(300, 0.036 x 5000) = 180 shares, then position-constrained to 180.
Order: action=sell, quantity=180, bid_price=97.
Rationale: The media is amplifying the negative deviation into a salient pessimistic signal. The investor overreacts by selling into an already undervalued market, creating the destabilizing media-availability channel.

#### 4.2.7  Academic References

| # | Citation                                                                                                                                                        | Notes                                                                               |
|---|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|
| 1 | Tetlock, P. C. (2007). "Giving content to investor sentiment." *Journal of Finance*, 62(3), 1139-1168. DOI: 10.1111/j.1540-6261.2007.01232.x                    | media_weight and social_amplification calibration; return predictability from media |
| 2 | Schwarz, N., et al. (1991). "Ease of retrieval as information." *Journal of Personality and Social Psychology*, 61(2), 195-202. DOI: 10.1037/0022-3514.61.2.195 | Ease of retrieval as signal amplifier; basis for media availability channel         |
| 3 | Kasperson, R. E., et al. (1988). "The social amplification of risk." *Risk Analysis*, 8(2), 177-187. DOI: 10.1111/j.1539-6924.1988.tb01168.x                    | social_amplification calibration; network effects in risk perception                |


---

## Source Docstring Excerpts

### Rule / `MediaInfluencedTrader`

```text
Overweights information from prominent media/social coverage.

Theory: simulation-bases.md Section 4.2 -- MediaInfluencedTrader
Theoretical basis: Schwarz et al. (1991); Tetlock (2007) -- Media-driven availability channel.
Amplifies the perceived deviation by social_amplification factor,
then trades when media-weighted signal exceeds threshold.
See simulation-bases.md Section 4.2.4.3 for mathematical model.
```

### LLM / `LLMMediaInfluencedTrader`

```text
LLM-driven trader influenced by media coverage and social signals. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMMediaInfluencedTrader`

```text
RuleLLM -- influenced by media coverage and social signals. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMMediaInfluencedTrader`

```text
RAG-augmented -- influenced by media coverage and social signals. Theory: simulation-bases.md Section 4.2.
```
