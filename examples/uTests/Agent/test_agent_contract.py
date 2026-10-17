"""Acceptance tests for the Agent part (canonical agent contract).

Two layers, and the split is the point:

* ``masim.agents`` — the **platform templates**: four canonical bases
  (Rule / LLM / RAG / Market Coordinator) sharing ``GeneralPlayer`` + the
  per-agent RNG. The platform never imports a concrete archetype.
* ``agent_library`` — the **concrete library**: 209 archetypes plus their
  profiles. It imports the templates, never the other way around.

Archetypes fill only the sanctioned hooks and never override
``perceive``/``decide``/``act``.
"""

from __future__ import annotations

import ast
import unittest
from typing import Any, Dict, Iterator, Tuple

from examples.uTests._helpers import PROJECT_ROOT, make_rule_agent

_TEMPLATES_ROOT = PROJECT_ROOT / "masim" / "agents"
_AGENTS_ROOT = PROJECT_ROOT / "agent_library"
_ARCHETYPE_PARTS = ("finance", "market", "opinion")

# The only archetypes allowed to override ``on_fill`` (docs/framework-contract.md
# §4): each maintains per-fill state such as VWAP anchors or cost basis.
_DOCUMENTED_ON_FILL = {
    "RuleDispositionInvestor",
    "RuleDispositionTrader",
    "RuleEndowedHolder",
    "RuleInstitutionalInvestor",
    "RuleLongTermInvestor",
}


