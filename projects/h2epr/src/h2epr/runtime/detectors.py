"""Generated-only P007 runtime annotation detectors."""

from __future__ import annotations

from typing import Any, Iterable, Mapping


VOCABULARY = (
    "resource_withdrawal",
    "resource_support",
    "operational_transition",
    "resource_stress",
    "coordination_transfer",
    "contagion_transition",
    "local_stabilization",
    "local_failure",
)
STAGE_PRECEDENCE = ("local_failure", "local_stabilization", "response_coordination", "stress_onset")


class P007Detector:
    def __init__(self, exposure_pairs: Iterable[tuple[str, str]], active_owners: Iterable[str]) -> None:
        self.exposures = {tuple(sorted(pair)) for pair in exposure_pairs}
        self.active_owners = tuple(sorted(active_owners))
        self._stress_ticks: dict[str, int] = {}
        self._stable_ticks = 0
        self._stage_first_hits: set[str] = set()

    def detect(
        self,
        logical_tick: int,
        state: Mapping[str, Any],
        dispositions: Iterable[Mapping[str, Any]],
        deltas: Iterable[Mapping[str, Any]],
        unresolved_ids: Iterable[str],
    ) -> tuple[list[dict[str, Any]], str | None]:
        annotations: list[dict[str, Any]] = []
        delta_rows = list(deltas)
        disposition_rows = list(dispositions)
        accepted_intents = {item["intent_id"] for item in disposition_rows if item["status"] == "accepted"}
        for delta in delta_rows:
            if delta["field_name"] == "liquid_resource_bp" and delta["after"] < delta["before"] and delta["delta_class"] == "withdrawal_sink":
                annotations.append(self._annotation("resource_withdrawal", logical_tick, [delta["source_intent_id"]], [delta["entity_id"]]))
            if delta["field_name"] == "liquid_resource_bp" and delta["after"] > delta["before"] and delta["delta_class"] == "support_transfer":
                annotations.append(self._annotation("resource_support", logical_tick, [delta["source_intent_id"]], [delta["entity_id"]]))
                annotations.append(self._annotation("coordination_transfer", logical_tick, [delta["source_intent_id"]], [delta["entity_id"]]))
            if delta["field_name"] == "operational_status":
                annotations.append(self._annotation("operational_transition", logical_tick, [delta["source_intent_id"]], [delta["entity_id"]]))
        stressed = []
        failed = []
        for actor_id in self.active_owners:
            actor = state["actors"][actor_id]
            if actor["liquid_resource_bp"] <= 2500 or actor["withdrawal_pressure_bp"] >= 2500:
                stressed.append(actor_id)
                self._stress_ticks[actor_id] = logical_tick
                annotations.append(self._annotation("resource_stress", logical_tick, [], [actor_id]))
            if actor["operational_status"] == "closed" or (actor["liquid_resource_bp"] == 0 and actor.get("latest_support_terminal") in {"rejected", "failed"}):
                failed.append(actor_id)
                annotations.append(self._annotation("local_failure", logical_tick, [], [actor_id]))
        contagious = sorted(
            {actor for actor in stressed for other in stressed if actor != other and tuple(sorted((actor, other))) in self.exposures}
        )
        if len(contagious) >= 2:
            annotations.append(self._annotation("contagion_transition", logical_tick, [], contagious))
        stable = all(state["actors"][actor]["liquid_resource_bp"] >= 4000 for actor in self.active_owners) and not tuple(unresolved_ids)
        self._stable_ticks = self._stable_ticks + 1 if stable else 0
        if self._stable_ticks >= 2:
            annotations.append(self._annotation("local_stabilization", logical_tick, [], list(self.active_owners)))

        kinds = {item["annotation_type"] for item in annotations}
        response_present = bool({"resource_support", "coordination_transfer", "operational_transition"}.intersection(kinds)) or any(
            item["status"] == "accepted" and item.get("action_type") in {"request_support", "coordinate_collective_action"}
            for item in disposition_rows
        )
        candidates = []
        if "local_failure" in kinds:
            candidates.append("local_failure")
        if "local_stabilization" in kinds:
            candidates.append("local_stabilization")
        if response_present:
            candidates.append("response_coordination")
        if {"resource_withdrawal", "resource_stress"}.intersection(kinds):
            candidates.append("stress_onset")
        stage = next((name for name in STAGE_PRECEDENCE if name in candidates and name not in self._stage_first_hits), None)
        if stage:
            self._stage_first_hits.add(stage)
        return annotations, stage

    @staticmethod
    def _annotation(kind: str, tick: int, intent_ids: list[str], participant_ids: list[str]) -> dict[str, Any]:
        if kind not in VOCABULARY:
            raise ValueError("unknown_p007_annotation")
        return {
            "annotation_type": kind,
            "logical_tick": tick,
            "source_intent_ids": sorted(set(intent_ids)),
            "participant_ids": sorted(set(participant_ids)),
            "provenance": "generated_simulation_trace_only",
        }
