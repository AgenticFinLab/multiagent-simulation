from __future__ import annotations

import json
from pathlib import Path
import unittest

import jsonschema


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_ROOT = PROJECT_ROOT / "schemas"


def _strict_json(path: Path):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"duplicate_json_key:{path.name}:{key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


class SchemaCatalogTests(unittest.TestCase):
    def test_catalog_is_complete_and_every_schema_is_valid(self) -> None:
        catalog = _strict_json(SCHEMA_ROOT / "catalog.json")
        declared = catalog["schemas"]
        self.assertEqual(35, len(declared))
        self.assertEqual(len(declared), len(set(declared)))
        self.assertEqual(
            set(declared),
            {path.name for path in SCHEMA_ROOT.glob("*.schema.json")},
        )
        for name in declared:
            with self.subTest(schema=name):
                value = _strict_json(SCHEMA_ROOT / name)
                jsonschema.Draft202012Validator.check_schema(value)
                self.assertTrue(value["$id"].startswith("h2epr."))

    def test_no_parallel_schema_generation_is_published(self) -> None:
        self.assertFalse(
            any(
                path.is_dir() and path.name.startswith("v")
                for path in SCHEMA_ROOT.iterdir()
            )
        )


if __name__ == "__main__":
    unittest.main()
