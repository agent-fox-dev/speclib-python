# Implementation Plan: afspec

<!-- AGENT INSTRUCTIONS
- Implement exactly ONE top-level task group per session
- Task group 1 writes failing tests from test_spec.md — all subsequent groups
  implement code to make those tests pass
- Follow the git-flow: feature branch from develop -> implement -> test -> merge to develop
- Update checkbox states as you go: [-] in progress, [x] complete
-->

## Overview

The implementation builds the `afspec` Python library in layers: Pydantic models and
constructors first, then I/O, then validation, lifecycle, rendering, discovery, and
programmatic construction API. Task group 1 writes all failing tests from the test
specification. Subsequent groups implement code to make those tests pass, with
checkpoints after core I/O and after validation. Group 12 implements the mutation
API (add/get/remove functions, ID helpers). The final group (13) is wiring verification.

Golden fixture files in `tests/golden/` are created in group 2 and used
throughout. The Makefile and pyproject.toml are created in group 2 to establish
the quality gate from the start.

## Test Commands

- Spec tests: `uv run pytest -v -k 'test_spec' tests/`
- Unit tests: `uv run pytest -v tests/`
- Property tests: `uv run pytest -v -k 'test_property' tests/`
- All tests: `uv run pytest -q`
- Linter: `uv run ruff check && uv run mypy afspec/`

## Tasks

- [x] 1. Write failing spec tests
  - [x] 1.1 Create project structure and golden fixtures
    - Create `pyproject.toml` with dependencies (pydantic, PyYAML, jsonschema)
    - Create `afspec/__init__.py` with empty exports
    - Create `afspec/models.py` with stub classes
    - Create `tests/conftest.py` with shared fixtures
    - Create `tests/test_models.py` for type and constructor tests
    - Create `tests/test_io.py` for load/save tests
    - Create `tests/test_validation.py` for schema and cross-file tests
    - Create `tests/test_lifecycle.py` for lifecycle and intent hash tests
    - Create `tests/test_bootstrap.py` for bootstrap mode tests
    - Create `tests/test_render.py` for rendering tests
    - Create `tests/test_discovery.py` for discovery tests
    - Create `tests/test_mutate.py` for mutation API tests
    - Create `tests/golden/valid_spec/` with all four artifact files (valid, complete spec)
    - Create `tests/golden/draft_spec/` with a spec in draft state
    - _Test Spec: TS-01-1 through TS-01-53, TS-01-E1 through TS-01-E34, TS-01-P1 through TS-01-P12, TS-01-SMOKE-1 through TS-01-SMOKE-9_

  - [x] 1.2 Translate unit tests for data model types
    - TS-01-1: Spec model has all four artifact fields
    - TS-01-2: Criterion supports six EARS patterns
    - TS-01-3: SubtaskState valid_transition for all 30 pairs
    - TS-01-4: All sub-types are importable
    - _Test Spec: TS-01-1, TS-01-2, TS-01-3, TS-01-4_

  - [x] 1.3 Translate unit and integration tests for file I/O
    - TS-01-5: load_spec reads all four artifacts
    - TS-01-6: PRD frontmatter and body parsed correctly
    - TS-01-7: JSON artifacts deserialized correctly
    - TS-01-8: save writes all four files
    - TS-01-9: Deterministic JSON serialization
    - TS-01-10: Atomic file writes
    - TS-01-11: updated_at auto-set on save
    - TS-01-12: Coverage auto-computed on save
    - _Test Spec: TS-01-5 through TS-01-12_

  - [x] 1.4 Translate tests for validation, lifecycle, bootstrap, rendering, discovery, intent hash
    - TS-01-13 through TS-01-41, TS-01-52, TS-01-53 (remaining unit/integration tests)
    - _Test Spec: TS-01-13 through TS-01-41, TS-01-52, TS-01-53_

  - [x] 1.5 Translate edge case tests
    - TS-01-E1 through TS-01-E27 (data model, I/O, validation, lifecycle, discovery, mutation)
    - TS-01-E28 through TS-01-E34 (supersede, archive, and traceability edge cases)
    - _Test Spec: TS-01-E1 through TS-01-E34_

  - [x] 1.6 Translate property tests and smoke tests
    - TS-01-P1 through TS-01-P12
    - TS-01-SMOKE-1 through TS-01-SMOKE-9
    - _Test Spec: TS-01-P1 through TS-01-P12, TS-01-SMOKE-1 through TS-01-SMOKE-9_

  - [x] 1.V Verify task group 1
    - [x] All spec tests exist and are syntactically valid: `uv run python -m py_compile tests/test_models.py tests/test_io.py tests/test_validation.py tests/test_lifecycle.py tests/test_bootstrap.py tests/test_render.py tests/test_discovery.py tests/test_mutate.py`
    - [x] All spec tests FAIL (red) — no implementation yet: `uv run pytest -q 2>&1 | grep FAILED`
    - [x] No linter warnings introduced: `uv run ruff check`

