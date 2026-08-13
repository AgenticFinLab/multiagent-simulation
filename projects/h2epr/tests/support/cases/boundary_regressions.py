"""Cross-object acceptance controls and adversarial boundary regressions."""

from __future__ import annotations

import copy
from typing import Any

from ..canonical_json import (
    manifest_hash,
    projection_attestation_hash,
    reseal_graph,
    reseal_trace,
)
from ..schema_registry import schema_errors
from ..validators.communication import (
    communication_errors,
    communication_history_errors,
    duplicate_values,
    exact_interval,
    linked_run_global_identity_errors,
    linked_run_transport_errors,
)
from ..validators.construction import (
    anchored_chain_request_errors,
    artifact_chain_errors,
    construction_lineage_ref,
    projection_attestation_errors,
    reseal_chain_from_construction,
    reseal_graph_and_evaluation_from_trace,
)
from ..validators.trace_and_seals import (
    graph_errors,
    run_seal_coordinate_errors,
    trace_eligibility_errors,
    trace_integrity_errors,
)
from .common import SYNTHETIC, bounded_helper_descriptor, fixture_bases, make_case
from .communication import (
    rechain_and_reseal,
    transport_controls,
    update_terminal_and_reseal,
    update_trace_payload,
)


def _probe(
    legacy_case_id: str,
    semantic_condition_id: str,
    responsibility: str,
    suite: str,
    expected: str,
    errors: list[str],
    position: int,
) -> dict[str, Any]:
    case = make_case(
        legacy_case_id,
        "boundary_regression",
        expected,
        errors,
        suite.replace("-", " "),
        responsibility,
        "h2epr_contract_boundary_validator",
        semantic_condition_id=semantic_condition_id,
        mutation_descriptor=bounded_helper_descriptor(
            helper=semantic_condition_id,
            parameters={},
            validator_subject="h2epr_contract_boundary_validator",
            expected_result=expected,
            base_locator=f"bounded-boundary-probe:{semantic_condition_id}",
        ),
    )
    case["suite"] = suite
    case["legacy_position"] = position
    return case


