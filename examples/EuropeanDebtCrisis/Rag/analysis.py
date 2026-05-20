#!/usr/bin/env python
"""EuropeanDebtCrisis RAG analysis utilities."""

from examples.EuropeanDebtCrisis.Rule.analysis import (
    calculate_metrics,
    create_visualizations,
    load_simulation_data,
    main,
)

_RAG_FALLBACK = "(No relevant knowledge retrieved this round.)"


def analyze_rag_knowledge_effect(retrieval_records):
    """Summarize RAG retrieval coverage for EuropeanDebtCrisis runs."""
    total = len(retrieval_records)
    if total == 0:
        raise ValueError("retrieval_records must not be empty")
    retrieved = sum(
        1
        for record in retrieval_records
        if record["rag_context"] != _RAG_FALLBACK
    )
    return {"retrieval_success_rate": retrieved / total, "total_records": total}


__all__ = [
    "load_simulation_data",
    "calculate_metrics",
    "create_visualizations",
    "analyze_rag_knowledge_effect",
    "main",
]


if __name__ == "__main__":
    main()
