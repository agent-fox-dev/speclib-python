"""Bootstrap mode for incremental spec creation."""

from __future__ import annotations

from afspec.models import PRDDocument, Requirements, Spec, Tasks, TestSpec


class BootstrapSpec:
    """Bootstrap handle for incremental spec population."""

    def __init__(self, spec_id: str, spec_name: str) -> None:
        raise NotImplementedError

    def set_prd(self, prd: PRDDocument) -> None:
        """Set the PRD artifact."""
        raise NotImplementedError

    def set_requirements(self, req: Requirements) -> None:
        """Set the requirements artifact."""
        raise NotImplementedError

    def set_test_spec(self, ts: TestSpec) -> None:
        """Set the test spec artifact."""
        raise NotImplementedError

    def set_tasks(self, t: Tasks) -> None:
        """Set the tasks artifact."""
        raise NotImplementedError

    def finalize(self) -> tuple[Spec | None, list]:
        """Validate and return a Spec, or None with errors."""
        raise NotImplementedError
