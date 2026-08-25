from __future__ import annotations

from pathlib import Path

from h2epr.agents.definition_profile import (
    check_definition_text,
    check_population_text,
    check_publication_surface,
    main,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _valid_definition() -> str:
    return """# Example Institution

## 1. Model overview

| Field | Description |
|---|---|
| Historical participant | Example Institution |
| Modeled role | authorized institutional interface |
| Event and interval | H2EPR-TEST, one bounded interval |
| Primary decision situations | one delivered request |
| Decision cadence | event-driven |
| Decision form | constrained set-valued policy |
| State authority | business truth is environment-owned |
| Evidence use and explanatory scope | illustrative structural fixture; not calibrated |

## 2. Historical participant and representation

The model represents one authorized interface.

## 3. Evidence and theoretical foundation

The behavior is an explicit test assumption.

## 4. Institutional role and relationships

The institution may answer a scoped request.

## 5. Decision situations, information, and state

| Observation | Meaning | Consumers |
|---|---|---|
| `delivered_request` | a scoped delivered request | `DC-EX-01` |

## 6. Behavioral model

### Decision Commitments

#### `DC-EX-01` — answer a delivered request

**Situation.** A request is delivered.

**Permitted intents.** `issue_scoped_response` or abstention for a named blocker.

## 7. Intent and result boundary

| Intent | Required content | Result owned elsewhere |
|---|---|---|
| `issue_scoped_response` | request and response scope | delivery and effect |

## 8. Operationalization and uncertainty

The test uses qualitative state.

## 9. Worked cases and falsification

Removing the request prevents the response.

## 10. Limitations and references

This is a structural fixture.
"""


def _codes(text: str) -> set[str]:
    return {issue.code for issue in check_definition_text(text)}


def _valid_population() -> str:
    return """# Example Choice-Unit Population

## 1. Model overview

| Field | Description |
|---|---|
| Model name | Example choice units |
| Event and interval | H2EPR-TEST, one bounded interval |
| Choice unit | one responsibility-bounded unit |
| Population scope | units admitted by the event roster |
| Primary decision situations | one delivered signal and one pending result |
| Aggregation boundary | summaries retain unit identity and ownership |
| State authority | delivery and realized results are scenario-owned |
| Evidence use and explanatory scope | illustrative structural fixture; not calibrated |

## 2. Population scope and representation

Units remain heterogeneous and do not form one actor.

## 3. Evidence and theoretical foundation

The behavior is an explicit test assumption.

## 4. Event role and relationships

Each unit retains its own information and authority.

## 5. Decision situations, information, and state

Only delivered signals and own lifecycle notices are observed.

## 6. Behavioral model

The unit may respond or wait for a named pending result.

## 7. Intent and result boundary

The unit emits an intent; delivery and effect remain elsewhere.

## 8. Operationalization and uncertainty

The fixture uses qualitative unit types without fitted weights.

## 9. Worked cases and falsification

Removing the signal removes the response.

## 10. Limitations and references

This is a structural fixture.
"""


def test_new_definition_profile_accepts_closed_inventory() -> None:
    assert check_definition_text(_valid_definition()) == ()


def test_profile_accepts_wrapped_label_and_collective_consumer() -> None:
    text = _valid_definition().replace("`DC-EX-01` |", "all commitments |", 1)
    text = text.replace("**Permitted intents.**", "**Permitted\nintents.**")
    assert check_definition_text(text) == ()


def test_profile_requires_exact_numbered_module_order() -> None:
    text = _valid_definition().replace("## 5. Decision", "## Decision", 1)
    assert "module_profile_mismatch" in _codes(text)


def test_population_profile_requires_its_exact_ten_module_order() -> None:
    assert check_population_text(_valid_population()) == ()
    text = _valid_population().replace("## 4. Event role", "## 4. Institutional role")
    codes = {issue.code for issue in check_population_text(text)}
    assert "population_module_profile_mismatch" in codes


def test_profile_rejects_project_metadata_from_public_definition() -> None:
    text = _valid_definition().replace(
        "| Evidence use and explanatory scope | illustrative structural fixture; not calibrated |",
        "| Evidence use and explanatory scope | `FULL_DRAFT_EXPOSED` |\n"
        "| Definition identity | `h2epr.agent-definition.test.example`, version `0.1.0` |",
    )
    codes = _codes(text)
    assert "project_identity_metadata" in codes
    assert "workflow_status_metadata" in codes


def test_publication_surface_rejects_prose_version_and_status_rows() -> None:
    text = _valid_definition().replace(
        "This is a structural fixture.",
        "Version `0.1.0` records the current candidate.\n\n"
        "| Evidence status | accepted |\n"
        "|---|---|",
    )
    codes = {issue.code for issue in check_publication_surface(text)}
    assert codes == {"project_identity_metadata", "workflow_status_metadata"}


def test_profile_rejects_dangling_commitment_and_observation_without_consumer() -> None:
    text = _valid_definition().replace("`DC-EX-01` |", "`DC-EX-99` |", 1)
    codes = _codes(text)
    assert "commitment_reference_dangling" in codes


def test_profile_rejects_observation_without_commitment_or_context_label() -> None:
    text = _valid_definition().replace("`DC-EX-01` |", "unassigned |", 1)
    assert "observation_consumer_missing" in _codes(text)


def test_profile_rejects_unmapped_and_orphan_intents() -> None:
    text = _valid_definition().replace(
        "`issue_scoped_response` or abstention",
        "`request_hidden_result` or abstention",
    )
    codes = _codes(text)
    assert "intent_reference_dangling" in codes
    assert "intent_without_commitment" in codes


def test_profile_does_not_borrow_intent_link_from_later_module() -> None:
    text = _valid_definition().replace(
        "**Permitted intents.** `issue_scoped_response` or abstention for a named blocker.",
        "The response remains bounded by the institutional interface.",
    )
    text = text.replace(
        "| `issue_scoped_response` | request and response scope | delivery and effect |",
        "| `issue_scoped_response` | request and response scope; **Permitted intents.** `issue_scoped_response` | delivery and effect |",
    )
    assert "commitment_intent_link_missing" in _codes(text)


def test_profile_ignores_commitment_heading_outside_behavior_module() -> None:
    text = _valid_definition().replace(
        "#### `DC-EX-01` — answer a delivered request\n\n"
        "**Situation.** A request is delivered.\n\n"
        "**Permitted intents.** `issue_scoped_response` or abstention for a named blocker.\n",
        "The behavioral module contains no Decision Commitment.\n",
    )
    text = text.replace(
        "Removing the request prevents the response.",
        "#### `DC-EX-01` — misplaced worked-case heading\n\n"
        "**Permitted intents.** `issue_scoped_response`.\n",
    )
    assert "commitment_inventory_missing" in _codes(text)


def test_cli_reports_pass_and_fail(tmp_path: Path, capsys) -> None:
    valid = tmp_path / "valid.md"
    invalid = tmp_path / "invalid.md"
    valid.write_text(_valid_definition(), encoding="utf-8")
    invalid.write_text(_valid_definition().replace("## 10.", "## 11."), encoding="utf-8")

    assert main([str(valid)]) == 0
    assert capsys.readouterr().out.startswith("PASS ")
    assert main([str(invalid)]) == 1
    output = capsys.readouterr().out
    assert output.startswith("FAIL ")
    assert "module_profile_mismatch" in output


def test_canonical_agent_definitions_follow_the_public_profile() -> None:
    paths = [
        path
        for event_dir in (PROJECT_ROOT / "agents/defines").iterdir()
        if event_dir.is_dir()
        for path in event_dir.glob("*.md")
        if path.name != "README.md"
    ]

    findings = {
        str(path.relative_to(PROJECT_ROOT)): check_definition_text(
            path.read_text(encoding="utf-8")
        )
        for path in paths
    }
    failures = {
        path: tuple(issue.code for issue in issues)
        for path, issues in findings.items()
        if issues
    }
    assert failures == {}


def test_canonical_population_models_follow_the_public_profile() -> None:
    paths = (PROJECT_ROOT / "populations/defines").glob("*/*.md")
    findings = {
        str(path.relative_to(PROJECT_ROOT)): check_population_text(
            path.read_text(encoding="utf-8")
        )
        for path in paths
    }
    failures = {
        path: tuple(issue.code for issue in issues)
        for path, issues in findings.items()
        if issues
    }
    assert failures == {}
