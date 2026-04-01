# Phase 2: Modular Architecture Design

> **Actor:** LLM (Autonomous Execution)
> **Status:** Automated Phase
> **Prerequisite:** Completed Phase 1 with installable package
> **Output:** Module hierarchy, base classes, config templates, uTEST framework

---

## Overview

Establish clear module hierarchy within the core package. Each module has `base.py` defining basic interfaces and data structures, extensible through inheritance and composition.

This phase creates the architectural foundation that all subsequent implementation will follow.

---

## 2.1 Architecture Design Principles

| Principle                                  | Description                                                                                           |
|--------------------------------------------|-------------------------------------------------------------------------------------------------------|
| **Base Class First**                       | Write `base.py` first for each module (or define uniformly in `generic.py`), specify abstract methods |
| **Document Data Flow**                     | Each base class's docstring must include data flow overview                                           |
| **Standard Dimension Notation**            | Uniformly define tensor dimension symbols: B, L, H, D_head, D_h, V, etc.                              |
| **Separate Interface from Implementation** | Abstract classes define what, subclasses implement how                                                |
| **Config-Driven Initialization**           | Subclasses initialize via config dict, not positional parameters                                      |

---

## 2.2 Module Structure Design

Module structure should be designed based on **research direction, objectives, and required capabilities**, not by applying a fixed template. During design, refer to existing related work code (Phase 3-4 outputs) and team base libraries.

### General Design Principles

| Principle                               | Description                                                                    |
|-----------------------------------------|--------------------------------------------------------------------------------|
| **Core Modules Reflect Research Goals** | Module divisions directly correspond to key capabilities in research           |
| **Each Module Has Base Definition**     | Define abstract class / dataclass in `generic.py` or module's `base.py`        |
| **evaluate/ as Independent Module**     | Evaluation logic should not be scattered in experiment scripts                 |
| **utils/ Collects Domain Utilities**    | Domain-related low-level operations go uniformly in utils/                     |
| **visual/ Isolated**                    | Plotting code separated from experiment logic                                  |
| **Reference Existing Work**             | After analyzing reference implementations, identify what to implement vs reuse |

### VSGR Module Structure

For the VSGR project, the module structure is:

```
vsgr/                           # Core package
├── __init__.py                 # Version and public API exports
├── gr_reason/                  # Graph-based reasoning module
│   ├── __init__.py
│   ├── base.py                 # Region, Edge, RegionGraph dataclasses
│   └── graphregion_model.py    # GraphRegion implementation
├── models/                     # VLM model wrappers
│   ├── __init__.py
│   ├── base.py                 # VLMOutput, RegionFeatures, BaseVLM
│   ├── llava_model.py          # LLaVA implementation
│   └── qwen_model.py           # Qwen2VL implementation
├── evaluate/                   # Evaluation module
│   ├── __init__.py
│   └── visual_reasoning_eval.py
├── utils/                      # Domain utilities
│   ├── __init__.py
│   └── config_loader.py        # YAML config loading
└── visual/                     # Visualization (future)
    └── __init__.py
```

---

## 2.3 Base Class Design Pattern

Each base class should include the following elements:

| Element                 | Description                                                        |
|-------------------------|--------------------------------------------------------------------|
| **Data Flow Docstring** | Describe complete data flow (input → intermediate states → output) |
| **Dimension Notation**  | Standard symbols within the domain (B, L, H, D_head, etc.)         |
| **Abstract Methods**    | Only define what (interface), not how                              |
| **Config-driven Init**  | Initialize via config dict, not positional parameters              |

### Example Base Class Template

```python
"""Module docstring: MUST include Data Flow Overview.

Data flow:
  Config → {initialization steps}
  → {core_operation}(inputs) → {intermediate_states}
  → [optional loop]
  → {output_operation} → final_output

Standard Dimension Notations:
  B: Batch size
  L: Sequence length
  H: Number of attention heads
  D_head: Dimension per head
  D_h: Hidden dimension (H × D_head)
  V: Vocabulary size
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class BaseOutput:
    """Base output dataclass."""
    pass


class BaseCoreConcept(ABC):
    """Base class for core research concept.
    
    Data flow:
      config → __init__ → setup_components
      → process(input) → intermediate
      → generate() → output
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize from config dict.
        
        Args:
            config: Configuration dictionary with all parameters
        """
        self.config = config
        self._setup_components()
    
    def _setup_components(self):
        """Setup internal components."""
        pass
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input data.
        
        Args:
            input_data: Input to process
            
        Returns:
            Processed intermediate result
        """
        pass
    
    @abstractmethod
    def generate(self, intermediate: Any) -> BaseOutput:
        """Generate final output.
        
        Args:
            intermediate: Intermediate processing result
            
        Returns:
            Final output dataclass
        """
        pass
```

