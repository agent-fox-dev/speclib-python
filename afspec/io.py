"""File I/O for loading and saving spec packages."""

from __future__ import annotations

from pathlib import Path
from typing import Union

from afspec.models import Spec


def load_spec(dir: Union[str, Path]) -> Spec:
    """Load a spec from a directory containing all four artifact files."""
    raise NotImplementedError


def save(spec: Spec, dir: Union[str, Path]) -> None:
    """Save a spec to disk atomically."""
    raise NotImplementedError


def marshal_json(model: object) -> str:
    """Serialize a Pydantic model to deterministic JSON."""
    raise NotImplementedError
