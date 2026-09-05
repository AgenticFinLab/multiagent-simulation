# Baoneng–Vanke Takeover Battle Rule realization

## Identity and semantic parents

`h2epr.1031.rule-realization.v1` binds configuration `h2epr.1031.rule.v1`
to the common `h2epr.backend.rule.declarative.v4` implementation and all eight
exact Agent parents. Four implementation source files are hash-pinned. No new
event-specific Python, MASim change, model caller or alternative backend is used.

## Actor and capability coverage

| Actor | Non-default intents |
| --- | --- |
| baoneng_group | disclose_initial_stake, disclose_increased_stake, oppose_asset_proposal, submit_removal_request, reaffirm_opposition |
| china_resources | oppose_asset_proposal_cr |
| csrc | issue_governance_guidance |
| evergrande_group | disclose_evergrande_stake, record_negotiation_participation |
| shenzhen_metro | submit_restructuring_terms, confirm_proposal_participation, submit_negotiation_position, disclose_metro_acquisition, submit_board_nominees |
| vanke_corporate_governance | issue_suspension_notice, record_conditional_loi, announce_metro_proposal, issue_resumption_notice, record_board_rejection, open_resolution_discussion, report_operating_impacts, register_board_nominees, schedule_shareholder_meeting |
| wang_shi | state_takeover_opposition, publish_management_statement, decline_board_nomination |
| yu_liang | state_management_risk |

Every actor receives exactly its four declared observation classes and own
intent set plus no_op. No Population is silently removed: the source roster
selects eight named Agents and zero populations. Parent/index hashes, actor
parity and handler coverage are compiler admission requirements.

## Decision production

Rows use inclusive activation windows, ascending unique own priorities and
stable rule IDs. State guards and actually received-message memory must all
match. An accepted row is complete; a rejected row can reopen after a changed
visible information fingerprint. Own rejection or clock advance alone does not
cause an identical retry. One action per actor per coordinate and no_op waiting
retain the shared decision contract; generated opaque IDs never rank choices.

This Rule selects exposed statement contents and a sparse communication model.
It does not solve a shareholder game, infer preferences or optimize an investment
return. Receipt dependencies and availability windows are documented structural
assumptions. LLM/RuleLLM remain planned and fail closed at admission.

## Failure routing

Malformed parents, schemas, provenance, identities or unavailable backends fail
admission. Wrong actor/target, invalid parameters or failed state prerequisites
produce typed rejected dispositions; they do not get repaired into valid actions.
Runtime integrity or transport failure retains manifest and sealed-prefix custody
with a failed-attempt receipt where available, and cannot yield a complete run
release. Graph/replay/reproduction mismatch rejects publication. There is no
silent backend substitution, dependency installation or external retrieval.

## Environment boundary

The backend emits actions and statement messages. The authoritative environment
and reducer validate effects; transport owns delivery and runtime owns memory.
Messages alone do not prove action acceptance. Shareholding disclosures do not
clear securities, opposition does not veto a transaction, guidance does not
choose a winner, and a nominee or meeting notice does not elect the board.

## Verification and verdict

Semantic realization is accepted for deterministic runtime verification with the
published disclosure-only and composite-board limitations. This is author
self-review, not a second independent human. Runtime acceptance separately
requires fresh A/B, generated-ID perturbation, trace chain and tick/run seals,
authoritative replay, exact final state, complete trace-derived graph and zero
unresolved transport. The publisher rederives evidence and rematerializes rather
than trusting this verdict. Local candidate probes test missing/late nomination
information and a valid open endpoint; they are not scientific experiments.
