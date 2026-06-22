# GFC2008 / Rating Agency

## Basic Information

| Field | Content |
| --- | --- |
| Scenario | GFC2008 |
| Agent type | Rating Agency |
| Canonical class | `RatingAgency` |
| Catalog category | Financial/investment-market participant |
| Implemented mechanisms | Rule, LLM, RuleLLM, Rag |

## Definition and Goal

- **Primary Citation**: Bolton, P., Freixas, X. & Shapiro, J. (2012). "The Credit Ratings Game." *Journal of Finance*, 67(1), 85-111. https://doi.org/10.1111/j.1540-6261.2011.01708.x - **Theory Status**: Canonical theoretical model -- provides rigorous equilibrium characterization of rating inflation under issuer-pays incentive - **Original Context**: Credit rating agency equilibrium model; issuer-pays vs. investor-pays; rating inflation and selective shopping

## Financial Theory / Theoretical Basis

### Rule / `RatingAgency`
- Theory: simulation-bases.md Section 4.2 -- RatingAgency
- Theoretical basis: Rating agency conflict of interest (Bolton et al., 2012).

### LLM / `LLMRatingAgency`
- LLM-driven RatingAgency: overrates securities due to issuer-pays model. Theory: simulation-bases.md Section 4.2.

### RuleLLM / `RuleLLMRatingAgency`
- RuleLLM-driven RatingAgency: overrates securities due to issuer-pays model. Theory: simulation-bases.md Section 4.2.

### Rag / `RagLLMRatingAgency`
- RAG-augmented RatingAgency: overrates securities due to issuer-pays model. Theory: simulation-bases.md Section 4.2.

## Behavior and Decision Logic

- Key implementation methods: `act`, `decide`, `perceive`
- This profile includes configured `role: player` agents only; market coordinators are excluded.
- Concrete trading, holding, intervention, communication, and risk-control behavior is implemented in `decide()` / `_make_decision()` and parameterized by `players.yml`.

## Configuration Parameters

| Parameter | Value by mechanism | Mechanisms |
| --- | --- | --- |
| base_size | Rule: `250`<br>LLM: `250`<br>RuleLLM: `250`<br>Rag: `250` | LLM, Rag, Rule, RuleLLM |
| custom_state_hot_limit | Rule: `3`<br>LLM: `3`<br>RuleLLM: `3`<br>Rag: `3` | LLM, Rag, Rule, RuleLLM |
| fundamental_value | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| initial_cash | Rule: `1500000.0`<br>LLM: `1500000.0`<br>RuleLLM: `1500000.0`<br>Rag: `1500000.0` | LLM, Rag, Rule, RuleLLM |
| initial_position | Rule: `500`<br>LLM: `500`<br>RuleLLM: `500`<br>Rag: `500` | LLM, Rag, Rule, RuleLLM |
| initial_price | Rule: `100.0`<br>LLM: `100.0`<br>RuleLLM: `100.0`<br>Rag: `100.0` | LLM, Rag, Rule, RuleLLM |
| llm | LLM: `{'sys_message': 'examples.GFC2008.LLM.prompts:LLM_RATING_AGENCY_SYS', 'user_message': 'examples.GFC2008.LLM.prompts:LLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 512}}`<br>RuleLLM: `{'sys_message': 'examples.GFC2008.RuleLLM.prompts:RULELLM_RATING_AGENCY_SYS', 'user_message': 'examples.GFC2008.RuleLLM.prompts:RULELLM_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.3, 'max_tokens': 512}}`<br>Rag: `{'sys_message': 'examples.GFC2008.Rag.prompts:RAGLLM_RATING_AGENCY_SYS', 'user_message': 'examples.GFC2008.Rag.prompts:RAG_USER_TEMPLATE', 'lm_type': 'api', 'lm_name': 'ark/doubao-seed-2-0-mini-260428', 'generation_config': {'temperature': 0.4, 'max_tokens': 600}}` | LLM, Rag, RuleLLM |
| overrating_bias | Rule: `0.2`<br>LLM: `0.2`<br>RuleLLM: `0.2`<br>Rag: `0.2` | LLM, Rag, Rule, RuleLLM |
| private_knowledge | Rag: `{'from_global_resources': ['MinerU_processed'], 'local_resources': {'local_uri': '', 'local_resources': []}, 'rag': {'from_global_index_dir': ['rag_index'], 'local_index_dir': '', 'embed_type': 'litellm', 'embed_model': 'openai/hunyuan-embedding', 'embed_api_key': '{{ HUNYUAN_API_KEY }}', 'embed_api_base': 'https://api.hunyuan.cloud.tencent.com/v1', 'chunk_size': 512, 'chunk_overlap': 64, 'top_k': 5}}` | Rag |

## Implemented Variants

| Mechanism | Config key | Display name | Class | Instances | Source |
| --- | --- | --- | --- | --- | --- |
| Rule | ratingagency | RatingAgency | `RatingAgency` | 2 | `examples/GFC2008/Rule/players.py` |
| LLM | ratingagency | RatingAgency | `LLMRatingAgency` | 2 | `examples/GFC2008/LLM/players.py` |
| RuleLLM | ratingagency | RatingAgency | `RuleLLMRatingAgency` | 2 | `examples/GFC2008/RuleLLM/players.py` |
| Rag | ratingagency | RatingAgency | `RagLLMRatingAgency` | 2 | `examples/GFC2008/Rag/players.py` |

