# Semantic review record

## Candidate and boundary

| Field | Value |
|---|---|
| Event and selected interval | |
| Candidate path, semantic ID, and SHA-256 | |
| Candidate kind | Agent Definition / Population Model / participant batch / Scenario |
| Source Profile and exposure | |
| Roster, registries, and Scenario parents | |
| Template and Skill revisions | |
| Reviewer and review date | |
| Inputs explicitly excluded | |

State the representation or event-world claim being reviewed. Separate direct
file facts from reviewer inference.

## Coverage

Record modules and anchors read, actor/observation/intent/lifecycle/state rows
checked, registry projections compared, and any item not reviewed with reason.
The review is invalid after candidate or parent bytes change.

## Adversarial cases

| Case | Mutation or question | Expected boundary | Observed result | Evidence |
|---|---|---|---|---|
| name erasure | | | | |
| actor/role swap | | | | |
| missing or stale information | | | | |
| future/private information | | | | |
| invalid authority/target/payload | | | | |
| pending or adverse result | | | | |
| material perturbation | | | | |
| aggregation or concurrency change | | | | |

Add product-specific cases from the owning Skill. A successful nominal path is
not an adversarial review.

## Findings

| ID | Severity | Direct evidence | Contract and impact | Owning layer | Required correction | Retest | Status |
|---|---|---|---|---|---|---|---|
| | blocker/high/medium/low | | | | | | open/closed |

Do not average findings. One unresolved blocker or high finding prevents
acceptance. Close a finding only against the revised candidate identity.

## Limitations and decision

List accepted dataset, representation, aggregation, or mechanism limitations
and the successor trigger for each material limitation.

Use one verdict: `accept`, `accept with recorded limitations`, or `return to
owning layer`. Record validation results, final candidate hash, responsible
owner, and the next legal action. This review does not admit a backend, run, or
scientific conclusion.
