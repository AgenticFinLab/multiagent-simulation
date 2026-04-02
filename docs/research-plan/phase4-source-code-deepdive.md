# Phase 4: Source Code Deep-Dive

> **Actor:** LLM (Autonomous Execution)
> **Status:** Automated Phase
> **Prerequisite:** Completed Phase 3 with literature survey
> **Output:** `third-part/`, `docs/{source}.md`, analysis documents

---

## Overview

From the most relevant work identified in Phase 3, download their open-source code, conduct file-by-file, function-by-function analysis, understand implementation details and potential issues.

This phase reveals the engineering realities behind the papers — what works, what doesn't, and what assumptions were made.

---

## 4.1 Steps

### Step 1: Code Acquisition

Download most relevant work's open-source code to `third-part/`:

```
third-part/
├── vlm-r3/                      # Core comparison target
├── cofft/                       # Multi-step reasoning reference
├── pargo/                       # Grid-based region reference
└── {base_library}/              # Team base library (if any)
```

**Download methods:**
```bash
# Method 1: Git clone
cd third-part/
git clone https://github.com/xxx/vlm-r3.git

# Method 2: Download release
curl -L https://github.com/xxx/vlm-r3/archive/refs/tags/v1.0.tar.gz | tar xz

# Method 3: Git submodule (if tracking updates)
git submodule add https://github.com/xxx/vlm-r3.git third-part/vlm-r3
```

### VSGR Target Sources

| Source     | Priority | Why                                            |
|------------|----------|------------------------------------------------|
| **VLM-R³** | High     | Primary baseline — sequential region reasoning |
| **CoFFT**  | High     | Multi-step visual reasoning approach           |
| **ParGo**  | Medium   | Grid-based region extraction                   |
| **LLaVA**  | Medium   | VLM architecture reference                     |

---

### Step 2: File-by-File Analysis

For each important file, produce analysis record using unified template:

```
File: third-part/{project}/{file}.py

1. Class/Function List:
   - {ClassName}: Function description (line number range)
   - {function_name}: Function description (line number range)

2. Data Flow:
   input → {step_1} → {intermediate} → {step_2} → output

3. Key Findings:
   - {Finding 1: Technical details/limitations/design decisions}
   - {Finding 2: Relationship to our research}
   - {Finding 3: Potential issues/questionable aspects}
```

### Example: VLM-R³ Analysis

```
File: third-part/vlm-r3/vlmr3/model.py

1. Class/Function List:
   - VLMR3Reasoner: Main reasoning class (L45-180)
   - RegionExtractor: Extracts regions from coordinates (L182-240)
   - ReflectionModule: Reflection mechanism (L242-310)
   - forward_step(): Single reasoning step (L312-380)

2. Data Flow:
   image + question → VLMR3Reasoner.__init__() → load base VLM
   → forward_step():
     → generate_region_coords() → [x1, y1, x2, y2]
     → RegionExtractor.crop() → region_image
     → VLM.encode(region_image) → region_features
     → ReflectionModule.reflect() → reflection_text
     → update_state() → new_reasoning_state
   → [loop max_steps times]
   → generate_answer() → final_output

3. Key Findings:
   - Finding 1: Region coordinates generated as text tokens, parsed with regex
     → Potential issue: Coordinate precision limited by tokenization
   
   - Finding 2: Each step loads full VLM, no KV cache sharing between steps
     → Inefficient: O(N) VLM forward passes for N steps
     → Our opportunity: Single-pass with graph structure
   
   - Finding 3: Reflection is just additional text generation, no special mechanism
     → Could be simplified or enhanced with explicit verification
   
   - Finding 4: No explicit cross-region relationship modeling
     → Validates our hypothesis about missing cross-region reasoning
```

---

### Step 3: Problem Identification

During source code analysis, record key issues and design flaws discovered. Build a **Finding → Impact → Verification Method** tracking table:

| Finding                                          | Impact                                                | Verification Method                                                   |
|--------------------------------------------------|-------------------------------------------------------|-----------------------------------------------------------------------|
| VLM-R³ loads full model each step, no KV sharing | Inefficient O(N) inference                            | Compare inference time: GraphRegion (single-pass) vs VLM-R³ (N steps) |
| CoFFT uses fixed iteration count                 | May over-process simple images, under-process complex | Design adaptive stopping criterion experiment                         |
| ParGo uniform grid misses small objects          | Reduced accuracy on detail-intensive tasks            | Compare adaptive vs uniform region extraction                         |
| VLM-R³ reflection is just text generation        | May not actually improve reasoning                    | Ablation: with/without reflection module                              |

