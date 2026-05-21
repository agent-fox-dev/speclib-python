# Implementation Plan: Architecture Support

<!-- AGENT INSTRUCTIONS
- Implement exactly ONE top-level task group per session
- Task group 1 writes failing tests from test_spec.md — all subsequent groups
  implement code to make those tests pass
- Follow the git-flow: feature branch from develop -> implement -> test -> merge to develop
- Update checkbox states as you go: [-] in progress, [x] complete
-->

## Overview

This implementation adds optional `architecture.md` support to the `afspec`
library. Task group 1 writes failing tests. Task group 2 implements the
model and I/O changes (the core). Task group 3 adds rendering and bootstrap
support. Task group 4 verifies wiring end-to-end. The ordering ensures
model and I/O are in place before rendering and bootstrap depend on them.

## Test Commands

- Spec tests: `uv run pytest -q tests/test_architecture.py`
- Unit tests: `uv run pytest -q tests/`
- Property tests: `uv run pytest -q tests/test_architecture.py -k property`
- All tests: `uv run pytest -q`
- Linter: `uv run ruff check`

## Tasks

- [x] 1. Write failing spec tests
  - [x] 1.1 Create test file structure
    - Create `tests/test_architecture.py` with imports from `afspec`
    - Set up test fixtures for valid spec creation (reuse existing conftest patterns)
    - Set up temp directory fixtures for I/O tests
    - _Test Spec: TS-02-1 through TS-02-15, TS-02-E1 through TS-02-E5_

  - [x] 1.2 Translate model and I/O acceptance-criterion tests
    - TS-02-1: Spec model architecture field
    - TS-02-2: load_spec with architecture.md present
    - TS-02-3: load_spec without architecture.md
    - TS-02-4: save with architecture content
    - TS-02-5: save without architecture content
    - TS-02-6: _save_internal with architecture
    - TS-02-7: _save_internal without architecture
    - _Test Spec: TS-02-1 through TS-02-7_

  - [x] 1.3 Translate validation and rendering tests
    - TS-02-8: validate_schema ignores architecture
    - TS-02-9: validate_cross_file ignores architecture
    - TS-02-10: load_spec requires only four files
    - TS-02-11: render_combined with architecture
    - TS-02-12: render_combined without architecture
    - _Test Spec: TS-02-8 through TS-02-12_

  - [x] 1.4 Translate bootstrap tests
    - TS-02-13: set_architecture stores content
    - TS-02-14: finalize with architecture
    - TS-02-15: finalize without architecture
    - _Test Spec: TS-02-13 through TS-02-15_

  - [x] 1.5 Translate edge case and property tests
    - TS-02-E1: default construction
    - TS-02-E2: empty architecture.md
    - TS-02-E3: save with empty string architecture
    - TS-02-E4: validation unchanged by architecture
    - TS-02-E5: render with empty architecture string
    - TS-02-P1: round-trip preservation
    - TS-02-P2: None preserves absence
    - TS-02-P3: validation neutrality
    - TS-02-P4: combined render ordering
    - _Test Spec: TS-02-E1 through TS-02-E5, TS-02-P1 through TS-02-P4_

  - [x] 1.6 Translate integration smoke tests
    - TS-02-SMOKE-1: load-save round-trip with architecture
    - TS-02-SMOKE-2: combined rendering end-to-end
    - TS-02-SMOKE-3: bootstrap finalize with architecture
    - _Test Spec: TS-02-SMOKE-1 through TS-02-SMOKE-3_

  - [x] 1.V Verify task group 1
    - [x] All spec tests exist and are syntactically valid
    - [x] All spec tests FAIL (red) — no implementation yet
    - [x] No linter warnings introduced: `uv run ruff check`

