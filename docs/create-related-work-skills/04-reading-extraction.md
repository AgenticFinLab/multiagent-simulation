# Reading and Extraction

## Purpose

This file specifies how to read a paper and extract structured information ready for writing a `related-work.md` entry. It bridges the gap between accessing a paper (covered in `02-search-reactive.md`) and writing the full entry (covered in `05-writing-guidelines.md`).

---

## §1 Reading Depth by Relevance Level

### [REL: Critical] — Full Paper Read

Required sections (in this order):

| Section               | What to Extract                                                                 |
|-----------------------|---------------------------------------------------------------------------------|
| Abstract              | Core claim, method name, key metric result                                      |
| Introduction          | Problem statement, gap in prior work, motivation, contributions list            |
| Related Work          | How the authors position themselves; papers they cite (discover new references) |
| Method / Architecture | Technical approach, formulas, data flow, training procedure, loss functions     |
| Experiments           | Datasets, baselines, metrics, ablations, key quantitative results               |
| Conclusion            | Confirmed contributions, stated limitations, future work                        |
| Appendix              | Proofs, additional ablations, hyperparameters                                   |

**Time budget**: 60–90 minutes per paper  
**Multi-source verification**: arXiv PDF + GitHub + OpenReview (minimum)

### [REL: High] — Focused Read

Required sections:

| Section                        | What to Extract                             |
|--------------------------------|---------------------------------------------|
| Abstract                       | Core claim, method name, key metric result  |
| Introduction                   | Full read — motivation and gap are critical |
| Method (skim + key paragraphs) | Main mechanism, key formula or diagram      |
| Experiments (summary)          | Best result, main baseline comparison       |

**Time budget**: 30–45 minutes per paper  
**Multi-source verification**: arXiv PDF + at least 1 other source

### [REL: Medium] — Quick Scan

Required sections:

| Section      | What to Extract                        |
|--------------|----------------------------------------|
| Abstract     | Full read                              |
| Introduction | First 2–3 paragraphs                   |
| Key Figure   | The architecture or main result figure |
| Conclusion   | 1 paragraph                            |

**Time budget**: 10–15 minutes per paper  
**Source**: arXiv PDF only is sufficient

### [REL: Low] — Abstract Only

| Section  | What to Extract |
|----------|-----------------|
| Abstract | Full read       |

**Time budget**: 3–5 minutes per paper  
**Source**: arXiv abstract page only

---

## §2 Structured Extraction Template

After reading, immediately extract into this template. This is the raw material for writing the full entry. Do this BEFORE writing the entry — extraction keeps reading and writing separate, preventing confusion.

```
## Extraction: [Paper Title]

**Link**: [arxiv URL]
**Venue**: [Conference/Journal Year]
**Authors**: [Names]
**Code**: [GitHub URL or Null]

### 1. PROBLEM
[1 sentence — what are they solving? Start with the problem, not the method.]

### 2. GAP
[1-2 sentences — what is insufficient about prior work? What specific limitation do they address?]

### 3. INSIGHT
[1 sentence — what is the key idea? Express as a transformation or before/after.]

### 4. METHOD
[3-5 sentences — how do they implement it? Include: architecture, formula, training procedure.]

### 5. RESULT
[1-2 sentences — what did they achieve? Include specific numbers and benchmark names.]

### 6. LIMITATIONS
[1 sentence — what doesn't it do? What are the failure modes or scope restrictions?]

### 7. CONNECTION TO OUR WORK
[2-3 sentences — how does this relate to our research target from 00-user-define.md?
Include: similarities, differences, complementary aspects, limitations we address.]

### 8. RELEVANCE CATEGORY
- CAT: [Core / Efficiency / Training / Analysis / Theory / or field-specific]
- REL: [Critical / High / Medium / Low]
- Rationale: [1 sentence justifying the REL assignment]
```

---

## §3 Figure and Diagram Extraction

For Critical and High relevance papers, extract the key figure or architecture diagram from the paper and reproduce it as an ASCII representation in the extraction notes. This becomes the basis for the Core Method ASCII diagram.

