# Phase 1: Codebase Initialization

> **Actor:** LLM (Autonomous Execution)
> **Status:** Automated Phase
> **Prerequisite:** Completed Phase 0 with research direction defined
> **Output:** `pip install -e .` ready repository

---

## Overview

Transform the organization's template repository into a standard Python research package that can be installed via `pip install -e .`. All subsequent development will be conducted within this framework.

This phase establishes the foundation for the entire research codebase.

---

## 1.1 Starting Point: Organization Template Repository

Typically, research teams maintain a **repository template**. When creating a new project, it automatically includes a standard skeleton:

```
project-root/
├── cdemo/                   # Placeholder demo package (needs renaming)
│   └── __init__.py
├── .github/                 # PR templates, CI configs
│   └── pull_request_template.md
├── setup.py                 # Package install config (references cdemo/)
├── requirements.txt         # Dependencies (pre-filled by template)
├── description.txt          # Project description
├── README.md
├── LICENSE
├── .gitignore
└── .env                     # Environment variables template
```

> **Key insight:** You don't need to create these files from scratch — the template provides the standard skeleton. Your job is to **rename and adapt**.

---

## 1.2 Step-by-Step Execution

### Step 1: Determine Package Name and Rename Placeholder

Extract the package name from Phase 0 input:

```
Project name: visual-spatial-chain
Package name: vsgr  (abbreviation for Visual Spatial Graph Region)

Action: cdemo/ → rename to vsgr/
```

**Implementation:**
- Rename directory `cdemo/` to `{package}/`
- Update `__init__.py` to reflect new package name
- Ensure `__version__` is defined

---

### Step 2: Update setup.py References

Replace all references to `cdemo` in `setup.py` with the new package name:

| Field      | Update Required                                                  |
|------------|------------------------------------------------------------------|
| `name`     | Update to research project name (e.g., `"visual-spatial-chain"`) |
| `packages` | Change from `cdemo` to `{package}`                               |
| `version`  | Read from `{package}/__init__.py`                                |
| `keywords` | Add research domain keywords                                     |

**Example setup.py structure:**
```python
from setuptools import setup, find_packages
import {package}

setup(
    name="{project-name}",
    version={package}.__version__,
    packages=find_packages(),
    install_requires=[
        # Dependencies from requirements.txt
    ],
    python_requires=">=3.8",
    keywords="vision-language, multi-agent, graph-reasoning",
)
```

---

### Step 3: Create Research-Specific Directory Structure

Add research-specific directories on top of the template:

```
project-root/
├── {package}/                    # Renamed from cdemo/ (core research package)
│   └── __init__.py               # __version__ = "0.0.1"
├── configs/                      # NEW: All config files
│   └── TEMPLATE/                 #   Config templates (designed in Phase 2)
├── docs/                         # NEW: All research documentation
├── examples/                     # NEW: Experiment scripts
├── EXPERIMENT/                   # NEW: Experiment outputs (not in git)
│   └── data/                     #   Dataset storage
├── third-part/                   # NEW: Third-party code
├── .github/                      # Existing: PR templates
├── setup.py                      # Existing: Updated references
├── requirements.txt              # Existing: Add research dependencies
├── description.txt               # Existing: Update project description
├── .env                          # Existing: Fill in API keys
└── .gitignore                    # Existing: Add EXPERIMENT/, build/
```

**Commands to create directories:**
```bash
mkdir -p configs/TEMPLATE
mkdir -p docs/ideas
mkdir -p examples/uTEST
mkdir -p EXPERIMENT/data
mkdir -p third-part
```

---

### Step 4: Install and Verify

```bash
# Install main package (editable mode, code changes take effect immediately)
pip install -e .

# If you have a base utility library, install it too
pip install -e third-part/{base_library}

# Verify installation
python -c "import {package}; print({package}.__version__)"
# → 0.0.1
```

> **Why use `pip install -e .`?** Editable mode means the package is imported directly from the current directory. After modifying source code, no reinstallation is needed. This is crucial for research development — code changes frequently, and you can't repackage every time.

---

### Step 5: Configure .gitignore

Ensure the following paths are not tracked by version control:

```gitignore
# Experiment outputs (large files, reproducible)
EXPERIMENT/

# Python installation artifacts
build/
*.egg-info/
__pycache__/

# Environment variables (contains API keys)
.env

# IDE
.vscode/
.idea/

# OS
.DS_Store
```

---

### Step 6: Integrate External Base Library (Optional)

If your team maintains a base utility library (e.g., `lmbase`):

1. **Placement:** Place in `third-part/` or as a git submodule
2. **Installation:** Ensure it can be imported via `pip install -e third-part/lmbase`
3. **Dependency Boundaries:** Clarify separation:
   - **Base library:** Storage, inference interfaces, device management
   - **Research package:** Experiments, evaluation, research logic

