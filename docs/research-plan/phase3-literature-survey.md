# Phase 3: Literature Survey

> **Actor:** LLM (Autonomous Execution)
> **Status:** Automated Phase
> **Prerequisite:** Completed Phase 2 with module architecture
> **Output:** `docs/reference.md`, `docs/{topic}-reference.md`, paper analysis

---

## Overview

Systematically search, read, classify, and organize papers related to the research direction. Build a knowledge map, identify most relevant work and research gaps.

This phase builds the theoretical foundation for your research and identifies what has been done before.

---

## 3.1 Search Strategy

| Source                  | Method                                                                   |
|-------------------------|--------------------------------------------------------------------------|
| Top Conferences         | NeurIPS, ICML, ICLR, ACL, EMNLP, CVPR, ICCV, ECCV from recent 1-2 years  |
| arXiv Preprints         | Keyword search + citation chain tracing                                  |
| Related Work References | Recursively trace from found papers' references                          |
| GitHub                  | Search code repositories, focus on work with open-source implementations |

### VSGR-Specific Search Keywords

Primary keywords:
- "visual reasoning region"
- "vision language model spatial"
- "multi-step visual reasoning"
- "visual question answering region"
- "image understanding attention"

Secondary keywords:
- "chain of thought visual"
- "visual reasoning graph"
- "region-based VLM"
- "visual grounding reasoning"

---

## 3.2 Funnel-Style Filtering Process

Literature survey is a **progressively narrowing** process, not one-time completion:

```
┌─────────────────────────────────────────────┐
│  Step 1: Broad Search                         │
│  Search keywords: visual reasoning, region,   │
│  VLM, multi-step, graph, attention            │
│  → Collect 30-50 candidate papers             │
└─────────────────┬───────────────────────────┘
                  ▼
┌─────────────────────────────────────────────┐
│  Step 2: Quick Scan (abstract + conclusion)   │
│  Judge relevance to VSGR research             │
│  → Filter to 15-20 papers worth reading       │
│  → Record in docs/reference.md                │
└─────────────────┬───────────────────────────┘
                  ▼
┌─────────────────────────────────────────────┐
│  Step 3: Deep Reading + Template Analysis     │
│  Analyze each paper's core mechanism          │
│  → Filter to 5-10 most relevant               │
│  → Write to docs/vsgr-reference.md            │
└─────────────────┬───────────────────────────┘
                  ▼
┌─────────────────────────────────────────────┐
│  Step 4: Select Typical Work, Download Source │
│  With open source + directly comparable:      │
│  - VLM-R³ (sequential region reasoning)       │
│  - CoFFT (multi-step visual reasoning)        │
│  - ParGo (grid-based regions)                 │
│  → Download to third-part/ (enter Phase 4)    │
│  → Write topic analysis docs/{source}.md      │
└─────────────────────────────────────────────┘
```

---

## 3.3 Reading and Analysis Template

Analyze each paper using the following fixed format:

```
Paper: [Title]
Venue: [Conference/Journal/arXiv]
Code:  [GitHub URL or N/A]

★ Core Idea:    (One sentence summarizing core innovation)
★ Mechanism:    (Step-by-step technical flow description)
★ Key Claims:   (Main results claimed by paper)
★ Limitations:  (Method limitations/questionable aspects)
★ Relevance:    (Relationship to our research: directly relevant/reference/comparison baseline)
★ Training?:    (Requires training? Training what? Or pure inference-time method?)
```

### Example: VLM-R³ Analysis

```
Paper: VLM-R³: A Universal Reflective Region Representation and Reasoning for
       Visual Understanding
Venue: arXiv 2024
Code:  https://github.com/xxx/vlm-r3

★ Core Idea:
Sequential region extraction and reasoning where each step focuses on one
region, building understanding progressively through reflection.

★ Mechanism:
1. Start with full image and question
2. Iteratively:
   a. Generate coordinates for next relevant region
   b. Crop and encode the region
   c. Reflect on region content
   d. Update reasoning state
3. Generate final answer based on accumulated region information

★ Key Claims:
- Better than full-image reasoning on region-intensive tasks
- Reflection mechanism improves reasoning quality
- Works with any VLM without fine-tuning

★ Limitations:
- Sequential processing is slow (multiple VLM calls)
- May miss cross-region relationships
- No parallel exploration of multiple regions

★ Relevance:
DIRECTLY RELEVANT — This is our primary comparison baseline. Our hypothesis
is that graph-based parallel reasoning outperforms this sequential approach.

★ Training?:
NO TRAINING REQUIRED — Pure inference-time method using frozen VLM.
```