- [x] 2. Data model types and build system
  - [x] 2.1 Create Makefile with check, test, lint targets
    - `make check` runs `uv run ruff check && uv run mypy afspec/ && uv run pytest -q`
    - `make test` runs `uv run pytest -q`
    - `make lint` runs `uv run ruff check && uv run mypy afspec/`
    - _Requirements: all (build infrastructure)_

  - [x] 2.2 Implement enums in models.py
    - `Status` enum with five values (str, Enum)
    - `EARSPattern` enum with six values (str, Enum)
    - `SubtaskState` enum with six values (str, Enum) and `valid_transition` function
    - `TaskGroupKind` enum with four values (str, Enum)
    - _Requirements: 01-REQ-1.1, 01-REQ-1.3_

  - [x] 2.3 Implement PRD models in models.py
    - `PRDDocument` and `PRDFrontmatter` Pydantic models
    - Field declarations in spec-format.md §4.1 order
    - _Requirements: 01-REQ-1.1_

  - [x] 2.4 Implement requirements models in models.py
    - `Requirements`, `Requirement`, `UserStory`, `Criterion`, `CorrectnessProperty`, `ExecutionPath`, `PathStep`, `ErrorHandlingEntry`
    - `Criterion` with common + pattern-specific fields (Optional for pattern-specific)
    - `with_return_contract` method on `Criterion`
    - _Requirements: 01-REQ-1.2, 01-REQ-1.4_

  - [x] 2.5 Implement test_spec and tasks models in models.py
    - `TestSpec`, `TestCase`, `PropertyTest`, `EdgeCaseTest`, `SmokeTest`, `Coverage`
    - `Tasks`, `TestCommands`, `TaskDependency`, `TaskGroup`, `Subtask`, `VerificationSubtask`, `TraceabilityEntry`
    - `Any` for `input` and `expected` fields
    - `transition_to` method on `Subtask`
    - _Requirements: 01-REQ-1.4_

  - [x] 2.6 Implement factory functions in constructors.py
    - `create_spec(spec_id, spec_name)` → `Spec`
    - Six EARS criterion builders: `ubiquitous_criterion`, `event_driven_criterion`, `complex_event_criterion`, `state_driven_criterion`, `unwanted_criterion`, `optional_criterion`
    - _Requirements: 01-REQ-1.5, 01-REQ-1.6, 01-REQ-11.7_

  - [x] 2.V Verify task group 2
    - [x] Type tests pass: `uv run pytest -v -k 'test_spec_model or test_criterion or test_subtask_state or test_sub_types' tests/`
    - [x] Constructor tests pass: `uv run pytest -v -k 'test_create or test_with_return' tests/`
    - [x] All existing tests still pass: `uv run pytest -q`
    - [x] No linter warnings introduced: `uv run ruff check && uv run mypy afspec/`
    - [x] Requirements 01-REQ-1.1 through 01-REQ-1.7 acceptance criteria met

- [x] 3. File I/O — Load
  - [x] 3.1 Implement PRD parser in io.py
    - Parse YAML frontmatter (between `---` delimiters) using PyYAML
    - Extract markdown body (everything after closing `---`)
    - Return `PRDDocument`
    - _Requirements: 01-REQ-2.2_

  - [x] 3.2 Implement JSON artifact loader in io.py
    - Read and deserialize `requirements.json`, `test_spec.json`, `tasks.json`
    - Use `json.loads` then Pydantic `model_validate`
    - _Requirements: 01-REQ-2.3_

  - [x] 3.3 Implement load_spec orchestrator in io.py
    - Check all four files exist, raise LoadError listing missing ones
    - Call PRD parser and JSON loader
    - Assemble and return `Spec`
    - Capture `_ImmutableSnapshot` from PRD frontmatter
    - _Requirements: 01-REQ-2.1_

  - [x] 3.4 Implement compute_intent_hash in intent.py
    - Extract text between `## Intent` and next `##` (or EOF)
    - Normalize: LF line endings, collapse blank lines, lower-case, trim
    - Compute SHA-256, return lowercase hex
    - Handle missing/empty intent section edge cases
    - _Requirements: 01-REQ-10.1, 01-REQ-10.2_

  - [x] 3.V Verify task group 3
    - [x] Load tests pass: `uv run pytest -v -k 'test_load or test_prd or test_json or test_intent' tests/`
    - [x] All existing tests still pass: `uv run pytest -q`
    - [x] No linter warnings introduced: `uv run ruff check && uv run mypy afspec/`
    - [x] Requirements 01-REQ-2.1, 01-REQ-2.2, 01-REQ-2.3, 01-REQ-10.1, 01-REQ-10.2 acceptance criteria met

