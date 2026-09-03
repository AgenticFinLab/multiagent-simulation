from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from h2epr.benchmark.package import load_event_package
from h2epr.canonical import file_sha256
from h2epr.conformance import (
    build_cross_event_contract_receipt,
    build_identity_invariance_receipt,
)
from h2epr.publication import publish_rule_run_release
from h2epr.runtime.benchmark_runner import (
    OUTPUT_ROLES,
    build_determinism_receipt,
    materialize_run,
)

from synthetic import DISPATCH_CASE, SIGNAL_CASE, build_synthetic_event


class SyntheticContractTests(unittest.TestCase):
    def test_two_distinct_vocabularies_compile_run_and_conform(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cases = [
                build_synthetic_event(root, vocabulary)
                for vocabulary in (SIGNAL_CASE, DISPATCH_CASE)
            ]
            runs = []
            for case in cases:
                package = load_event_package(
                    case.package_root,
                    case.data_root,
                    "rule",
                )
                run_root = root / case.slug / "run-a"
                repeat_root = root / case.slug / "run-b"
                probe_root = root / case.slug / "identity-probe"
                locator = (
                    f".local-runtime/h2epr-simulation/runs/tests/{case.slug}/run"
                )
                receipt = materialize_run(
                    package_root=case.package_root,
                    data_root=case.data_root,
                    output_root=run_root,
                    backend="rule",
                    run_seed=0,
                    custody_locator=locator,
                )
                materialize_run(
                    package_root=case.package_root,
                    data_root=case.data_root,
                    output_root=repeat_root,
                    backend="rule",
                    run_seed=0,
                    custody_locator=locator,
                )
                materialize_run(
                    package_root=case.package_root,
                    data_root=case.data_root,
                    output_root=probe_root,
                    backend="rule",
                    run_seed=0,
                    identity_variant="generated-id-probe",
                    custody_locator=(
                        f".local-runtime/h2epr-simulation/runs/tests/{case.slug}/probe"
                    ),
                )
                self.assertTrue(receipt["replay_passed"])
                self.assertTrue(receipt["trace_coverage_passed"])
                self.assertEqual(0, receipt["unresolved_transport_count"])
                identity = build_identity_invariance_receipt(
                    run_root,
                    probe_root,
                )
                self.assertTrue(identity["passed"])
                determinism = build_determinism_receipt(
                    left_root=run_root,
                    right_root=repeat_root,
                    package=package,
                    identity_conformance_receipt_sha256=identity["receipt_sha256"],
                )
                self.assertTrue(determinism["all_byte_identical"])
                for filename in (*OUTPUT_ROLES, "run_receipt.json"):
                    self.assertEqual(
                        file_sha256(run_root / filename),
                        file_sha256(repeat_root / filename),
                    )
                release_root = root / case.slug / "release"
                summary = publish_rule_run_release(
                    package_root=case.package_root,
                    data_root=case.data_root,
                    canonical_root=run_root,
                    repeat_root=repeat_root,
                    probe_root=probe_root,
                    release_root=release_root,
                    event_title=case.title,
                    simulation_reading_link="../../../reports/example.md",
                )
                self.assertEqual(case.event_id, summary["event_id"])
                self.assertTrue((release_root / "SHA256SUMS").is_file())
                runs.append((package, run_root))

            conformance = build_cross_event_contract_receipt(runs)
            self.assertTrue(conformance["passed"])
            self.assertTrue(all(row["passed"] for row in conformance["checks"]))


if __name__ == "__main__":
    unittest.main()