**Example dependency structure:**
```
lmbase provides:
  - InferInput / InferOutput / InferCost — Inference I/O abstractions
  - BlockBasedStoreManager — Incremental storage (supports checkpoint resume)
  - LLMInference / LangChainAPIInference — Model invocation wrappers
  - set_seed, get_device, setup_environment — Environment utilities

{package} is responsible for:
  - Research-specific logic
  - Experiment evaluation framework
  - Visualization tools
  - Domain-specific operations
```

---

## 1.3 Development Standards (Established in Phase 1)

These coding standards apply throughout the entire workflow:

| Standard                        | Description                                                                                             | Rationale                              |
|---------------------------------|---------------------------------------------------------------------------------------------------------|----------------------------------------|
| **No Defensive Programming**    | Don't use `.get()` for known keys — use `dict["key"]` directly, let errors surface early                | Fail fast, catch bugs early            |
| **All Imports at File Top**     | No function-level imports, conditional imports, or lazy imports                                         | Clear dependencies, easier refactoring |
| **Maximize Base Library Usage** | When a base library exists, use its storage, inference, and environment management interfaces uniformly | Consistency, less code to maintain     |
| **Config-Driven**               | All variable parameters go through YAML configs, no hardcoding                                          | Reproducibility, easy experimentation  |
| **Modular Prompts**             | Define Prompts as module-level constants, organized by experiment in `prompts.py`, expressed naturally  | Maintainability, clarity               |

---

## 1.4 VSGR-Specific Implementation

For the VSGR project, Phase 1 produces:

```
visual-spatial-chain/
├── vsgr/                         # Core package (renamed from cdemo/)
│   ├── __init__.py               # __version__ = "0.0.1"
│   └── ...                       # Modules added in Phase 2
├── configs/
│   └── TEMPLATE/                 # Config templates
├── docs/
│   ├── research-plans/           # This document
│   └── ...                       # Other documentation
├── examples/
│   └── uTEST/                    # Unit tests
├── EXPERIMENT/
│   └── data/                     # Datasets
├── third-part/                   # Reference implementations
├── setup.py                      # Updated for vsgr
├── requirements.txt              # Dependencies
├── description.txt               # VSGR project description
└── .gitignore                    # Includes EXPERIMENT/
```

**Key dependencies for VSGR:**
```
torch>=2.0.0
transformers>=4.35.0
pillow>=9.0.0
numpy>=1.24.0
pyyaml>=6.0
python-dotenv>=1.0.0
```

---

## 1.5 Output Verification

### Automated Verification Commands

```bash
# 1. pip install verification
pip install -e . && python -c "import {package}; print({package}.__version__)"
# → Should output version number (e.g., 0.0.1)

# 2. Base library verification (if applicable)
pip install -e third-part/{base_library} && python -c "import {base_library}"

# 3. Directory structure verification
ls {package}/ configs/ docs/ examples/ EXPERIMENT/ third-part/
# → All directories should exist

# 4. .gitignore verification
git status --ignored | grep EXPERIMENT
# → EXPERIMENT/ should be in the ignored list
```

### Verification Checklist

| Check Item                                     | Verification Method                    | Expected Result            |
|------------------------------------------------|----------------------------------------|----------------------------|
| `cdemo/` renamed to `{package}/`?              | `ls` to confirm old name doesn't exist | Only `{package}/` exists   |
| All references in `setup.py` updated?          | `grep cdemo setup.py`                  | Returns empty              |
| `pip install -e .` successful?                 | Execute command                        | No errors, package imports |
| `EXPERIMENT/`, `configs/`, `docs/` created?    | `ls` to confirm                        | All directories exist      |
| `.gitignore` includes `EXPERIMENT/`, `build/`? | `cat .gitignore`                       | Both patterns present      |
| `.env` configured?                             | `cat .env`                             | Token placeholders exist   |
| Development standards documented?              | Review code                            | Follows standards from 1.3 |

---

## 1.6 Common Issues and Solutions

| Issue                               | Cause                               | Solution                                       |
|-------------------------------------|-------------------------------------|------------------------------------------------|
| `ModuleNotFoundError` after install | Package not in PYTHONPATH           | Use `pip install -e .` not `pip install .`     |
| Version not found                   | `__init__.py` missing `__version__` | Add `__version__ = "0.0.1"`                    |
| cdemo references persist            | Missed some files                   | `grep -r "cdemo" . --include="*.py"`           |
| EXPERIMENT/ tracked by git          | .gitignore not applied              | `git rm -r --cached EXPERIMENT/` then recommit |

---

## Next Phase

After Phase 1 completion, proceed to:

**Phase 2: Modular Architecture Design**
- Design module hierarchy within `{package}/`
- Create base classes and data structures
- Establish config templates
- Write module documentation
