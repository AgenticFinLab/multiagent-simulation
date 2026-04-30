# Code Repair

## Purpose

This file specifies how to audit and repair `players.py` and `prompts.py` files across all four variants of any simulation. It covers:

1. **Docstring citation patching** — the most common repair needed in a revision workflow
2. **Python code standards** — module docstrings, imports, API contracts, coding rules
3. **Variant-specific code rules** — what each variant's code must and must not contain
4. **Common error table** — every known wrong/correct pattern
5. **Automated detection and fix patterns** — bulk repair scripts with validation

---

## §1 Docstring Citation Patching

This is the primary code repair task in most revision workflows. Every investor class must cite its theoretical basis using the `Theory: simulation-bases.md §4.N` format.

### §1.1 Investor-to-§4.N Mapping

Before patching, establish the mapping from class names to §4.N section numbers:

| §4.N | Class Name (Rule) | Class Name (LLM)   | Class Name (RuleLLM)   | Class Name (Rag)      |
|------|-------------------|--------------------|------------------------|-----------------------|
| §4.1 | [InvestorType1]   | LLM[InvestorType1] | RuleLLM[InvestorType1] | RagLLM[InvestorType1] |
| §4.2 | [InvestorType2]   | LLM[InvestorType2] | RuleLLM[InvestorType2] | RagLLM[InvestorType2] |
| ...  | ...               | ...                | ...                    | ...                   |

Extract this from `simulation-bases.md §4` headings:
```bash
grep "^### §4\." examples/<Scenario>/simulation-bases.md
```

### §1.2 Checking existing docstrings

```bash
# Check which investor classes already have Theory citations
grep -A5 "^class " examples/<Scenario>/Rule/players.py | grep "Theory:"

# Check LLM variant
grep -A2 "^class LLM" examples/<Scenario>/LLM/players.py | grep "Theory:"

# Check all at once
for variant in Rule LLM RuleLLM Rag; do
  echo "=== $variant ==="
  grep -c "simulation-bases.md §4" examples/<Scenario>/$variant/players.py
done
```

### §1.3 Rule variant — multi-line docstring format

For each investor class in `Rule/players.py` that is missing or has an incomplete docstring, apply this format:

```python
class ClassName(GeneralPlayer):
    """Brief one-line description of the investor's behavioral role.

    Theory: simulation-bases.md §4.N — ClassName
    Theoretical basis: Author (Year) theory name; brief mechanism description.
    See simulation-bases.md §4.N for mathematical model.
    """
```

**Example (NewEconomyEvangelist, §4.1)**:
```python
class NewEconomyEvangelist(GeneralPlayer):
    """Narrative-driven buyer who ignores traditional valuation metrics.

    Theory: simulation-bases.md §4.1 — NewEconomyEvangelist
    Theoretical basis: Shiller (2000) narrative economics; internet narrative
    drives persistent buying even at extreme overvaluations.
    See simulation-bases.md §4.1 for mathematical model.
    """
```

### §1.4 LLM / RuleLLM / Rag variants — one-liner docstring format

```python
class LLMClassName(LLMInvestor):
    """LLM-driven [mechanism description] — [brief behavioral detail]. Theory: simulation-bases.md §4.N."""
```

**Example**:
```python
class LLMNewEconomyEvangelist(LLMInvestor):
    """LLM-driven narrative buyer — ignores valuation, buys on internet narrative. Theory: simulation-bases.md §4.1."""
```

### §1.5 Patching a class with an existing but incomplete docstring

If the class has a docstring that lacks the `Theory:` citation, add the citation line:

**Before**:
```python
class NewEconomyEvangelist(GeneralPlayer):
    """Investor who believes in the new internet economy paradigm."""
```

**After**:
```python
class NewEconomyEvangelist(GeneralPlayer):
    """Investor who believes in the new internet economy paradigm.

    Theory: simulation-bases.md §4.1 — NewEconomyEvangelist
    Theoretical basis: Shiller (2000) narrative economics; internet narrative
    drives persistent buying even at extreme overvaluations.
    See simulation-bases.md §4.1 for mathematical model.
    """
```

### §1.6 Patching a class with no docstring

If the class has `pass` or no docstring at all, add the full docstring immediately after the class definition line.

---

## §2 Python Code Compliance Audit

Run this checklist on `players.py` for all four variants. All checks must return zero findings before marking a variant as repaired.

### §2.1 Syntax check

```bash
python3 -m py_compile examples/<Scenario>/Rule/players.py
python3 -m py_compile examples/<Scenario>/LLM/players.py
python3 -m py_compile examples/<Scenario>/RuleLLM/players.py
python3 -m py_compile examples/<Scenario>/Rag/players.py
```

### §2.2 Import correctness

```bash
# Wrong inference module path
grep -n "masim.interface.inference" examples/<Scenario>/*/players.py

# Non-existent prompt utility
grep -n "masim.utils.prompt" examples/<Scenario>/*/players.py

# Wrong utils path
grep -n "masim.utils.llm_utils" examples/<Scenario>/*/players.py

# Wrong LLM client class
grep -n "LLMClient" examples/<Scenario>/*/players.py
```

All must return zero. Correct replacements:

| Wrong                                                         | Correct                                                       |
|---------------------------------------------------------------|---------------------------------------------------------------|
| `from masim.interface.inference import LangChainAPIInference` | `from lmbase.inference.api_call import LangChainAPIInference` |
| `from masim.interface.inference import InferInput`            | `from lmbase.inference.base import InferInput`                |
| `from masim.utils.prompt import load_prompt`                  | Local `load_prompt` using `importlib`                         |
| `from masim.utils.llm_utils import ...`                       | `from examples.llm_utils import ...`                          |

### §2.3 lmbase API usage

```bash
# Wrong constructor kwargs
grep -n "LangChainAPIInference" examples/<Scenario>/*/players.py | grep -E "api_key=|model=|base_url="

# Wrong InferInput kwargs
grep -n "InferInput(" examples/<Scenario>/*/players.py | grep -E "sys_message=|user_message=|\bsystem=|\buser="

# Wrong method calls
grep -n "\.ainfer\|\.infer(" examples/<Scenario>/*/players.py

# Wrong response field
grep -n "outputs\[0\]\.text\|outputs\[0\]\.content" examples/<Scenario>/*/players.py
```

### §2.4 Observation API

```bash
grep -n "observation\.messages\|observation\.outbounds" examples/<Scenario>/*/players.py
```

Must use `observation.inbounds` only.

### §2.5 KnowledgeStore API (Rag variant)

```bash
grep -n "rag_store\.save\|knowledge_store\.save" examples/<Scenario>/Rag/players.py
```

`save()` does not exist. `build()` auto-persists.

### §2.6 HistoryBuffer constructor

```bash
grep -n "HistoryBuffer(" examples/<Scenario>/*/players.py | grep -v "folder="
```

Must use `HistoryBuffer(folder=..., entry_limit=...)` — not `maxlen=`.

### §2.7 No hardcoded constants

```bash
# Check for numeric literals in decide() methods (approximate)
grep -n "threshold = [0-9]\|weight = [0-9]" examples/<Scenario>/Rule/players.py
```