def build_baseline_adversarial_cases(start: int = 297) -> list[dict[str, Any]]:
    """Recreate the original eleven independent adversarial controls."""
    bases = fixture_bases()
    definitions: list[tuple[str, str, str, str, list[str]]] = []

    chain = copy.deepcopy(bases["typed-chain"])
    chain["run_manifest"]["artifact_identity"]["parent_artifacts"][0][
        "artifact_id"
    ] = "runtime.redirected"
    chain["run_manifest"]["manifest_sha256"] = manifest_hash(chain["run_manifest"])
    definitions.append(
        ("CONTROL-B1-PARENT-ID",
            "manifest-runtime-parent-id-mismatch-rejected",
            "trace_and_identity",
            "reject",
            artifact_chain_errors(chain))
    )

    communication = copy.deepcopy(bases["communications"])
    communication["attempts"][0]["sent"]["route_id"] = "route.redirected"
    definitions.append(
        (
            "CONTROL-B2-ROUTE",
            "communication-route-mismatch-rejected",
            "communication",
            "reject",
            communication_errors(communication),
        )
    )
    definitions.append(
        (
            "CONTROL-B3-AUDIT-ONLY", "audit-only-trace-rejected-by-compiler-gate", "trace_and_identity",
            "reject",
            trace_eligibility_errors(copy.deepcopy(bases["auditable-invalid-trace"])),
        )
    )

    graph = copy.deepcopy(bases["graph"])
    graph["edges"][0]["target_node_id"] = "generated.node.missing"
    definitions.append(
        (
            "CONTROL-B4-DANGLING-ENDPOINT", "generated-graph-dangling-endpoint-rejected", "trace_and_identity",
            "reject",
            graph_errors(reseal_graph(graph)),
        )
    )

    attestation = copy.deepcopy(bases["projection-attestation"])
    attestation["producer_identity"]["prior_target_full_draft_exposure"] = True
    attestation["attestation_sha256"] = projection_attestation_hash(attestation)
    definitions.append(
        (
            "CONTROL-B5-CONTAMINATED-PRODUCER", "contaminated-prefix-producer-rejected", "trace_and_identity",
            "reject",
            projection_attestation_errors(attestation),
        )
    )

    communication = copy.deepcopy(bases["communications"])
    attempt = communication["attempts"][0]
    for value in (attempt["intent"], attempt["disposition"], attempt["sent"]):
        value["recipient_ids"].append("synthetic.actor.second_recipient")
    definitions.append(
        (
            "ESCAPE-B2-PARTIAL-MULTIRECIPIENT-DELIVERY",
                "multi-recipient-partial-delivery-rejected",
                "communication",
            "reject",
            communication_errors(communication),
        )
    )

    trace = copy.deepcopy(bases["trace"])
    extra = copy.deepcopy(trace["records"][0])
    extra.update({"trace_id": "trace.record.after.tick.seal", "sequence_in_tick": 99})
    extra["simulation_time"].update(
        {"lower": "2000-01-02T23:59:59Z", "upper": "2000-01-02T23:59:59Z"}
    )
    trace["records"].insert(-1, extra)
    trace = reseal_trace(trace)
    definitions.append(
        (
            "ESCAPE-B3-RECORD-AFTER-TICK-SEAL", "scientific-record-after-tick-seal-rejected", "trace_and_identity",
            "reject",
            schema_errors("simulation_trace.schema.json", trace)
            + trace_eligibility_errors(trace),
        )
    )

    trace = copy.deepcopy(bases["trace"])
    extra = copy.deepcopy(trace["records"][0])
    extra.update(
        {
            "trace_id": "trace.record.unsealed.tick.1",
            "logical_tick": 1,
            "sequence_in_tick": 0,
        }
    )
    extra["simulation_time"].update(
        {"lower": "2000-01-02T23:59:59Z", "upper": "2000-01-02T23:59:59Z"}
    )
    trace["records"].insert(-1, extra)
    trace = reseal_trace(trace)
    definitions.append(
        (
            "ESCAPE-B3-UNSEALED-LOGICAL-TICK", "scientific-tick-without-seal-rejected", "trace_and_identity",
            "reject",
            schema_errors("simulation_trace.schema.json", trace)
            + trace_eligibility_errors(trace),
        )
    )

    chain = copy.deepcopy(bases["typed-chain"])
    source_trace = chain["simulation_trace"]
    source_trace["records"][1]["trace_id"] = source_trace["records"][0]["trace_id"]
    for item in [
        *chain["generated_epg"]["nodes"],
        *chain["generated_epg"]["edges"],
        *chain["generated_epg"]["trace_provenance_index"],
    ]:
        item["trace_refs"] = list(
            dict.fromkeys(
                source_trace["records"][0]["trace_id"]
                if ref == "trace.record.001"
                else ref
                for ref in item["trace_refs"]
            )
        )
    chain = reseal_graph_and_evaluation_from_trace(chain)
    definitions.append(
        (
            "ESCAPE-B4-DUPLICATE-TRACE-ID", "duplicate-trace-id-rejected-by-chain-closure", "communication",
            "reject",
            schema_errors("simulation_trace.schema.json", chain["simulation_trace"])
            + schema_errors("generated_epg.schema.json", chain["generated_epg"])
            + artifact_chain_errors(chain),
        )
    )

    trace = copy.deepcopy(bases["trace"])
    trace["records"][0]["parent_trace_ids"] = ["trace.record.missing.parent"]
    trace = reseal_trace(trace)
    definitions.append(
        (
            "ESCAPE-B3-DANGLING-PARENT-TRACE-REF", "dangling-parent-trace-reference-rejected", "trace_and_identity",
            "reject",
            schema_errors("simulation_trace.schema.json", trace)
            + trace_integrity_errors(trace),
        )
    )

    binding_errors = (
        []
        if bases["strict-runtime"]["source_construction_bundle"].get("artifact_id")
        != bases["strict-bundle"]["artifact_identity"].get("artifact_id")
        else ["CONSTRUCTION_OBJECT_IS_BOUND"]
    )
    definitions.append(
        ("ESCAPE-B1-CONSTRUCTION-OBJECT-NOT-BOUND",
            "runtime-construction-object-binding-required",
            "construction",
            "reject",
            binding_errors)
    )
    return [
        _probe(
            case_id,
            semantic_condition_id,
            responsibility,
            "baseline-adversarial",
            expected,
            errors,
            start + index,
        )
        for index, (
            case_id,
            semantic_condition_id,
            responsibility,
            expected,
            errors,
        ) in enumerate(definitions)
    ]


