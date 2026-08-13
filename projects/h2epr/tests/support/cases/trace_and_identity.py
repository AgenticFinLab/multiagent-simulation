"""Declarative trace and identity contract behavior cases."""

from __future__ import annotations

from .common import build_declarative_cases, load_case_specs

CASE_SPECS = load_case_specs("trace_and_identity")

def build_cases() -> list[dict]:
    return build_declarative_cases(CASE_SPECS, 'trace_and_identity')