All parameters must come from `self.config.extras["key"]`.

### §2.8 No .get() with defaults

```bash
python3 -c "
import re, glob
for f in glob.glob('examples/<Scenario>/**/*.py', recursive=True):
    for i, line in enumerate(open(f).readlines(), 1):
        if re.search(r'\.get\s*\(\s*[\"\'][^\"\']+[\"\']\s*,', line):
            print(f'{f}:{i}: {line.rstrip()}')
"
```

Direct dict access `dict["key"]` must be used. This applies to **both `players.py` and `analysis.py`** across all four variants — not just players.py. See §12 for the full no-default audit protocol.

### §2.9 No inline comments

```bash
grep -n "[^ ]  *#" examples/<Scenario>/Rule/players.py | grep -v "^[[:space:]]*#"
```

Comments must be on a separate line above the code.

### §2.10 Output format tags in prompts

```bash
# Check for deprecated <think> tag
grep -n "<think>" examples/<Scenario>/*/prompts.py

# Check for canonical tags
grep -n "<analysis>" examples/<Scenario>/*/prompts.py
grep -n "<decision>" examples/<Scenario>/*/prompts.py
```

All prompts must use `<analysis>...</analysis>` and `<decision>...</decision>` — not `<think>`.

### §2.11 Ray serialization (LLM/RuleLLM/Rag)

```bash
grep -n "__getstate__\|__setstate__" examples/<Scenario>/LLM/players.py
grep -n "__getstate__\|__setstate__" examples/<Scenario>/RuleLLM/players.py
grep -n "__getstate__\|__setstate__" examples/<Scenario>/Rag/players.py
```

Both methods must be present in the LLM base class.

---

## §3 Common Code Error Fixes

### §3.1 Fix wrong InferInput kwargs (bulk)

```python
import re, glob

files = glob.glob("examples/<Scenario>/**/players.py", recursive=True)
for f in files:
    content = open(f).read()
    original = content
    content = re.sub(r'\bsys_message\s*=', 'system_msg=', content)
    content = re.sub(r'\buser_message\s*=', 'user_msg=', content)
    content = re.sub(r'(?<!\w)system\s*=\s*(?=[^\s=])', 'system_msg=', content)
    content = re.sub(r'(?<!\w)user\s*=\s*(?=[^\s=])', 'user_msg=', content)
    if content != original:
        open(f, 'w').write(content)
        print(f"[FIXED] {f}")
```

Always run `py_compile` after.

### §3.2 Fix wrong inference method calls

```python
import re, glob

files = glob.glob("examples/<Scenario>/**/players.py", recursive=True)
for f in files:
    content = open(f).read()
    original = content
    for attr in ['_llm_client', '_llm']:
        content = re.sub(
            rf'await\s+(self\.{attr})\.(ainfer|infer)\s*\(\s*(\w+)\s*\)',
            rf'\1.run([\3]).outputs[0].response',
            content
        )
    if content != original:
        open(f, 'w').write(content)
        print(f"[FIXED] {f}")
```

### §3.3 Fix wrong import path (masim.interface.inference)

Replace:
```python
from masim.interface.inference import LangChainAPIInference, InferInput
```
With:
```python
from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput
```

### §3.4 Fix missing local load_prompt function

Add after imports (LLM/RuleLLM/Rag variants only):
```python
import importlib

def load_prompt(prompt_path: str) -> str:
    """Load a prompt string from 'module:VARIABLE' path."""
    module_path, var_name = prompt_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, var_name)
```

### §3.5 Fix wrong output format tags in prompts

```python
import glob

for f in glob.glob("examples/<Scenario>/**/prompts.py", recursive=True):
    content = open(f).read()
    if "<think>" in content:
        content = content.replace("<think>", "<analysis>").replace("</think>", "</analysis>")
        open(f, 'w').write(content)
        print(f"[FIXED] {f}")
```

---

## §4 `__init__.py` Audit

For each of the 4 `__init__.py` files:

```bash
python3 -m py_compile examples/<Scenario>/Rule/__init__.py
python3 -m py_compile examples/<Scenario>/LLM/__init__.py
python3 -m py_compile examples/<Scenario>/RuleLLM/__init__.py
python3 -m py_compile examples/<Scenario>/Rag/__init__.py
```

Check:
- Class names in imports exactly match class definitions in `players.py`
- `__all__` is a list of separate strings — NOT `["A, B, C"]` (one string with commas)
- Class name prefixes match the variant: `LLM`, `RuleLLM`, `RagLLM`

---

## §5 Batch Syntax Check (All Variants)

Run after every repair to confirm no regressions:

```bash
python3 -c "
import glob, py_compile, sys
files = sorted(glob.glob('examples/<Scenario>/**/*.py', recursive=True))
errors = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        errors.append(str(e))
if errors:
    for e in errors: print('ERROR:', e)
    sys.exit(1)
else:
    print(f'ALL OK: {len(files)} files')
"
```

---

## §6 Docstring Patch Verification

After patching all investor docstrings, verify:

```bash
# Count Theory citations in each variant
for variant in Rule LLM RuleLLM Rag; do
  count=$(grep -c "simulation-bases.md §4" examples/<Scenario>/$variant/players.py 2>/dev/null || echo 0)
  classes=$(grep -c "^class [A-Z]" examples/<Scenario>/$variant/players.py 2>/dev/null || echo 0)
  echo "$variant: $count Theory citations / $classes classes"
done
```

The citation count should equal the number of investor classes (excludes Market class and base classes). All investor subclasses must have a citation.

---

## §7 Python Code Standards Reference

### §7.1 Module Docstring

The module docstring MUST be the first statement in every `players.py`, before all imports:

```python
"""<Scenario> <Variant> — <description of this variant>.

Theoretical Foundation:
    - Author (Year): Key insight relevant to this simulation.
    - Author2 (Year): Second key insight.
"""

import logging
import os
...
```

Never put imports above the docstring.

### §7.2 Import Structure

Canonical import order:
→ Standard library first, then third-party, then `lmbase`, then `masim`, then `examples.*`

Key rules:
- **Never use `masim.utils.llm_client.LLMClient`** — that module does not exist. Always use `LangChainAPIInference` + `InferInput` from `lmbase`
- LLM/RuleLLM/Rag must add `sys.path.insert(0, ...)` before importing from `examples.*`
- Market is always re-imported from `examples.<Scenario>.Rule.players` in LLM/RuleLLM/Rag

### §7.3 lmbase API Contract

The exact public API for the inference classes used in every LLM/RuleLLM/Rag variant:

**`LangChainAPIInference` constructor** (`lmbase.inference.api_call`):
```python
LangChainAPIInference(
    lm_name="ark/doubao-seed-1-6-lite-251015",  # required: "<provider>/<model>"
    generation_config={"temperature": 0.3, "max_new_tokens": 500},  # optional
)
```
- Only two constructor parameters: `lm_name` and `generation_config`
- API key is **automatically read** from `os.getenv("<PROVIDER>_API_KEY")` — never pass `api_key=` or `base_url=` explicitly
- Provider is inferred from the prefix before `/` in `lm_name` (e.g., `"ark"` → reads `ARK_API_KEY`)

