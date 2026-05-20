"""Tests for afspec I/O: loading, saving, serialization, and error handling."""

from __future__ import annotations

import concurrent.futures
import json
import os
import shutil
import stat
from pathlib import Path

import pytest

import afspec
from afspec import LoadError, SaveError

# ---------------------------------------------------------------------------
# TS-01-5: Integration — load_spec succeeds on valid fixture
# ---------------------------------------------------------------------------


def test_load_spec(valid_spec_dir: Path) -> None:
    """Load a valid spec from disk and verify all artifacts have spec_id set."""
    spec = afspec.load_spec(valid_spec_dir)

    assert spec.prd.frontmatter.spec_id != ""
    assert spec.requirements.spec_id != ""
    assert spec.test_spec.spec_id != ""
    assert spec.tasks.spec_id != ""


# ---------------------------------------------------------------------------
# TS-01-6: PRD frontmatter is correctly parsed
# ---------------------------------------------------------------------------


def test_prd_frontmatter_parsed(valid_spec_dir: Path) -> None:
    """Verify frontmatter fields are populated and body excludes delimiters."""
    spec = afspec.load_spec(valid_spec_dir)

    assert spec.prd.frontmatter.spec_id == "01"
    assert spec.prd.frontmatter.title == "Test Feature"
    assert "## Intent" in spec.prd.body
    assert "---" not in spec.prd.body


# ---------------------------------------------------------------------------
# TS-01-7: JSON artifacts are deserialized into rich models
# ---------------------------------------------------------------------------


def test_json_artifacts_deserialized(valid_spec_dir: Path) -> None:
    """Verify requirements, test_spec, and tasks are fully deserialized."""
    spec = afspec.load_spec(valid_spec_dir)

    # Requirements
    assert spec.requirements.introduction != ""
    assert len(spec.requirements.requirements) > 0

    # TestSpec
    assert len(spec.test_spec.test_cases) > 0

    # Tasks
    assert len(spec.tasks.task_groups) > 0


# ---------------------------------------------------------------------------
# TS-01-8: Integration — save writes all four files
# ---------------------------------------------------------------------------


def test_save_writes_files(valid_spec_dir: Path, tmp_spec_dir: Path) -> None:
    """Save a loaded spec and verify all four artifact files are written."""
    spec = afspec.load_spec(valid_spec_dir)
    afspec.save(spec, tmp_spec_dir)

    expected_files = ["prd.md", "requirements.json", "test_spec.json", "tasks.json"]
    for name in expected_files:
        path = tmp_spec_dir / name
        assert path.exists(), f"{name} was not written"
        assert path.stat().st_size > 0, f"{name} is empty"


# ---------------------------------------------------------------------------
# TS-01-9: Deterministic JSON serialization
# ---------------------------------------------------------------------------


def test_deterministic_json() -> None:
    """marshal_json produces stable, sorted, 2-space-indented output."""
    req = afspec.Requirements(
        glossary={"zebra": "z", "alpha": "a"},
        spec_id="01",
        spec_name="test",
        introduction="intro",
    )

    output_a = afspec.marshal_json(req)
    output_b = afspec.marshal_json(req)

    assert output_a == output_b, "marshal_json is not deterministic"
    assert output_a.endswith("}\n"), "JSON output must end with '}\\n'"

    # Verify 2-space indent (at least one line should start with two spaces)
    lines = output_a.splitlines()
    assert any(line.startswith("  ") for line in lines), "Expected 2-space indentation"

    # Sorted keys: "alpha" must appear before "zebra"
    alpha_pos = output_a.index('"alpha"')
    zebra_pos = output_a.index('"zebra"')
    assert alpha_pos < zebra_pos, "Keys are not sorted: 'alpha' should precede 'zebra'"


# ---------------------------------------------------------------------------
# TS-01-10: Atomic writes leave no temp files
# ---------------------------------------------------------------------------