- [x] 4. File I/O — Save
  - [x] 4.1 Implement deterministic JSON serialization
    - Custom serializer: 2-space indent, trailing newline
    - Model fields in declaration order (Pydantic default)
    - Dict keys sorted alphabetically
    - Optional pattern-specific criterion fields excluded when None
    - _Requirements: 01-REQ-3.2_

  - [x] 4.2 Implement PRD frontmatter serialization in io.py
    - Render YAML frontmatter with `---` delimiters
    - Field order matches model declaration order
    - Concatenate with body
    - _Requirements: 01-REQ-3.1_

  - [x] 4.3 Implement atomic file writes in io.py
    - Write to temp file (same directory, random suffix) via `tempfile.NamedTemporaryFile`
    - `os.rename` to final path
    - Cleanup temp files on any failure
    - _Requirements: 01-REQ-3.3_

  - [x] 4.4 Implement compute_coverage in coverage.py
    - Scan test cases → requirements_covered
    - Scan property tests → properties_covered
    - Scan smoke tests → paths_covered
    - Diff against all IDs → gaps
    - _Requirements: 01-REQ-3.5_

  - [x] 4.5 Implement save orchestrator in io.py
    - Set `updated_at` to `datetime.now(UTC)` formatted as ISO 8601
    - Call `compute_coverage` and update `spec.test_spec.coverage`
    - Serialize all four files
    - Write atomically; rollback on failure
    - Mutation guard: reject saves for sealed/superseded/archived specs
    - Mutation guard: check immutable fields and intent hash for active specs
    - _Requirements: 01-REQ-3.1, 01-REQ-3.4_

  - [x] 4.V Verify task group 4
    - [x] Save tests pass: `uv run pytest -v -k 'test_save or test_deterministic or test_atomic or test_updated_at or test_coverage' tests/`
    - [x] Round-trip property test passes: `uv run pytest -v -k 'test_property_round_trip' tests/`
    - [x] All existing tests still pass: `uv run pytest -q`
    - [x] No linter warnings introduced: `uv run ruff check && uv run mypy afspec/`
    - [x] Requirements 01-REQ-3.1 through 01-REQ-3.5 acceptance criteria met

- [x] 5. Checkpoint - Core I/O Complete
  - Ensure all load/save tests pass, ask the user if questions arise.
  - Verify golden fixture round-trip works.
  - Update documentation if needed.

- [x] 6. Schema Validation
  - [x] 6.1 Create and embed JSON Schema files
    - Create `afspec/schemas/requirements.v1.json`
    - Create `afspec/schemas/test_spec.v1.json`
    - Create `afspec/schemas/tasks.v1.json`
    - Create `afspec/schemas/prd-frontmatter.v1.json`
    - Add `__init__.py` with schema loading via `importlib.resources`
    - _Requirements: 01-REQ-4.2_

  - [x] 6.2 Implement validate_schema in validation.py
    - Load schema bytes via `importlib.resources`
    - Use `jsonschema.validate` for each artifact
    - Collect all errors into `list[ValidationError]`
    - Enforce EARS pattern discriminated union
    - _Requirements: 01-REQ-4.1, 01-REQ-4.3_

  - [x] 6.3 Implement exceptions in exceptions.py
    - `SpecError` base class
    - `LoadError`, `SaveError`, `LifecycleError`, `IntentError`, `BootstrapError`
    - _Requirements: all (error handling infrastructure)_

  - [x] 6.V Verify task group 6
    - [x] Schema validation tests pass: `uv run pytest -v -k 'test_schema or test_ears_mismatch' tests/`
    - [x] All existing tests still pass: `uv run pytest -q`
    - [x] No linter warnings introduced: `uv run ruff check && uv run mypy afspec/`
    - [x] Requirements 01-REQ-4.1 through 01-REQ-4.3 acceptance criteria met