**`InferInput` dataclass** (`lmbase.inference.base`):
```python
InferInput(
    system_msg="...",   # required kwarg — NOT system=, NOT sys_message=
    user_msg="...",     # required kwarg — NOT user=, NOT user_message=
)
```

**`BaseLMAPIInference.run()`** (synchronous — no `await`):
```python
infer_output = llm_client.run([infer_input])       # returns InferBatchOutput
response_text = infer_output.outputs[0].response   # str — NOT .text, NOT .content
```

Full correct call sequence:
```python
infer_input = InferInput(system_msg=system_prompt, user_msg=user_prompt)
infer_output = llm_client.run([infer_input])
raw = infer_output.outputs[0].response
result = parse_llm_response_with_thinking(raw)
```

### §7.4 Three-Method Player Contract

Every player class must implement exactly three async methods: `perceive → decide → act`.

Key rules:
- `perceive`: reads `observation.round` + `observation.inbounds`, initializes state on first call
- `decide`: ALL logic goes here (formulas, LLM calls, RAG retrieval); returns dict with `outbound_messages` key
- `act`: constructs and returns `Action(action_type=..., payload=..., source_id=self.identity)` only
- **Never put LLM calls in `act()`**

### §7.5 Observation API

```python
# CORRECT
if observation.inbounds:
    for inb in observation.inbounds:
        data = inb.payload      # the message content dict
        sender = inb.sender_id  # identity string of the sender

# WRONG — these fields do not exist
observation.messages            # AttributeError
observation.outbounds           # AttributeError
```

### §7.6 State Initialization Pattern

Initialize all custom state in `perceive()` on first call, guarded by a key-existence check:

```python
if "cash" not in self.state.custom_state:
    self.state.custom_state["cash"] = self.config.extras["initial_cash"]
    ...
```

Key points: all state (cash, position, HistoryBuffer, llm_client) is created on round 0 only; all values come from `self.config.extras`; `HistoryBuffer` takes `folder=` and `entry_limit=`; LLM client creation also stores `lm_name` and `generation_config` separately for Ray `__setstate__` reconstruction.

### §7.7 Ray Serialization (LLM/RuleLLM/Rag)

`LangChainAPIInference` cannot be pickled by Ray. Always add `__getstate__`/`__setstate__` to the LLM investor base class.

Pattern: `__getstate__` pops `llm_client` from `custom_state` before pickling; `__setstate__` recreates it from the stored `lm_name` + `generation_config`.

→ See `examples/AssetBubble/LLM/players.py` — `LLMInvestor.__getstate__` and `__setstate__`

### §7.8 LLM Call Pattern

Key steps: load system prompt via `load_prompt(self.config.extras["llm"]["sys_message"])`, build user prompt, call `llm_client.run([InferInput(system_msg=..., user_msg=...)])`, parse with `parse_llm_response_with_thinking(infer_output.outputs[0].response)`, retry up to 3 times, fallback to `hold` on persistent failure.

### §7.9 Prompt Loading

`load_prompt(path)` splits `"module.path:VARIABLE_NAME"` at `:`, calls `importlib.import_module`, returns `getattr(module, var_name)`.

Prompt paths in `players.yml` always use: `"examples.<Scenario>.<Variant>.prompts:PROMPT_CONSTANT_NAME"`

### §7.10 No Hardcoded Constants

All parameters come from `self.config.extras` (populated from `players.yml`):

```python
# CORRECT
threshold = self.config.extras["deviation_threshold"]

# WRONG
threshold = 0.05    # hardcoded — breaks configurability
```

### §7.11 Outbound Messages Format

`decide()` must return a dict containing an `outbound_messages` list. Each item is `{"payload": <dict>, "content_type": <str>}`; the `payload` is exactly what the recipient sees in `inb.payload`.

### §7.12 Canonical LLM Output Format

All system prompts (LLM, RuleLLM, Rag variants) must instruct the LLM to produce output in this canonical two-tag format:

```
<analysis>
... reasoning about current market conditions, portfolio state, strategy logic ...
</analysis>

<decision>
{"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
</decision>
```

- Use `<analysis>` not `<think>` — `<think>` is a deprecated legacy tag (parser accepts it as fallback only)
- The `<decision>` block must contain valid JSON with: `action`, `bid_price`, `quantity`, `reasoning`
- `bid_price` and `quantity` must be **numeric literals** — not expressions, not strings, not formulas

Embed at the end of every LLM/RuleLLM/Rag system prompt:
```python
OUTPUT_FORMAT_INSTRUCTION = """OUTPUT FORMAT:
First output your reasoning inside <analysis>...</analysis> tags, then output your decision inside <decision>...</decision> tags.
The decision must be valid JSON: {"action": "buy"|"sell"|"hold", "bid_price": float, "quantity": float, "reasoning": string}
IMPORTANT: bid_price and quantity MUST be numeric values (e.g., 10.5), NOT expressions or formulas."""
```

### §7.13 No `.get()` with Default Values — Comprehensive No-Default Policy

Do not use `dict.get(key, default)` for any known dictionary key. Use direct `dict[key]` access and let `KeyError` surface immediately ("fail-fast" principle). This rule extends beyond `.get()` to cover **all forms of default values and defensive programming**.

**Scope**: applies to ALL `players.py` and `analysis.py` files across all four variants.

**The 8 prohibited pattern categories**:

```python
# PATTERN 1: LLM parse failure → silent hold
# WRONG — masks LLM failures as valid trading decisions
if decision is None:
    action, quantity = "hold", 0
# CORRECT — fails loudly
if decision is None:
    raise RuntimeError(f"LLM parse failed after {retries} retries")

# PATTERN 2: .get() on LLM response dict
# WRONG
action = decision.get("action", "hold")
# CORRECT
action = decision["action"]

# PATTERN 3: .get() on message payload dict
# WRONG
quantity = decision_payload.get("quantity", 0)
# CORRECT
quantity = decision_payload["quantity"]

# PATTERN 4: .get() on coordinator data dict
# WRONG
fundamental = fundamentals.get(r, 100.0)
# CORRECT
fundamental = fundamentals[r]

# PATTERN 5: Ternary fallback for required data
# WRONG
fundamental_value = fundamentals[rnd] if fundamentals else 1.0
# CORRECT
if not fundamentals:
    raise ValueError("fundamentals dict is empty")
fundamental_value = fundamentals[rnd]

# PATTERN 6: .get() on analysis payload dict
# WRONG
rag_context = payload.get("rag_context", None)
# CORRECT
rag_context = payload["rag_context"]

# PATTERN 7: Empty-collection fallback for computed metrics
# WRONG
"mean_adherence_rate": float(np.mean(rates)) if rates else 0.0,
# CORRECT
if not rates:
    raise ValueError("No adherence rates collected — all agents failed")
"mean_adherence_rate": float(np.mean(rates)),

# PATTERN 8: Index fallback
# WRONG
price = prices_list[rnd-1] if rnd <= len(prices_list) else 0.0
# CORRECT
price = prices_list[rnd-1]  # let IndexError surface
```

