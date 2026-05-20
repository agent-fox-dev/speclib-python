"""Factory functions for EARS criteria and spec construction."""

from __future__ import annotations

from afspec.models import Criterion, Spec


def create_spec(spec_id: str, spec_name: str) -> Spec:
    """Create a new Spec with initialized sub-artifacts."""
    raise NotImplementedError


def ubiquitous_criterion(id: str, system: str, action: str) -> Criterion:
    """Create a ubiquitous EARS criterion."""
    raise NotImplementedError


def event_driven_criterion(id: str, trigger: str, system: str, action: str) -> Criterion:
    """Create an event-driven EARS criterion."""
    raise NotImplementedError


def complex_event_criterion(id: str, trigger: str, condition: str, system: str, action: str) -> Criterion:
    """Create a complex-event EARS criterion."""
    raise NotImplementedError


def state_driven_criterion(id: str, state: str, system: str, action: str) -> Criterion:
    """Create a state-driven EARS criterion."""
    raise NotImplementedError


def unwanted_criterion(id: str, error_condition: str, system: str, action: str) -> Criterion:
    """Create an unwanted-behavior EARS criterion."""
    raise NotImplementedError


def optional_criterion(id: str, feature: str, system: str, action: str) -> Criterion:
    """Create an optional-feature EARS criterion."""
    raise NotImplementedError
