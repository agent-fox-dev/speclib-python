"""Schema and cross-file validation for spec packages."""

from __future__ import annotations

from pydantic import BaseModel

from afspec.models import Spec


class ValidationError(BaseModel):
    """A single validation error."""

    file: str = ""
    path: str = ""
    message: str = ""
    rule: str = ""


def validate_schema(spec: Spec) -> list[ValidationError]:
    """Validate spec artifacts against bundled JSON Schemas."""
    raise NotImplementedError


def validate_cross_file(spec: Spec) -> list[ValidationError]:
    """Check cross-file integrity rules."""
    raise NotImplementedError


def validate(spec: Spec) -> list[ValidationError]:
    """Run both schema and cross-file validation."""
    raise NotImplementedError
