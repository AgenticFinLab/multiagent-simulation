# AGENTS.md — working conventions for this repository

Concise, enforceable conventions for anyone (human or agent) changing MASim.
`docs/structure.md` is the architecture overview; `docs/framework-contract.md`
is the authoritative Player lifecycle contract.

## Commits

- **Commit every completed change set, without being asked.** When a unit of
  work is finished and verified, create the commit(s) in the same turn.
- Split by concern, not by file count. Typical types used in this repo:
  `fix:` (correctness), `feat:` (capability), `build:` (packaging/CI),
  `docs:` (documentation only), `chore:` (tooling/conventions).
- Subject line: `type: short imperative summary` (no trailing period).
- Never commit generated run output: `EXPERIMENT/`, `examples/CUSTOMIZED_SIMULATION/`,
  `__pycache__/`, `*.egg-info/` are ignored on purpose.

## Verification gates (run before every commit)

```bash
python -m compileall -q masim examples scripts tests   # syntax
python scripts/check_module_imports.py                 # real imports (catches
                                                       # NameError in signatures)
python scripts/check_example_reexports.py              # internal re-exports resolve
PYTHONPATH=. python -m unittest discover -s tests -t tests -p "test_*.py"
PYTHONPATH=. python -m unittest discover -s examples/uTests -t . -p "test_*.py"
python scripts/audit_scenario_contract.py --scope archetypes --no-legacy-info
python scripts/audit_scenario_contract.py --scope scenarios --scenario AnchoringEffect --no-legacy-info
python scripts/check_diagrams.py docs/design/diagrams      # SVG text collisions
```

Two test suites, by design:

* `tests/` — framework unit tests (fast, no Ray): contracts and internals.
* `examples/uTests/<Part>/` — **per-part acceptance tests**: one module per
  platform part (Agent, Time, Communication, Storage, Execution, Observability,
  World, Config), each stating that part's guarantee. When you change a part,
  the matching module is the spec you must keep green. `python` is not on PATH
  in some environments; use `python3`.

`compileall` alone is **not** sufficient: a runtime annotation such as
`x: Optional[int]` in a module that never imported `Optional` compiles cleanly
and raises `NameError` on first import. That is why the import sweep exists.

## Code conventions

- `masim/platform/*/base.py` are **contracts only** (ABC + dataclass +
  annotations + docstrings, method bodies `...`). Behaviour goes in
  implementations. Changing a contract is a decision — record it in
  `docs/hybrid-design/discussion/02-decisions-log.md`.
- Financial players derive from `CanonicalRulePlayer` / `CanonicalLLMPlayer` /
  `CanonicalRagPlayer` / `CanonicalMarketCoordinator` and MUST NOT override
  `perceive()` / `decide()` / `act()`. Use `decide_order()`, `on_market_data()`,
  `on_fill()`, `init_market_data`/`advance_market` instead — see
  `docs/framework-contract.md`.
- Randomness goes through `self.rng` (`SeededRngMixin`), never the global
  `random` module, so `setting.seed` reproduces a run.
- Record keys written to `BlockBasedStoreManager` MUST be unique: a repeated
  key is treated as an *update* and silently drops the earlier record. Use the
  `msg_r{round:06d}_{seq:06d}` / `turn_r{round:06d}_{seq:06d}` shape.
- `masim/` core must import without `lmbase` (it is not on PyPI); the block
  store is resolved lazily by `masim/utils/store_backend.py`.
- Tests live in the versioned `tests/` package. Tests requiring the lmbase
  backend must skip cleanly when it is absent.
- Cash and position change **only** through
  `masim.player.portfolio.Portfolio.apply_fill()`. Never write
  `custom_state["cash"]` / `["position"]` directly; the audit reports those as
  `SEM-CASH-MUT`.
- An order becomes a fill **only** through the agent's `FillModel`
  (`masim/platform/execution/base.py`). The default
  `SelfFillModel` reproduces the historical agent-side fill; a scenario swaps
  the policy with `extras.fill_model` ("module:Class" or an instance), or an
  archetype overrides the `FILL_MODEL` class attribute.
- Dispatch batches every message bound for the same recipient into one
  `receive_batch` RPC. Keep `BasePersona.receive_batch` on any new persona; the
  default loops `receive_message`, so per-message handling stays identical.
- Market signals reach agents **per source**: `Info.sender_id` keys
  `custom_state["market_data_by_source"]`, read through
  `self.market_data_for(source_id)`. `custom_state["market_data"]` is kept as a
  last-wins alias for backwards compatibility — never rely on it in a
  multi-market scenario.
- Everything that participates in the simulation is an **agent**, including
  information sources: a news feed is an agent, and a financial entity receives
  it by having a topology edge to it. Do not add a separate "source" concept —
  extend the agent/topology layer instead.
- `monitoring/` and `checkpoints/` are namespaced per player id (like
  `records/`). Sharing one directory across actors silently drops records,
  because BlockBasedStoreManager treats a duplicate key as an update.
