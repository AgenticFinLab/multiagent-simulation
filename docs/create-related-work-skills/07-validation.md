# Validation

## Purpose

This file specifies the validation workflow for `docs/related-work.md`. Validation is not just a final check — it is the **primary navigation tool** throughout the entire writing process. Run it frequently.

**Core principle**: Validation-driven development. Run → identify incomplete → fix → re-run → repeat.

---

## §1 Per-Paper Quality Checklist

Before marking any individual paper entry as complete, verify every item:

### §1.1 Structure Checklist

- [ ] `[CAT: X] [REL: Y]` tags are present and accurate
- [ ] Paper title is exact — matches the PDF title character-for-character
- [ ] arXiv link is present and resolves correctly (click it)
- [ ] Venue and year are confirmed (not guessed)
- [ ] Code link is present (or explicitly `Null`)
- [ ] All 9 sections are present: Summary, Core Motivation, Core Idea, Core Method, Example, Key Results, Relationship to Our Work (+ tags + metadata)

### §1.2 Content Checklist

- [ ] Summary explains what the paper DOES, not just what it claims
- [ ] Summary includes the method name and at least one quantitative result
- [ ] Core Motivation states the PROBLEM, not the solution
- [ ] Core Motivation identifies the specific gap in prior work
- [ ] Core Idea is expressed as a transformation, formula, or before/after (not just a method name)
- [ ] Core Method includes step-by-step technical details with named components
- [ ] Core Method has at least one ASCII diagram (for Critical/High papers)
- [ ] Example shows BEFORE and AFTER comparison concretely
- [ ] Example can be understood without any background knowledge
- [ ] Key Results include specific numbers from the paper with table/figure citations
- [ ] Relationship to Our Work has a comparison table with ≥3 rows
- [ ] Comparison table uses dimensions from `00-user-define.md`
- [ ] Comparison table "Their Work" column is specific — not vague

### §1.3 Accuracy Checklist

- [ ] All quantitative claims verified against the paper PDF (not from memory)
- [ ] No placeholder text: no "TBD", no "TODO", no "[Generic...]", no "..."
- [ ] No garbled generic text from bulk scripts ("Existing methods face challenges in efficiency...")
- [ ] Technical terms used consistently with the rest of the document
- [ ] Method description matches what the paper actually proposes (not a confabulation)

---

## §2 Automated Validation Script

Run this script after every batch to track progress. Paper entries use `####` headers (under `###` sub-categories).

```python
import re

with open('docs/related-work.md') as f:
    content = f.read()

# Find all paper entries (#### level, e.g., #### 1.1.1 PaperTitle)
papers = re.findall(r'^(#### \d+\.\d+\.\d+ .+?)$', content, re.MULTILINE)
positions = [m.start() for m in re.finditer(r'^#### \d+\.\d+\.\d+ ', content, re.MULTILINE)]

# Required sections for a complete entry
required_sections = [
    'Summary',
    'Core Motivation',
    'Core Idea',
    'Core Method',
    'Example',
    'Relationship to Our Work'
]

incomplete = []
organization_headers = []

for i, pos in enumerate(positions):
    end_pos = positions[i+1] if i+1 < len(positions) else len(content)
    block = content[pos:end_pos]
    title = papers[i] if i < len(papers) else "Unknown"

    # Detect organization headers (no Paper line, no CAT/REL tags)
    is_paper = '**Paper**:' in block or '[CAT:' in block
    if not is_paper:
        organization_headers.append(title)
        continue

    # Check for required sections (##### level within paper entry)
    has_tags = '[CAT:' in block and '[REL:' in block
    missing = [s for s in required_sections if not re.search(r'#{4,5}\s+' + re.escape(s), block)]

    # Check for placeholder text
    placeholders = []
    for pattern in ['TBD', 'TODO', '[Generic', 'To be completed', 'PLACEHOLDER']:
        if pattern in block:
            placeholders.append(pattern)

    if not has_tags or missing or placeholders:
        incomplete.append({
            'title': title,
            'missing_sections': missing,
            'missing_tags': not has_tags,
            'placeholders': placeholders
        })

# Report
total_papers = len(papers) - len(organization_headers)
complete = total_papers - len(incomplete)

print("=" * 60)
print("Related Work Validation Report")
print("=" * 60)
print(f"Total #### headers:   {len(papers)}")
print(f"Organization headers: {len(organization_headers)} (skipped)")
print(f"Paper entries:        {total_papers}")
print(f"Complete:             {complete}")
print(f"Incomplete:           {len(incomplete)}")
print(f"Completion rate:      {complete/total_papers*100:.1f}%" if total_papers > 0 else "N/A")
print()

if incomplete:
    print("INCOMPLETE PAPERS:")
    for p in incomplete:
        issues = []
        if p['missing_tags']:
            issues.append("no CAT/REL tags")
        if p['missing_sections']:
            issues.append(f"missing: {', '.join(p['missing_sections'])}")
        if p['placeholders']:
            issues.append(f"placeholders: {', '.join(p['placeholders'])}")
        print(f"  {p['title']}")
        print(f"    Issues: {'; '.join(issues)}")
    print()
    print("Fix these papers before marking the document complete.")
else:
    print("ALL PAPERS COMPLETE.")
```

---