---

## 2.4 VSGR Base Classes

### models/base.py

```python
"""Base classes for VLM models in VSGR.

Data flow:
  image + text → VLM processor → token embeddings
  → forward pass → hidden states + logits + attention
  → extract region features → RegionFeatures
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple
import torch


@dataclass
class VLMOutput:
    """Standard VLM output structure.
    
    Attributes:
        logits: Output logits for next token prediction [B, L, V]
        hidden_states: Hidden states from all layers [num_layers, B, L, D_h]
        visual_attentions: Visual attention weights [B, H, L_visual, L_visual]
        text: Generated text sequence
    """
    logits: torch.Tensor
    hidden_states: torch.Tensor
    visual_attentions: Optional[torch.Tensor] = None
    text: Optional[str] = None


@dataclass
class RegionFeatures:
    """Features extracted from image regions.
    
    Attributes:
        region_features: Feature vectors per region [num_regions, D_h]
        region_tokens: Token indices for each region
        region_boxes: Bounding boxes [num_regions, 4] (x1, y1, x2, y2)
    """
    region_features: torch.Tensor
    region_tokens: torch.Tensor
    region_boxes: torch.Tensor


class BaseVLMConfig:
    """Base configuration for VLM models."""
    
    def __init__(self, config_dict: dict):
        self.model_name = config_dict["model_name"]
        self.device = config_dict.get("device", "auto")
        self.torch_dtype = config_dict.get("torch_dtype", "float16")


class BaseVLM(ABC):
    """Base class for Vision-Language Models.
    
    Data flow:
      config → load model → processor
      → forward(image, text) → model outputs
      → post_process → VLMOutput
    """
    
    def __init__(self, config: BaseVLMConfig):
        self.config = config
        self.model = None
        self.processor = None
        self._load_model()
    
    @abstractmethod
    def _load_model(self):
        """Load model and processor from HuggingFace."""
        pass
    
    @abstractmethod
    def forward(
        self,
        image,
        text: str,
        return_logits: bool = True,
        return_hidden_states: bool = True
    ) -> VLMOutput:
        """Forward pass through VLM.
        
        Args:
            image: Input image (PIL or tensor)
            text: Input text prompt
            return_logits: Whether to return logits
            return_hidden_states: Whether to return hidden states
            
        Returns:
            VLMOutput with logits, hidden states, and attention
        """
        pass
    
    @abstractmethod
    def extract_region_features(
        self,
        image,
        region_boxes: torch.Tensor
    ) -> RegionFeatures:
        """Extract features from specified regions.
        
        Args:
            image: Input image
            region_boxes: Bounding boxes [num_regions, 4]
            
        Returns:
            RegionFeatures with per-region representations
        """
        pass
```

### gr_reason/base.py

```python
"""Base classes for graph-based reasoning.

Data flow:
  image → region extraction → Region list
  → graph construction → RegionGraph
  → multi-agent reasoning → reasoning steps
  → answer generation → final output
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
import torch


@dataclass
class Region:
    """A region in the image with features and relationships.
    
    Attributes:
        region_id: Unique identifier
        box: Bounding box [4] (x1, y1, x2, y2)
        features: Feature vector [D_h]
        description: Text description of region content
    """
    region_id: int
    box: torch.Tensor
    features: torch.Tensor
    description: Optional[str] = None


@dataclass
class Edge:
    """Relationship edge between two regions.
    
    Attributes:
        source_id: Source region ID
        target_id: Target region ID
        relation_type: Type of relationship
        weight: Edge weight/strength
    """
    source_id: int
    target_id: int
    relation_type: str
    weight: float = 1.0


@dataclass
class RegionGraph:
    """Graph structure representing image regions and relationships.
    
    Attributes:
        regions: List of Region objects
        edges: List of Edge objects
        global_features: Global image features
    """
    regions: List[Region] = field(default_factory=list)
    edges: List[Edge] = field(default_factory=list)
    global_features: Optional[torch.Tensor] = None
    
    def add_region(self, region: Region):
        """Add a region to the graph."""
        self.regions.append(region)
    
    def add_edge(self, edge: Edge):
        """Add an edge to the graph."""
        self.edges.append(edge)


@dataclass
class ReasoningStep:
    """A single step in the reasoning process.
    
    Attributes:
        step_id: Step number
        active_regions: List of region IDs involved
        thought: Reasoning text for this step
        action: Action taken (e.g., "verify", "relate", "conclude")
    """
    step_id: int
    active_regions: List[int]
    thought: str
    action: str


class BaseRegionExtractor(ABC):
    """Base class for region extraction strategies.
    
    Data flow:
      image + config → extract regions → List[Region]
    """
    
    @abstractmethod
    def extract(self, image, **kwargs) -> List[Region]:
        """Extract regions from image.
        
        Args:
            image: Input image
            **kwargs: Additional extraction parameters
            
        Returns:
            List of Region objects
        """
        pass


class BaseGraphConstructor(ABC):
    """Base class for graph construction strategies.
    
    Data flow:
      regions → build relationships → RegionGraph
    """
    
    @abstractmethod
    def construct(self, regions: List[Region], **kwargs) -> RegionGraph:
        """Construct graph from regions.
        
        Args:
            regions: List of extracted regions
            **kwargs: Additional construction parameters
            
        Returns:
            RegionGraph with regions and edges
        """
        pass


class BaseGraphReasoning(ABC):
    """Base class for graph-based visual reasoning.
    
    Data flow:
      RegionGraph + question → multi-agent reasoning
      → List[ReasoningStep] → final answer
    """
    
    @abstractmethod
    def reason(
        self,
        graph: RegionGraph,
        question: str,
        **kwargs
    ) -> Tuple[List[ReasoningStep], str]:
        """Perform reasoning on region graph.
        
        Args:
            graph: RegionGraph with image structure
            question: Question to answer
            **kwargs: Additional reasoning parameters
            
        Returns:
            Tuple of (reasoning steps, final answer)
        """
        pass
```

