"""Collection mutation methods and ID generation helpers.

Since Pydantic models are immutable, mutation methods return new model instances.
Stub module — functions will be implemented in task group 12.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from afspec.models import (
        Criterion,
        Requirement,
        Requirements,
        Subtask,
        TaskGroup,
        Tasks,
        TestCase,
        TestSpec,
        TraceabilityEntry,
    )


def add_requirement(req: Requirements, r: Requirement) -> Requirements:
    """Add a requirement to the collection. Raises ValueError on duplicate ID."""
    raise NotImplementedError


def get_requirement(req: Requirements, id: str) -> Optional[Requirement]:
    """Get a requirement by ID, or None if not found."""
    raise NotImplementedError


def remove_requirement(req: Requirements, id: str) -> tuple[Requirements, bool]:
    """Remove a requirement by ID. Returns (updated_model, was_found)."""
    raise NotImplementedError


def set_glossary_entry(req: Requirements, term: str, definition: str) -> Requirements:
    """Insert or overwrite a glossary entry."""
    raise NotImplementedError


def remove_glossary_entry(req: Requirements, term: str) -> tuple[Requirements, bool]:
    """Remove a glossary entry. Returns (updated_model, was_found)."""
    raise NotImplementedError


def add_criterion(r: Requirement, c: Criterion) -> Requirement:
    """Add a criterion to a requirement. Raises ValueError on duplicate ID."""
    raise NotImplementedError


def add_edge_case(r: Requirement, c: Criterion) -> Requirement:
    """Add an edge case to a requirement. Raises ValueError on duplicate ID."""
    raise NotImplementedError


def get_criterion(r: Requirement, id: str) -> Optional[Criterion]:
    """Get a criterion by ID, or None if not found."""
    raise NotImplementedError


def add_test_case(ts: TestSpec, tc: TestCase) -> TestSpec:
    """Add a test case. Raises ValueError on duplicate ID."""
    raise NotImplementedError


def add_subtask(g: TaskGroup, s: Subtask) -> TaskGroup:
    """Add a subtask to a task group. Raises ValueError on duplicate ID."""
    raise NotImplementedError


def add_task_group(t: Tasks, g: TaskGroup) -> Tasks:
    """Add a task group. Raises ValueError on duplicate ID."""
    raise NotImplementedError


def add_traceability_entry(t: Tasks, e: TraceabilityEntry) -> Tasks:
    """Add a traceability entry. Raises ValueError on duplicate (req_id, ts_id) pair."""
    raise NotImplementedError


def add_dependency(t: Tasks, d: object) -> Tasks:
    """Add a dependency entry."""
    raise NotImplementedError


def next_requirement_id(req: Requirements) -> str:
    """Return the next sequential requirement ID."""
    raise NotImplementedError


def next_test_case_id(ts: TestSpec) -> str:
    """Return the next sequential test case ID."""
    raise NotImplementedError


def next_criterion_id(r: Requirement) -> str:
    """Return the next sequential criterion ID."""
    raise NotImplementedError


def next_edge_case_id(r: Requirement) -> str:
    """Return the next sequential edge case ID."""
    raise NotImplementedError


def next_correctness_property_id(req: Requirements) -> str:
    """Return the next sequential correctness property ID."""
    raise NotImplementedError


def next_execution_path_id(req: Requirements) -> str:
    """Return the next sequential execution path ID."""
    raise NotImplementedError


def next_error_handling_id(req: Requirements) -> str:
    """Return the next sequential error handling ID."""
    raise NotImplementedError


def next_property_test_id(ts: TestSpec) -> str:
    """Return the next sequential property test ID."""
    raise NotImplementedError


def next_edge_case_test_id(ts: TestSpec) -> str:
    """Return the next sequential edge case test ID."""
    raise NotImplementedError


def next_smoke_test_id(ts: TestSpec) -> str:
    """Return the next sequential smoke test ID."""
    raise NotImplementedError