> This table is direct input for Phase 6 experiment design — each "Verification Method" column may evolve into a preliminary experiment.

---

## 4.2 Output Deliverables

### Per-Source Analysis Document

Each downloaded source gets a detailed analysis document:

```markdown
# VLM-R³ Source Code Analysis

## Overview
- **Paper:** VLM-R³: A Universal Reflective Region Representation...
- **Code:** https://github.com/xxx/vlm-r3
- **Version analyzed:** commit abc123

## Architecture Overview
```
[ASCII diagram of overall architecture]
```

## File-by-File Analysis

### model.py
[Analysis from template above]

### region_extractor.py
[Analysis from template above]

### reflection_module.py
[Analysis from template above]

## Key Insights

### Insight 1: Sequential Processing Bottleneck
VLM-R³ processes regions sequentially, loading the full VLM for each step.
This is the primary inefficiency our graph-based approach addresses.

### Insight 2: Coordinate Generation Mechanism
Coordinates are generated as text and parsed with regex. This limits precision
and could fail with malformed outputs.

### Insight 3: No Cross-Region Relationships
Each region is processed independently. No explicit modeling of spatial or
semantic relationships between regions.

## Relevance to VSGR

| VLM-R³ Component    | VSGR Equivalent            | Improvement              |
|---------------------|----------------------------|--------------------------|
| Sequential steps    | Parallel graph nodes       | Single-pass inference    |
| Independent regions | Connected region graph     | Cross-region reasoning   |
| Text reflection     | Structured reasoning steps | Clearer decision process |

## Identified Issues for Experiments

1. **Issue:** Sequential inefficiency
   **Experiment:** Compare inference time (Experiment 2)

2. **Issue:** No relationship modeling
   **Experiment:** Ablation with/without graph edges (Experiment 3)
```

---

## 4.3 VSGR-Specific Source Analysis

### VLM-R³ Deep Analysis

Focus areas:
1. **Region coordinate generation** — How are bounding boxes produced?
2. **Reflection mechanism** — What does "reflection" actually do?
3. **State management** — How is reasoning state maintained across steps?
4. **VLM integration** — Which VLM is used, how is it called?

Expected findings:
- Coordinate generation is text-based (not direct regression)
- Reflection adds overhead without clear benefit
- No KV cache optimization between steps

### CoFFT Deep Analysis

Focus areas:
1. **Multi-step reasoning loop** — How are steps organized?
2. **Stopping criteria** — When does reasoning end?
3. **Visual attention** — How is visual attention managed?

Expected findings:
- Fixed iteration count is suboptimal
- Attention mechanism could be more efficient

### ParGo Deep Analysis

Focus areas:
1. **Grid generation** — How are uniform grids created?
2. **Region selection** — Which regions are kept?
3. **Feature extraction** — How are region features computed?

Expected findings:
- Uniform grid is simple but inflexible
- Region selection heuristic is hand-crafted

---

## 4.4 Output Verification

### Automated Verification

```bash
# 1. Third-party code verification
ls third-part/
# → Should see 2-4 reference implementation directories

# 2. Analysis document verification
ls docs/ | grep -v reference | grep -v ideas | grep -v preExp
# → Should see various {source}.md files
```

### Verification Checklist

| Check Item                                                           | Verification Method                                |
|----------------------------------------------------------------------|----------------------------------------------------|
| `third-part/` has downloaded 2-4 reference implementations?          | `ls third-part/` to confirm directories exist      |
| Each reference has corresponding `docs/{source}.md`?                 | Check one-to-one correspondence                    |
| Analysis docs contain: class/function list, data flow, key findings? | Open document to check all three parts complete    |
| "Finding → Impact → Verification Method" table established?          | Table has at least 2-3 rows of actual content      |
| If major findings, Phase 0 hypothesis updated?                       | Compare current hypothesis with initial hypothesis |

---

## Next Phase

After Phase 4 completion, proceed to:

**Phase 5: Hypothesis Refinement**
- Update hypothesis based on literature and source analysis
- Adapt code architecture based on findings
- Refine config templates
