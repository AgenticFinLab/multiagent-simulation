# Phase 0: Research Direction Setting

> **Actor:** USER (Human Researcher)
> **Status:** Required Input Phase
> **Output:** Filled Phase 0 YAML Block

---

## Overview

This is the **ONLY section that requires USER input**. All subsequent phases (Phase 1-8) are executed autonomously by the LLM based on the information you provide here.

The research direction you define in this phase drives:
- Project naming and structure
- Module architecture design
- Literature search keywords
- Experiment design priorities
- Final conclusion framework

---

## How to Use This Phase

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Step 1: Fill in the Required Input table below                          │
│                                                                          │
│  Step 2: Review Field Guidelines to ensure quality                       │
│                                                                          │
│  Step 3: Complete Output Verification checklist                          │
│                                                                          │
│  Step 4: Provide this document to LLM for autonomous execution           │
│          of Phases 1-8                                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 0.1 Required User Input

**Fill in the table below before starting:**

| # | Field                                  | Your Input | VSGR Example                                                                                                                                                                 |
|---|----------------------------------------|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1 | **Research Domain**                    |            | Multi-agent reinforcement learning for graph-based visual reasoning in vision-language models                                                                                |
| 2 | **Core Hypothesis**                    |            | Visual reasoning with region relationship graphs via multi-agent reinforcement learning outperforms sequential one-step-one-region approaches while maintaining full context |
| 3 | **Verification Approach 1**            |            | Compare GraphRegion (parallel graph-based) vs VLM-R³ (sequential crop-based) on cross-region reasoning tasks                                                                 |
| 4 | **Verification Approach 2**            |            | Compare inference efficiency: single-pass GraphRegion vs multi-iteration CoFFT                                                                                               |
| 5 | **Verification Approach 3** (optional) |            | Ablation study: uniform grid (ParGo) vs adaptive graph (GraphRegion) vs sequential (VLM-R³)                                                                                  |
| 6 | **Project Name**                       |            | `visual-spatial-chain`                                                                                                                                                       |
| 7 | **Package Name**                       |            | `vsgr` (Visual Spatial Graph Region)                                                                                                                                         |
| 8 | **Base Library** (optional)            |            |                                                                                                                                                                              |

---

## 0.2 Field Guidelines

### Research Domain
- **Requirement:** One sentence, understandable to non-experts
- **Purpose:** Defines the broad area of investigation
- **Example:** "Multi-agent reinforcement learning for graph-based visual reasoning in vision-language models"
- **Tips:**
  - Avoid jargon where possible
  - Include both the technical approach and the target problem
  - Should be broad enough to encompass your work but specific enough to be meaningful

### Core Hypothesis
- **Requirement:** Must be falsifiable — you must be able to state what result would disprove it
- **Purpose:** The central claim your research aims to validate or invalidate
- **Example:** "Visual reasoning with region relationship graphs via multi-agent RL outperforms sequential one-step-one-region approaches"
- **Tips:**
  - Use comparative language (better than, more efficient than, etc.)
  - Include measurable outcomes when possible
  - Test: Ask yourself "What experimental result would prove me wrong?"

### Verification Approaches
- **Requirement:** 2-3 concrete, executable experimental paths
- **Purpose:** Different angles to test your hypothesis
- **Examples:**
  - Comparative experiments against baselines
  - Ablation studies
  - Efficiency measurements
  - Scaling analysis
- **Tips:**
  - Each approach should test a different aspect of the hypothesis
  - Should be feasible with available resources
  - Consider both positive and negative cases

### Project Name
- **Requirement:** Descriptive, memorable, no spaces
- **Purpose:** Repository name, documentation title
- **Example:** `visual-spatial-chain`, `latent-multiagent`, `kv-communication`
- **Tips:**
  - Used in GitHub repository name
  - Appears in README and documentation headers

### Package Name
- **Requirement:** Short (3-6 characters), reflects research area, valid Python identifier
- **Purpose:** Python package import name
- **Examples:**
  - `vsgr` - Visual Spatial Graph Region
  - `lmag` - Latent Multi-Agent Graph
  - `cocot` - Chain of Cognitive Thought
