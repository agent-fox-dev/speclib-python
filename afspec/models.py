"""Data model types for the afspec library.

Stub module — all classes and functions defined here are placeholders
that will be implemented in task group 2.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class Status(str, Enum):
    """Lifecycle states for specs."""

    DRAFT = "draft"
    ACTIVE = "active"
    SEALED = "sealed"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class EARSPattern(str, Enum):
    """EARS requirement patterns."""

    UBIQUITOUS = "ubiquitous"
    EVENT_DRIVEN = "event_driven"
    COMPLEX_EVENT = "complex_event"
    STATE_DRIVEN = "state_driven"
    UNWANTED = "unwanted"
    OPTIONAL = "optional"


class SubtaskState(str, Enum):
    """Subtask states in the task state machine."""

    PENDING = "pending"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    PENDING_REEVALUATION = "pending_reevaluation"
    DROPPED = "dropped"


class TaskGroupKind(str, Enum):
    """Task group kinds."""

    TESTS = "tests"
    STANDARD = "standard"
    CHECKPOINT = "checkpoint"
    WIRING_VERIFICATION = "wiring_verification"


def valid_transition(current: SubtaskState, target: SubtaskState) -> bool:
    """Check if a subtask state transition is legal."""
    raise NotImplementedError


# ---------------------------------------------------------------------------
# PRD Models
# ---------------------------------------------------------------------------


class PRDFrontmatter(BaseModel):
    """YAML frontmatter from prd.md."""

    pass


class PRDDocument(BaseModel):
    """Parsed prd.md document."""

    pass


# ---------------------------------------------------------------------------
# Requirements Models
# ---------------------------------------------------------------------------


class UserStory(BaseModel):
    """User story for a requirement."""

    pass


class Criterion(BaseModel):
    """EARS acceptance criterion or edge case."""

    pass

    def with_return_contract(self, rc: str) -> Criterion:
        """Return a new Criterion with return_contract set."""
        raise NotImplementedError


class Requirement(BaseModel):
    """A single requirement with criteria and edge cases."""

    pass


class CorrectnessProperty(BaseModel):
    """Correctness property / invariant."""

    pass


class PathStep(BaseModel):
    """A single step in an execution path."""

    pass


class ExecutionPath(BaseModel):
    """An execution path through the system."""

    pass


class ErrorHandlingEntry(BaseModel):
    """Error condition → behavior mapping."""

    pass


class Requirements(BaseModel):
    """The requirements.json artifact."""

    pass


# ---------------------------------------------------------------------------
# TestSpec Models
# ---------------------------------------------------------------------------


class TestCase(BaseModel):
    """A test case for an acceptance criterion."""

    pass


class PropertyTest(BaseModel):
    """A property-based test for a correctness property."""

    pass


class EdgeCaseTest(BaseModel):
    """A test for an edge case."""

    pass


class SmokeTest(BaseModel):
    """An integration smoke test for an execution path."""

    pass


class Coverage(BaseModel):
    """Computed coverage summary."""

    pass


class TestSpec(BaseModel):
    """The test_spec.json artifact."""

    pass


# ---------------------------------------------------------------------------
# Tasks Models
# ---------------------------------------------------------------------------


class TestCommands(BaseModel):
    """Test command configuration."""

    pass


class TaskDependency(BaseModel):
    """Cross-spec dependency declaration."""

    pass


class VerificationSubtask(BaseModel):
    """Verification subtask for a task group."""

    pass


class Subtask(BaseModel):
    """A subtask within a task group."""

    pass

    def transition_to(self, target: SubtaskState) -> Subtask:
        """Transition to a new state."""
        raise NotImplementedError


class TaskGroup(BaseModel):
    """A task group containing subtasks."""

    pass


class TraceabilityEntry(BaseModel):
    """Traceability link from requirement to test to task."""

    pass


class Tasks(BaseModel):
    """The tasks.json artifact."""

    pass


# ---------------------------------------------------------------------------
# Spec (top-level)
# ---------------------------------------------------------------------------


class Spec(BaseModel):
    """Complete specification package with all four artifacts."""

    pass


# ---------------------------------------------------------------------------
# Discovery Models
# ---------------------------------------------------------------------------


class SpecMeta(BaseModel):
    """Lightweight spec metadata from discovery."""

    pass


class DependencyEdge(BaseModel):
    """An edge in the dependency graph."""

    pass
