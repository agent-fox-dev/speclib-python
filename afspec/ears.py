"""EARS sentence rendering from criterion fields."""

from __future__ import annotations

from afspec.models import Criterion


def render_ears_sentence(c: Criterion) -> str:
    """Render an EARS sentence from a criterion's fields."""
    raise NotImplementedError
