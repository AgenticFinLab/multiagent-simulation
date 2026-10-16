"""Acceptance tests for the World part (the shared-state contract).

``masim/platform/world/base.py`` is definitions only: a ``WorldVersion``
dataclass plus an abstract ``SharedState`` with ``get``/``set``/``version``/
``snapshot``.

The contract now has exactly one implementation, ``masim/world/shared_state.py``
(``VersionedSharedState``), which the Simulator holds and commits once per round
from coordinator broadcasts. The implementation's own semantics are covered in
``test_versioned_world.py``; this module pins the contract and the wiring.
"""

from __future__ import annotations

import ast
import dataclasses
import unittest

from examples.uTests._helpers import PROJECT_ROOT

_WORLD_MODULE = PROJECT_ROOT / "masim" / "platform" / "world" / "base.py"
_PLATFORM_ROOT = PROJECT_ROOT / "masim" / "platform"
_MASIM_ROOT = PROJECT_ROOT / "masim"

_EXPECTED_METHODS = {"get", "set", "version", "snapshot"}


def _world_tree() -> ast.Module:
    """Parse the world contract module once per call."""
    return ast.parse(_WORLD_MODULE.read_text(encoding="utf-8"))


def _method_nodes(tree: ast.Module, class_name: str):
    """Return {method_name: node} for a top-level class in ``tree``."""
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {
                item.name: item
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
    return {}


class TestSharedStateContract(unittest.TestCase):
    """The contract exists and can be imported without any implementation."""

    def test_shared_state_is_an_abstract_base_class(self) -> None:
        from masim.platform.world.base import SharedState

        self.assertTrue(hasattr(SharedState, "__abstractmethods__"))
        self.assertEqual(set(SharedState.__abstractmethods__), _EXPECTED_METHODS)
        with self.assertRaises(TypeError):
            SharedState()

    def test_the_contract_exposes_exactly_the_four_documented_methods(self) -> None:
        tree = _world_tree()
        methods = _method_nodes(tree, "SharedState")
        self.assertEqual(set(methods), _EXPECTED_METHODS)
        for name, node in methods.items():
            with self.subTest(method=name):
                self.assertTrue(
                    any(
                        isinstance(decorator, ast.Name)
                        and decorator.id == "abstractmethod"
                        for decorator in node.decorator_list
                    ),
                    f"SharedState.{name} must be decorated @abstractmethod",
                )

    def test_world_version_is_a_dataclass_with_round_level_and_seq(self) -> None:
        from masim.platform.world.base import WorldVersion

        self.assertTrue(dataclasses.is_dataclass(WorldVersion))
        self.assertEqual(
            [field.name for field in dataclasses.fields(WorldVersion)],
            ["round_num", "level", "seq"],
        )
        version = WorldVersion(round_num=2, level=1)
        self.assertEqual((version.round_num, version.level, version.seq), (2, 1, 0))

    def test_every_contract_method_body_is_an_ellipsis(self) -> None:
        """Definitions only: behaviour lives in implementations, never here."""
        methods = _method_nodes(_world_tree(), "SharedState")
        offenders = []
        undocumented = []
        for name, node in methods.items():
            statements = list(node.body)
            # A leading string literal is the contract docstring, not behaviour.
            if (
                statements
                and isinstance(statements[0], ast.Expr)
                and isinstance(statements[0].value, ast.Constant)
                and isinstance(statements[0].value.value, str)
            ):
                if not statements[0].value.value.strip():
                    undocumented.append(name)
                statements = statements[1:]
            definition_only = (
                len(statements) == 1
                and isinstance(statements[0], ast.Expr)
                and isinstance(statements[0].value, ast.Constant)
                and statements[0].value.value is Ellipsis
            )
            if not definition_only:
                offenders.append(name)
        self.assertEqual(offenders, [], "contract bodies must be `...`")
        self.assertEqual(undocumented, [], "every contract method needs a docstring")


class TestWorldStateWiring(unittest.TestCase):
    """Exactly one implementation exists, and the Simulator owns it."""

    def _imports_world_contract(self, path) -> bool:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "platform" in node.module and "world" in node.module:
                    return True
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "platform" in alias.name and "world" in alias.name:
                        return True
        return False

    def test_only_the_world_package_imports_the_contract(self) -> None:
        """The contract is consumed by its implementation, not by ad-hoc code."""
        allowed = {"world", "simulator"}
        offenders = []
        for path in sorted(_MASIM_ROOT.rglob("*.py")):
            if _PLATFORM_ROOT in path.parents:
                continue
            parts = path.relative_to(_MASIM_ROOT).parts
            if parts and parts[0] in allowed:
                continue
            if self._imports_world_contract(path):
                offenders.append(str(path.relative_to(_MASIM_ROOT)))
        self.assertEqual(
            offenders,
            [],
            "modules outside masim/world and masim/simulator must not reach "
            "into the world contract directly; go through VersionedSharedState",
        )

    def test_the_simulator_owns_a_versioned_world(self) -> None:
        source = (_MASIM_ROOT / "simulator" / "general.py").read_text(encoding="utf-8")
        self.assertIn("self.world = VersionedSharedState()", source)
        self.assertIn("self.world.commit(", source)

    def test_shared_state_subclasses_live_only_where_declared(self) -> None:
        """Every concrete ``SharedState`` is a deliberate, registered choice."""
        subclasses = []
        for path in sorted(_MASIM_ROOT.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                for base in node.bases:
                    if "SharedState" in ast.unparse(base):
                        subclasses.append(str(path.relative_to(_MASIM_ROOT)))
        self.assertEqual(sorted(set(subclasses)), ["world/shared_state.py"])


if __name__ == "__main__":
    unittest.main()