def build_communication_boundary_cases(start: int = 308) -> list[dict[str, Any]]:
    """Recreate three acceptance controls and five closed escape regressions."""
    bases = fixture_bases()
    anchor_request = bases["anchor-request"]
    anchor_context = bases["anchor-context"]
    allowlist = bases["anchor-allowlist"]

    def anchor_errors(value: dict[str, Any]) -> list[str]:
        return anchored_chain_request_errors(
            anchor_request,
            value,
            anchor_context,
            allowlist,
            SYNTHETIC / "external_construction_anchor_context.json",
            SYNTHETIC / "construction_anchor_allowlist.json",
        )

    definitions: list[tuple[str, str, str, str, list[str]]] = [
        (
            "CONTROL-R4-VALID-EXTERNALLY-ANCHORED-CHAIN",
                "communication-boundary-valid-externally-anchored-chain",
                "construction",
            "accept",
            anchor_errors(copy.deepcopy(bases["typed-chain"])),
        ),
        (
            "CONTROL-R4-VALID-APPEND-ONLY-COMMUNICATION",
                "communication-boundary-valid-append-only-communication",
                "communication",
            "accept",
            communication_history_errors(
                copy.deepcopy(bases["communication-closed"])
            ),
        ),
        (
            "CONTROL-R4-VALID-MULTI-TICK-TRACE", "communication-boundary-valid-multi-tick-trace", "trace_and_identity",
            "accept",
            run_seal_coordinate_errors(copy.deepcopy(bases["multi-tick-trace"])),
        ),
    ]

    chain = copy.deepcopy(bases["typed-chain"])
    construction = chain["construction_bundle"]
    construction["artifact_identity"]["artifact_id"] = (
        "construction.adversarial.self.anchored"
    )
    construction["construction_seal"]["artifact_id"] = (
        "construction.adversarial.self.anchored"
    )
    construction["initial_world_state"]["entities"].append(
        "synthetic.actor.adversarial"
    )
    chain["runtime_bundle"]["initial_world_state"]["entities"].append(
        "synthetic.actor.adversarial"
    )
    chain = reseal_chain_from_construction(chain)
    chain["chain_anchor"] = construction_lineage_ref(chain["construction_bundle"])
    definitions.append(
        (
            "ESCAPE-R3-B1-SELF-ASSERTED-ANCHOR", "communication-boundary-self-asserted-anchor", "construction",
            "reject",
            anchor_errors(chain),
        )
    )

    communication = copy.deepcopy(bases["communication-unresolved"])
    communication["run_seal_closure"].update(
        {
            "closure_status": "closed",
            "compiler_evaluator_eligible": True,
            "unresolved_message_intent_ids": [],
            "unresolved_recipient_ids": [],
        }
    )
    definitions.append(
        (
            "ESCAPE-R3-B2-DELAYED-UNRESOLVED-AT-RUN-SEAL",
                "communication-boundary-delayed-unresolved-at-run-seal",
                "communication",
            "reject",
            communication_history_errors(communication),
        )
    )
    communication = copy.deepcopy(bases["communication-closed"])
    communication["attempts"][1]["disposition_history"][-1][
        "duplicate_of_message_intent_id"
    ] = communication["attempts"][1]["intent"]["message_intent_id"]
    definitions.append(
        (
            "ESCAPE-R3-B2-DUPLICATE-SELF-REFERENCE", "communication-boundary-duplicate-self-reference", "communication",
            "reject",
            communication_history_errors(communication),
        )
    )
    communication = copy.deepcopy(bases["communication-closed"])
    communication["attempts"][0]["sent"]["canonical_content_sha256"] = "a" * 64
    definitions.append(
        (
            "ESCAPE-R3-B2-UNBOUND-CONTENT-HASH", "communication-boundary-unbound-content-hash", "communication",
            "reject",
            communication_history_errors(communication),
        )
    )
    trace = copy.deepcopy(bases["single-tick-trace"])
    trace["records"][-1]["sequence_in_tick"] = 99
    definitions.append(
        (
            "ESCAPE-R3-B3-RUN-SEAL-SEQUENCE-GAP", "communication-boundary-run-seal-sequence-gap", "trace_and_identity",
            "reject",
            run_seal_coordinate_errors(reseal_trace(trace)),
        )
    )
    return [
        _probe(
            case_id,
            semantic_condition_id,
            responsibility,
            "communication-boundary",
            expected,
            errors,
            start + index,
        )
        for index, (
            case_id,
            semantic_condition_id,
            responsibility,
            expected,
            errors,
        ) in enumerate(definitions)
    ]