def test_atomic_writes(valid_spec_dir: Path, tmp_spec_dir: Path) -> None:
    """After save, no .tmp files remain and requirements.json is valid JSON."""
    spec = afspec.load_spec(valid_spec_dir)
    afspec.save(spec, tmp_spec_dir)

    tmp_files = list(tmp_spec_dir.glob("*.tmp*"))
    assert tmp_files == [], f"Temporary files remain: {tmp_files}"

    req_path = tmp_spec_dir / "requirements.json"
    content = req_path.read_text(encoding="utf-8")
    json.loads(content)  # Should not raise


# ---------------------------------------------------------------------------
# TS-01-11: updated_at is auto-set on save
# ---------------------------------------------------------------------------


def test_updated_at_auto_set(valid_spec_dir: Path, tmp_spec_dir: Path) -> None:
    """Save and reload a spec; updated_at should differ from the original."""
    spec = afspec.load_spec(valid_spec_dir)
    original_updated = spec.prd.frontmatter.updated_at

    afspec.save(spec, tmp_spec_dir)
    reloaded = afspec.load_spec(tmp_spec_dir)

    assert reloaded.prd.frontmatter.updated_at != original_updated


# ---------------------------------------------------------------------------
# TS-01-12: coverage is auto-computed on save
# ---------------------------------------------------------------------------


def test_coverage_auto_computed(valid_spec_dir: Path, tmp_spec_dir: Path) -> None:
    """Save and reload; coverage.requirements_covered should be non-empty."""
    spec = afspec.load_spec(valid_spec_dir)
    afspec.save(spec, tmp_spec_dir)

    reloaded = afspec.load_spec(tmp_spec_dir)
    assert len(reloaded.test_spec.coverage.requirements_covered) > 0


# ---------------------------------------------------------------------------
# TS-01-E2: Load with missing files raises LoadError
# ---------------------------------------------------------------------------


def test_load_missing_files(tmp_spec_dir: Path, valid_spec_dir: Path) -> None:
    """A directory with only prd.md (missing other 3 files) raises LoadError."""
    shutil.copy(valid_spec_dir / "prd.md", tmp_spec_dir / "prd.md")

    with pytest.raises(LoadError):
        afspec.load_spec(tmp_spec_dir)


# ---------------------------------------------------------------------------
# TS-01-E3: Malformed JSON raises LoadError
# ---------------------------------------------------------------------------


def test_load_malformed_json(tmp_spec_dir: Path, valid_spec_dir: Path) -> None:
    """A directory with broken requirements.json raises LoadError mentioning the file."""
    # Copy all valid files first
    for name in ["prd.md", "test_spec.json", "tasks.json"]:
        shutil.copy(valid_spec_dir / name, tmp_spec_dir / name)

    # Write broken JSON for requirements.json
    (tmp_spec_dir / "requirements.json").write_text("{broken", encoding="utf-8")

    with pytest.raises(LoadError, match="requirements.json"):
        afspec.load_spec(tmp_spec_dir)


# ---------------------------------------------------------------------------
# TS-01-E4: Bad frontmatter raises LoadError
# ---------------------------------------------------------------------------


def test_load_bad_frontmatter(tmp_spec_dir: Path, valid_spec_dir: Path) -> None:
    """A prd.md without --- delimiters raises LoadError mentioning frontmatter."""
    # Copy JSON artifacts from valid spec
    for name in ["requirements.json", "test_spec.json", "tasks.json"]:
        shutil.copy(valid_spec_dir / name, tmp_spec_dir / name)

    # Write prd.md with no frontmatter delimiters
    (tmp_spec_dir / "prd.md").write_text(
        "# Title\n\nJust a markdown file with no frontmatter.\n",
        encoding="utf-8",
    )

    with pytest.raises(LoadError, match="frontmatter"):
        afspec.load_spec(tmp_spec_dir)


# ---------------------------------------------------------------------------
# TS-01-E5: Save to nonexistent directory raises SaveError
# ---------------------------------------------------------------------------


def test_save_nonexistent_dir(valid_spec_dir: Path) -> None:
    """Saving to a path that does not exist raises SaveError."""
    spec = afspec.load_spec(valid_spec_dir)

    with pytest.raises(SaveError):
        afspec.save(spec, "/nonexistent/path/xyz")


# ---------------------------------------------------------------------------
# TS-01-E6: Partial failure cleanup
# ---------------------------------------------------------------------------


