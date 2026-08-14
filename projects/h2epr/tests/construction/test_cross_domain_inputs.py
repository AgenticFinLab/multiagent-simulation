from __future__ import annotations

import hashlib
from pathlib import Path

from h2epr.construction import (
    ArchitectureGenericIdentity,
    ArchitectureSourceManifest,
    Availability,
    EndpointStatus,
    ReviewState,
    SourceAdapter,
    SourceDescriptor,
    SourceKind,
    parse_architecture_generic,
)


REPO_ROOT = Path(__file__).parents[4]
INPUT_ROOT = REPO_ROOT / "data/h2epr/development_samples_v1"
EVENT_HASHES = {
    "H2EPR-0170": {
        "event_spec.json": "c74f9bb20e1a8a6815c2c3a0657b2b5e881a606737a0438f6dd8b3caad173690",
        "frozen_evidence.json": "7f5e4b7d636615e3f9cd3da292caa8ce3bffc768e7ddc9d994a370f89def5c4a",
        "draft_epg.json": "ddfb541247a91173784961a2586780cf476cd2edebd49c209d54de0ce284913e",
    },
    "H2EPR-0196": {
        "event_spec.json": "3c3bb90db96416d542bdf5615660ebe535c15ea638dbc6020127e9c78a36b4f1",
        "frozen_evidence.json": "4167bbf09a0c54341582c55b8c923f3ab016e3657875614969a09bdb9d2f0a2a",
        "draft_epg.json": "d3b8ad44ae709318950c315fe16892981ee01bdfc734848c4af08be63440ca5c",
    },
    "H2EPR-0288": {
        "event_spec.json": "a9f262b9d48a1b594b8a65f5ebdd39184996b34423be3d432390a3917bad1a52",
        "frozen_evidence.json": "c27f6f36dcb008c3314e458e9d4c4fa714a3b1a7ba4150b13e0e33d94a7f6bb3",
        "draft_epg.json": "4f98abfe0432fa1f41b6494e5966622f92ecf163584f5a8023fa5c2af8c9d8a3",
    },
    "H2EPR-0481": {
        "event_spec.json": "d61821a6b9042b7645b215300bce2ebab5e3933eae17b00421352a81121aed33",
        "frozen_evidence.json": "c57db941c601de94e0f8826bd74537b2d4b4bc08c94d1ea3d7cec249b1a3c325",
        "draft_epg.json": "9883cae0a41d1345de43efa4658b8d4162fdf5843dadf94da36be5a6e9a26254",
    },
    "H2EPR-0551": {
        "event_spec.json": "ff668a0b27fcca9146b845fd520219878d42d513a171fe88bdfc6e99f92f033f",
        "frozen_evidence.json": "c3f122bb3058be45e07d8a3620b28b0b7df352df92cf8c362fed8bb9ceb006d5",
        "draft_epg.json": "869488ce843b661328cc9e0c26ceabec4201cb5445aec8c10f80eba0aab2621f",
    },
    "H2EPR-0616": {
        "event_spec.json": "5a69486c0c3cff4dab019e43a75b9f959ebb47e3b52b17241bb637dd0cdfbbfb",
        "frozen_evidence.json": "ea356fc9f0f7dfede9e7415f61d144e8ba13e61c3ad5647318abe7b5449f5e7c",
        "draft_epg.json": "aa6b725305e2fbcc101ca5189af84535a58338f6c5e28fbe7b3e6787723ee54c",
    },
    "H2EPR-0892": {
        "event_spec.json": "30ef79f0b36d35dbc154dc8f89ba854230a823f397954f7f945fc29751a4c85a",
        "frozen_evidence.json": "b101a619571ebad60130ce0abf9022c24d4a14c858aefe5e53811ba1fc234d55",
        "draft_epg.json": "084f224e9e2424073ebe94c83a5882ca1e9efe6127f8d239346a6592e415708b",
    },
    "H2EPR-1031": {
        "event_spec.json": "9904a05984540a09668b76db69790940dc9819a3c936ea8a5270b58c2a7239fd",
        "frozen_evidence.json": "04050597abe437e1cc23c1f548e57aad9fc536d0d4d04bebc95536ad79430cda",
        "draft_epg.json": "4eae92aee3d5f3d1e37e769ccce708fae92a549d29c9e907907ae16176469e6c",
    },
}
COMMON_HASHES = {
    "source_identity.json": "adaac1f4e6c1dc087acabc3631d9dec5a48c0d0b05d3db1a23d847723e6b1566",
    "sample_manifest.csv": "e8145857b17b5efc1bdfa8aeeaf097d1db21142b8dd5519ecfa93e74908d62bc",
}
KINDS = {
    "event_spec.json": SourceKind.EVENT_SPEC,
    "frozen_evidence.json": SourceKind.FROZEN_EVIDENCE,
    "draft_epg.json": SourceKind.DRAFT_EPG,
}


