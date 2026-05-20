"""Spec root discovery and dependency graph construction."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from afspec.models import DependencyEdge, SpecMeta


class DependencyGraph:
    """Directed dependency graph across specs."""

    def edges(self) -> list[DependencyEdge]:
        """Return all edges in the graph."""
        raise NotImplementedError

    def dependencies(self, spec_id: str) -> list[DependencyEdge]:
        """Return direct dependencies of spec_id."""
        raise NotImplementedError

    def dependents(self, spec_id: str) -> list[DependencyEdge]:
        """Return direct dependents of spec_id."""
        raise NotImplementedError

    def topological_sort(self) -> list[str]:
        """Return topological ordering of spec IDs."""
        raise NotImplementedError


def discover_specs(root: Union[str, Path]) -> list[SpecMeta]:
    """Discover spec folders in a root directory."""
    raise NotImplementedError


def build_dependency_graph(metas: list[SpecMeta], root: Union[str, Path]) -> DependencyGraph:
    """Build a dependency graph from discovered specs."""
    raise NotImplementedError