---

## 2.5 Config Template Design

All experiments are driven by YAML config files. Design standard config templates in `configs/TEMPLATE/`.

### Standard BLOCK Structure

| Block | Name           | Content                                           | Universality        |
|-------|----------------|---------------------------------------------------|---------------------|
| 1     | `data`         | Dataset name, path, split                         | Universal           |
| 2     | `environment`  | dotenv path, random seed, device                  | Universal           |
| 3     | `model`        | Model definition (name, path, config)             | Universal           |
| 4     | `graph_region` | Graph construction and reasoning config           | Domain-specific     |
| 5     | `training`     | Training parameters (if applicable)               | Domain-specific     |
| 6     | `log`          | Output directory, log level, checkpoint frequency | Universal           |
| 7     | `evaluation`   | Evaluation config                                 | Universal           |
| 8+    | `experiment`   | Experiment-specific parameters                    | Experiment-specific |

### Example Config Template

```yaml
# configs/TEMPLATE/vsgr_experiment.yml

# BLOCK 1: Data Configuration
data:
  dataset_name: "VisualReasoningDataset"
  data_path: "EXPERIMENT/data/"
  split: "test"
  num_samples: 100

# BLOCK 2: Environment Configuration
environment:
  dotenv_path: ".env"
  seed: 42
  device: "cuda"
  num_workers: 4

# BLOCK 3: Model Configuration
model:
  name: "llava-hf/llava-1.5-7b-hf"
  torch_dtype: "float16"
  device_map: "auto"
  generation:
    max_new_tokens: 512
    temperature: 0.2
    do_sample: false

# BLOCK 4: Graph Region Configuration (VSGR-specific)
graph_region:
  region_extraction:
    method: "vlm_guided"  # or "grid", "saliency"
    num_regions: 8
    min_region_size: 0.05
  
  graph_construction:
    method: "adaptive"  # or "fully_connected", "knn"
    edge_threshold: 0.5
    relation_types: ["spatial", "semantic"]
  
  reasoning:
    method: "multi_agent_rl"
    num_agents: 3
    max_steps: 10
    agent_config:
      verifier:
        role: "verify_region_relevance"
      navigator:
        role: "navigate_relationships"
      reasoner:
        role: "synthesize_answer"

# BLOCK 5: Training Configuration (if training)
training:
  enabled: false
  batch_size: 4
  learning_rate: 1e-5
  num_epochs: 10

# BLOCK 6: Logging Configuration
log:
  output_dir: "EXPERIMENT/results/"
  log_level: "INFO"
  save_checkpoints: true
  checkpoint_frequency: 100

# BLOCK 7: Evaluation Configuration
evaluation:
  metrics: ["accuracy", "f1", "exact_match"]
  save_predictions: true
  visualize_results: false

# BLOCK 8: Experiment-specific Configuration
experiment:
  name: "baseline_graph_region"
  description: "Baseline GraphRegion experiment"
  tags: ["baseline", "llava-7b"]
```

---

## 2.6 Unit Test Framework (uTEST)

Establish functional validation tests to ensure each core capability works correctly.