def _archetype_classes() -> Iterator[Tuple[Any, ast.ClassDef, Dict[str, Any]]]:
    """Yield ``(path, class_node, {method_name: node})`` for every archetype."""
    for part in _ARCHETYPE_PARTS:
        for path in sorted((_AGENTS_ROOT / part).glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                methods = {
                    item.name: item
                    for item in node.body
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                yield path, node, methods


class TestCanonicalBases(unittest.TestCase):
    """The four canonical bases are the only entry points agents inherit from."""

    def test_the_four_canonical_bases_are_importable_from_masim_agents(self) -> None:
        import masim.agents as agents

        expected = (
            "CanonicalRulePlayer",
            "CanonicalLLMPlayer",
            "CanonicalRagPlayer",
            "CanonicalMarketCoordinator",
        )
        for name in expected:
            with self.subTest(base=name):
                self.assertTrue(hasattr(agents, name), f"masim.agents lacks {name}")
                self.assertIn(name, agents.__all__)

    def test_every_canonical_base_derives_from_general_player_and_seeded_rng(
        self,
    ) -> None:
        import masim.agents as agents
        from masim.agents._base import SeededRngMixin
        from masim.player.general import GeneralPlayer

        for name in (
            "CanonicalRulePlayer",
            "CanonicalLLMPlayer",
            "CanonicalRagPlayer",
            "CanonicalMarketCoordinator",
        ):
            base = getattr(agents, name)
            with self.subTest(base=name):
                self.assertTrue(
                    issubclass(base, GeneralPlayer),
                    f"{name} must plug into the existing simulator",
                )
                self.assertTrue(
                    issubclass(base, SeededRngMixin),
                    f"{name} must draw randomness through self.rng",
                )

    def test_rag_base_extends_the_llm_base_and_exports_its_fallback_sentinel(
        self,
    ) -> None:
        import masim.agents as agents
        from masim.agents._base import CanonicalLLMPlayer

        self.assertTrue(issubclass(agents.CanonicalRagPlayer, CanonicalLLMPlayer))
        self.assertIsInstance(agents.RAG_FALLBACK_MESSAGE, str)
        self.assertTrue(agents.RAG_FALLBACK_MESSAGE)

    def test_registry_entries_pair_a_rule_and_an_llm_class_sharing_the_strategy(
        self,
    ) -> None:
        import agent_library as agents
        from masim.agents._base import CanonicalLLMPlayer, CanonicalRulePlayer

        self.assertGreater(len(agents.REGISTRY), 100)
        for archetype, (rule_cls, llm_cls) in agents.REGISTRY.items():
            with self.subTest(archetype=archetype):
                self.assertTrue(issubclass(rule_cls, CanonicalRulePlayer))
                self.assertTrue(issubclass(llm_cls, CanonicalLLMPlayer))
                # The kebab stem is the wire ``strategy`` on both engines.
                self.assertEqual(rule_cls.STRATEGY, archetype)
                self.assertEqual(llm_cls.STRATEGY, archetype)

    def test_coordinator_registry_classes_derive_from_the_coordinator_base(
        self,
    ) -> None:
        import agent_library as agents
        from masim.agents import CanonicalMarketCoordinator

        self.assertTrue(agents.COORDINATOR_REGISTRY)
        for archetype, cls in agents.COORDINATOR_REGISTRY.items():
            with self.subTest(archetype=archetype):
                self.assertTrue(
                    issubclass(cls, CanonicalMarketCoordinator)
                )
                self.assertEqual(cls.STRATEGY, archetype)

    def test_get_agent_and_get_coordinator_reject_unknown_names_and_engines(
        self,
    ) -> None:
        import agent_library as agents

        with self.assertRaises(KeyError):
            agents.get_agent("no-such-archetype")
        with self.assertRaises(ValueError):
            agents.get_agent("noise-trader", engine="Rag")
        with self.assertRaises(KeyError):
            agents.get_coordinator("no-such-coordinator")


class TestArchetypeDiscipline(unittest.TestCase):
    """Archetypes may only fill the sanctioned hooks, never the lifecycle."""

    def test_rule_archetypes_implement_decide_order(self) -> None:
        scanned = 0
        missing = []
        for path, node, methods in _archetype_classes():
            bases = {ast.unparse(base) for base in node.bases}
            if "CanonicalRulePlayer" not in bases:
                continue
            scanned += 1
            if "decide_order" not in methods:
                missing.append(f"{path.name}:{node.name}")
        # Guard against a green-but-vacuous scan if the packages move.
        self.assertGreater(scanned, 100)
        self.assertEqual(missing, [], "Rule archetypes must implement decide_order")

    def test_archetypes_never_override_perceive_decide_or_act(self) -> None:
        scanned = 0
        offenders = []
        for path, node, methods in _archetype_classes():
            scanned += 1
            for forbidden in ("perceive", "decide", "act"):
                if forbidden in methods:
                    offenders.append(f"{path.name}:{node.name}.{forbidden}")
        self.assertGreater(scanned, 300)
        self.assertEqual(
            offenders,
            [],
            "Archetypes must use decide_order/on_market_data/on_fill instead",
        )

    def test_every_archetype_derives_from_one_of_the_canonical_bases(self) -> None:
        offenders = []
        for path, node, _ in _archetype_classes():
            bases = {ast.unparse(base) for base in node.bases}
            allowed = {
                "CanonicalRulePlayer",
                "CanonicalLLMPlayer",
                "CanonicalMarketCoordinator",
            }
            if not (bases & allowed):
                offenders.append(f"{path.name}:{node.name} bases={sorted(bases)}")
        self.assertEqual(offenders, [])

    def test_only_the_documented_archetypes_override_on_fill(self) -> None:
        overrides = set()
        undocumented = []
        for path, node, methods in _archetype_classes():
            if "on_fill" not in methods:
                continue
            overrides.add(node.name)
            if ast.get_docstring(methods["on_fill"]) is None:
                undocumented.append(f"{path.name}:{node.name}")
        self.assertEqual(
            overrides,
            _DOCUMENTED_ON_FILL,
            "on_fill overrides are a documented allowlist (contract §4)",
        )
        self.assertEqual(undocumented, [], "every on_fill override needs a docstring")


class TestSeededRngContract(unittest.TestCase):
    """``self.rng`` is deterministic per (seed, identity) and salted per agent."""

    def test_rng_is_deterministic_for_a_fixed_seed_and_identity(self) -> None:
        first = make_rule_agent(identity="alpha", seed=1234)
        second = make_rule_agent(identity="alpha", seed=1234)
        self.assertEqual(
            [first.rng.random() for _ in range(5)],
            [second.rng.random() for _ in range(5)],
        )

    def test_rng_is_salted_by_agent_identity(self) -> None:
        first = make_rule_agent(identity="alpha", seed=1234)
        second = make_rule_agent(identity="beta", seed=1234)
        self.assertNotEqual(
            [first.rng.random() for _ in range(5)],
            [second.rng.random() for _ in range(5)],
        )

    def test_rng_differs_across_seeds_for_the_same_identity(self) -> None:
        first = make_rule_agent(identity="alpha", seed=1)
        second = make_rule_agent(identity="alpha", seed=2)
        self.assertNotEqual(
            [first.rng.random() for _ in range(5)],
            [second.rng.random() for _ in range(5)],
        )

    def test_rng_is_cached_on_the_agent_state(self) -> None:
        agent = make_rule_agent(identity="alpha", seed=7)
        self.assertIs(agent.rng, agent.rng)

    def test_without_a_seed_the_stream_is_not_reproducible(self) -> None:
        first = make_rule_agent(identity="alpha")
        second = make_rule_agent(identity="alpha")
        self.assertNotEqual(
            [first.rng.random() for _ in range(5)],
            [second.rng.random() for _ in range(5)],
        )

    def test_rng_is_derived_from_the_config_seed_not_the_global_module(self) -> None:
        from masim.utils.rng import derive_rng

        agent = make_rule_agent(identity="alpha", seed=99)
        expected = derive_rng(99, salt="alpha").random()
        self.assertEqual(agent.rng.random(), expected)


class TestActionPayloadContract(unittest.TestCase):
    """``Action`` accepts only serialisation-friendly payload types."""

    def test_action_accepts_dict_list_bytes_and_ndarray(self) -> None:
        import numpy as np

        from masim.player.base import Action

        for payload in ({"a": 1}, [1, 2], b"raw", np.array([1.0, 2.0])):
            with self.subTest(payload=type(payload).__name__):
                action = Action(action_type="t", payload=payload, source_id="s")
                self.assertIs(action.payload, payload)

    def test_action_allows_a_none_payload(self) -> None:
        from masim.player.base import Action

        self.assertIsNone(Action(action_type="t", payload=None, source_id="s").payload)

    def test_action_rejects_a_non_serialisable_payload(self) -> None:
        from masim.player.base import Action

        for payload in (object(), 3.5, {1, 2}, lambda: None):
            with self.subTest(payload=type(payload).__name__):
                with self.assertRaises(TypeError):
                    Action(action_type="t", payload=payload, source_id="s")

    def test_action_to_dict_flattens_ndarray_and_status(self) -> None:
        import numpy as np

        from masim.player.base import Action, ActionStatus

        action = Action(
            action_type="t", payload=np.array([1, 2]), source_id="s"
        )
        serialised = action.to_dict()
        self.assertEqual(serialised["payload"], [1, 2])
        self.assertEqual(serialised["status"], ActionStatus.CREATED.name)
        self.assertEqual(serialised["source_id"], "s")


class TestInvalidationGuard(unittest.TestCase):
    """``validate_archetype_extras`` is the archetype parameter gate."""

    def test_out_of_range_and_mistyped_extras_fail_loudly(self) -> None:
        from masim.agents._base import validate_archetype_extras

        specs = {"threshold": {"type": "float", "range": (0.0, 1.0)}}
        validate_archetype_extras("probe", {"threshold": 0.5}, specs)
        # Parameters absent from extras fall back to the archetype default.
        validate_archetype_extras("probe", {}, specs)
        with self.assertRaises(ValueError):
            validate_archetype_extras("probe", {"threshold": 2.0}, specs)
        with self.assertRaises(ValueError):
            validate_archetype_extras("probe", {"threshold": "x"}, specs)