- [x] 2. Implement model and I/O changes
  - [x] 2.1 Add architecture field to Spec model
    - Add `architecture: str | None = None` field to `Spec` class in `models.py`
    - Field goes after `tasks` and before the `_loaded` private attribute
    - _Requirements: 02-REQ-1.1, 02-REQ-1.E1_

  - [x] 2.2 Update load_spec to read architecture.md
    - In `io.py: load_spec`, after loading four required artifacts:
    - Check if `architecture.md` exists in the directory
    - If present, read its content as UTF-8 text
    - Pass content to `Spec` constructor via `architecture=` parameter
    - If absent, leave architecture as None (default)
    - _Requirements: 02-REQ-2.1, 02-REQ-2.2, 02-REQ-2.E1_

  - [x] 2.3 Update save to write architecture.md
    - In `io.py: save`, after writing the four required artifacts:
    - If `spec.architecture is not None`, call `_atomic_write(dir_path / "architecture.md", spec.architecture)`
    - If `spec.architecture is None`, do nothing
    - _Requirements: 02-REQ-3.1, 02-REQ-3.2, 02-REQ-3.E1_

  - [x] 2.4 Update _save_internal to write architecture.md
    - Same logic as save: write architecture.md when non-None, skip when None
    - _Requirements: 02-REQ-3.3, 02-REQ-3.4_

  - [x] 2.V Verify task group 2
    - [x] Spec tests for this group pass: `uv run pytest -q tests/test_architecture.py -k "test_model or test_load or test_save"`
    - [x] All existing tests still pass: `uv run pytest -q`
    - [x] No linter warnings introduced: `uv run ruff check`
    - [x] Requirements 02-REQ-1.1, 02-REQ-1.E1, 02-REQ-2.1, 02-REQ-2.2, 02-REQ-2.E1, 02-REQ-3.1, 02-REQ-3.2, 02-REQ-3.3, 02-REQ-3.4, 02-REQ-3.E1 acceptance criteria met

- [x] 3. Implement rendering and bootstrap changes
  - [x] 3.1 Update render_combined to include architecture
    - In `render.py: render_combined`, after appending PRD body:
    - If `spec.architecture is not None`, append architecture content (rstripped) between separator rules
    - If None, keep existing behavior unchanged
    - _Requirements: 02-REQ-5.1, 02-REQ-5.2, 02-REQ-5.E1_

  - [x] 3.2 Add set_architecture to BootstrapSpec
    - In `bootstrap.py`, add `_architecture: Optional[str] = None` instance variable
    - Add `set_architecture(self, content: str) -> None` method
    - _Requirements: 02-REQ-6.1_

  - [x] 3.3 Update BootstrapSpec.finalize to pass architecture
    - In `finalize`, pass `architecture=self._architecture` when constructing Spec
    - _Requirements: 02-REQ-6.2, 02-REQ-6.3_

  - [x] 3.V Verify task group 3
    - [x] Spec tests for this group pass: `uv run pytest -q tests/test_architecture.py -k "test_render or test_bootstrap"`
    - [x] All existing tests still pass: `uv run pytest -q`
    - [x] No linter warnings introduced: `uv run ruff check`
    - [x] Requirements 02-REQ-5.1, 02-REQ-5.2, 02-REQ-5.E1, 02-REQ-6.1, 02-REQ-6.2, 02-REQ-6.3 acceptance criteria met

- [ ] 4. Checkpoint - All Tests Green
  - Ensure all tests pass including property tests and smoke tests.
  - Run `make check` for full quality gate.

- [ ] 5. Wiring verification

  - [ ] 5.1 Trace every execution path from design.md end-to-end
    - Path 1: load_spec reads architecture.md → Spec.architecture populated
    - Path 2: save writes architecture.md from Spec.architecture
    - Path 3: render_combined includes architecture between PRD and requirements
    - Path 4: BootstrapSpec.set_architecture → finalize → Spec.architecture
    - For each path, verify the entry point actually calls the next function
    - Confirm no stub remains
    - _Requirements: all_

  - [ ] 5.2 Verify return values propagate correctly
    - load_spec returns Spec with architecture field populated
    - render_combined uses spec.architecture in output
    - finalize passes _architecture to Spec constructor
    - _Requirements: all_

  - [ ] 5.3 Run the integration smoke tests
    - All TS-02-SMOKE-* tests pass using real components
    - `uv run pytest -q tests/test_architecture.py -k smoke`
    - _Test Spec: TS-02-SMOKE-1 through TS-02-SMOKE-3_

  - [ ] 5.4 Stub / dead-code audit
    - Search all files touched by this spec for: `return []`, `return None`
      on non-Optional returns, `pass` in non-abstract methods, `# TODO`,
      `# stub`, `NotImplementedError`
    - Each hit must be justified or replaced
    - _Requirements: all_

  - [ ] 5.5 Cross-spec entry point verification
    - All entry points (load_spec, save, _save_internal, render_combined,
      BootstrapSpec methods) are public API or used by lifecycle.py
    - Verify callers exist in production code
    - _Requirements: all_

  - [ ] 5.V Verify wiring group
    - [ ] All smoke tests pass
    - [ ] No unjustified stubs remain in touched files
    - [ ] All execution paths from design.md are live (traceable in code)
    - [ ] All cross-spec entry points are called from production code
    - [ ] All existing tests still pass: `uv run pytest -q`