**Legitimate exceptions** (these `.get()` patterns are allowed):
- RAG config resolution: `resolved_rag.get("embed_model", "openai/hunyuan-embedding")` — external library config with genuine optional fields
- `__getstate__`/`__setstate__` serialization: `state.get("state", {})`, `custom.pop(key, None)`
- Truly optional config sections: `extras.get("private_knowledge", {})`, `extras.get("knowledge", {})`
- Matplotlib styling defaults (colors, line widths, figure sizes)
- `rag_store`/`rag_cfg` retrieval from custom_state: `self.state.custom_state.get("rag_store")`

See §12 for the full detection-and-fix audit protocol.

---

## §8 Variant-Specific Code Rules

### §8.1 Rule Variant

- `players.py`: Market + N agent classes, no imports of `LangChainAPIInference` or `dotenv`
- No `llm:` block usage anywhere
- Market class path: `"examples.<Scenario>.Rule.players:Market"`
- LLM prompts design: NOT applicable

### §8.2 LLM Variant

- `players.py`: Market re-imported from Rule, `LLMInvestor` base + `LLM<Type>` subclasses
- `prompts.py`: Rich behavioral persona ONLY — no quantitative rules, no scenario name
- Market class path: `"examples.<Scenario>.LLM.players:Market"`
- Agent keys: `llm_<agent_type>` (e.g., `llm_momentum_follower`)

**Prompt design rule**: LLM system prompts describe ONLY the investor's personality and trading style. They must NOT reveal the simulation scenario name or target outcome. Say "I am a trader who gives extra weight to recently observed price movements" — never say "I am simulating availability bias."

### §8.3 RuleLLM Variant

- `players.py`: Identical structure to LLM variant but class prefix `RuleLLM<Type>`
- `prompts.py`: System prompts embed BOTH behavioral persona AND explicit quantitative rules

**Prompt design rule**: RuleLLM prompts must include the exact numerical thresholds and formulas from the Rule variant. Example: "When effective_signal = deviation_pct × 0.70 + return_pct × 0.30 exceeds 2%, buy proportionally..."

### §8.4 Rag Variant

The Rag variant uses `masim.knowledge` — `KnowledgeStore`, `KnowledgeLoader`, `KnowledgeQuery`, `ResourceManager` — for real document retrieval. **Any implementation that does not import from `masim.knowledge` is wrong.**

#### §8.4.1 Correct imports

```python
from __future__ import annotations

import importlib
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lmbase.inference.api_call import LangChainAPIInference
from lmbase.inference.base import InferInput

from examples.llm_utils import parse_llm_response_with_thinking
from masim.knowledge import (
    KnowledgeLoader,
    KnowledgeQuery,
    KnowledgeStore,
    ResourceManager,
)
from masim.player.base import Action, Observation, StepResult
from masim.player.general import GeneralPlayer
```

#### §8.4.2 `_initialize_agent()` — store LLM client in `custom_state`

```python
async def _initialize_agent(self) -> None:
    extras = self.config.extras
    record_path = extras["record_path"]
    base_path = os.path.join(record_path, self.config.identity)

    self.state.custom_state["cash"] = extras["initial_cash"]
    self.state.custom_state["position"] = extras["initial_position"]

    project_root = Path(__file__).parent.parent.parent
    load_dotenv(project_root / ".env")

    llm_cfg = extras["llm"]
    lm_name = llm_cfg["lm_name"]
    generation_config = llm_cfg["generation_config"]
    # Store separately for Ray __setstate__ reconstruction
    self.state.custom_state["lm_name"] = lm_name
    self.state.custom_state["generation_config"] = generation_config

    llm_client = LangChainAPIInference(lm_name=lm_name, generation_config=generation_config)
    self.state.custom_state["llm_client"] = llm_client

    # rag_cfg comes from private_knowledge.rag (players.yml schema)
    private_knowledge = extras.get("private_knowledge", {})
    rag_cfg = private_knowledge.get("rag", extras.get("rag", {}))
    await self._initialize_rag(rag_cfg, llm_client, llm_cfg)
```

#### §8.4.3 `_initialize_rag()` — 5-step canonical pattern

```python
async def _initialize_rag(
    self, rag_cfg: Dict[str, Any], llm_client: Any, llm_config: Dict[str, Any]
) -> None:
    extras = self.config.extras
    record_path = extras.get("record_path", "EXPERIMENT")

    # STEP 1: Resolve knowledge config via ResourceManager
    knowledge_config = extras.get("knowledge", {})
    if not knowledge_config:
        knowledge_config = {
            "backend": "local",
            "global_uri": rag_cfg.get("docs_dir", "examples/document-sources"),
            "preprocessing": {
                "parser": "mineru",
                "output_position": rag_cfg.get("mineru_output_dir", "MinerU_processed"),
            },
            "rag": {
                "output_position": rag_cfg.get("shared_rag_index_dir", "rag_index"),
            },
        }

    resource_manager = ResourceManager(knowledge_config)
    private_knowledge = extras.get("private_knowledge", {})
    if not private_knowledge:
        private_knowledge = {
            "from_global_resources": ["MinerU_processed"],
            "local_resources": {"local_uri": "", "local_resources": []},
            "rag": rag_cfg,
        }
    agent_knowledge = resource_manager.resolve_agent_knowledge(
        agent_id=self.identity,
        private_knowledge=private_knowledge,
        record_path=record_path,
    )
    processed_dir = agent_knowledge["processed_dir"]
    shared_rag_dir = agent_knowledge["shared_rag_dir"]
    local_uri = agent_knowledge["local_uri"]
    local_rag_dir = agent_knowledge["local_rag_dir"]
    resolved_rag = agent_knowledge["rag"]
    os.makedirs(local_uri, exist_ok=True)
    os.makedirs(local_rag_dir, exist_ok=True)

    # STEP 2: Build KnowledgeStore with resolved RAG config
    embed_type = resolved_rag.get("embed_type", "litellm")
    embed_api_key = resolved_rag.get("embed_api_key", "")
    if not embed_api_key:
        embed_api_key = (
            os.getenv("HUNYUAN_API_KEY", "") if embed_type == "litellm"
            else os.getenv("ARK_API_KEY", "")
        )
    rag_store = KnowledgeStore(
        embed_model_name=resolved_rag.get("embed_model", "openai/hunyuan-embedding"),
        embed_api_key=embed_api_key,
        embed_api_base=resolved_rag.get("embed_api_base", ""),
        embed_type=embed_type,
        persist_dir=local_rag_dir,
        chunk_size=int(resolved_rag.get("chunk_size", 512)),
        chunk_overlap=int(resolved_rag.get("chunk_overlap", 64)),
    )

    # STEP 3: Try loading existing local RAG index (resume support)
    if os.path.isdir(local_rag_dir):
        index_files = [f for f in os.listdir(local_rag_dir) if not f.startswith(".")]
        if index_files:
            try:
                rag_store.load(local_rag_dir)
                self.state.custom_state["rag_store"] = rag_store
                self.state.custom_state["rag_cfg"] = resolved_rag
                return
            except Exception as exc:
                logger.warning("[%s] Local index load failed: %s", self.identity, exc)

    # STEP 4: Try copying shared RAG index to local
    shared_rag_dirs = resolved_rag.get("shared_rag_index_dirs", [])
    if not shared_rag_dirs and os.path.isdir(shared_rag_dir):
        shared_rag_dirs = [shared_rag_dir]
    for s_dir in shared_rag_dirs:
        if os.path.isdir(s_dir):
            shared_files = [f for f in os.listdir(s_dir) if not f.startswith(".")]
            if shared_files:
                try:
                    for item in shared_files:
                        src = os.path.join(s_dir, item)
                        dst = os.path.join(local_rag_dir, item)
                        if os.path.isdir(src):
                            shutil.copytree(src, dst, dirs_exist_ok=True)
                        else:
                            shutil.copy2(src, dst)
                    rag_store.load(local_rag_dir)
                    self.state.custom_state["rag_store"] = rag_store
                    self.state.custom_state["rag_cfg"] = resolved_rag
                    return
                except Exception as exc:
                    logger.warning("[%s] Shared copy failed: %s", self.identity, exc)

    # STEP 5: Load processed documents and build index from scratch
    loader = KnowledgeLoader()
    if os.path.isdir(processed_dir) and os.listdir(processed_dir):
        docs = loader.load_from_dir(processed_dir)
    else:
        raise RuntimeError(
            f"[{self.identity}] No processed documents in {processed_dir}. "
            "Ensure ResourceManager pre-processed documents during simulation setup."
        )
    rag_store.build(docs)
    # Copy to shared for other agents to reuse
    try:
        for item in os.listdir(local_rag_dir):
            if item.startswith("."):
                continue
            src = os.path.join(local_rag_dir, item)
            dst = os.path.join(shared_rag_dir, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
    except Exception as exc:
        logger.warning("[%s] Copy to shared failed: %s", self.identity, exc)
    self.state.custom_state["rag_store"] = rag_store
    self.state.custom_state["rag_cfg"] = resolved_rag
```

