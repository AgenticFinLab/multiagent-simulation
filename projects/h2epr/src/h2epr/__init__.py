"""Repository-local H2EPR research implementation.

The top-level package exposes only lightweight construction and artifact
namespaces. Execution, runtime, compiler, and evaluator surfaces remain
explicit, opt-in imports so importing :mod:`h2epr` does not activate
simulation or evaluation code.
"""

from . import artifacts, bundles, construction, policies, world

__all__ = ["artifacts", "bundles", "construction", "policies", "world"]