### ASCII Extraction Protocol

```
1. Find the paper's main architecture figure (usually Figure 1 or Figure 2)
2. Identify the key components and their connections
3. Reproduce as ASCII using box-drawing characters:

   [Input] → [Component A] → [Component B] → [Output]
       ↑                          |
       └──────────────────────────┘

4. Add labels with actual component names from the paper
5. Add data shapes/dimensions if relevant
```

### Figure Priority

| Figure Type             | What to Extract                    | Priority              |
|-------------------------|------------------------------------|-----------------------|
| Architecture overview   | Full component diagram             | Highest               |
| Data flow diagram       | Input → process → output           | High                  |
| Before/After comparison | Baseline vs. method                | High                  |
| Training procedure      | Loss landscape, optimization steps | Medium                |
| Result plot             | Main accuracy vs. baseline curve   | Low (numbers suffice) |

---

## §4 Quantitative Results Extraction

Always extract results with full context:

```
## Results: [Paper Title]

### Primary Benchmark
- Dataset: [Name]
- Metric: [Name]
- Their result: [Number] [Unit if applicable]
- Previous SOTA: [Number] (by [Method])
- Improvement: [+X%]
- Source: Table [N] in the paper

### Secondary Benchmarks
- [Dataset]: [Their result] vs. [Baseline: their result] — [Table N]
- ...

### Ablation Key Findings
- Removing [Component X] drops performance by [Y points] — ablation Table N
- [Other key ablation finding]

### Computational Cost
- Training: [GPU-hours or cost if reported]
- Inference: [Latency or throughput if reported]
- Parameters: [Model size if reported]
```

---

## §5 Relationship Mapping

Before writing the "Relationship to Our Work" section, explicitly work through this mapping:

```
## Relationship Mapping: [Paper Title] vs. Our Work

### Similarities
- [Aspect 1]: Both [description]
- [Aspect 2]: Both [description]

### Differences
- [Aspect 1]: They [description] — we [description from 00-user-define.md]
- [Aspect 2]: They [description] — we [description from 00-user-define.md]

### Complementary Aspects
- Their [Component X] could inform our [Component Y] because [reason]

### Limitations They Don't Address (That We Do)
- [Limitation 1]: They [description] — we address this by [approach from 00-user-define.md]

### Draft Comparison Table (pre-write)
| Aspect                         | Their Work       | Our Work       |
|--------------------------------|------------------|----------------|
| [Dim 1 from 00-user-define.md] | [their approach] | [our approach] |
| [Dim 2 from 00-user-define.md] | [their approach] | [our approach] |
| [Dim 3 from 00-user-define.md] | [their approach] | [our approach] |
```

**Rule**: If "Our Work" column cannot be filled (because our work is not yet defined), write "TBD" explicitly — never write something vague or invented.

---

## §6 Cross-Reference Discovery During Reading

While reading a paper, actively watch for new papers to add to the search queue:

```
While reading any paper:
  ✓ Read the Related Work section fully → note unfamiliar relevant papers
  ✓ Check the references list for foundational papers you haven't covered
  ✓ Note any "concurrent work" mentions → search those immediately
  ✓ Note any "builds on X" or "extends X" mentions → check X if not yet covered

After reading:
  → Add all newly discovered papers to the search queue
  → For each newly discovered paper, assess REL level before adding
  → High/Critical: add to next reading batch
  → Medium/Low: add as stub immediately
```

---

## §7 Extraction Quality Checklist

Before moving from extraction to writing, verify:

- [ ] Problem is stated as a problem (not a method)
- [ ] Gap describes what prior work fails to do (not what this paper does)
- [ ] Insight is expressed as a transformation or before/after (not just a method name)
- [ ] Method has 3+ sentences with specific component names
- [ ] Results have specific numbers (not "significant improvement")
- [ ] Results are cited with table/figure numbers from the paper
- [ ] Relationship mapping has identified at least 2 similarities AND 2 differences
- [ ] CAT and REL assignments are justified
- [ ] All claims have been verified against the paper PDF (not from memory or third-party summaries)