def build_narrow_correction_boundary_cases(
    start: int = 316,
) -> list[dict[str, Any]]:
    """Recreate the four linked-run transport boundary outcomes."""
    controls = transport_controls()
    definitions = (
        ("ESCAPE-R4-B2-UNBOUND-RUN-SEAL-TRACE-ID",
            "transport-boundary-unbound-run-seal-trace-id",
            "communication",
            "reject",
            "unbound-run-seal"),
        ("ESCAPE-R4-B2-DELIVERED-BEFORE-SENT",
            "transport-boundary-delivered-before-sent",
            "communication",
            "reject",
            "delivered-before-sent"),
        (
            "ESCAPE-R4-B2-CONSUMABLE-WITHOUT-LATER-TICK-OR-ROUND",
                "transport-boundary-consumable-without-later-tick-or-round",
                "communication",
            "reject",
            "consumable-without-later",
        ),
        (
            "FALSE-REJECT-R4-B2-TWO-UNRESOLVED-SAME-RECIPIENT-SET",
                "transport-boundary-two-unresolved-same-recipient-set",
                "communication",
            "accept",
            "linked-shared-unresolved",
        ),
    )
    return [
        _probe(
            case_id,
            semantic_condition_id,
            responsibility,
            "communication-narrow-correction-boundary",
            expected,
            schema_errors("linked_communication_run.schema.json", controls[key])
            + linked_run_transport_errors(controls[key]),
            start + index,
        )
        for index, (
            case_id,
            semantic_condition_id,
            responsibility,
            expected,
            key,
        ) in enumerate(definitions)
    ]