## Scenario-Theory Excerpts

### Theory 2: Rating Agency Conflict of Interest and Inflation of Fundamentals

#### 1.1 Citation and Status

- **Primary Citation**: Bolton, P., Freixas, X. & Shapiro, J. (2012). "The Credit Ratings Game." *Journal of Finance*, 67(1), 85-111. https://doi.org/10.1111/j.1540-6261.2011.01708.x
- **Theory Status**: Canonical theoretical model -- provides rigorous equilibrium characterization of rating inflation under issuer-pays incentive
- **Original Context**: Credit rating agency equilibrium model; issuer-pays vs. investor-pays; rating inflation and selective shopping

#### 1.2 Core Theoretical Mechanism

Under the issuer-pays model, rating agencies receive fees from the same issuers whose securities they rate, creating a conflict of interest: agencies that issue harsh ratings lose business to competitors who inflate. Bolton et al. (2012) show that in a competitive equilibrium with naïve (trusting) investors, all rating agencies inflate to the maximum degree consistent with maintaining reputation -- an inflation level that exceeds what would occur under investor-pays. The model predicts that rating inflation is highest for complex opaque products (CDOs, CMOs) where it is hardest to detect ex-post, which is precisely the category of MBS that failed in 2007-2009.

In the simulation, RatingAgency (Section 4.2) implements this through the overrating_bias parameter: perceived_fundamental = fundamental x (1 + overrating_bias). The agent then buys whenever price < perceived_fundamental x 0.95 -- it is purchasing securities at prices that it believes represent value (based on inflated fundamental) but which are actually overvalued relative to true fundamental F. This creates sustained demand that keeps price above F throughout the bubble phase, directly mimicking the role of AAA ratings in sustaining demand for subprime MBS.

#### 1.3 Mathematical Formulation

**Rating inflation model**:
```
perceived_fundamental = F x (1 + overrating_bias)

Buy condition: price < perceived_fundamental x 0.95
  -> i.e., buy when price < F x (1 + overrating_bias) x 0.95
  -> agent buys up to 5% below the inflated fundamental

Inflation magnitude: overrating_bias ∈ [0.10, 0.40]
  (AAA-rated CDO tranches overvalued 15-30% based on realized default rates)
```

| Symbol          | Definition                                    | Calibrated Value | Source                                                |
|-----------------|-----------------------------------------------|------------------|-------------------------------------------------------|
| overrating_bias | Fractional inflation of perceived fundamental | 0.20             | Gorton (2010): CDO overvaluation 15-30%               |
| Buy cap         | max 300 shares per round                      | Fixed            | Represents finite investor-base for each rating cycle |

#### 1.4 Empirical Evidence

| Study                             | Context                                     | Finding                                                                          | Relevance                                      |
|-----------------------------------|---------------------------------------------|----------------------------------------------------------------------------------|------------------------------------------------|
| Bolton et al. (2012). *JF* 67(1)  | Theoretical; calibrated to S&P/Moody's data | Rating inflation maximized for opaque products                                   | Validates overrating_bias ∈ [0.15, 0.30] range |
| Pagano & Volpin (2012). *RFS*     | CDO ratings 2000-07                         | CDOs rated AAA had loss rates 40-60% in stress scenarios; true probability ≈ BBB | Calibrates overrating_bias ≈ 0.20-0.40         |
| Griffin & Tang (2012). *JF* 67(4) | CDO ratings                                 | Moody's consistently inflated subprime CDO ratings by 2-3 notch equivalents      | Sets overrating_bias ≈ 0.15-0.25               |

#### 1.5 Relevance to Simulation

Theory 2 is encoded by RatingAgency (Section 4.2). Its presence during the bubble phase creates artificial demand that allows MBSOriginator to continue distributing overpriced securities. When price eventually drops below F (triggered by a noise shock or LeveragedInvestor fire sale), RatingAgency continues buying based on inflated fundamental -- slowing but not stopping the decline.

---

## Source Docstring Excerpts

### Rule / `RatingAgency`

```text
Theory: simulation-bases.md Section 4.2 -- RatingAgency

Theoretical basis: Rating agency conflict of interest (Bolton et al., 2012).
Overrates securities due to issuer-pays model; creates inflated valuations.
See simulation-bases.md Section 4.2 for mathematical model.
```

### LLM / `LLMRatingAgency`

```text
LLM-driven RatingAgency: overrates securities due to issuer-pays model. Theory: simulation-bases.md Section 4.2.
```

### RuleLLM / `RuleLLMRatingAgency`

```text
RuleLLM-driven RatingAgency: overrates securities due to issuer-pays model. Theory: simulation-bases.md Section 4.2.
```

### Rag / `RagLLMRatingAgency`

```text
RAG-augmented RatingAgency: overrates securities due to issuer-pays model. Theory: simulation-bases.md Section 4.2.
```
