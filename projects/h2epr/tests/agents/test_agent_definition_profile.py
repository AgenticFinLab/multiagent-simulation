from __future__ import annotations

from pathlib import Path

from h2epr.agents.definition_profile import check_definition_text, main


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
| Evidence and model status | event-bound candidate; not calibrated |
| Definition identity | `h2epr.agent-definition.test.example`, version `0.1.0` |

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

## 10. Limitations, references, and provenance

This is a structural fixture.
"""


def _codes(text: str) -> set[str]:
    return {issue.code for issue in check_definition_text(text)}


def test_new_definition_profile_accepts_closed_inventory() -> None:
    assert check_definition_text(_valid_definition()) == ()


def test_profile_accepts_wrapped_label_and_collective_consumer() -> None:
    text = _valid_definition().replace("`DC-EX-01` |", "all commitments |", 1)
    text = text.replace("**Permitted intents.**", "**Permitted\nintents.**")
    assert check_definition_text(text) == ()


def test_profile_requires_exact_numbered_module_order() -> None:
    text = _valid_definition().replace("## 5. Decision", "## Decision", 1)
    assert "module_profile_mismatch" in _codes(text)


def test_profile_requires_stable_identity_and_semantic_version() -> None:
    text = _valid_definition().replace(
        "`h2epr.agent-definition.test.example`, version `0.1.0`",
        "Example Institution",
    )
    assert "definition_identity_invalid" in _codes(text)


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