#### §8.4.4 `__getstate__` / `__setstate__` — Ray serialization

Both `llm_client` and `rag_store` must be removed before pickling and reconstructed after:

```python
def __getstate__(self) -> Dict:
    state = self.__dict__.copy()
    if hasattr(self, "state") and hasattr(self.state, "custom_state"):
        custom = dict(self.state.custom_state)
        for key in ("llm_client", "rag_store"):
            custom.pop(key, None)
        state["state"].custom_state = custom
    return state

def __setstate__(self, state: Dict) -> None:
    self.__dict__.update(state)
    if hasattr(self, "state") and hasattr(self.state, "custom_state"):
        custom = self.state.custom_state
        if "lm_name" in custom and "llm_client" not in custom:
            custom["llm_client"] = LangChainAPIInference(
                lm_name=custom["lm_name"],
                generation_config=custom["generation_config"],
            )
        if "rag_cfg" in custom and "rag_store" not in custom:
            rag_cfg = custom["rag_cfg"]
            local_rag_dir = rag_cfg.get("local_index_dir", "")
            if not local_rag_dir:
                local_ws = rag_cfg.get("local_workspace_dir", "")
                if local_ws:
                    local_rag_dir = os.path.join(local_ws, "rag_index")
            if not local_rag_dir:
                return
            embed_type = rag_cfg.get("embed_type", "litellm")
            embed_api_key = rag_cfg.get("embed_api_key", "")
            if not embed_api_key:
                embed_api_key = (
                    os.getenv("HUNYUAN_API_KEY", "") if embed_type == "litellm"
                    else os.getenv("ARK_API_KEY", "")
                )
            rag_store = KnowledgeStore(
                embed_model_name=rag_cfg.get("embed_model", "openai/hunyuan-embedding"),
                embed_api_key=embed_api_key,
                embed_api_base=rag_cfg.get("embed_api_base", ""),
                embed_type=embed_type,
                persist_dir=local_rag_dir,
                chunk_size=int(rag_cfg.get("chunk_size", 512)),
                chunk_overlap=int(rag_cfg.get("chunk_overlap", 64)),
            )
            if os.path.isdir(local_rag_dir):
                try:
                    rag_store.load(local_rag_dir)
                except Exception as exc:
                    logger.warning("RAG store reload failed: %s", exc)
            custom["rag_store"] = rag_store
```

#### §8.4.5 RAG retrieval in `_build_prompt()` / `decide()`

```python
rag_store: KnowledgeStore = self.state.custom_state.get("rag_store")
rag_cfg: Dict[str, Any] = self.state.custom_state.get("rag_cfg", {})
rag_context = ""
if rag_store and rag_store.is_built():
    top_k = rag_cfg.get("top_k", 3)
    query = KnowledgeQuery(
        text=(
            f"<scenario-specific query keywords> "
            f"price={price:.2f} deviation={deviation:+.2%}"
        ),
        top_k=top_k,
        round_num=round_num,
        agent_id=self.config.identity,
    )
    result = rag_store.query(query)
    rag_context = result.formatted_text
if not rag_context:
    rag_context = "(No relevant knowledge retrieved this round.)"
```

#### §8.4.6 `prompts.py` rules for Rag variant

- `RAG_USER_TEMPLATE` MUST include a `{rag_context}` placeholder — injected via `.format()`, NOT appended manually after formatting
- All prompt constants referenced in `players.yml` must be importable from `Rag/prompts.py` — if `players.yml` uses `LLM_USER_TEMPLATE`, that alias must be exported
- Never import `LLM_USER_TEMPLATE` from `RuleLLM/prompts.py` — it does not exist there (only `RULELLM_USER_TEMPLATE` exists)
- Correct pattern for re-using RuleLLM system prompts:
```python
from examples.<Scenario>.RuleLLM.prompts import (
    RULELLM_<TYPE>_SYS as RAGLLM_<TYPE>_SYS,
    # ...
)
RAG_USER_TEMPLATE = """...{rag_context}..."""
LLM_USER_TEMPLATE = RAG_USER_TEMPLATE  # alias for players.yml compatibility
```

→ Canonical reference: `examples/AssetBubble/Rag/players.py` and `examples/EchoChamber/Rag/players.py`

---

## §9 Common Code Errors — Quick Reference

