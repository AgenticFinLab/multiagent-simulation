from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from h2epr.canonical import canonical_sha256
from h2epr.cli import _parser, main


class CLISurfaceTests(unittest.TestCase):
    def _registry(self) -> dict[str, object]:
        value: dict[str, object] = {
            "schema_version": "h2epr.current-event-registry.v4",
            "registry_id": "h2epr.current-events.cli-test",
            "registry_version": "1.0.0",
            "events": [],
            "registry_sha256": "0" * 64,
        }
        value["registry_sha256"] = canonical_sha256(
            {
                key: item
                for key, item in value.items()
                if key != "registry_sha256"
            }
        )
        return value

    def test_command_inventory_is_explicit(self) -> None:
        choices = next(
            action.choices
            for action in _parser()._actions
            if getattr(action, "choices", None)
        )
        self.assertEqual(
            {
                "validate-registry",
                "build-package",
                "validate-package",
                "materialize",
                "identity-conformance",
                "admit-experiment",
                "publish-run-release",
                "publish-cross-event-release",
            },
            set(choices),
        )

    def test_validate_registry_success_is_json_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "registry.json"
            path.write_text(json.dumps(self._registry()) + "\n", encoding="utf-8")
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = main(
                    [
                        "validate-registry",
                        "--project-root",
                        str(root),
                        "--registry",
                        str(path),
                    ]
                )
        self.assertEqual(0, status)
        self.assertEqual("", stderr.getvalue())
        result = json.loads(stdout.getvalue())
        self.assertEqual("pass", result["status"])
        self.assertEqual(0, result["event_count"])

    def test_expected_failure_is_typed_json_stderr(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "registry.json"
            value = self._registry()
            value["registry_sha256"] = "f" * 64
            path.write_text(json.dumps(value) + "\n", encoding="utf-8")
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                status = main(
                    [
                        "validate-registry",
                        "--project-root",
                        str(root),
                        "--registry",
                        str(path),
                    ]
                )
        self.assertEqual(2, status)
        self.assertEqual("", stdout.getvalue())
        result = json.loads(stderr.getvalue())
        self.assertEqual("fail", result["status"])
        self.assertEqual("validate-registry", result["command"])
        self.assertEqual(
            "current_event_registry_self_hash_mismatch",
            result["error_code"],
        )
        self.assertEqual("CurrentEventRegistryError", result["error_type"])


if __name__ == "__main__":
    unittest.main()