```
examples/uTEST/                  # Functional validation scripts
├── test_vlm_forward.py          # Test VLM forward pass
├── test_region_extraction.py    # Test region extraction
├── test_graph_construction.py   # Test graph building
└── test_reasoning.py            # Test reasoning loop

configs/uTEST/                   # Corresponding test configs
├── test_vlm_forward.yml
├── test_region_extraction.yml
└── ...
```

### Why uTEST Before Formal Experiments?

- Verify newly implemented modules are correct
- **Discover hidden engineering issues** — many important discoveries first appear in uTEST
- Establish regression baseline
- uTEST scope should expand with modules

---

## 2.7 Environment Configuration

| Config Item       | Location            | Description                                         |
|-------------------|---------------------|-----------------------------------------------------|
| HuggingFace Token | `.env`              | Download model weights (`HUGGINGFACE_TOKEN=hf_xxx`) |
| WandB Key         | `.env`              | Experiment tracking (`WANDB_KEY=xxx`)               |
| API Keys          | `.env`              | External LLM API (`DEEPSEEK_API_KEY=xxx`)           |
| Datasets          | `EXPERIMENT/data/`  | Downloaded and stored here                          |
| Model Cache       | HuggingFace default | Auto-downloads on first run                         |

Use `python-dotenv` to load `.env`, ensure `.env` is in `.gitignore`.

---

## 2.8 Code Quality Gate

After writing or modifying code, MUST execute the following check flow:

```
Code Writing Complete
    │
    ▼
┌─────────────────────────────────────────────────┐
│  Step 1: Check against Development Standards      │
│  □ Any .get() defensive programming?              │
│  □ All imports at file top?                       │
│  □ Fully using base library interfaces?           │
│  □ Variable params go through YAML config?        │
│  □ Prompts as module-level constants?             │
└─────────────────┬───────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────┐
│  Step 2: Check against Architecture Principles    │
│  □ New classes inherit from correct base class?   │
│  □ Docstring includes data flow overview?         │
│  □ Initialize via config dict?                    │
│  □ Tensor dimensions use standard notation?       │
└─────────────────┬───────────────────────────────┘
                  ▼
┌─────────────────────────────────────────────────┐
│  Step 3: Run related uTEST verification           │
│  Ensure changes don't introduce regression        │
└─────────────────┬───────────────────────────────┘
                  ▼
  Pass → Continue to next step
  Fail → Fix and restart from Step 1
```

---

## 2.9 Module Documentation

Every module in the core package MUST have corresponding `docs/` documentation:

```
docs/
├── vsgr-overview.md             # Package overview
├── gr_reason.md                 # Graph reasoning module
├── models.md                    # VLM models module
└── evaluate.md                  # Evaluation module
```

### Documentation Content Requirements

| Section                       | Content                                                            |
|-------------------------------|--------------------------------------------------------------------|
| **Module Purpose**            | What problem does this module solve? Why is it needed?             |
| **Core Concepts**             | Key concepts, terminology, data structures (use tables/diagrams)   |
| **Data Flow**                 | Input → Processing → Output (ASCII flow diagram)                   |
| **Class/Interface Hierarchy** | Base class → subclass inheritance and responsibilities             |
| **Relationships**             | Which modules it depends on, which modules use it                  |
| **Design Decisions**          | Why choose this implementation? What existing work was referenced? |

> Documentation should explain WHY and WHAT, not HOW. Don't show code snippets, only reference file names and key class names.

---

## 2.10 Output Verification

### Automated Verification

```bash
# 1. Module structure verification
ls {package}/ | grep -E '\.py$|^[a-z]+$'
# → Should see generic.py and submodule directories

# 2. Base class verification
grep -l 'ABC\|abstractmethod' {package}/*.py {package}/*/*.py
# → Should return base.py files

# 3. Config template verification
ls configs/TEMPLATE/
# → Should have .yml files

# 4. uTEST verification
python examples/uTEST/test_{capability}.py -c configs/uTEST/test_{capability}.yml
# → Should run successfully
```

### Verification Checklist

| Check Item                                             | Verification Method                              |
|--------------------------------------------------------|--------------------------------------------------|
| `base.py` files have base class + dataclass defined?   | Open file to confirm `@abstractmethod` exists    |
| Each base class has data flow docstring?               | Review each class docstring                      |
| `configs/TEMPLATE/` contains standard BLOCK structure? | Check YAML files for standard blocks             |
| Each core module has `docs/{module}.md`?               | Compare `ls docs/` with `ls {package}/`          |
| uTEST covers at least 1 core capability?               | `ls examples/uTEST/` to confirm test files exist |
| All written code passed Code Quality Gate?             | Check item by item                               |

---

## Next Phase

After Phase 2 completion, proceed to:

**Phase 3: Literature Survey**
- Systematically search related papers
- Build knowledge map
- Identify most relevant work and research gaps