## Traceability

| Requirement | Test Spec Entry | Implemented By Task | Verified By Test |
|-------------|-----------------|---------------------|------------------|
| 02-REQ-1.1 | TS-02-1 | 2.1 | tests/test_architecture.py::test_model_architecture_field |
| 02-REQ-1.E1 | TS-02-E1 | 2.1 | tests/test_architecture.py::test_model_default_none |
| 02-REQ-2.1 | TS-02-2 | 2.2 | tests/test_architecture.py::test_load_with_architecture |
| 02-REQ-2.2 | TS-02-3 | 2.2 | tests/test_architecture.py::test_load_without_architecture |
| 02-REQ-2.E1 | TS-02-E2 | 2.2 | tests/test_architecture.py::test_load_empty_architecture |
| 02-REQ-3.1 | TS-02-4 | 2.3 | tests/test_architecture.py::test_save_with_architecture |
| 02-REQ-3.2 | TS-02-5 | 2.3 | tests/test_architecture.py::test_save_without_architecture |
| 02-REQ-3.3 | TS-02-6 | 2.4 | tests/test_architecture.py::test_save_internal_with_architecture |
| 02-REQ-3.4 | TS-02-7 | 2.4 | tests/test_architecture.py::test_save_internal_without_architecture |
| 02-REQ-3.E1 | TS-02-E3 | 2.3 | tests/test_architecture.py::test_save_empty_architecture |
| 02-REQ-4.1 | TS-02-8 | — | tests/test_architecture.py::test_validate_schema_ignores_architecture |
| 02-REQ-4.2 | TS-02-9 | — | tests/test_architecture.py::test_validate_cross_file_ignores_architecture |
| 02-REQ-4.3 | TS-02-10 | — | tests/test_architecture.py::test_load_requires_only_four_files |
| 02-REQ-4.E1 | TS-02-E4 | — | tests/test_architecture.py::test_validate_unchanged_by_architecture |
| 02-REQ-5.1 | TS-02-11 | 3.1 | tests/test_architecture.py::test_render_combined_with_architecture |
| 02-REQ-5.2 | TS-02-12 | 3.1 | tests/test_architecture.py::test_render_combined_without_architecture |
| 02-REQ-5.E1 | TS-02-E5 | 3.1 | tests/test_architecture.py::test_render_combined_empty_architecture |
| 02-REQ-6.1 | TS-02-13 | 3.2 | tests/test_architecture.py::test_bootstrap_set_architecture |
| 02-REQ-6.2 | TS-02-14 | 3.3 | tests/test_architecture.py::test_bootstrap_finalize_with_architecture |
| 02-REQ-6.3 | TS-02-15 | 3.3 | tests/test_architecture.py::test_bootstrap_finalize_without_architecture |
| Property 1 | TS-02-P1 | 2.2, 2.3 | tests/test_architecture.py::test_property_round_trip |
| Property 2 | TS-02-P2 | 2.2, 2.3 | tests/test_architecture.py::test_property_none_preserves_absence |
| Property 3 | TS-02-P3 | — | tests/test_architecture.py::test_property_validation_neutrality |
| Property 4 | TS-02-P4 | 3.1 | tests/test_architecture.py::test_property_render_ordering |
| Paths 1+2 | TS-02-SMOKE-1 | 2.2, 2.3 | tests/test_architecture.py::test_smoke_load_save_roundtrip |
| Path 3 | TS-02-SMOKE-2 | 3.1 | tests/test_architecture.py::test_smoke_combined_rendering |
| Path 4 | TS-02-SMOKE-3 | 3.2, 3.3 | tests/test_architecture.py::test_smoke_bootstrap_finalize |

## Notes

- Validation (02-REQ-4.*) requires no implementation changes — the existing
  validation code already only validates the four known artifacts. The tests
  confirm this behavior is preserved.
- The `_ARTIFACT_FILES` constant in `io.py` should NOT include `architecture.md`
  since it lists required files only.
- lifecycle.py changes are unnecessary — `_save_internal` is defined in `io.py`
  and lifecycle.py calls it. The `move_to_archive` function uses `shutil.move`
  on the entire directory, so architecture.md moves automatically.
