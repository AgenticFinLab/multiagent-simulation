# EndowmentEffect LLM — Implementation Guide

## 1. Overview

| Field | Value |
|---|---|
| Variant | LLM |
| Decision logic | Persona-driven language-model deliberation |
| Shared environment | `Market` imported from `Rule/players.py` |
| Configuration | `configs/EndowmentEffect/LLM/` |
| Entry point | `run_endowmenteffect_llm.py` |

The variant keeps the shared market mechanism and replaces deterministic
investor rules with persona-only prompts. Executable constraints remain in
`LLMInvestor.decide`: output validation, order-size caps, cash limits, and
inventory limits.

## 2. Theory → Implementation Mapping

| Design source | Runtime implementation | Prompt implementation |
|---|---|---|
| `simulation-bases.md §4.1` EndowedHolder | `players.py:LLMEndowedHolder`, inheriting `LLMInvestor.decide` | `prompts.py:LLM_ENDOWED_HOLDER_SYS` |
| `simulation-bases.md §4.2` StatusQuoSeller | `players.py:LLMStatusQuoSeller`, inheriting `LLMInvestor.decide` | `prompts.py:LLM_STATUS_QUO_SELLER_SYS` |
| `simulation-bases.md §4.3` RationalArbitrageur | `players.py:LLMRationalArbitrageur`, inheriting `LLMInvestor.decide` | `prompts.py:LLM_RATIONAL_ARBITRAGEUR_SYS` |
| `simulation-bases.md §4.4` NewBuyer | `players.py:LLMNewBuyer`, inheriting `LLMInvestor.decide` | `prompts.py:LLM_NEW_BUYER_SYS` |
| `simulation-bases.md §4.5` NoiseTrader | `players.py:LLMNoiseTrader`, inheriting `LLMInvestor.decide` | `prompts.py:LLM_NOISE_TRADER_SYS` |
| `simulation-bases.md §3` market design | `Rule/players.py:Market`, re-exported by `LLM/players.py` | Not applicable |

The prompts encode preferences and reasoning styles, not numeric trading
thresholds. This preserves the purpose of the LLM variant described in
`simulation-bases.md §9`.

## 3. Market Mechanism

`Market` is shared with the Rule variant. Each round it broadcasts `price`,
`fundamental`, `deviation`, and `round`. Investors return one order containing
`action`, `bid_price`, `quantity`, `reasoning`, `analysis`, and `strategy`.
The star topology in `topology.yml` routes market broadcasts to all investors
and routes their orders back to the market.

## 4. LLM Variant-Specific Features

- System and user prompt paths come from each player's `extras.llm` config.
- Prompts do not name the studied phenomenon or reveal the price-update law.
- Responses must use `<analysis>...</analysis>` followed by a JSON
  `<decision>...</decision>` block.
- `decide` reads every required response field directly and rejects missing,
  non-finite, negative, or inconsistent values.
- A configured, counted retry policy handles malformed or transient model
  output. Exhaustion raises `RuntimeError`; there is no silent hold fallback.
- `base_size`, available cash, and inventory cap the executable quantity.

## 5. Configuration

`configs/EndowmentEffect/LLM/players.yml` supplies all required runtime values:

| Key | Purpose |
|---|---|
| `initial_cash`, `initial_position` | Initial portfolio state |
| `base_size` | Maximum units in one order |
| `record_path`, `custom_state_hot_limit` | History storage |
| `llm.lm_type`, `llm.lm_name` | Inference backend and model |
| `llm.sys_message`, `llm.user_message` | Prompt constants |
| `llm.max_retries` | Counted inference/parse attempts |
| `llm.generation_config` | Model generation settings |

Required values use direct key access. Missing configuration therefore fails
at setup instead of activating hidden defaults.

## 6. Running Instructions

From the repository root, configure the API credentials required by the model
named in `players.yml`, then run:

```bash
python -m examples.EndowmentEffect.LLM.run_endowmenteffect_llm \
  -c configs/EndowmentEffect/LLM/simulation.yml
```

For a cheap smoke test, use a temporary copy of the configuration with a small
`setting.total_rounds`; do not alter the calibrated 200-round file merely for
validation.

## 7. Output and Round Structure

Initialization occurs on an investor's first observation. On each round the
investor stores the market broadcast, builds the two prompts, calls the model,
validates the response, clamps quantity to executable limits, updates its
portfolio state, and emits an order. The simulator writes records under
`EXPERIMENT/EndowmentEffect/LLM/` as configured.

## 8. Dependencies and Failure Modes

Runtime dependencies include MASim, `lmbase`, `python-dotenv`, and the provider
credentials for the configured model. Missing keys, unsupported `lm_type`,
missing market fields, malformed tagged output, invalid numeric values, and
retry exhaustion are intentional fail-fast errors. Shutdown remains protected
by the runner's `finally` block.

## 9. Validation Checklist

- Python modules compile and import in the project virtual environment.
- Included YAML files load into `SimulationConfig`.
- Every `simulation-bases.md §4.N` investor maps to a class and prompt.
- Prompt output parses with `parse_llm_response_with_thinking`.
- Model decisions cannot exceed configured order size, cash, or inventory.
- The documented command resolves to the actual runner module.