## §3 Validation-Driven Development Workflow

The iterative loop that governs all batch processing:

```
Step 1: Run validation script
        → Get count: "X/N complete"
        → Get list of all incomplete papers with their missing sections

Step 2: Identify patterns in missing sections
        → "All missing Core Method" → run a targeted research pass
        → "All missing tags" → run a classification pass
        → "Half complete, half stubs" → prioritize by relevance

Step 3: Fix one batch (4-6 papers at a time)
        → For Critical/High: individual research + writing
        → For Medium/Low: batch processing with agents

Step 4: Re-run validation script
        → Confirm the batch fixed the identified issues
        → New count: "X+N/Total complete"

Step 5: Repeat until 0 incomplete papers
```

**Progress reporting**: Use the output as a completion metric in each session:
```
Session start: "69/116 papers complete (59.5%)"
After batch 1: "83/116 papers complete (71.6%)"
After batch 2: "104/116 papers complete (89.7%)"
Final: "116/116 papers complete (100%)"
```

---

## §4 Validation After Bulk Edits

After running any bulk script or large `search_replace` operation:

### Step 1: Structure Integrity Check

```bash
# Confirm total paper entry count (#### level)
grep -c "^#### " docs/related-work.md

# Confirm CAT/REL tag count
grep -c "\[CAT:" docs/related-work.md

# Confirm no sections got merged (all required ##### headers still present)
grep -c "^##### Core Method" docs/related-work.md
grep -c "^##### Example" docs/related-work.md
grep -c "^##### Relationship to Our Work" docs/related-work.md
```

### Step 2: Content Spot Check

```bash
# Search for 5 random paper titles and read their sections
# Confirm content is present and not truncated
grep -n "PAPER_TITLE" docs/related-work.md
# Then read lines [found_line:found_line+60]
```

### Step 3: Placeholder and Garbled Text Scan

```bash
# Detect any placeholders introduced by bulk operations
grep -n "TBD\|TODO\|\[Generic\|To be completed\|PLACEHOLDER" docs/related-work.md

# Detect garbled bulk-script text
grep -n "Existing methods face challenges" docs/related-work.md
grep -n "novel latent-space techniques" docs/related-work.md
```

---

## §5 Consistency Check

| What to Check                   | How                                                                  | Pass Criteria                     |
|---------------------------------|----------------------------------------------------------------------|-----------------------------------|
| Same paper in multiple sections | `grep -n "PaperTitle" docs/related-work.md` — facts must match       | No contradictory descriptions     |
| Terminology consistency         | Grep for term variants → unify with glossary                         | Single canonical term per concept |
| Comparison table columns        | All tables use same dimension names from `00-user-define.md` field 7 | Consistent column headers         |
| Reference format                | All paper entries use `####` header level                            | No `###` paper entries            |
| Venue policy                    | All papers from CCF-A or recognized top venues                       | 0 non-compliant papers            |

### Duplicate Detection

```bash
# Find papers appearing in multiple sections
grep -o "^#### [0-9.]* .*" docs/related-work.md | sort -t' ' -k3 | uniq -d -f2
```

If a paper appears in multiple sections:
- Keep consistent core facts (method, key result, link)
- Section-appropriate emphasis (overview section = shorter, technical section = longer)
- Add cross-reference: "See Section X.Y.Z for detailed technical discussion"

---

## §5 Manual Validation for Critical Papers

For papers marked [REL: Critical] or [REL: High], automated validation is insufficient. Also perform manual validation:

1. **Re-read the written summary** against the paper abstract — do they match?
2. **Verify the Core Idea** matches the paper's central claim
3. **Check the Example** accurately illustrates the method's contribution
4. **Confirm the comparison table** is fair and specific — not vague
5. **Verify all quantitative claims** against Tables/Figures in the paper

### Manual Verification Spot-Check Template

```
Paper: [Title]

Claim check 1: Summary says [X] — verify against abstract → [MATCH / MISMATCH]
Claim check 2: Core Idea says [Y] — verify against §3 of paper → [MATCH / MISMATCH]
Result check: Key Results say [Z%] on [benchmark] — verify against Table [N] → [MATCH / MISMATCH]
Example check: BEFORE/AFTER example — does it illustrate the correct contribution? [YES / NO]
```

---

## §6 Document-Level Completeness Checklist

Run before finalizing `docs/related-work.md` for any milestone (submission, review, etc.):

- [ ] Validation script reports 0 incomplete papers
- [ ] No placeholder text anywhere in the document (`grep -n "TBD\|TODO" docs/related-work.md`)
- [ ] No garbled generic content (`grep -n "Existing methods face challenges" docs/related-work.md`)
- [ ] All paper links verified as resolving correctly (spot-check ≥5)
- [ ] Venue taxonomy coverage: papers present from all Tier 1 venues
- [ ] Year coverage: papers from multiple years (no single-year clustering)
- [ ] Workshop papers present (not all papers from main conferences only)
- [ ] Synthesis sections present for major topic clusters
- [ ] Terminology glossary in `08-quality-standards.md §3` is consistent with document
- [ ] All `[REL: Critical]` papers have ≥4-row comparison tables
- [ ] Cross-references between duplicate-appearing sections are present
- [ ] All `[CAT:]` assignments are consistent with the category taxonomy
