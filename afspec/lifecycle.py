"""Lifecycle state machine management."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from afspec.models import Spec, Status


def transition(spec: Spec, target: Status, dir: Union[str, Path]) -> Spec:
    """Transition a spec to a new lifecycle state."""
    raise NotImplementedError


def supersede(spec: Spec, superseding_spec_id: str, dir: Union[str, Path]) -> Spec:
    """Mark a sealed spec as superseded."""
    raise NotImplementedError


def move_to_archive(spec_dir: Union[str, Path], root: Union[str, Path]) -> None:
    """Archive a spec by transitioning and moving to archive/ folder."""
    raise NotImplementedError
