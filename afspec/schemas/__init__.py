"""Bundled JSON Schema files for spec validation."""

from __future__ import annotations


def schemas() -> dict[str, bytes]:
    """Return a dict of schema name -> schema bytes."""
    raise NotImplementedError
