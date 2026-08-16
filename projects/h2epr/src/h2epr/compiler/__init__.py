"""Reference-blind deterministic trace-to-EPG compiler for H2EPR."""

from .adapter import (
    SourcePackageError,
    V1Wrappers,
    validate_source_package,
    validate_v1_trace,
)
from .graph import (
    EventCandidate,
    GraphCompilationError,
    compile_generated_epg,
    group_candidates,
    merge_time_intervals,
    validate_generated_epg,
)
from .inventory import InputRoots, InventoryError
from .pipeline import (
    CompilationResult,
    DependencyBoundaryError,
    compile_objects,
    compile_to_directory,
    validate_dependency_boundary,
)
from .policy import PolicyError

__all__ = [
    "CompilationResult",
    "DependencyBoundaryError",
    "EventCandidate",
    "GraphCompilationError",
    "InputRoots",
    "InventoryError",
    "PolicyError",
    "SourcePackageError",
    "V1Wrappers",
    "compile_generated_epg",
    "compile_objects",
    "compile_to_directory",
    "group_candidates",
    "merge_time_intervals",
    "validate_dependency_boundary",
    "validate_generated_epg",
    "validate_source_package",
    "validate_v1_trace",
]