| Error                             | Wrong                                           | Correct                                                                    |
|-----------------------------------|-------------------------------------------------|----------------------------------------------------------------------------|
| Wrong observation field           | `observation.messages`                          | `observation.inbounds`                                                     |
| Wrong LLM client class            | `from masim.utils.llm_client import LLMClient`  | `from lmbase.inference.api_call import LangChainAPIInference`              |
| Wrong LLM import module           | `from masim.interface.inference import ...`     | `from lmbase.inference.api_call import LangChainAPIInference`              |
| Wrong `LangChainAPIInference` arg | `LangChainAPIInference(model=..., api_key=...)` | `LangChainAPIInference(lm_name=..., generation_config=...)`                |
| Wrong `InferInput` kwarg names    | `InferInput(system=..., user=...)`              | `InferInput(system_msg=..., user_msg=...)`                                 |
| Wrong `InferInput` kwarg names    | `InferInput(sys_message=..., user_message=...)` | `InferInput(system_msg=..., user_msg=...)`                                 |
| Wrong LLM call method             | `await self._llm_client.ainfer(infer_input)`    | `self._llm_client.run([infer_input]).outputs[0].response`                  |
| Wrong response field              | `infer_output.outputs[0].text`                  | `infer_output.outputs[0].response`                                         |
| Wrong prompt utility import       | `from masim.utils.prompt import load_prompt`    | Local `load_prompt` function using `importlib`                             |
| Wrong utils import path           | `from masim.utils.llm_utils import ...`         | `from examples.llm_utils import ...`                                       |
| Calling non-existent method       | `rag_store.save(persist_dir)`                   | Remove — `build()` auto-persists to `persist_dir`                          |
| `.get()` with default             | `payload.get("action", "hold")`                 | `payload["action"]`                                                        |
| Inline comment                    | `threshold = 0.05  # from theory`               | Comment on separate line above the code                                    |
| LLM logic in wrong method         | LLM call inside `act()`                         | LLM call inside `decide()`                                                 |
| Docstring not first               | imports before docstring                        | Module docstring must precede all imports                                  |
| Hardcoded parameters              | `threshold = 0.05` in code                      | `threshold = self.config.extras["threshold"]`                              |
| No Ray serialization              | no `__getstate__`/`__setstate__`                | Required for all LLM/RuleLLM/Rag players                                   |
| Wrong Action constructor          | `Action(outbounds=[...])`                       | `Action(action_type=..., payload=..., source_id=...)`                      |
| Wrong import for Market           | each variant re-defines Market                  | `from examples.<Scenario>.Rule.players import Market`                      |
| Character-split `__all__`         | `__all__ = ["M, a, r, k, e, t"]`                | `__all__ = ["Market"]`                                                     |
| Wrong `Rag/prompts.py` import     | `from RuleLLM.prompts import LLM_USER_TEMPLATE` | Import `RULELLM_USER_TEMPLATE`; define `RAG_USER_TEMPLATE` locally         |
| RAG context injected manually     | `user_prompt += rag_context` after `.format()`  | Include `{rag_context}` in template; pass via `.format(rag_context=...)`   |
| Missing masim.knowledge import    | No `from masim.knowledge import ...`            | Import `KnowledgeLoader, KnowledgeQuery, KnowledgeStore, ResourceManager`  |
| Wrong RAG retriever class         | `from masim.utils.rag import RAGRetriever`      | `RAGRetriever` does not exist; use `KnowledgeStore` from `masim.knowledge` |
| Wrong RAG query method            | `self.knowledge.retrieve(query)`                | `rag_store.query(KnowledgeQuery(...))` → `result.formatted_text`           |
| RAG state stored as instance attr | `self._rag_retriever = ...`                     | Store in `self.state.custom_state["rag_store"]` for Ray serialization      |
| RAG context from config           | `extras.get("rag_context", "No context")`       | Build real index via `_initialize_rag()` with `ResourceManager`            |
| llm_client not in custom_state    | `self._llm_client = LangChainAPIInference(...)` | Store in `custom_state["llm_client"]`; exclude in `__getstate__`           |
| Wrong analysis tag in prompt      | `<think>...</think>` in OUTPUT FORMAT section   | Use `<analysis>...</analysis>` (canonical tag; `<think>` is deprecated)    |
| Wrong HistoryBuffer args          | `HistoryBuffer(maxlen=100)`                     | `HistoryBuffer(folder=path, entry_limit=N)`                                |

---

## §10 Full Compliance Audit Workflow

Use this when auditing a scenario for the first time or verifying after significant changes.

### §10.1 Step 1 — Baseline Syntax Check

```bash
python3 -c "
import glob, py_compile, sys
files = sorted(glob.glob('examples/<Scenario>/**/*.py', recursive=True))
errors = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        errors.append(str(e))
if errors:
    for e in errors: print('ERROR:', e)
    sys.exit(1)
else:
    print(f'ALL OK: {len(files)} files')
"
```

Fix all syntax errors before proceeding.

### §10.2 Step 2 — Import Correctness Audit

```bash
# Wrong inference module path
grep -rn "masim.interface.inference" examples/<Scenario>/ --include="players.py"

# Non-existent prompt utility module
grep -rn "masim.utils.prompt" examples/<Scenario>/ --include="players.py"

# Wrong utils path
grep -rn "masim.utils.llm_utils" examples/<Scenario>/ --include="players.py"

# Wrong LLM client class
grep -rn "LLMClient" examples/<Scenario>/ --include="players.py"
```

All must return zero. After fixing, re-run the baseline syntax check.

### §10.3 Step 3 — API Usage Audit

```bash
# Wrong constructor kwargs
grep -rn "LangChainAPIInference" examples/<Scenario>/ --include="players.py" | grep -E "api_key=|model=|base_url="

# Wrong InferInput kwarg names
grep -rn "InferInput(" examples/<Scenario>/ --include="players.py" | grep -E "sys_message=|user_message=|\bsystem=|\buser="

# Wrong method calls
grep -rn "\.ainfer\|\.infer(" examples/<Scenario>/ --include="players.py"

# Wrong response field
grep -rn "\.outputs\[0\]\.text\|\.outputs\[0\]\.content" examples/<Scenario>/ --include="players.py"

# KnowledgeStore.save() does not exist
grep -rn "rag_store\.save\|knowledge_store\.save" examples/<Scenario>/ --include="players.py"
```

### §10.4 Step 4 — llm-coding-rules.md Compliance

#### No Inline (End-of-Line) Comments

```bash
grep -n "[^ ]  *#" examples/<Scenario>/*/players.py | grep -v "^[[:space:]]*#"
```

#### All Imports at File Top

```bash
grep -rn "^    import \|^        import \|^    from " examples/<Scenario>/ --include="players.py"
```

#### No `.get()` with Default Values

```python
import re, glob
for f in glob.glob("examples/<Scenario>/**/players.py", recursive=True):
    for i, line in enumerate(open(f).readlines(), 1):
        if re.search(r'\.get\s*\(\s*[\"\'][^\"\']+[\"\'\]\s*,', line):
            print(f'{f}:{i}: {line.rstrip()}')
```

### §10.5 Step 5 — HistoryBuffer Constructor

```bash
grep -rn "HistoryBuffer(" examples/<Scenario>/ --include="players.py" | grep -v "folder="
```

Must use `HistoryBuffer(folder=..., entry_limit=...)` — not `maxlen=`.

### §10.6 Step 6 — Final Validation

```bash
# 1. Syntax check
python3 -c "
import glob, py_compile, sys
files = sorted(glob.glob('examples/<Scenario>/**/*.py', recursive=True))
errors = []
for f in files:
    try: py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e: errors.append(str(e))
if errors:
    for e in errors: print('ERROR:', e); sys.exit(1)
else:
    print(f'ALL OK: {len(files)} files')
"

# 2. Confirm no invalid lmbase API usage
grep -rn "LangChainAPIInference" examples/<Scenario>/ --include="players.py" | grep -E "api_key=|model=|base_url="
grep -rn "\.ainfer\|\.infer(" examples/<Scenario>/ --include="players.py"
grep -rn "outputs\[0\]\.text\|outputs\[0\]\.content" examples/<Scenario>/ --include="players.py"

# 3. Confirm no invalid KnowledgeStore methods
grep -rn "\.save(" examples/<Scenario>/ --include="players.py"

# 4. Confirm no .get(key, default) in players.py
python3 -c "
import re, glob
count = 0
for f in glob.glob('examples/<Scenario>/**/players.py', recursive=True):
    for line in open(f):
        if re.search(r'\.get\s*\(\s*[\"\']+[^\"\']+[\"\']+\s*,', line):
            count += 1
print(f'Remaining .get(key,default): {count}')
"

# 5. Confirm no wrong import paths
grep -rn "masim.interface.inference\|masim.utils.prompt\|masim.utils.llm_utils" examples/<Scenario>/ --include="players.py"
```

