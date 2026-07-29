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
| **Alphabetize**             | Within each group, imports should be alphabetized               |

### 1.3 Documentation Strings
- All modules, classes, and methods must have docstrings
- Use Google-style docstrings
- Document tensor shapes in docstrings, not inline

### 1.4 Detailed Annotation for Size, Principle, Logic, and Flow
- **Annotations involving size/dimensions MUST be detailed and accurate**
- Mark all dimension changes, length transformations, and shape operations explicitly
- Explain the underlying principle/logic behind complex operations
- Document the flow of data through processing pipelines

**Correct:**
```python
# Reshape hidden states for cross-attention
# Input shape: (batch_size, seq_len, hidden_dim) -> (32, 128, 768)
# Output shape: (batch_size, num_heads, seq_len, head_dim) -> (32, 12, 128, 64)
# Principle: Split hidden_dim into num_heads * head_dim for multi-head attention
# Flow: Linear projection -> reshape -> transpose
hidden_states = hidden_states.view(batch_size, seq_len, self.num_heads, self.head_dim)
hidden_states = hidden_states.transpose(1, 2)

# Apply 1D convolution with kernel_size=3, stride=1, padding=1
# Input length: 128 -> Output length: 128 (preserved due to padding)
# Principle: Same padding maintains sequence length for residual connection
# Logic: (L - kernel_size + 2*padding) / stride + 1 = (128 - 3 + 2*1) / 1 + 1 = 128
conv_output = self.conv1d(x)
```

**Incorrect:**
```python
# Reshape for attention
hidden_states = hidden_states.view(batch_size, seq_len, self.num_heads, self.head_dim)
hidden_states = hidden_states.transpose(1, 2)

# Apply convolution
conv_output = self.conv1d(x)
```

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

### 2.3 No Default Settings

**Core Principle**: NO default values anywhere in code. Every parameter must be explicitly defined in configuration files.

**Why**: Default values (e.g., buffer length, hidden dimension, learning rate) hidden in code make experiments hard to reproduce and compare. All parameters should be explicit in config files for clarity and auditability.

**WRONG:**
```python
# DO NOT: Default buffer length hidden in code
class HistoryBuffer:
    def __init__(self, max_length: int = 100):  # Why 100?
        # ...

# DO NOT: Hardcoded defaults
optimizer = Adam(model.parameters(), lr=0.001)
```

**CORRECT:**
```python
# All values from config
buffer = HistoryBuffer(max_length=config["buffer_length"])
optimizer = Adam(model.parameters(), lr=config["learning_rate"])
```

### 2.4 Base Library Usage
- When a base library exists, use its storage, inference, and environment management interfaces uniformly
- Don't reinvent functionality provided by base libraries

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

## 10. No Redundant Code

**Core Principle**: Write minimal, direct code. Every line must serve a clear purpose. Avoid unnecessary abstraction, wrappers, and complexity.

### 10.1 No Unnecessary Wrappers

**WRONG - Unnecessary wrapper class:**
```python
# DO NOT: Create wrapper classes that add no value
class ModelManager:
    """Wrapper around HuggingFace model."""
    def __init__(self, model_name):
        self.model_name = model_name
        self._model = None
    
    def load(self):
        self._model = AutoModel.from_pretrained(self.model_name)
    
    def get_model(self):
        return self._model
    
    def forward(self, *args, **kwargs):
        return self._model(*args, **kwargs)

# Usage requires extra steps
manager = ModelManager("bert-base-uncased")
manager.load()
output = manager.forward(input_ids)
```

**CORRECT - Direct usage:**
```python
# Use the library directly
from transformers import AutoModel

model = AutoModel.from_pretrained("bert-base-uncased")
output = model(input_ids)
```

### 10.2 No Redundant Abstraction Layers

**WRONG - Excessive abstraction:**
```python
# DO NOT: Multiple layers of abstraction
class DataProcessor:
    def process(self, data):
        return self._process_internal(data)
    
    def _process_internal(self, data):
        return self._apply_transform(data)
    
    def _apply_transform(self, data):
        return self._finalize(data)
    
    def _finalize(self, data):
        return data.strip().lower()

processor = DataProcessor()
result = processor.process(text)
```

**CORRECT - Simple and direct:**
```python
# Direct function call
result = text.strip().lower()

# Or a simple function if reused
def normalize_text(text: str) -> str:
    return text.strip().lower()

result = normalize_text(text)
```

### 10.3 No Empty Pass-Through Methods

