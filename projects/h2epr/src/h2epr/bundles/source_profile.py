"""Hash-pinned, non-evaluation development source profile for the G2 canary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from h2epr.construction import (
    ArchitectureGenericIdentity,
    ArchitectureSourceManifest,
    Availability,
    ConstructionIR,
    ReviewState,
    SourceAdapter,
    SourceDescriptor,
    SourceKind,
    parse_architecture_generic,
)
from h2epr.construction.model import LoadedSource


COMMON_HASHES = {
    "source_identity.json": "adaac1f4e6c1dc087acabc3631d9dec5a48c0d0b05d3db1a23d847723e6b1566",
    "sample_manifest.csv": "e8145857b17b5efc1bdfa8aeeaf097d1db21142b8dd5519ecfa93e74908d62bc",
}
EVENT_HASHES = {
    "0170": ("c74f9bb20e1a8a6815c2c3a0657b2b5e881a606737a0438f6dd8b3caad173690", "7f5e4b7d636615e3f9cd3da292caa8ce3bffc768e7ddc9d994a370f89def5c4a", "ddfb541247a91173784961a2586780cf476cd2edebd49c209d54de0ce284913e"),
    "0196": ("3c3bb90db96416d542bdf5615660ebe535c15ea638dbc6020127e9c78a36b4f1", "4167bbf09a0c54341582c55b8c923f3ab016e3657875614969a09bdb9d2f0a2a", "d3b8ad44ae709318950c315fe16892981ee01bdfc734848c4af08be63440ca5c"),
    "0288": ("a9f262b9d48a1b594b8a65f5ebdd39184996b34423be3d432390a3917bad1a52", "c27f6f36dcb008c3314e458e9d4c4fa714a3b1a7ba4150b13e0e33d94a7f6bb3", "4f98abfe0432fa1f41b6494e5966622f92ecf163584f5a8023fa5c2af8c9d8a3"),
    "0481": ("d61821a6b9042b7645b215300bce2ebab5e3933eae17b00421352a81121aed33", "c57db941c601de94e0f8826bd74537b2d4b4bc08c94d1ea3d7cec249b1a3c325", "9883cae0a41d1345de43efa4658b8d4162fdf5843dadf94da36be5a6e9a26254"),
    "0551": ("ff668a0b27fcca9146b845fd520219878d42d513a171fe88bdfc6e99f92f033f", "c3f122bb3058be45e07d8a3620b28b0b7df352df92cf8c362fed8bb9ceb006d5", "869488ce843b661328cc9e0c26ceabec4201cb5445aec8c10f80eba0aab2621f"),
    "0616": ("5a69486c0c3cff4dab019e43a75b9f959ebb47e3b52b17241bb637dd0cdfbbfb", "ea356fc9f0f7dfede9e7415f61d144e8ba13e61c3ad5647318abe7b5449f5e7c", "aa6b725305e2fbcc101ca5189af84535a58338f6c5e28fbe7b3e6787723ee54c"),
    "0892": ("30ef79f0b36d35dbc154dc8f89ba854230a823f397954f7f945fc29751a4c85a", "b101a619571ebad60130ce0abf9022c24d4a14c858aefe5e53811ba1fc234d55", "084f224e9e2424073ebe94c83a5882ca1e9efe6127f8d239346a6592e415708b"),
    "1031": ("9904a05984540a09668b76db69790940dc9819a3c936ea8a5270b58c2a7239fd", "04050597abe437e1cc23c1f548e57aad9fc536d0d4d04bebc95536ad79430cda", "4eae92aee3d5f3d1e37e769ccce708fae92a549d29c9e907907ae16176469e6c"),
}


def authorized_development_descriptors() -> tuple[SourceDescriptor, ...]:
    descriptors = [
        SourceDescriptor("common-source-identity", SourceKind.SOURCE_IDENTITY, "source_identity.json", COMMON_HASHES["source_identity.json"], Availability.CONSTRUCTION_ONLY, ReviewState.REVIEWED),
        SourceDescriptor("common-sample-manifest", SourceKind.SAMPLE_MANIFEST, "sample_manifest.csv", COMMON_HASHES["sample_manifest.csv"], Availability.CONSTRUCTION_ONLY, ReviewState.REVIEWED),
    ]
    filenames = ("event_spec.json", "frozen_evidence.json", "draft_epg.json")
    kinds = (SourceKind.EVENT_SPEC, SourceKind.FROZEN_EVIDENCE, SourceKind.DRAFT_EPG)
    for event_number in sorted(EVENT_HASHES):
        event_id = f"H2EPR-{event_number}"
        for filename, kind, digest in zip(filenames, kinds, EVENT_HASHES[event_number], strict=True):
            descriptors.append(
                SourceDescriptor(
                    f"{event_id.lower()}-{filename[:-5].replace('_', '-')}",
                    kind,
                    f"events/{event_id}/{filename}",
                    digest,
                    Availability.CONSTRUCTION_ONLY,
                    ReviewState.REVIEWED,
                )
            )
    return tuple(descriptors)


def _descriptor_identity(descriptor: SourceDescriptor) -> tuple[object, ...]:
    return (
        descriptor.logical_source_id,
        SourceKind(descriptor.source_kind).value,
        descriptor.relative_path,
        descriptor.expected_sha256,
        descriptor.availability.value,
        descriptor.review_state.value,
    )


def verify_authorized_development_profile(
    descriptors: tuple[SourceDescriptor, ...],
) -> None:
    expected = tuple(map(_descriptor_identity, authorized_development_descriptors()))
    observed = tuple(map(_descriptor_identity, descriptors))
    if observed != expected:
        raise ValueError("authorized_source_profile_mismatch")


@dataclass(frozen=True)
class TargetSourceContext:
    authorized_sources: tuple[LoadedSource, ...]
    target_sources: tuple[LoadedSource, ...]
    target_ir: ConstructionIR


def load_panic_1907_source_context(
    approved_root: Path,
    descriptors: tuple[SourceDescriptor, ...] | None = None,
) -> TargetSourceContext:
    """Read the 26-file profile, then isolate the exact five-file 0288 parent."""
    manifest_descriptors = descriptors or authorized_development_descriptors()
    verify_authorized_development_profile(manifest_descriptors)
    loaded = SourceAdapter(approved_root).read_architecture(
        ArchitectureSourceManifest(manifest_descriptors)
    )
    target_ids = {"common-source-identity", "common-sample-manifest"}
    target_ids.update(
        descriptor.logical_source_id
        for descriptor in manifest_descriptors
        if descriptor.logical_source_id.startswith("h2epr-0288-")
    )
    target_sources = tuple(
        source for source in loaded if source.descriptor.logical_source_id in target_ids
    )
    if len(target_sources) != 5:
        raise ValueError("target_source_cardinality_mismatch")
    target_ir = parse_architecture_generic(
        ArchitectureGenericIdentity("h2epr.0288.g1.source.ir.v1"), target_sources
    )
    return TargetSourceContext(loaded, target_sources, target_ir)