All checks must return zero findings.

### §10.7 Automated Bulk Fix Scripts

#### Fix wrong InferInput kwargs

```python
import re, glob

files = glob.glob("examples/<Scenario>/**/players.py", recursive=True)
for f in files:
    content = open(f).read()
    original = content
    content = re.sub(r'\bsys_message\s*=', 'system_msg=', content)
    content = re.sub(r'\buser_message\s*=', 'user_msg=', content)
    content = re.sub(r'(?<!\w)system\s*=\s*(?=[^\s=])', 'system_msg=', content)
    content = re.sub(r'(?<!\w)user\s*=\s*(?=[^\s=])', 'user_msg=', content)
    if content != original:
        open(f, 'w').write(content)
        print(f"[FIXED] {f}")
```

#### Fix wrong inference method calls

```python
import re, glob

files = glob.glob("examples/<Scenario>/**/players.py", recursive=True)
for f in files:
    content = open(f).read()
    original = content
    for attr in ['_llm_client', '_llm']:
        content = re.sub(
            rf'await\s+(self\.{attr})\.(ainfer|infer)\s*\(\s*(\w+)\s*\)',
            rf'\1.run([\3]).outputs[0].response',
            content
        )
    if content != original:
        open(f, 'w').write(content)
        print(f"[FIXED] {f}")
```

#### Fix deprecated `<think>` tag in prompts

```python
import glob

for f in glob.glob("examples/<Scenario>/**/prompts.py", recursive=True):
    content = open(f).read()
    if "<think>" in content:
        content = content.replace("<think>", "<analysis>").replace("</think>", "</analysis>")
        open(f, 'w').write(content)
        print(f"[FIXED] {f}")
```

**Always run `py_compile` after every bulk edit pass.**

### §10.8 Canonical Repair Script Pattern

```python
import re, glob, py_compile, sys

files = sorted(glob.glob("examples/<Scenario>/**/players.py", recursive=True))
fixed = 0

for f in files:
    with open(f) as fh:
        content = fh.read()
    original = content

    # Apply targeted, well-scoped transformations here
    # ...

    if content != original:
        with open(f, "w") as fh:
            fh.write(content)
        fixed += 1
        print(f"[FIXED] {f}")

print(f"\nFixed: {fixed} files")

# Always verify syntax after bulk edits
errors = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        errors.append(str(e))

if errors:
    print(f"\nSYNTAX ERRORS ({len(errors)}):")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print(f"py_compile: ALL OK ({len(files)} files)")
```

Key principles:
- Always read → transform → compare before writing
- Always run `py_compile` after every bulk edit pass
- Fix one category per script; do not batch unrelated transformations
- Test on a single file first before running on all files at scale

### §10.9 Edge Cases and Pitfalls

#### Multiline `.get()` leaves stray parenthesis

When a `.get()` call spans multiple lines, a single-line regex replacement may leave the outer closing `)` as a syntax error. Always run `py_compile` after automated fixes.

```python
# Before
cs["peg_rate"] = float(
    extras.get("peg_rate", 1.2)
)

# After naive regex — WRONG (stray closing paren)
cs["peg_rate"] = float(
    extras["peg_rate"]
)  # <-- the outer ) is now unmatched

# CORRECT manual fix
cs["peg_rate"] = float(extras["peg_rate"])
```

#### Docstring lines starting with `from`

A routine that matches lines starting with `from ` can incorrectly move docstring prose into the imports section if the docstring contains text like `"from narrative-driven buying..."`. Guard the import detector against lines inside triple-quoted strings.

#### `system=` regex over-matching

A regex replacing `(?<!\w)system\s*=` with `system_msg=` will correctly fix `InferInput(system=...)` but may match other `*_system = ...` variable assignments if the lookbehind is too loose. Always verify with `py_compile` after any bulk regex pass.

#### `analysis.py` scope update

The `.get(key, default)` prohibition applies to **both `players.py` and `analysis.py`** across all four variants. Analysis scripts that parse simulation records must use direct dict access for required fields (e.g., `payload["action"]`, `payload["rag_context"]`). If a record field is unexpectedly absent, `KeyError` must surface immediately — do not mask it with `.get(key, default)`. Runner scripts (`run_*.py`) are exempt from this rule as they handle user-facing argument parsing.

---

## §11 EXPERIMENT Record Structure and `analysis.py` Loading API

Full reference: **`docs/save-structure.md`**

Key rule: `analysis.py` must never parse batch/turn JSON files directly. Always use `masim.utils.load_results()`. `docs/save-structure.md` covers: how `simulation.yml` config keys map to save paths, the full EXPERIMENT directory layout, batch store JSON format, turn record JSON format, the complete `load_results` API tables, and the canonical `_load_data` pattern.

### Quick summary of the on-disk layout

After running a simulation with `record_path: EXPERIMENT/{Scenario}/{Variant}/records`, the framework writes:

```
EXPERIMENT/{Scenario}/{Variant}/
├── records/
│   ├── market/                         ← coordinator player
│   │   ├── price/                      ← batch store (scenario-specific name)
│   │   ├── fundamental/                ← batch store
│   │   ├── volume/                     ← batch store
│   │   ├── turns/                      ← per-round turn records
│   │   └── messages/
│   ├── {investor_id}/               ← one dir per investor player
│   │   ├── turns/
│   │   └── messages/
│   └── ...
└── communication/               ← set via communication.storage_path
```

Batch store names under `market/` depend on what the scenario's `Market.act()` registers. Common: `price`, `fundamental`, `volume`. Scenario-specific: `bubble_metric` (AssetBubble), `stock` (EquityPremium). Full details in `docs/save-structure.md`.

### `analysis.py` loading compliance checklist

- [ ] `from masim.utils import load_config, load_results` at top of file
- [ ] Coordinator data via `player.batch(name).all()` — not manual file parsing
- [ ] Investor data via `player.turns.payloads()` or `player.turns.field(name)`
- [ ] `main()` calls `load_results(config)` then `_load_data(results)`
- [ ] LLM/RuleLLM/Rag `analysis.py` imports `_load_data` from `Rule/analysis.py`
- [ ] `py_compile` passes on all four variant `analysis.py` files

### `analysis.py` output standard compliance checklist

Every `Rule/analysis.py` must produce a structured validation report. When reviewing or repairing an `analysis.py`, verify all of the following:

