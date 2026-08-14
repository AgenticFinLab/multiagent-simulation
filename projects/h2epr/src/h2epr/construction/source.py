"""Explicit-manifest, Reference-blind source loading."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath

from .model import (
    ArchitectureSourceManifest,
    LoadedSource,
    SourceDescriptor,
    SourceKind,
    validated_source_descriptor,
    validated_source_manifest_descriptors,
)


class SourcePolicyError(ValueError):
    """An explicit construction-source boundary was violated."""


EXPECTED_BASENAME = {
    SourceKind.SOURCE_IDENTITY: "source_identity.json",
    SourceKind.SAMPLE_MANIFEST: "sample_manifest.csv",
    SourceKind.EVENT_SPEC: "event_spec.json",
    SourceKind.FROZEN_EVIDENCE: "frozen_evidence.json",
    SourceKind.DRAFT_EPG: "draft_epg.json",
    SourceKind.DRAFT_EPG_PREFIX_PROJECTION: "draft_epg_prefix_projection.json",
}


class SourceAdapter:
    """Load only explicitly described files under one caller-approved root."""

    def __init__(self, approved_root: Path):
        self._root = approved_root.resolve(strict=True)
        if not self._root.is_dir():
            raise SourcePolicyError("approved_root_not_directory")

    def _validate_descriptor(self, descriptor: SourceDescriptor) -> tuple[SourceKind, Path]:
        relative = descriptor.relative_path
        if not relative or Path(relative).is_absolute():
            raise SourcePolicyError("absolute_path_forbidden")
        if any(character in relative for character in "*?[]{}"):
            raise SourcePolicyError("glob_forbidden")
        pure = PurePosixPath(relative)
        if ".." in pure.parts:
            raise SourcePolicyError("path_traversal")
        if pure.name.lower() == "reference_epg.json" or "reference_epg" in pure.name.lower():
            raise SourcePolicyError("reference_forbidden")
        try:
            kind = SourceKind(descriptor.source_kind)
        except ValueError as exc:
            raise SourcePolicyError("unknown_source_kind") from exc
        expected = EXPECTED_BASENAME.get(kind)
        if expected is not None and pure.name != expected:
            raise SourcePolicyError("source_kind_path_mismatch")
        candidate = self._root.joinpath(*pure.parts)
        try:
            resolved = candidate.resolve(strict=True)
        except FileNotFoundError as exc:
            raise SourcePolicyError("source_not_found") from exc
        if resolved != self._root and self._root not in resolved.parents:
            raise SourcePolicyError("approved_root_escape")
        if not resolved.is_file():
            raise SourcePolicyError("not_regular_file")
        return kind, resolved

    def read_architecture(
        self, manifest: ArchitectureSourceManifest
    ) -> tuple[LoadedSource, ...]:
        try:
            descriptors = validated_source_manifest_descriptors(
                manifest, ArchitectureSourceManifest
            )
        except ValueError as exc:
            raise SourcePolicyError(str(exc)) from exc
        logical_ids: set[str] = set()
        resolved_paths: set[Path] = set()
        prepared: list[tuple[SourceDescriptor, SourceKind, Path]] = []
        for descriptor in descriptors:
            if descriptor.logical_source_id in logical_ids:
                raise SourcePolicyError("duplicate_logical_source")
            logical_ids.add(descriptor.logical_source_id)
            descriptor = validated_source_descriptor(descriptor)
            kind, path = self._validate_descriptor(descriptor)
            if path in resolved_paths:
                raise SourcePolicyError("duplicate_resolved_path")
            resolved_paths.add(path)
            prepared.append((descriptor, kind, path))

        loaded = []
        for descriptor, kind, path in prepared:
            with path.open("rb") as handle:
                content = handle.read()
            observed = hashlib.sha256(content).hexdigest()
            if observed != descriptor.expected_sha256:
                raise SourcePolicyError("content_hash_mismatch")
            try:
                if kind is SourceKind.SAMPLE_MANIFEST:
                    rows = list(csv.DictReader(io.StringIO(content.decode("utf-8"))))
                    document = {"rows": rows}
                else:
                    document = json.loads(content)
            except (UnicodeDecodeError, json.JSONDecodeError, csv.Error) as exc:
                raise SourcePolicyError("invalid_source_encoding") from exc
            loaded.append(
                LoadedSource(
                    descriptor=SourceDescriptor(
                        logical_source_id=descriptor.logical_source_id,
                        source_kind=kind,
                        relative_path=descriptor.relative_path,
                        expected_sha256=descriptor.expected_sha256,
                        availability=descriptor.availability,
                        review_state=descriptor.review_state,
                    ),
                    content_sha256=observed,
                    document=document,
                    content_size_bytes=len(content),
                )
            )
        return tuple(loaded)