- [x] 7. Cross-File Integrity Validation
  - [x] 7.1 Implement validate_cross_file in validation.py
    - Check artifact completeness (empty spec_id sentinel)
    - Implement all eight cross-file integrity rules
    - Return `list[ValidationError]` with rule identifiers
    - _Requirements: 01-REQ-5.1 through 01-REQ-5.7_

  - [x] 7.2 Implement validate function in validation.py
    - Combine `validate_schema` and `validate_cross_file` results
    - _Requirements: 01-REQ-4.1, 01-REQ-5.1_

  - [x] 7.V Verify task group 7
    - [x] Cross-file tests pass: `uv run pytest -v -k 'test_cross_file or test_dangling or test_glossary or test_spec_id_consistency or test_duplicate_traceability' tests/`
    - [x] All existing tests still pass: `uv run pytest -q`
    - [x] No linter warnings introduced: `uv run ruff check && uv run mypy afspec/`
    - [x] Requirements 01-REQ-5.1 through 01-REQ-5.7 acceptance criteria met

- [x] 8. Lifecycle Management and Bootstrap
  - [x] 8.1 Implement lifecycle state machine in lifecycle.py
    - `_is_legal_transition` function
    - `transition(spec, target, dir)` function
    - Intent hash computation and storage on draft→active
    - Mutation guards (immutable fields, intent hash)
    - _Requirements: 01-REQ-6.1, 01-REQ-6.2, 01-REQ-6.3, 01-REQ-6.4, 01-REQ-6.5_

  - [x] 8.2 Implement supersede in lifecycle.py
    - `supersede(spec, superseding_spec_id, dir)` function
    - Deprecation banner prepend
    - Internal save
    - _Requirements: 01-REQ-6.6_

  - [x] 8.3 Implement move_to_archive in lifecycle.py
    - `move_to_archive(spec_dir, root)` function
    - Load, transition (if needed), save, move folder
    - Handle all state combinations
    - _Requirements: 01-REQ-6.7_

  - [x] 8.4 Implement bootstrap in bootstrap.py
    - `BootstrapSpec` class
    - `set_prd`, `set_requirements`, `set_test_spec`, `set_tasks` methods
    - `finalize` method with validation
    - _Requirements: 01-REQ-7.1, 01-REQ-7.2, 01-REQ-7.3_

  - [x] 8.V Verify task group 8
    - [x] Lifecycle tests pass: `uv run pytest -v -k 'test_lifecycle or test_transition or test_supersede or test_archive' tests/`
    - [x] Bootstrap tests pass: `uv run pytest -v -k 'test_bootstrap or test_finalize' tests/`
    - [x] All existing tests still pass: `uv run pytest -q`
    - [x] No linter warnings introduced: `uv run ruff check && uv run mypy afspec/`
    - [x] Requirements 01-REQ-6.1 through 01-REQ-6.7, 01-REQ-7.1 through 01-REQ-7.3 acceptance criteria met

- [x] 9. Checkpoint - Validation and Lifecycle Complete
  - Ensure all validation and lifecycle tests pass.
  - Run full property test suite.
  - Update documentation if needed.

- [ ] 10. Markdown Rendering
  - [ ] 10.1 Implement EARS sentence rendering in ears.py
    - `render_ears_sentence(criterion)` function
    - Six EARS templates
    - Return contract appending
    - _Requirements: 01-REQ-8.2_

  - [ ] 10.2 Implement render_requirements in render.py
    - Introduction, glossary table, requirements with EARS-rendered criteria
    - Correctness properties, execution paths, error handling table
    - _Requirements: 01-REQ-8.1_

  - [ ] 10.3 Implement render_test_spec in render.py
    - Test cases, property tests, edge case tests, smoke tests, coverage summary
    - _Requirements: 01-REQ-8.3_

  - [ ] 10.4 Implement render_tasks in render.py
    - Test commands, dependencies table, task groups with checkbox subtasks
    - Traceability table
    - Subtask state to checkbox mapping
    - Optional subtask marking
    - _Requirements: 01-REQ-8.4_

  - [ ] 10.5 Implement render_combined in render.py
    - PRD body (as-is) + rendered requirements + test_spec + tasks
    - _Requirements: 01-REQ-8.5_

  - [ ] 10.V Verify task group 10
    - [ ] Render tests pass: `uv run pytest -v -k 'test_render or test_ears' tests/`
    - [ ] Deterministic rendering property test passes: `uv run pytest -v -k 'test_property_deterministic' tests/`
    - [ ] All existing tests still pass: `uv run pytest -q`
    - [ ] No linter warnings introduced: `uv run ruff check && uv run mypy afspec/`
    - [ ] Requirements 01-REQ-8.1 through 01-REQ-8.6 acceptance criteria met