- [ ] Console output includes `=== {SCENARIO} SIMULATION VALIDATION: VALID|INVALID ===` header
- [ ] `Overall Fit Score: XX.X% (threshold: 50%)` line present
- [ ] At least 2 criterion blocks, each formatted as `[N] {NAME}` with `Observed:`, `Expected:`, `Score:`, `Assessment:`
- [ ] `Expected:` lines reference calibration ranges from `analysis-bases.md §6`, not invented values
- [ ] `Assessment:` text cites the calibration source (e.g., `Campbell & Sharpe 2009`)
- [ ] `[SUMMARY]` block at end of validation output
- [ ] `_validate_{scenario}()` docstring documents criterion weights (must sum to 1.0)
- [ ] Saves `summary.json` with `metrics` dict and `validation` dict (`.score`, `.is_valid`, `.criteria`, `.interpretation`)
- [ ] Saves `agent_volumes.json` or equivalent investor breakdown if applicable
- [ ] Generates exactly 3 PNG files: `01_*.png`, `02_*.png`, `03_*.png` in `{base_dir}/analysis/`
- [ ] `base_dir` is `os.path.dirname(config["setting"]["record_path"])`, not `record_path` itself

---

## §12 Strict No-Default Audit Protocol

This section defines the complete audit-and-fix workflow for eliminating all default values, fallback code, and silent error handling from simulation code. The prohibition covers **all `players.py` and `analysis.py` files** across all four variants.

### §12.1 Scope

| In Scope                                 | Out of Scope                                                 |
|------------------------------------------|--------------------------------------------------------------|
| `{Variant}/players.py` (all 4 variants)  | `run_*.py` runner scripts                                    |
| `{Variant}/analysis.py` (all 4 variants) | `prompts.py` (string constants only)                         |
| Coordinator (Market) code                | `__init__.py` (import-only)                                  |
| Investor code                            | RAG config resolution (`resolved_rag.get()`)                 |
| Analysis metric computation              | `__getstate__`/`__setstate__` serialization                  |
| Analysis record parsing                  | Matplotlib styling defaults                                  |
|                                          | Truly optional config: `extras.get("private_knowledge", {})` |

### §12.2 The 8 Dangerous Pattern Categories

See §7.13 for the full wrong/correct code examples for each pattern.

| # | Pattern                         | Detection Regex                       | Typical Location                           |
|---|---------------------------------|---------------------------------------|--------------------------------------------|
| 1 | LLM parse failure → silent hold | `decision is None` followed by `hold` | LLM/RuleLLM/Rag `players.py` decide()      |
| 2 | `.get()` on LLM response        | `decision\.get\(`                     | LLM/RuleLLM/Rag `players.py` decide()      |
| 3 | `.get()` on message payload     | `decision_payload\.get\(`             | LLM/RuleLLM/Rag `players.py` decide()      |
| 4 | `.get()` on coordinator data    | `fundamentals\.get\(`                 | Rule `players.py` coordinator, analysis.py |
| 5 | Ternary fallback                | `if fundamentals else`                | Rule `analysis.py` metric computation      |
| 6 | `.get()` on analysis payload    | `payload\.get\(`                      | RuleLLM/Rag `analysis.py`                  |
| 7 | Empty-collection fallback       | `if rates else`                       | RuleLLM `analysis.py` adherence stats      |
| 8 | Index fallback                  | `if .* <= len\(.*\) else`             | Rule `analysis.py` price lookups           |

### §12.3 Automated Detection Scripts

#### Detect all `.get(key, default)` in scope

```bash
python3 -c "
import re, glob, os
EXCLUDE = {'__getstate__', '__setstate__'}
for f in sorted(glob.glob('examples/<Scenario>/**/*.py', recursive=True)):
    bn = os.path.basename(f)
    if bn.startswith('run_') or bn == '__init__.py' or bn == 'prompts.py':
        continue
    lines = open(f).readlines()
    for i, line in enumerate(lines, 1):
        if re.search(r'\.get\s*\(\s*[\"\''][^\"\']+[\"\'']\s*,', line):
            # Check if inside a legitimate exception
            stripped = line.strip()
            if any(kw in stripped for kw in [
                'resolved_rag', 'rag_cfg.get', 'embed_', 'chunk_',
                'pop(', 'plt.', 'fig', 'color', 'linewidth',
                'private_knowledge', 'knowledge',
            ]):
                continue
            print(f'{f}:{i}: {stripped}')
"
```

#### Detect `if X else fallback` patterns

```bash
grep -rn 'if .* else [0-9]' examples/<Scenario>/*/players.py examples/<Scenario>/*/analysis.py \
  | grep -v 'plt\.' | grep -v '#' | grep -v 'color'
```

#### Detect silent hold on LLM failure

```bash
grep -rn 'decision is None' examples/<Scenario>/*/players.py \
  | grep -v 'raise'
```

### §12.4 Fix Patterns

| Pattern                    | Transformation                                                        |
|----------------------------|-----------------------------------------------------------------------|
| `dict.get("key", default)` | `dict["key"]`                                                         |
| `if X else fallback`       | `if not X: raise ValueError(...)` then use `X` directly               |
| `decision is None → hold`  | `raise RuntimeError(...)`                                             |
| `if rates else 0.0`        | `if not rates: raise ValueError(...)` then compute without ternary    |
| Chained `.get().get()`     | Replace outermost first: `d.get("a", {}).get("b", 0)` → `d["a"]["b"]` |

**Important**: When replacing chained `.get()` calls (e.g., `self.state.custom_state.get("market_data", {}).get("price", 100.0)`), always replace the FULL chained expression first before replacing standalone `.get()` patterns, to avoid partial replacements.

### §12.5 Verification

After every batch of fixes:

```bash
# 1. Syntax check
python3 -c "
import glob, py_compile, sys
ok = fail = 0
for f in sorted(glob.glob('examples/<Scenario>/**/*.py', recursive=True)):
    try:
        py_compile.compile(f, doraise=True)
        ok += 1
    except py_compile.PyCompileError as e:
        print('ERROR:', e)
        fail += 1
print(f'OK={ok} FAIL={fail}')
if fail: sys.exit(1)
"

# 2. Re-run detection to confirm zero remaining violations
python3 -c "
import re, glob, os
count = 0
for f in sorted(glob.glob('examples/<Scenario>/**/*.py', recursive=True)):
    bn = os.path.basename(f)
    if bn.startswith('run_') or bn == '__init__.py' or bn == 'prompts.py':
        continue
    for line in open(f):
        if re.search(r'\.get\s*\(\s*[\"\''][^\"\']+[\"\'']\s*,', line):
            stripped = line.strip()
            if any(kw in stripped for kw in [
                'resolved_rag', 'rag_cfg.get', 'embed_', 'chunk_',
                'pop(', 'plt.', 'fig', 'color', 'linewidth',
                'private_knowledge', 'knowledge',
            ]):
                continue
            count += 1
print(f'Remaining violations: {count}')
"
```

### §12.6 Audit Record Template

After completing the audit for a scenario, record the results:

```
> **No-default audit** (<Scenario>, <date>):
>   - Files scanned: N players.py + N analysis.py
>   - Violations found: N
>   - Violations fixed: N
>   - Legitimate exceptions retained: N
>   - py_compile: ALL OK (N files)
```