- **Tips:**
  - Will be used as `import {package}` in Python
  - Should be unique and not conflict with popular packages
  - Abbreviations are preferred for brevity

### Base Library (Optional)
- **Requirement:** Path to team/organization's base utility library
- **Purpose:** Shared infrastructure for storage, inference, device management
- **Example:** `third-part/lmbase`
- **Tips:**
  - Leave empty if no base library exists
  - Base libraries typically provide: storage managers, inference wrappers, environment utilities

---

## 0.3 Output Deliverables

Once Phase 0 is filled, the LLM will generate:

| Deliverable         | Location             | Content                                              |
|---------------------|----------------------|------------------------------------------------------|
| Project Description | `description.txt`    | One-paragraph summary based on research domain       |
| Project README      | `README.md`          | Overview with hypothesis and verification approaches |
| Package Structure   | `{package}/`         | Complete module hierarchy (Phase 1-2)                |
| Literature Survey   | `docs/reference.md`  | Paper analysis (Phase 3)                             |
| Source Analysis     | `docs/{source}.md`   | Third-party code analysis (Phase 4)                  |
| Experiments         | `EXPERIMENT/`        | Progressive experiment results (Phase 6-7)           |
| Conclusions         | `docs/conclusion.md` | Hypothesis validation results (Phase 8)              |

---

## 0.4 Output Verification

Before proceeding to Phase 1, verify:

| Check Item                                        | Verification Method              | Pass Criteria                                                 |
|---------------------------------------------------|----------------------------------|---------------------------------------------------------------|
| Research domain is one sentence and clear?        | Explain to a non-expert          | They understand the general area without technical background |
| Core hypothesis is falsifiable?                   | State "what would disprove this" | Can clearly articulate disproving evidence                    |
| Verification approaches has 2-3 executable paths? | Review each path                 | Each is concrete and actionable                               |
| Package name is 3-6 characters?                   | Count characters                 | Valid Python identifier, 3-6 chars                            |
| All fields in table are filled?                   | Review table                     | No empty required fields                                      |

---

## 0.5 VSGR Example: Completed Phase 0

For reference, here is the completed Phase 0 for the VSGR project:

```yaml
research_direction:
  domain: "Multi-agent reinforcement learning for graph-based visual reasoning in vision-language models"
  
  hypothesis: |
    Visual reasoning with region relationship graphs via multi-agent reinforcement 
    learning outperforms sequential one-step-one-region approaches while maintaining 
    full image context and reducing inference iterations.
  
  verification:
    approach_1: |
      Compare GraphRegion (parallel graph-based) vs VLM-R³ (sequential crop-based) 
      on cross-region reasoning tasks requiring multiple spatial relationships
    
    approach_2: |
      Compare inference efficiency: single-pass GraphRegion vs multi-iteration 
      CoFFT on complex visual reasoning benchmarks
    
    approach_3: |
      Ablation study comparing: uniform grid regions (ParGo), adaptive graph 
      regions (GraphRegion), sequential regions (VLM-R³)
  
  naming:
    project: "visual-spatial-chain"
    package: "vsgr"
    
  # base_library: "third-part/lmbase"  # Optional
```

---

## Next Steps

After completing Phase 0:

1. **Save this document** with your filled-in values
2. **Provide to LLM** along with the instruction to execute Phases 1-8
3. **Review outputs** at each phase completion
4. **Iterate as needed** based on findings from literature and experiments

The LLM will now autonomously execute:
- **Phase 1:** Codebase initialization (`setup.py`, package structure)
- **Phase 2:** Modular architecture (base classes, config templates)
- **Phase 3:** Literature survey (paper search and analysis)
- **Phase 4:** Source code deep-dive (reference implementation analysis)
- **Phase 5:** Hypothesis refinement (updates based on findings)
- **Phase 6:** Experiment design (progressive experiment planning)
- **Phase 7:** Experiment execution (running and recording results)
- **Phase 8:** Cross-experiment analysis (final conclusions)