- [ ] 11. Spec Root Discovery
  - [ ] 11.1 Implement discover_specs in discovery.py
    - Scan root directory for matching pattern
    - Skip `archive/` subdirectory
    - Load PRD frontmatter only → `SpecMeta`
    - _Requirements: 01-REQ-9.1, 01-REQ-9.2_

  - [ ] 11.2 Implement build_dependency_graph in discovery.py
    - Parse `tasks.json` dependencies from each spec folder
    - Validate all references exist
    - Build directed graph, check for cycles
    - `DependencyGraph` class with `dependencies`, `dependents`, `topological_sort` methods
    - _Requirements: 01-REQ-9.3, 01-REQ-9.4, 01-REQ-9.5_

  - [ ] 11.V Verify task group 11
    - [ ] Discovery tests pass: `uv run pytest -v -k 'test_discover or test_dependency' tests/`
    - [ ] All existing tests still pass: `uv run pytest -q`
    - [ ] No linter warnings introduced: `uv run ruff check && uv run mypy afspec/`
    - [ ] Requirements 01-REQ-9.1 through 01-REQ-9.5 acceptance criteria met

- [ ] 12. Programmatic Construction API
  - [ ] 12.1 Implement collection mutation functions in mutate.py
    - `add_requirement`, `get_requirement`, `remove_requirement`
    - `set_glossary_entry`, `remove_glossary_entry`
    - `add_correctness_property`, `add_execution_path`, `add_error_handling`
    - `add_criterion`, `add_edge_case`, `get_criterion`
    - `add_test_case`, `add_property_test`, `add_edge_case_test`, `add_smoke_test`
    - `add_task_group`, `add_dependency`, `add_traceability_entry`, `add_subtask`
    - Duplicate ID detection with `ValueError`
    - _Requirements: 01-REQ-11.1, 01-REQ-11.2, 01-REQ-11.3, 01-REQ-11.4, 01-REQ-11.6_

  - [ ] 12.2 Implement ID generation helpers in mutate.py
    - `next_requirement_id`, `next_criterion_id`, `next_edge_case_id`
    - `next_correctness_property_id`, `next_execution_path_id`, `next_error_handling_id`
    - `next_test_case_id`, `next_property_test_id`, `next_edge_case_test_id`, `next_smoke_test_id`
    - _Requirements: 01-REQ-11.5_

  - [ ] 12.V Verify task group 12
    - [ ] Mutation tests pass: `uv run pytest -v -k 'test_add or test_get or test_remove or test_set_glossary or test_next' tests/`
    - [ ] Collection mutation property test passes: `uv run pytest -v -k 'test_property_mutation' tests/`
    - [ ] All existing tests still pass: `uv run pytest -q`
    - [ ] No linter warnings introduced: `uv run ruff check && uv run mypy afspec/`
    - [ ] Requirements 01-REQ-11.1 through 01-REQ-11.7 acceptance criteria met

- [ ] 13. Wiring verification

  - [ ] 13.1 Trace every execution path from design.md end-to-end
    - For each path, verify the entry point actually calls the next function
      in the chain (read the calling code, do not assume)
    - Confirm no function in the chain is a stub (`return []`, `return None`,
      `pass`, `raise NotImplementedError`) that was never replaced
    - Every path must be live in production code — errata or deferrals do not
      satisfy this check
    - _Requirements: all_

  - [ ] 13.2 Verify return values propagate correctly
    - For every function in this spec that returns data consumed by a caller,
      confirm the caller receives and uses the return value
    - Grep for callers of each such function; confirm none discards the return
    - _Requirements: all_

  - [ ] 13.3 Run the integration smoke tests
    - All `TS-01-SMOKE-*` tests pass using real components (no stub bypass)
    - _Test Spec: TS-01-SMOKE-1 through TS-01-SMOKE-9_

  - [ ] 13.4 Stub / dead-code audit
    - Search all files touched by this spec for: `return []`, `return None`
      on non-Optional returns, `pass` in non-abstract methods, `# TODO`,
      `# stub`, `NotImplementedError`
    - Each hit must be either: (a) justified with a comment explaining why it
      is intentional, or (b) replaced with a real implementation
    - Document any intentional stubs here with rationale

  - [ ] 13.5 Cross-spec entry point verification
    - For each execution path whose entry point is owned by another spec,
      grep the codebase to confirm the entry point is actually called from
      production code — not just from tests
    - If the upstream caller does not exist, either implement it within this
      spec or file an issue and remove the path from design.md
    - _Requirements: all_

  - [ ] 13.V Verify wiring group
    - [ ] All smoke tests pass
    - [ ] No unjustified stubs remain in touched files
    - [ ] All execution paths from design.md are live (traceable in code)
    - [ ] All cross-spec entry points are called from production code
    - [ ] All existing tests still pass: `uv run pytest -q`

