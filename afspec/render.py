"""Deterministic markdown rendering for spec artifacts."""

from __future__ import annotations

from afspec.models import Requirements, Spec, Tasks, TestSpec


def render_requirements(req: Requirements) -> str:
    """Render requirements to markdown."""
    raise NotImplementedError


def render_test_spec(ts: TestSpec) -> str:
    """Render test spec to markdown."""
    raise NotImplementedError


def render_tasks(t: Tasks) -> str:
    """Render tasks to markdown."""
    raise NotImplementedError


def render_combined(spec: Spec) -> str:
    """Render all spec artifacts to a single markdown document."""
    raise NotImplementedError