---

## 3.4 Classification and Organization

Classify papers by relationship to research:

| Level          | File                     | Content                                   | Funnel Stage |
|----------------|--------------------------|-------------------------------------------|--------------|
| All References | `docs/reference.md`      | List of all papers (title + one-liner)    | Step 2       |
| Deep Analysis  | `docs/vsgr-reference.md` | Detailed analysis of most relevant papers | Step 3       |
| Topic Analysis | `docs/{source}.md`       | Single most important work's deep-dive    | Step 4       |

### Expected VSGR Literature Structure

```
docs/
├── reference.md                 # 20+ paper list
├── vsgr-reference.md            # 7 most relevant papers deep analysis:
│   ├── VLM-R³                   #   Sequential region reasoning (baseline)
│   ├── CoFFT                    #   Multi-step visual reasoning (baseline)
│   ├── ParGo                    #   Grid-based region extraction (baseline)
│   ├── LISA                     #   Grounded segmentation (reference)
│   ├── Shikra                   #   Spatial grounding (reference)
│   ├── GPT4RoI                  #   Region-level understanding (reference)
│   └── LLaVA                    #   General VLM framework (reference)
├── vlm-r3.md                    # VLM-R³ source code analysis
├── cofft.md                     # CoFFT source code analysis
└── pargo.md                     # ParGo source code analysis
```

---

## 3.5 VSGR Key Paper Categories

### Directly Relevant (Core Comparison Targets)

| Paper      | Core Mechanism                              | Why Compare                                               |
|------------|---------------------------------------------|-----------------------------------------------------------|
| **VLM-R³** | Sequential region reasoning with reflection | Primary baseline — our graph approach vs their sequential |
| **CoFFT**  | Chain-of-thought for visual reasoning       | Efficiency comparison — single-pass vs multi-iteration    |
| **ParGo**  | Grid-based uniform region partition         | Ablation baseline — uniform vs adaptive regions           |

### Reference Implementations

| Paper       | Useful For                        |
|-------------|-----------------------------------|
| **LISA**    | Region segmentation techniques    |
| **Shikra**  | Spatial coordinate generation     |
| **GPT4RoI** | Region feature extraction methods |

### Framework Papers

| Paper       | Useful For                       |
|-------------|----------------------------------|
| **LLaVA**   | VLM architecture reference       |
| **Qwen-VL** | Alternative VLM architecture     |
| **CLIP**    | Visual feature extraction basics |

---

## 3.6 Key Findings Extraction

After literature survey, extract key findings that inform your research:

```markdown
## Key Findings from Literature Survey

### Finding 1: Sequential vs Parallel Region Processing
- VLM-R³ uses sequential region processing (one at a time)
- This is slow and may miss cross-region relationships
- **Our opportunity:** Parallel graph-based reasoning

### Finding 2: Region Representation Methods
- Grid-based (ParGo): Uniform but may miss important details
- Saliency-based: Adaptive but computationally expensive
- VLM-guided (VLM-R³): Precise but requires multiple iterations
- **Our opportunity:** Learned adaptive region extraction

### Finding 3: Training Requirements
- Most methods require NO training (inference-time only)
- This is a key advantage for practical deployment
- **Our decision:** Maintain inference-time only approach

### Finding 4: Evaluation Benchmarks
- Standard: VQAv2, GQA, Visual7W
- Region-intensive: RefCOCO, PointQA
- **Our benchmark selection:** Focus on multi-region reasoning tasks
```

---

## 3.7 Output Verification

| Check Item                                         | Verification Method                      |
|----------------------------------------------------|------------------------------------------|
| `docs/reference.md` created with 15-20 papers?     | Open file, count paper entries           |
| Each paper has one-liner describing relationship?  | Check format item by item                |
| `docs/vsgr-reference.md` created?                  | `ls docs/` to confirm existence          |
| Most relevant papers analyzed with fixed template? | Open file to check for 6 required fields |
| Identified 2-4 papers needing source download?     | Document clearly marks which → Phase 4   |
| Key findings summarized?                           | Clear findings list at document end      |

---

## Next Phase

After Phase 3 completion, proceed to:

**Phase 4: Source Code Deep-Dive**
- Download most relevant work's open-source code
- File-by-file, function-by-function analysis
- Understand implementation details and potential issues