def build_run_global_identity_closure_cases(
    start: int = 320,
) -> list[dict[str, Any]]:
    """Recreate the twenty complete linked-run identity closure controls."""
    controls = transport_controls()
    definitions: list[tuple[str, str, str, str, dict[str, Any]]] = [
        ("CONTROL-R5-SUP-VALID-LINKED-CLOSED-RUN",
            "run-closure-boundary-valid-linked-closed-run",
            "trace_and_identity",
            "accept",
            controls["linked-closed"]),
        (
            "FALSE-REJECT-R4-B2-TWO-UNRESOLVED-SAME-RECIPIENT-SET",
                "run-closure-boundary-two-unresolved-same-recipient-set",
                "communication",
            "accept",
            controls["linked-shared-unresolved"],
        ),
        (
            "CONTROL-R5-SUP-VALID-TWO-DECISION-COMPLETE-RUN",
                "run-closure-boundary-valid-two-decision-complete-run",
                "trace_and_identity",
            "accept",
            controls["two-decision"],
        ),
        ("ESCAPE-R4-B2-UNBOUND-RUN-SEAL-TRACE-ID",
            "run-closure-boundary-unbound-run-seal-trace-id",
            "communication",
            "reject",
            controls["unbound-run-seal"]),
        ("ESCAPE-R4-B2-DELIVERED-BEFORE-SENT",
            "run-closure-boundary-delivered-before-sent",
            "communication",
            "reject",
            controls["delivered-before-sent"]),
        (
            "ESCAPE-R4-B2-CONSUMABLE-WITHOUT-LATER-TICK-OR-ROUND",
                "run-closure-boundary-consumable-without-later-tick-or-round",
                "communication",
            "reject",
            controls["consumable-without-later"],
        ),
    ]

    value = copy.deepcopy(controls["linked-closed"])
    value["run_seal_closure"]["run_seal_trace_id"] = value["trace"]["records"][0][
        "trace_id"
    ]
    definitions.append(("COMPANION-R5-B2-RUN-SEAL-ID-WRONG-TYPE",
        "run-closure-boundary-run-seal-id-wrong-type",
        "communication",
        "reject",
        value))
    value = copy.deepcopy(controls["linked-closed"])
    value["run_seal_closure"]["run_id"] = "run.synthetic.wrong"
    definitions.append(("COMPANION-R5-B2-RUN-SEAL-WRONG-RUN",
        "run-closure-boundary-run-seal-wrong-run",
        "communication",
        "reject",
        value))
    value = copy.deepcopy(controls["linked-closed"])
    value["run_seal_closure"]["logical_tick"] = 1
    definitions.append(("COMPANION-R5-B2-RUN-SEAL-WRONG-TICK",
        "run-closure-boundary-run-seal-wrong-tick",
        "communication",
        "reject",
        value))
    value = copy.deepcopy(controls["linked-closed"])
    index = next(
        i
        for i, item in enumerate(value["trace"]["records"])
        if item["record_type"] == "message_intent_created"
    )
    value["trace"]["records"].pop(index)
    definitions.append(
        (
            "COMPANION-R5-B2-MISSING-TRACE-INTENT-POPULATION",
                "run-closure-boundary-missing-trace-intent-population",
                "communication",
            "reject",
            rechain_and_reseal(value),
        )
    )
    value = copy.deepcopy(controls["linked-closed"])
    intent = value["decision_communication_histories"][0]["attempts"][0]["intent"]
    intent["earliest_delivery_time"] = exact_interval("1907-10-14T09:03:00Z")
    next(
        item
        for item in value["trace"]["records"]
        if item["record_type"] == "message_intent_created"
        and item["payload"]["message_intent_id"] == intent["message_intent_id"]
    )["payload"] = copy.deepcopy(intent)
    value["trace"] = reseal_trace(value["trace"])
    definitions.append(("COMPANION-R5-B2-DELIVERED-BEFORE-EARLIEST",
        "run-closure-boundary-delivered-before-earliest",
        "communication",
        "reject",
        value))
    value = copy.deepcopy(controls["linked-closed"])
    sent = value["decision_communication_histories"][0]["attempts"][0]["sent"]
    sent["delivery_due_at"] = exact_interval("1907-10-14T09:03:00Z")
    next(
        item
        for item in value["trace"]["records"]
        if item["record_type"] == "message_sent"
        and item["payload"]["message_id"] == sent["message_id"]
    )["payload"] = copy.deepcopy(sent)
    value["trace"] = reseal_trace(value["trace"])
    definitions.append(("COMPANION-R5-B2-DELIVERED-BEFORE-DUE",
        "run-closure-boundary-delivered-before-due",
        "communication",
        "reject",
        value))
    definitions.append(
        (
            "COMPANION-R5-B2-CONSUMABLE-SAME-TICK-ONLY",
                "run-closure-boundary-consumable-same-tick-only",
                "communication",
            "reject",
            update_terminal_and_reseal(
                controls["linked-closed"],
                lambda terminal: terminal.__setitem__(
                    "first_consumable_logical_tick", terminal["delivered_logical_tick"]
                ),
            ),
        )
    )
    definitions.append(
        (
            "COMPANION-R5-B2-CONSUMABLE-SAME-ROUND-ONLY",
                "run-closure-boundary-consumable-same-round-only",
                "communication",
            "reject",
            update_terminal_and_reseal(
                controls["linked-closed"],
                lambda terminal: terminal.__setitem__(
                    "first_consumable_masim_round", terminal["delivery_masim_round"]
                ),
            ),
        )
    )
    value = copy.deepcopy(controls["linked-shared-unresolved"])
    value["run_seal_closure"]["unresolved_recipient_ids"].append(
        value["run_seal_closure"]["unresolved_recipient_ids"][0]
    )
    definitions.append(
        ("COMPANION-R5-B2-DUPLICATE-RECIPIENT-IN-UNIQUE-SET",
            "run-closure-boundary-duplicate-recipient-in-unique-set",
            "communication",
            "reject",
            value)
    )
    definitions.extend(
        (
            (
                "ESCAPE-R5-B2-DUPLICATE-DECISION-ID-ACROSS-HISTORIES",
                    "run-closure-boundary-duplicate-decision-id-across-histories",
                    "communication",
                "reject",
                controls["duplicate-decision"],
            ),
            (
                "ESCAPE-R5-B2-DUPLICATE-INTENT-ID-ACROSS-HISTORIES",
                    "run-closure-boundary-duplicate-intent-id-across-histories",
                    "communication",
                "reject",
                controls["duplicate-intent"],
            ),
            (
                "COMPANION-R6-B2-DUPLICATE-DISPOSITION-ID-ACROSS-HISTORIES",
                    "run-closure-boundary-duplicate-disposition-id-across-histories",
                    "communication",
                "reject",
                controls["duplicate-disposition"],
            ),
            (
                "COMPANION-R6-B2-DUPLICATE-SENT-MESSAGE-ID-ACROSS-HISTORIES",
                    "run-closure-boundary-duplicate-sent-message-id-across-histories",
                    "communication",
                "reject",
                controls["duplicate-message"],
            ),
            (
                "COMPANION-R6-B2-DUPLICATE-TERMINAL-ID-ACROSS-HISTORIES",
                    "run-closure-boundary-duplicate-terminal-id-across-histories",
                    "communication",
                "reject",
                controls["duplicate-terminal"],
            ),
        )
    )
    if len(definitions) != 20:
        raise RuntimeError(f"run-global closure count mismatch: {len(definitions)}")
    return [
        _probe(
            case_id,
            semantic_condition_id,
            responsibility,
            "run-global-identity-closure",
            expected,
            schema_errors("linked_communication_run.schema.json", value)
            + linked_run_global_identity_errors(value),
            start + index,
        )
        for index, (
            case_id,
            semantic_condition_id,
            responsibility,
            expected,
            value,
        ) in enumerate(definitions)
    ]