**WRONG - Pass-through methods:**
```python
# DO NOT: Methods that just call another method
class ExperimentRunner:
    def __init__(self, model):
        self.model = model
    
    def run(self, data):
        return self._run_experiment(data)
    
    def _run_experiment(self, data):
        return self._execute(data)
    
    def _execute(self, data):
        return self.model(data)

runner = ExperimentRunner(model)
result = runner.run(data)  # 3 layers to just call model(data)
```

**CORRECT - Direct call:**
```python
# Just call the model directly
result = model(data)

# Or if orchestration is needed, make it meaningful
class ExperimentRunner:
    def __init__(self, model, evaluator, logger):
        self.model = model
        self.evaluator = evaluator
        self.logger = logger
    
    def run(self, data):
        # Each step adds value
        outputs = self.model(data)
        metrics = self.evaluator(outputs)
        self.logger.log(metrics)
        return metrics
```

### 10.4 No Redundant Data Structures

**WRONG - Redundant container:**
```python
# DO NOT: Create dataclass just to hold what dict already provides
@dataclass
class ModelOutput:
    logits: torch.Tensor
    hidden_states: torch.Tensor
    
    def get_logits(self):
        return self.logits
    
    def get_hidden_states(self):
        return self.hidden_states

output = ModelOutput(logits=logits, hidden_states=hidden)
logits = output.get_logits()  # Unnecessary getter
```

**CORRECT - Use existing structures:**
```python
# Return tuple or dict directly
return {"logits": logits, "hidden_states": hidden}

# Or use NamedTuple if type hints needed
ModelOutput = namedtuple("ModelOutput", ["logits", "hidden_states"])
output = ModelOutput(logits, hidden)
logits = output.logits
```

### 10.5 No Premature Generalization

**WRONG - Over-engineering for future needs:**
```python
# DO NOT: Build extensible system for single use case
class BaseProcessor(ABC):
    @abstractmethod
    def process(self, data): pass

class TextProcessor(BaseProcessor):
    def process(self, data): return data.strip()

class ProcessorFactory:
    @staticmethod
    def create(processor_type: str) -> BaseProcessor:
        if processor_type == "text":
            return TextProcessor()
        raise ValueError(f"Unknown type: {processor_type}")

# Only ever used as:
processor = ProcessorFactory.create("text")
result = processor.process(text)
```

**CORRECT - Write what you need:**
```python
# Simple function for current needs
result = text.strip()

# Add abstraction ONLY when you have multiple implementations
```

### 10.6 No Redundant Conditions

**WRONG - Redundant checks:**
```python
# DO NOT: Check conditions that are already guaranteed
def process_items(items: List[str]) -> List[str]:
    if items is None:  # Type hint says List, None not allowed
        return []
    
    result = []
    for item in items:
        if item is not None:  # List[str] means no None items
            result.append(item.strip())
    return result
```

**CORRECT - Trust your contracts:**
```python
def process_items(items: List[str]) -> List[str]:
    # Trust type hints - let errors surface if contract violated
    return [item.strip() for item in items]
```

### 10.7 No Redundant Variable Assignments

**WRONG - Unnecessary intermediate variables:**
```python
# DO NOT: Variables that serve no purpose
def compute_loss(logits, labels):
    predictions = logits  # Why rename?
    targets = labels      # Why rename?
    loss_value = F.cross_entropy(predictions, targets)
    final_loss = loss_value  # Why another variable?
    return final_loss
```

**CORRECT - Direct computation:**
```python
def compute_loss(logits, labels):
    return F.cross_entropy(logits, labels)
```

### 10.8 Checklist: Is This Code Redundant?

Before writing any code, ask:

- [ ] **Does this wrapper add functionality?** If it only delegates, remove it.
- [ ] **Can I use the library directly?** If yes, do it.
- [ ] **Is this abstraction layer necessary?** Only abstract when you have 2+ implementations.
- [ ] **Does this variable serve a purpose?** If only renamed, use original name.
- [ ] **Is this class doing real work?** If only holding data, use dict/tuple/namedtuple.
- [ ] **Am I solving a real problem or imagined future problem?** Write for current needs.
- [ ] **Can I delete this method and call directly?** If yes, delete it.

### 10.9 Summary: Complexity Budget

| Code Element      | Allowed                                  | Not Allowed                    |
|-------------------|------------------------------------------|--------------------------------|
| Wrapper class     | Only if adds real functionality          | Pass-through delegation        |
| Abstraction layer | Only with 2+ implementations             | Single-implementation abstract |
| Getter/Setter     | Only if validation needed                | Simple attribute access        |
| Factory pattern   | Only for runtime selection               | Static type selection          |
| Config class      | Only if complex validation               | Simple dict access             |
| Manager class     | Only if orchestrates multiple components | Single component management    |
