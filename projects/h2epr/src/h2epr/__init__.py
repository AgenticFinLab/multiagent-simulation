"""Repository-local H2EPR research implementation incubator.

The exported G2 modules build declarative artifacts and EventBundles only.
They deliberately expose no simulation entry point.
"""

from . import artifacts, bundles, construction, policies, world

__all__ = ["artifacts", "bundles", "construction", "policies", "world"]