def _duplicate_latest_against_nonlatest(control: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(control)
    first, second = value["decision_communication_histories"]
    duplicate_id = first["attempts"][0]["disposition_history"][0][
        "communication_disposition_id"
    ]
    attempt = second["attempts"][0]
    accepted = attempt["disposition_history"][-1]
    old_id = accepted["communication_disposition_id"]
    accepted["communication_disposition_id"] = duplicate_id
    attempt["sent"]["communication_disposition_id"] = duplicate_id
    attempt["terminal"]["communication_disposition_id"] = duplicate_id
    value["run_seal_closure"]["latest_disposition_ids"][1] = duplicate_id
    update_trace_payload(
        value,
        "communication_disposition_recorded",
        "communication_disposition_id",
        old_id,
        accepted,
    )
    update_trace_payload(
        value,
        "message_sent",
        "message_id",
        attempt["sent"]["message_id"],
        attempt["sent"],
    )
    update_trace_payload(
        value,
        "message_delivered",
        "delivery_id",
        attempt["terminal"]["delivery_id"],
        attempt["terminal"],
    )
    return rechain_and_reseal(value)


def _duplicate_cross_kind_terminal(control: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(control)
    first, second = value["decision_communication_histories"]
    duplicate_id = first["attempts"][0]["terminal"]["delivery_id"]
    attempt = second["attempts"][0]
    sent = attempt["sent"]
    old_terminal = attempt["terminal"]
    old_delivery_id = old_terminal["delivery_id"]
    expired = {
        "expiration_id": duplicate_id,
        "message_id": sent["message_id"],
        "message_intent_id": sent["message_intent_id"],
        "communication_disposition_id": sent["communication_disposition_id"],
        "run_id": sent["run_id"],
        "sender_id": sent["sender_id"],
        "recipient_ids": copy.deepcopy(sent["recipient_ids"]),
        "route_id": sent["route_id"],
        "message_sent_trace_ref": old_terminal["message_sent_trace_ref"],
        "expired_logical_tick": old_terminal["delivered_logical_tick"],
        "expired_at": copy.deepcopy(sent["expiry_time"]),
        "reason_code": "delivery_due_after_expiry",
    }
    attempt["terminal"] = expired
    value["run_seal_closure"]["terminal_transport_ids"] = [
        duplicate_id,
        duplicate_id,
    ]
    record = next(
        item
        for item in value["trace"]["records"]
        if item.get("record_type") == "message_delivered"
        and item.get("payload", {}).get("delivery_id") == old_delivery_id
    )
    record["record_type"] = "message_expired"
    record["payload"] = copy.deepcopy(expired)
    return rechain_and_reseal(value)


def build_run_global_identity_independent_cases(
    start: int = 340,
) -> list[dict[str, Any]]:
    """Recreate the five independent identity-collision probes."""
    controls = transport_controls()
    definitions = (
        (
            "CONTROL-R6-INDEPENDENT-TWO-CLOSED-HISTORIES",
                "run-identity-boundary-independent-two-closed-histories",
                "trace_and_identity",
            "accept",
            controls["two-closed"],
        ),
        (
            "CONTROL-R6-INDEPENDENT-TWO-UNRESOLVED-HISTORIES",
                "run-identity-boundary-independent-two-unresolved-histories",
                "communication",
            "accept",
            controls["two-decision"],
        ),
        (
            "ADVERSARIAL-R6-DISPOSITION-COLLISION-NONLATEST-TO-LATEST",
                "run-identity-boundary-disposition-collision-nonlatest-to-latest",
                "communication",
            "reject",
            _duplicate_latest_against_nonlatest(controls["two-closed"]),
        ),
        (
            "ADVERSARIAL-R6-CROSS-KIND-DELIVERY-EXPIRATION-COLLISION",
                "run-identity-boundary-cross-kind-delivery-expiration-collision",
                "communication",
            "reject",
            _duplicate_cross_kind_terminal(controls["two-closed"]),
        ),
    )
    cases = [
        _probe(
            case_id,
            semantic_condition_id,
            responsibility,
            "run-global-identity-independent",
            expected,
            schema_errors("linked_communication_run.schema.json", value)
            + linked_run_global_identity_errors(value),
            start + index,
        )
        for index, (
            case_id,
            semantic_condition_id,
            responsibility,
            expected,
            value,
        ) in enumerate(definitions)
    ]
    duplicates = duplicate_values(
        ["stable.b", "stable.a", "stable.b", "stable.a", "stable.c"]
    )
    errors = (
        []
        if duplicates == ["stable.a", "stable.b"]
        else [f"DUPLICATE_ORDER_MISMATCH:{duplicates}"]
    )
    cases.append(
        _probe(
            "UNIT-R6-MULTIPLE-DUPLICATES-DETERMINISTIC",
            "run-identity-boundary-multiple-duplicates-deterministic",
            "communication",
            "run-global-identity-independent",
            "accept",
            errors,
            start + 4,
        )
    )
    return cases


def build_cases() -> list[dict[str, Any]]:
    """Return the exact 48 cross-object boundary regression cases."""
    cases = [
        *build_baseline_adversarial_cases(),
        *build_communication_boundary_cases(),
        *build_narrow_correction_boundary_cases(),
        *build_run_global_identity_closure_cases(),
        *build_run_global_identity_independent_cases(),
    ]
    if len(cases) != 48:
        raise RuntimeError(f"boundary regression count mismatch: {len(cases)}")
    return cases
