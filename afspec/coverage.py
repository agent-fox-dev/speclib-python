"""Coverage computation for test spec against requirements."""

from __future__ import annotations

from afspec.models import Coverage, Requirements, TestSpec


def compute_coverage(ts: TestSpec, req: Requirements) -> Coverage:
    """Compute coverage of requirements by tests."""
    raise NotImplementedError
