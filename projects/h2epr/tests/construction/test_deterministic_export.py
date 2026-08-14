from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from h2epr.construction import (
    ArchitectureGenericIdentity,
    ConstructionIR,
    canonical_snapshot_bytes,
    mutation_descriptor,
    snapshot_sha256,
)


def test_empty_synthetic_snapshot_matches_versioned_golden() -> None:
    fixture = Path(__file__).parents[1] / "fixtures/construction_ir/v1/synthetic_minimal_snapshot.json"
    ir = ConstructionIR.empty(ArchitectureGenericIdentity("synthetic-generic"))
    assert canonical_snapshot_bytes(ir) == fixture.read_bytes()


def test_mapping_order_is_canonical_but_list_order_is_meaningful() -> None:
    left = {"beta": 2, "alpha": ["first", "second"]}
    right = {"alpha": ["first", "second"], "beta": 2}
    reversed_list = {"alpha": ["second", "first"], "beta": 2}
    assert canonical_snapshot_bytes(left) == canonical_snapshot_bytes(right)
    assert canonical_snapshot_bytes(left) != canonical_snapshot_bytes(reversed_list)


def test_snapshot_hash_is_sha256_of_exact_canonical_bytes() -> None:
    value = {"synthetic": [1, 2, 3]}
    assert snapshot_sha256(value) == hashlib.sha256(canonical_snapshot_bytes(value)).hexdigest()


def test_mutation_descriptor_and_hash_are_stable() -> None:
    first = mutation_descriptor("replace", "/alpha", {"z": 1, "a": 2})
    second = mutation_descriptor("replace", "/alpha", {"a": 2, "z": 1})
    assert first == second
    assert first["mutation_sha256"] == second["mutation_sha256"]


def test_fresh_process_exports_are_byte_identical() -> None:
    code = (
        "from h2epr.construction import canonical_snapshot_bytes;"
        "import sys;sys.stdout.buffer.write(canonical_snapshot_bytes({"
        "'beta':2,'alpha':['first','second']}))"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).parents[2] / "src")
    one = subprocess.check_output([sys.executable, "-c", code], env=env)
    two = subprocess.check_output([sys.executable, "-c", code], env=env)
    assert one == two


def test_fresh_process_synthetic_ir_exports_are_byte_identical() -> None:
    fixture = Path(__file__).parents[1] / "fixtures/construction_ir/v1/synthetic_event.json"
    code = """
import hashlib,sys
from pathlib import Path
from h2epr.construction import (
    ArchitectureGenericIdentity, ArchitectureSourceManifest, Availability,
    ReviewState, SourceAdapter, SourceDescriptor, SourceKind,
    canonical_snapshot_bytes, parse_architecture_generic,
)
path=Path(sys.argv[1]).resolve()
raw=path.read_bytes()
descriptor=SourceDescriptor(
    logical_source_id='synthetic-event', source_kind=SourceKind.SYNTHETIC,
    relative_path=path.name, expected_sha256=hashlib.sha256(raw).hexdigest(),
    availability=Availability.CONSTRUCTION_ONLY, review_state=ReviewState.REVIEWED,
)
loaded=SourceAdapter(path.parent).read_architecture(ArchitectureSourceManifest((descriptor,)))
ir=parse_architecture_generic(ArchitectureGenericIdentity('synthetic-generic'), loaded)
sys.stdout.buffer.write(canonical_snapshot_bytes(ir))
"""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(Path(__file__).parents[2] / "src")
    one = subprocess.check_output([sys.executable, "-c", code, str(fixture)], env=env)
    two = subprocess.check_output([sys.executable, "-c", code, str(fixture)], env=env)
    assert one == two


def test_tracked_construction_fixtures_are_synthetic_and_reference_blind() -> None:
    root = Path(__file__).parents[1] / "fixtures/construction_ir"
    for path in root.rglob("*.json"):
        text = path.read_text(encoding="utf-8")
        assert "synthetic" in text.lower()
        assert "reference_" + "epg" not in text.lower()
