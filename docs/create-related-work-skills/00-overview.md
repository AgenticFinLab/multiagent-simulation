# Related Work Writing Guide — Overview

## What This Folder Is

This folder is the **authoritative skill guide** for writing, searching, and maintaining `docs/related-work.md` — a comprehensive literature review for any research project. It organizes each phase of the complete workflow into a dedicated, deeply specified file.

This guide is **research-agnostic** — it applies equally to NLP, computer vision, multi-agent systems, economics, finance, or any other field. The user fills `00-user-define.md` once, and every subsequent file is driven by that configuration.

---

## Folder Structure and Reading Order

| File                          | Stage              | Purpose                                                               |
|-------------------------------|--------------------|-----------------------------------------------------------------------|
| `00-user-define.md`           | **0 — User Input** | Fill this FIRST: 10-field table defining your research                |
| `00-overview.md`              | —                  | This file: orientation, reading order, key principles                 |
| `01-paper-entry-template.md`  | Standard           | The 9-component template every paper entry must follow                |
| `02-search-reactive.md`       | 2 — Search         | Reactive: access and read papers you already know about               |
| `03-search-proactive.md`      | 3 — Search         | Proactive: systematically discover papers you don't know exist        |
| `04-reading-extraction.md`    | 4 — Read           | Read papers, extract structured information                           |
| `04b-paper-classification.md` | 4b — Classify      | Derive taxonomy; organize papers into Categories and Sub-Categories   |
| `05-writing-guidelines.md`    | 5 — Write          | Writing order, style rules, ASCII diagrams, section-specific guidance |
| `06-batch-processing.md`      | 6 — Batch          | Batch strategies, stub-to-full pipelines, cross-section consistency   |
| `07-validation.md`            | 7 — Validate       | Per-paper checklist, automated validation script, iterative loop      |
| `08-quality-standards.md`     | 8 — Standards      | Common pitfalls, Our Work template, glossary, table patterns          |

---

## Complete Workflow

```
Stage 0: Fill 00-user-define.md
            ↓
Stage 1: Keyword + Venue Preparation  (03-search-proactive.md §1–§3)
            ↓
Stage 2: Search Execution              (03-search-proactive.md §4–§8)
         + Reactive search             (02-search-reactive.md)
            ↓
Stage 3: Paper Reading + Extraction   (04-reading-extraction.md)
            ↓
Stage 4: Classification + Taxonomy    (04b-paper-classification.md)
            ↓
Stage 5: Entry Writing                 (05-writing-guidelines.md)
         using template                (01-paper-entry-template.md)
            ↓
Stage 6: Batch Processing if needed   (06-batch-processing.md)
            ↓
Stage 7: Validation + Iteration       (07-validation.md)
            ↓
Stage 8: Quality Review               (08-quality-standards.md)
```

---

## How to Use This Guide

### Step 0 — Fill `00-user-define.md`

Fill in all 10 fields. These values drive everything:
- Fields 1, 8, 9, 10 → venue taxonomy and arXiv categories
- Fields 4, 5, 6 → keyword matrix (Domain × Method × Motivation)
- Field 7 → "Relationship to Our Work" comparison table dimensions
- Field 2 → "Our Work" column in all comparison tables

### Step 1 — Prepare search (`03-search-proactive.md §1–§3`)

The agent reads `00-user-define.md` and auto-generates:
- Extracted keywords (D1–Dn, M1–Mn, G1–Gn)
- Selected venues (CCF-A + recognized top venues)
- Keyword matrix (D×M cross-product)
- Coverage tracker (initialized)

### Step 2 — Execute search (`03-search-proactive.md §4–§8` + `02-search-reactive.md`)

- **Proactive** (`03-search-proactive.md`): proceedings scan, keyword queries, cross-reference expansion, keyword expansion loop
- **Reactive** (`02-search-reactive.md`): access and verify papers you already know about

### Step 3 — Read and extract (`04-reading-extraction.md`)

For each candidate paper: structured reading → structured extraction template → update Candidate Paper List status FOUND → READ.

### Step 4 — Classify (`04b-paper-classification.md`)

Derive taxonomy from `00-user-define.md`. Every Category traces back to a field. Paper assignments define the `related-work.md` section structure.

### Step 5 — Write (`05-writing-guidelines.md` + `01-paper-entry-template.md`)

Follow the writing order (Core Motivation → Core Idea → Core Method → Example → Summary → Relationship). Use ASCII diagrams. Add synthesis sections at the end of each thematic group.

### Step 6 — Batch if needed (`06-batch-processing.md`)

For 20+ papers: preparation → parallel research agents → bulk structural fill → manual upgrade of Critical papers → incremental refinement.

### Step 7 — Validate (`07-validation.md`)

Run the automated validation script after every batch. The script is the primary progress tracker — not just a final check.

### Step 8 — Review quality (`08-quality-standards.md`)

Check for common pitfalls, ensure "Relationship to Our Work" tables are specific and accurate, maintain terminology consistency.

---

## Key Principles

### 1. Configuration-first
Everything derives from the 10 fields in `00-user-define.md`. Fill them carefully before starting any search.

### 2. CCF-A venue policy
Only papers from CCF-A conferences or recognized top venues (COLM, TMLR, CoRL, etc.). Any exception requires explicit justification.

### 3. Full template, no shortcuts
Every paper entry must have all 9 components from `01-paper-entry-template.md`. No "Summary only" entries. No placeholder text.

### 4. Read before writing
Never write content without reading the paper. Multi-source verification (arXiv + GitHub + OpenReview) is required for Critical/High relevance papers.

### 5. Validate iteratively
Run the validation script after every batch. Do not wait until all papers are done.

### 6. Taxonomy before writing
Derive the paper taxonomy from `00-user-define.md` before writing entries. The taxonomy defines the section structure of `related-work.md`.

### 7. Concrete examples over abstractions
Every paper entry needs a concrete toy problem in the Example section (BEFORE/AFTER format). A reader should understand the paper's contribution from the Example alone.

---

## Quick Reference

| Need                                  | Go to                         |
|---------------------------------------|-------------------------------|
| Fill in research topic                | `00-user-define.md`           |
| Understand the full workflow          | This file                     |
| Know what a complete entry looks like | `01-paper-entry-template.md`  |
| Find papers you already know about    | `02-search-reactive.md`       |
| Discover new papers systematically    | `03-search-proactive.md`      |
| Know which venues to search           | `03-search-proactive.md §2`   |
| Build the keyword matrix              | `03-search-proactive.md §3`   |
| Know how deep to read                 | `04-reading-extraction.md §1` |
| Extract structured info from a paper  | `04-reading-extraction.md §2` |
| Organize papers into sections         | `04b-paper-classification.md` |
| Know the writing order                | `05-writing-guidelines.md §1` |
| Draw ASCII diagrams                   | `05-writing-guidelines.md §3` |
| Write a synthesis section             | `05-writing-guidelines.md §5` |
| Process many papers efficiently       | `06-batch-processing.md`      |
| Turn a stub into a full entry         | `06-batch-processing.md §3`   |
| Run the validation script             | `07-validation.md §2`         |
| Check a paper's quality               | `07-validation.md §1`         |
| Avoid common mistakes                 | `08-quality-standards.md §1`  |
| Write "Relationship to Our Work"      | `08-quality-standards.md §2`  |
| Maintain terminology consistency      | `08-quality-standards.md §3`  |