def test_save_partial_failure_cleanup(valid_spec_dir: Path, tmp_spec_dir: Path) -> None:
    """Write failure leaves no .tmp files behind."""
    spec = afspec.load_spec(valid_spec_dir)

    # Create a read-only subdirectory to provoke a write failure
    target = tmp_spec_dir / "readonly_target"
    target.mkdir()
    # Pre-create a file that will block directory writes
    (target / "requirements.json").write_text("{}", encoding="utf-8")
    os.chmod(target, stat.S_IRUSR | stat.S_IXUSR)

    try:
        with pytest.raises(SaveError):
            afspec.save(spec, target)

        # Regardless of failure, no temp files should remain
        # Restore permissions so we can inspect
        os.chmod(target, stat.S_IRWXU)
        tmp_files = list(target.glob("*.tmp*"))
        assert tmp_files == [], f"Temporary files remain after failure: {tmp_files}"
    finally:
        # Ensure cleanup can proceed
        os.chmod(target, stat.S_IRWXU)


# ---------------------------------------------------------------------------
# TS-01-E7: Integration — concurrent saves
# ---------------------------------------------------------------------------


def test_save_concurrent(valid_spec_dir: Path, tmp_spec_dir: Path) -> None:
    """Five concurrent saves to the same directory all succeed with valid JSON."""
    spec = afspec.load_spec(valid_spec_dir)

    def do_save(_i: int) -> None:
        afspec.save(spec, tmp_spec_dir)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(do_save, i) for i in range(5)]
        for f in concurrent.futures.as_completed(futures):
            f.result()  # Raises if any save failed

    # Final files should be valid JSON
    for name in ["requirements.json", "test_spec.json", "tasks.json"]:
        content = (tmp_spec_dir / name).read_text(encoding="utf-8")
        json.loads(content)  # Must not raise


# ---------------------------------------------------------------------------
# Property TS-01-P1: Round-trip preserves key fields
# ---------------------------------------------------------------------------


def test_property_round_trip(valid_spec_dir: Path, tmp_spec_dir: Path) -> None:
    """Load -> save -> reload preserves key fields (excluding updated_at, coverage)."""
    original = afspec.load_spec(valid_spec_dir)
    afspec.save(original, tmp_spec_dir)
    reloaded = afspec.load_spec(tmp_spec_dir)

    # PRD
    assert reloaded.prd.frontmatter.spec_id == original.prd.frontmatter.spec_id
    assert reloaded.prd.frontmatter.title == original.prd.frontmatter.title
    assert reloaded.prd.body == original.prd.body

    # Requirements
    assert reloaded.requirements.spec_id == original.requirements.spec_id
    assert reloaded.requirements.introduction == original.requirements.introduction
    assert len(reloaded.requirements.requirements) == len(original.requirements.requirements)

    # TestSpec
    assert reloaded.test_spec.spec_id == original.test_spec.spec_id
    assert len(reloaded.test_spec.test_cases) == len(original.test_spec.test_cases)

    # Tasks
    assert reloaded.tasks.spec_id == original.tasks.spec_id
    assert len(reloaded.tasks.task_groups) == len(original.tasks.task_groups)


# ---------------------------------------------------------------------------
# Property TS-01-P7: Atomic save leaves no temp files
# ---------------------------------------------------------------------------


def test_property_atomic_save(valid_spec_dir: Path, tmp_spec_dir: Path) -> None:
    """After a successful save, no .tmp files remain."""
    spec = afspec.load_spec(valid_spec_dir)
    afspec.save(spec, tmp_spec_dir)

    tmp_files = list(tmp_spec_dir.glob("*.tmp*"))
    assert tmp_files == [], f"Temporary files remain: {tmp_files}"


# ---------------------------------------------------------------------------
# Property TS-01-P10: Coverage correctness
# ---------------------------------------------------------------------------


def test_property_coverage_correctness(valid_spec_dir: Path) -> None:
    """compute_coverage returns non-empty requirements_covered."""
    spec = afspec.load_spec(valid_spec_dir)

    coverage = afspec.compute_coverage(spec.test_spec, spec.requirements)
    assert len(coverage.requirements_covered) > 0