def explicit_descriptors() -> tuple[SourceDescriptor, ...]:
    result = [
        SourceDescriptor(
            logical_source_id="common-source-identity",
            source_kind=SourceKind.SOURCE_IDENTITY,
            relative_path="source_identity.json",
            expected_sha256=COMMON_HASHES["source_identity.json"],
            availability=Availability.CONSTRUCTION_ONLY,
            review_state=ReviewState.REVIEWED,
        ),
        SourceDescriptor(
            logical_source_id="common-sample-manifest",
            source_kind=SourceKind.SAMPLE_MANIFEST,
            relative_path="sample_manifest.csv",
            expected_sha256=COMMON_HASHES["sample_manifest.csv"],
            availability=Availability.CONSTRUCTION_ONLY,
            review_state=ReviewState.REVIEWED,
        ),
    ]
    for event_id, files in EVENT_HASHES.items():
        for basename, sha256 in files.items():
            result.append(
                SourceDescriptor(
                    logical_source_id=f"{event_id.lower()}-{basename[:-5].replace('_', '-')}",
                    source_kind=KINDS[basename],
                    relative_path=f"events/{event_id}/{basename}",
                    expected_sha256=sha256,
                    availability=Availability.CONSTRUCTION_ONLY,
                    review_state=ReviewState.REVIEWED,
                )
            )
    return tuple(result)


def test_all_eight_authorized_events_parse_through_generic_entry() -> None:
    descriptors = explicit_descriptors()
    before = {item.relative_path: hashlib.sha256((INPUT_ROOT / item.relative_path).read_bytes()).hexdigest() for item in descriptors}
    loaded = SourceAdapter(INPUT_ROOT).read_architecture(ArchitectureSourceManifest(descriptors))
    ir = parse_architecture_generic(ArchitectureGenericIdentity("g1-architecture-generic"), loaded)
    after = {item.relative_path: hashlib.sha256((INPUT_ROOT / item.relative_path).read_bytes()).hexdigest() for item in descriptors}
    assert before == after == {item.relative_path: item.expected_sha256 for item in descriptors}
    assert len(ir.sources) == 26
    assert {source.source_kind for source in ir.sources} >= {
        SourceKind.EVENT_SPEC, SourceKind.FROZEN_EVIDENCE, SourceKind.DRAFT_EPG
    }
    assert len(ir.structures) > 0
    assert len(ir.entities) > 0
    assert len(ir.actions) > 0
    assert ir.identity.construction_state == "architecture_generic"
    assert ir.identity.protocol_eligibility == "architecture_demo_only"


def test_0288_and_0616_have_typed_pointer_time_and_endpoint_projections() -> None:
    descriptors = explicit_descriptors()
    loaded = SourceAdapter(INPUT_ROOT).read_architecture(ArchitectureSourceManifest(descriptors))
    ir = parse_architecture_generic(ArchitectureGenericIdentity("g1-architecture-generic"), loaded)
    for event_id in ("h2epr-0288", "h2epr-0616"):
        source_id = f"{event_id}-draft-epg"
        assert any(item.source_id == source_id and item.pointer.startswith("/stages/") for item in ir.values)
        assert any(item.source_id == source_id and item.pointer.endswith("/value") for item in ir.times)
        endpoints = [
            endpoint
            for item in (*ir.relations, *ir.transactions)
            if item.source_id == source_id
            for endpoint in item.endpoints
        ]
        assert endpoints
        assert all(endpoint.status in set(EndpointStatus) for endpoint in endpoints)


def test_architecture_parse_diagnostics_are_bounded_and_payload_free() -> None:
    loaded = SourceAdapter(INPUT_ROOT).read_architecture(
        ArchitectureSourceManifest(explicit_descriptors())
    )
    ir = parse_architecture_generic(ArchitectureGenericIdentity("g1-architecture-generic"), loaded)
    assert all(len(item.summary.encode("utf-8")) <= 160 for item in ir.diagnostics)
    assert all("\n" not in item.summary for item in ir.diagnostics)
    assert all(item.pointer.startswith("/") or item.pointer == "" for item in ir.diagnostics)