## Traceability

| Requirement | Test Spec Entry | Implemented By Task | Verified By Test |
|-------------|-----------------|---------------------|------------------|
| 01-REQ-1.1 | TS-01-1, TS-01-4 | 2.2, 2.3, 2.5 | tests/test_models.py::test_spec_model_fields, tests/test_models.py::test_sub_types |
| 01-REQ-1.2 | TS-01-2 | 2.4 | tests/test_models.py::test_criterion_ears_patterns |
| 01-REQ-1.3 | TS-01-3 | 2.2 | tests/test_models.py::test_valid_transition |
| 01-REQ-1.4 | TS-01-4 | 2.4, 2.5 | tests/test_models.py::test_sub_types |
| 01-REQ-1.5 | TS-01-42 | 2.6 | tests/test_models.py::test_constructors |
| 01-REQ-1.6 | TS-01-43, TS-01-44 | 2.6 | tests/test_models.py::test_ears_criterion_builders, tests/test_models.py::test_with_return_contract |
| 01-REQ-1.7 | TS-01-45, TS-01-E24 | 2.5 | tests/test_models.py::test_subtask_transition_to |
| 01-REQ-1.E1 | TS-01-E1 | 6.2 | tests/test_validation.py::test_ears_pattern_mismatch |
| 01-REQ-2.1 | TS-01-5 | 3.3 | tests/test_io.py::test_load_spec |
| 01-REQ-2.2 | TS-01-6 | 3.1 | tests/test_io.py::test_prd_frontmatter_parsed |
| 01-REQ-2.3 | TS-01-7 | 3.2 | tests/test_io.py::test_json_artifacts_deserialized |
| 01-REQ-2.E1 | TS-01-E2 | 3.3 | tests/test_io.py::test_load_missing_files |
| 01-REQ-2.E2 | TS-01-E3 | 3.2 | tests/test_io.py::test_load_malformed_json |
| 01-REQ-2.E3 | TS-01-E4 | 3.1 | tests/test_io.py::test_load_bad_frontmatter |
| 01-REQ-3.1 | TS-01-8 | 4.5 | tests/test_io.py::test_save_writes_files |
| 01-REQ-3.2 | TS-01-9 | 4.1 | tests/test_io.py::test_deterministic_json |
| 01-REQ-3.3 | TS-01-10 | 4.3 | tests/test_io.py::test_atomic_writes |
| 01-REQ-3.4 | TS-01-11 | 4.5 | tests/test_io.py::test_updated_at_auto_set |
| 01-REQ-3.5 | TS-01-12 | 4.4 | tests/test_io.py::test_coverage_auto_computed |
| 01-REQ-3.E1 | TS-01-E5 | 4.5 | tests/test_io.py::test_save_nonexistent_dir |
| 01-REQ-3.E2 | TS-01-E6 | 4.3 | tests/test_io.py::test_save_partial_failure_cleanup |
| 01-REQ-3.E3 | TS-01-E7 | 4.3 | tests/test_io.py::test_save_concurrent |
| 01-REQ-4.1 | TS-01-13 | 6.2 | tests/test_validation.py::test_schema_validation |
| 01-REQ-4.1 | TS-01-52 | 6.2 | tests/test_validation.py::test_schema_task_group |
| 01-REQ-4.2 | TS-01-14 | 6.1 | tests/test_validation.py::test_schemas_embedded |
| 01-REQ-4.3 | TS-01-15 | 6.2 | tests/test_validation.py::test_ears_pattern_mismatch |
| 01-REQ-4.E1 | TS-01-E8 | 6.2 | tests/test_validation.py::test_unknown_fields |
| 01-REQ-4.E2 | TS-01-E9 | 6.2 | tests/test_validation.py::test_invalid_ears_pattern |
| 01-REQ-5.1 | TS-01-16 | 7.1 | tests/test_validation.py::test_cross_file_valid |
| 01-REQ-5.2 | TS-01-17 | 7.1 | tests/test_validation.py::test_dangling_requirement_ref |
| 01-REQ-5.3 | TS-01-18 | 7.1 | tests/test_validation.py::test_missing_test_coverage |
| 01-REQ-5.4 | TS-01-19 | 7.1 | tests/test_validation.py::test_dangling_test_spec_ref |
| 01-REQ-5.5 | TS-01-20 | 7.1 | tests/test_validation.py::test_glossary_cross_check |
| 01-REQ-5.6 | TS-01-21 | 7.1 | tests/test_validation.py::test_spec_id_consistency |
| 01-REQ-5.7 | TS-01-53 | 7.1 | tests/test_validation.py::test_duplicate_traceability |
| 01-REQ-5.E1 | TS-01-E10 | 7.1 | tests/test_validation.py::test_incomplete_spec |
| 01-REQ-6.1 | TS-01-22 | 8.1 | tests/test_lifecycle.py::test_legal_transitions |
| 01-REQ-6.2 | TS-01-23 | 8.1 | tests/test_lifecycle.py::test_transition_saves |
| 01-REQ-6.3 | TS-01-24 | 8.1 | tests/test_lifecycle.py::test_draft_to_active_intent_hash |
| 01-REQ-6.4 | TS-01-25 | 8.1 | tests/test_lifecycle.py::test_active_intent_guard |
| 01-REQ-6.5 | TS-01-26 | 8.1 | tests/test_lifecycle.py::test_sealed_save_rejected |
| 01-REQ-6.6 | TS-01-27 | 8.2 | tests/test_lifecycle.py::test_supersede |
| 01-REQ-6.7 | TS-01-E29 | 8.3 | tests/test_lifecycle.py::test_move_to_archive |
| 01-REQ-6.E1 | TS-01-E11 | 8.1 | tests/test_lifecycle.py::test_illegal_transition |
| 01-REQ-6.E2 | TS-01-E12 | 8.1 | tests/test_lifecycle.py::test_intent_modified_active |
| 01-REQ-6.E3 | TS-01-E28 | 8.2 | tests/test_lifecycle.py::test_supersede_not_sealed |
| 01-REQ-6.E4 | TS-01-E30, TS-01-E31, TS-01-E33 | 8.3 | tests/test_lifecycle.py::test_archive_errors |
| 01-REQ-6.E5 | TS-01-E32 | 8.3 | tests/test_lifecycle.py::test_archive_already_archived |
| 01-REQ-7.1 | TS-01-28 | 8.4 | tests/test_bootstrap.py::test_bootstrap_create |
| 01-REQ-7.2 | TS-01-29 | 8.4 | tests/test_bootstrap.py::test_bootstrap_set_artifacts |
| 01-REQ-7.3 | TS-01-30 | 8.4 | tests/test_bootstrap.py::test_bootstrap_finalize |
| 01-REQ-7.E1 | TS-01-E13 | 8.4 | tests/test_bootstrap.py::test_finalize_incomplete |
| 01-REQ-7.E2 | TS-01-E14 | 8.4 | tests/test_bootstrap.py::test_bootstrap_overwrite |
| 01-REQ-8.1 | TS-01-31 | 10.2 | tests/test_render.py::test_render_requirements |
| 01-REQ-8.2 | TS-01-32 | 10.1 | tests/test_render.py::test_render_ears_sentence |
| 01-REQ-8.3 | TS-01-33 | 10.3 | tests/test_render.py::test_render_test_spec |
| 01-REQ-8.4 | TS-01-34 | 10.4 | tests/test_render.py::test_render_tasks |
| 01-REQ-8.5 | TS-01-35 | 10.5 | tests/test_render.py::test_render_combined |
| 01-REQ-8.6 | TS-01-36 | 10.1-10.5 | tests/test_render.py::test_render_deterministic |
| 01-REQ-8.E1 | TS-01-E15 | 10.1 | tests/test_render.py::test_render_return_contract |
| 01-REQ-9.1 | TS-01-37 | 11.1 | tests/test_discovery.py::test_discover_specs |
| 01-REQ-9.2 | TS-01-38 | 11.1 | tests/test_discovery.py::test_discover_loads_metadata |
| 01-REQ-9.3 | TS-01-39 | 11.2 | tests/test_discovery.py::test_build_dependency_graph |
| 01-REQ-9.4 | TS-01-50 | 11.2 | tests/test_discovery.py::test_graph_dependencies |
| 01-REQ-9.5 | TS-01-51 | 11.2 | tests/test_discovery.py::test_graph_dependents |
| 01-REQ-9.E1 | TS-01-E16 | 11.1 | tests/test_discovery.py::test_discover_nonexistent_root |
| 01-REQ-9.E2 | TS-01-E17 | 11.1 | tests/test_discovery.py::test_discover_skips_non_matching |
| 01-REQ-9.E3 | TS-01-E18 | 11.2 | tests/test_discovery.py::test_dependency_cycle |
| 01-REQ-9.E4 | TS-01-E26 | 11.2 | tests/test_discovery.py::test_dangling_dependency |
| 01-REQ-9.E5 | TS-01-E27 | 11.2 | tests/test_discovery.py::test_empty_dependencies |
| 01-REQ-10.1 | TS-01-40 | 3.4 | tests/test_lifecycle.py::test_compute_intent_hash |
| 01-REQ-10.2 | TS-01-41 | 3.4 | tests/test_lifecycle.py::test_compute_intent_hash_public |
| 01-REQ-10.E1 | TS-01-E19 | 3.4 | tests/test_lifecycle.py::test_intent_hash_no_section |
| 01-REQ-10.E2 | TS-01-E20 | 3.4 | tests/test_lifecycle.py::test_intent_hash_empty |
| 01-REQ-11.1 | TS-01-46 | 12.1 | tests/test_mutate.py::test_add_requirement, tests/test_mutate.py::test_add_duplicate |
| 01-REQ-11.2 | TS-01-47 | 12.1 | tests/test_mutate.py::test_get_requirement |
| 01-REQ-11.3 | TS-01-48 | 12.1 | tests/test_mutate.py::test_remove_requirement |
| 01-REQ-11.4 | TS-01-E25 | 12.1 | tests/test_mutate.py::test_set_glossary_entry |
| 01-REQ-11.5 | TS-01-49 | 12.2 | tests/test_mutate.py::test_next_ids |
| 01-REQ-11.6 | TS-01-46 | 12.1 | tests/test_mutate.py::test_add_task_group, tests/test_mutate.py::test_add_traceability |
| 01-REQ-11.7 | TS-01-42 | 2.6 | tests/test_models.py::test_create_spec |
| 01-REQ-11.E1 | TS-01-E21 | 12.1 | tests/test_mutate.py::test_add_requirement_duplicate_unchanged |
| 01-REQ-11.E2 | TS-01-E22 | 12.1 | tests/test_mutate.py::test_get_requirement_missing |
| 01-REQ-11.E3 | TS-01-E23 | 12.2 | tests/test_mutate.py::test_next_requirement_id_empty |
| 01-REQ-11.E4 | TS-01-E34 | 12.1 | tests/test_mutate.py::test_add_traceability_duplicate |
| Property 1 | TS-01-P1 | 4.5 | tests/test_io.py::test_property_round_trip |
| Property 2 | TS-01-P2 | 2.4, 6.2 | tests/test_validation.py::test_property_ears_fields |
| Property 3 | TS-01-P3 | 2.2 | tests/test_models.py::test_property_subtask_transitions |
| Property 4 | TS-01-P4 | 6.2 | tests/test_validation.py::test_property_schema_soundness |
| Property 5 | TS-01-P5 | 7.1 | tests/test_validation.py::test_property_cross_file_integrity |
| Property 6 | TS-01-P6 | 8.1 | tests/test_lifecycle.py::test_property_lifecycle_transitions |
| Property 7 | TS-01-P7 | 4.3 | tests/test_io.py::test_property_atomic_save |
| Property 8 | TS-01-P8 | 10.1-10.5 | tests/test_render.py::test_property_deterministic_render |
| Property 9 | TS-01-P9 | 3.4 | tests/test_lifecycle.py::test_property_intent_hash_stability |
| Property 10 | TS-01-P10 | 4.4 | tests/test_io.py::test_property_coverage_correctness |
| Property 11 | TS-01-P11 | 2.6 | tests/test_models.py::test_property_constructor_completeness |
| Property 12 | TS-01-P12 | 12.1 | tests/test_mutate.py::test_property_mutation_idempotency |

## Notes

- Golden fixtures in `tests/golden/` must be byte-identical copies of the Go library's `testdata/golden/` fixtures.
- All JSON output must match Go's output byte-for-byte (2-space indent, trailing newline, sorted map keys, declaration-order fields).
- YAML frontmatter field order must match Go's output (fixed order per struct declaration).
- Use `uv` for dependency management; `make check` is the quality gate.
- Property tests use `hypothesis`; configure `max_examples=100` for CI, higher for local deep testing.
- The `afspec/schemas/` directory contains the same JSON Schema files as the Go library's `internal/schema/` directory.
