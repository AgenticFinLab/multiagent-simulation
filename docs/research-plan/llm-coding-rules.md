# LLM Coding Rules for VSGR Project

> **Language Requirement**: All documentation, code comments, commit messages, and experimental reports MUST be written in **English**.

## 1. Code Structure Standards

### 1.1 Comment Placement
- **Comments MUST be placed ABOVE the code they describe**
- **NO inline comments** (end-of-line comments are prohibited)
- Use complete sentences for comments

**Correct:**
```python
# Remove batch dimension if present
if image.dim() == 4:
    image = image[0]

# Convert from CHW format to HWC
if image.shape[0] in [1, 3]:
    image = image.permute(1, 2, 0)
```

**Incorrect:**
```python
if image.dim() == 4:
    image = image[0]  # Remove batch dim
if image.shape[0] in [1, 3]:  # CHW format
    image = image.permute(1, 2, 0)
```

### 1.2 Import Standards
| Rule                        | Description                                                     |
|-----------------------------|-----------------------------------------------------------------|
| **All Imports at File Top** | No function-level imports, conditional imports, or lazy imports |
| **Group Imports**           | Group by: stdlib → third-party → local                          |
| **Sort by Length**          | Within each group, sort from shortest to longest                |

**Import Order Example:**
```python
# Standard library (shortest to longest)
import os
import sys
import argparse
import asyncio

# Third-party (shortest to longest)
from dotenv import load_dotenv

# Local packages (shortest to longest)
from masim.simulator.base import SimulationConfig
from masim.simulator.general import GeneralSimulator
from masim.utils.config import load_config, setup_logging
```

**Incorrect (function-level import):**
```python
def main():
    from dotenv import load_dotenv  # WRONG: import inside function
    load_dotenv()
```

### 1.3 Documentation Strings
- All modules, classes, and methods must have docstrings
- Use Google-style docstrings
- Document tensor shapes in docstrings, not inline

**Correct:**
```python
def encode_image(self, image: torch.Tensor) -> torch.Tensor:
    """
    Encode image into visual features.
    
    Args:
        image: Input image tensor
        
    Returns:
        Visual features
        Shape: (hidden_dim,)
    """
```

**Incorrect:**
```python
def encode_image(self, image: torch.Tensor) -> torch.Tensor:
    """Encode image."""
    return features  # (hidden_dim,)
```

## 2. Programming Standards

### 2.1 No Defensive Programming
- Don't use `.get()` for known keys
- Use `dict["key"]` directly, let errors surface early
- Trust the type system

**Correct:**
```python
value = config["required_key"]  # Will raise KeyError if missing
```

**Incorrect:**
```python
value = config.get("required_key")  # Silently returns None
if value is None:
    value = default
```

### 2.2 Configuration-Driven Development
| Rule                      | Description                                     |
|---------------------------|-------------------------------------------------|
| **No Hardcoding**         | All variable parameters go through YAML configs |
| **Centralized Config**    | Use `configs/` directory for all configurations |
| **Environment Variables** | Use `.env` for sensitive tokens                 |

### 2.3 Base Library Usage
- When a base library exists, use its storage, inference, and environment management interfaces uniformly
- Don't reinvent functionality provided by base libraries

### 2.4 Fail Fast, No Protective Programming (CRITICAL)
- **Let errors surface immediately rather than hiding them with fallbacks**
- **A loud crash is better than silent incorrect behavior**
- **No default values, no graceful degradation, no silent fallbacks**
- If something is required but missing, FAIL - don't guess or substitute

**Correct:**
```python
# Fail immediately when required dependency is missing
result = config["required_key"]  # KeyError surfaces the problem
client = get_llm_client()  # RuntimeError if not configured
```

**Incorrect (FORBIDDEN):**
```python
# WRONG: Protective programming hides errors
result = config.get("required_key", default_value)  # Silently uses wrong data
if not client:
    client = MockClient()  # Silently produces invalid results
```

**Why this matters:** Hidden errors propagate through the system, producing invalid research data and wasting computational resources. A crash is informative; silent wrong behavior is dangerous.

## 3. Modular Design Standards

### 3.1 Module Organization
```
vsgr/
├── {module}/
│   ├── base.py          # Base classes and data structures
│   ├── implementation.py # Concrete implementations
│   └── __init__.py      # Public exports
```

### 3.2 Base.py Ownership
- Each module owns its dataclasses in `base.py`
- No shared `generic.py` across modules
- Keep dataclasses close to where they're used

### 3.3 Prompt Organization
- Define prompts as module-level constants
- Organize by experiment in `prompts.py`
- Express naturally rather than artificially explicit

## 4. VLM Implementation Standards

### 4.1 HuggingFace-First
- **MUST use HuggingFace transformers** for all VLM implementations
- No custom model implementations
- Use official model classes:
  - `LlavaForConditionalGeneration`
  - `Qwen2VLForConditionalGeneration`

### 4.2 Model Output Requirements
All VLM models MUST return:
- **logits**: Output logits for analysis
- **hidden_states**: Hidden representations
- **visual_attention**: Attention maps when requested

### 4.3 Device Management
```python
default_device = "auto"  # Automatically select CUDA if available
```

## 5. File and Naming Conventions

### 5.1 File Naming
- Use `snake_case` for all Python files
- Test files: `test_{module}.py`
- Config files: `{experiment}.yml`

### 5.2 Class Naming
- Use `PascalCase` for class names
- Base classes: `Base{Functionality}`
- Model wrappers: `{ModelName}Model`

### 5.3 Function Naming
- Use `snake_case` for functions and methods
- Private methods: `_{method_name}`

## 6. Error Handling

### 6.1 Explicit Errors
- Raise specific exceptions with clear messages
- Don't suppress errors silently

```python
if self.model is None:
    raise RuntimeError("Model not loaded. Call load_model() first.")
```

### 6.2 Type Hints
- Use type hints for all function signatures
- Use `Optional[]` for nullable types
- Use `Union[]` for multiple types

## 7. Git and Version Control

### 7.1 Commit Standards
- Atomic commits (one logical change per commit)
- Use GitHub Desktop for visualization
- Clear commit messages in English

### 7.2 .gitignore Requirements
```gitignore
EXPERIMENT/
build/
*.egg-info/
.env
```

## 8. Verification Checklist

Before submitting code, verify:

- [ ] No inline comments (all comments above code)
- [ ] All imports at file top
- [ ] No hardcoded parameters (use YAML configs)
- [ ] Type hints on all functions
- [ ] Docstrings on all public methods
- [ ] English only in comments and documentation
- [ ] No defensive programming (let errors surface)
- [ ] HuggingFace transformers used for VLMs
- [ ] `pip install -e .` works successfully

## 9. Research-Specific Rules

### 9.1 Literature Documentation
- Document all papers in `reference.md`
- Include expert analysis, not just summaries
- Cite sources for all claims

### 9.2 Experiment Tracking
- Use `EXPERIMENT/` directory for all experiments
- Each experiment gets its own subdirectory
- Document hypotheses before running experiments

### 9.3 Code-to-Paper Fidelity
- Implementation must match paper methodology
- Document any deviations explicitly
- Keep original paper descriptions accurate
