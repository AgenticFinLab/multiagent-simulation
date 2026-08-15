from __future__ import annotations

from h2epr.runtime.detectors import P007Detector, VOCABULARY


OWNERS = ("a", "b")


def _state(liquid_a=5000, liquid_b=5000, status_a="open"):
    return {"actors": {"a": {"liquid_resource_bp": liquid_a, "withdrawal_pressure_bp": 0, "operational_status": status_a}, "b": {"liquid_resource_bp": liquid_b, "withdrawal_pressure_bp": 0, "operational_status": "open"}}}


def test_exact_generated_only_vocabulary() -> None:
    assert VOCABULARY == ("resource_withdrawal", "resource_support", "operational_transition", "resource_stress", "coordination_transfer", "contagion_transition", "local_stabilization", "local_failure")


def test_stress_and_contagion_detection_use_exposure() -> None:
    detector = P007Detector([("a", "b")], OWNERS)
    annotations, stage = detector.detect(1, _state(2500, 2500), [], [], [])
    assert {item["annotation_type"] for item in annotations} >= {"resource_stress", "contagion_transition"}
    assert stage == "stress_onset"


def test_two_sealed_stable_ticks_trigger_local_stabilization() -> None:
    detector = P007Detector([("a", "b")], OWNERS)
    assert "local_stabilization" not in {item["annotation_type"] for item in detector.detect(1, _state(), [], [], [])[0]}
    annotations, stage = detector.detect(2, _state(), [], [], [])
    assert "local_stabilization" in {item["annotation_type"] for item in annotations}
    assert stage == "local_stabilization"


def test_failure_precedence_beats_stress_onset() -> None:
    detector = P007Detector([("a", "b")], OWNERS)
    annotations, stage = detector.detect(1, _state(0, 5000, "closed"), [], [], [])
    assert "local_failure" in {item["annotation_type"] for item in annotations}
    assert stage == "local_failure"
