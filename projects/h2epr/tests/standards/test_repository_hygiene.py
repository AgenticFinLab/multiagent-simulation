from __future__ import annotations

import json
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXCLUDED_PARTS = {"build", "__pycache__", ".pytest_cache"}


def _maintained_files():
    result = []
    for path in PROJECT_ROOT.rglob("*"):
        relative_parts = path.relative_to(PROJECT_ROOT).parts
        if (
            path.is_file()
            and not (set(relative_parts) & EXCLUDED_PARTS)
            and not any(part.endswith(".egg-info") for part in relative_parts)
        ):
            result.append(path)
    return result


class RepositoryHygieneTests(unittest.TestCase):
    def test_every_json_document_is_strict(self) -> None:
        for path in _maintained_files():
            if path.suffix != ".json":
                continue

            def pairs(values, *, source=path):
                result = {}
                for key, value in values:
                    if key in result:
                        raise ValueError(
                            f"duplicate_json_key:{source.relative_to(PROJECT_ROOT)}:{key}"
                        )
                    result[key] = value
                return result

            with self.subTest(path=path.relative_to(PROJECT_ROOT)):
                json.loads(
                    path.read_text(encoding="utf-8"),
                    object_pairs_hook=pairs,
                )

    def test_maintained_text_is_utf8_clean(self) -> None:
        text_names = {"SHA256SUMS"}
        text_suffixes = {".json", ".md", ".py", ".toml", ".txt", ".TAG"}
        for path in _maintained_files():
            if path.name not in text_names and path.suffix not in text_suffixes:
                continue
            with self.subTest(path=path.relative_to(PROJECT_ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.endswith("\n"))
                self.assertTrue(
                    all(line == line.rstrip() for line in text.splitlines())
                )


if __name__ == "__main__":
    unittest.main()
