# Python Spec-Format Library (afspec)

## Intent

Build an idiomatic Python library that provides data structures, validation, file I/O, lifecycle management, and markdown rendering for the agent-fox specification format as defined in `docs/spec-format.md` v1. The Python library must be interoperable with the Go implementation (`github.com/af/speclib`), producing byte-identical output for the same input.

## Goals

- Provide Pydantic models for all four spec artifacts: PRD (markdown with YAML frontmatter), requirements.json, test_spec.json, tasks.json.
- Read a spec folder from disk into in-memory structures.
- Write in-memory structures back to disk.
- Validate specs: JSON Schema validation per file, plus cross-file integrity checks.
- Render JSON artifacts to deterministic markdown (per-file and combined).
- Implement and enforce the spec lifecycle state machine (draft, active, sealed, superseded, archived) with all guards.
- Support an explicit bootstrap mode for sequential file creation with deferred cross-file validation.
- Bundle JSON Schema files as package data via `importlib.resources`.
- Provide constructor classmethods, EARS criterion builders, and collection manipulation methods for programmatic spec construction by agents and tooling.
- Maintain and correct the four JSON Schema files (requirements.v1.json, test_spec.v1.json, tasks.v1.json, prd-frontmatter.v1.json) as part of this spec's implementation.
- Guarantee idempotent round-trip: load followed by save followed by load produces identical in-memory state (excluding auto-computed fields).
- Automatically compute and populate the `coverage` field in `test_spec.json` on every save.
- Automatically update the `updated_at` timestamp in PRD frontmatter on every save.
- Provide spec root discovery: scan a root directory to enumerate available specs and resolve cross-spec dependencies.
- Produce byte-identical JSON and markdown output to the Go implementation for the same input data.

## Non-Goals

- No JSON Patch (RFC 6902) mutation API. The library provides typed Python methods, not generic patch operations.
- No per-actor permission enforcement. Consumers handle access control.
- No diff rendering. Only per-file and combined rendering.
- No LLM integration at this level.
- No CLI. This is a library-only package.
- No network access. Schemas are bundled, not fetched from URLs.
- No async API. All operations are synchronous.

## Background

The spec format (`docs/spec-format.md` v1) defines a four-artifact package for spec-driven development. Each package consists of `prd.md` (markdown with YAML frontmatter), `requirements.json`, `test_spec.json`, and `tasks.json`. This library is a building block: other repositories will build on top of it (MCP servers, database bindings, CLI tools, etc.).

A Go implementation exists at `github.com/af/speclib`. This Python library must be interoperable with the Go version — both must produce byte-identical output for the same input. This is verified via golden fixture files shared between the two repositories.

### Spec-Format Reference

The full specification is in `docs/spec-format.md`. Key sections for implementors:

- Section 3: Folder layout, naming convention (`{NN}_{snake_case_name}`), completeness rules.
- Section 4: PRD structure — YAML frontmatter (required fields, protected fields, mutable fields), body with mandatory `## Intent` section, intent hash computation.
- Section 5: Requirements — requirements array, EARS criteria as discriminated union on `ears_pattern`, correctness properties, execution paths, error handling entries.
- Section 6: Test specification — test cases (1:1 with acceptance criteria), property tests (1:1 with correctness properties), edge case tests, smoke tests (1:1 with execution paths), computed coverage.
- Section 7: Tasks — task groups with subtask state machine (pending, queued, in_progress, done, pending_reevaluation, dropped), verification subtasks, cross-spec dependencies, traceability entries.
- Section 8: Lifecycle — five states with transition rules and mutation guards.
- Section 9: Validation — schema validation + eight cross-file integrity rules.
- Section 11: Rendering — deterministic markdown output from JSON, EARS sentence templates.

### Data Model Summary

The library must model these entities:

**PRD** — YAML frontmatter with 12 fields (spec_id, spec_name, title, status, created_at, updated_at, owner, source, supersedes, tags, intent_hash, schema_version) plus a free-form markdown body. The `## Intent` section body is machine-read for hash computation.

**Requirements** — Top-level container with introduction, glossary (term-to-definition map), array of Requirement objects (each with user_story, acceptance_criteria as EARS criteria, edge_cases), correctness properties, execution paths, error handling entries.

**EARS Criteria** — Discriminated union on `ears_pattern` with six variants (ubiquitous, event_driven, complex_event, state_driven, unwanted, optional). Each variant has pattern-specific fields plus common fields (id, system, action, return_contract).

**TestSpec** — Test cases, property tests, edge case tests, smoke tests, and a computed coverage object.

**Tasks** — Test commands, cross-spec dependencies, task groups (each with subtasks and a verification subtask), and traceability entries.

**Subtask State Machine** — Six states (pending, queued, in_progress, done, pending_reevaluation, dropped) with defined legal transitions per `docs/spec-format.md` §7.3.1.

### Validation Rules

**Schema validation (§9.1):** Per-file JSON Schema validation. Rejects malformed structure, missing fields, EARS pattern mismatches, illegal state transitions, invalid ID formats.

**Cross-file integrity (§9.2):** Eight rules:
1. Every `requirement_id` referenced in test_spec.json, tasks.json traceability, and error_handling must exist in requirements.json.
2. Every requirement and edge case must have a test case in test_spec.json.
3. Every correctness property must have a property test.
4. Every execution path must have a smoke test.
5. Every `test_spec_id` in tasks.json must exist in test_spec.json.
6. Glossary cross-check: backtick-wrapped terms in checked fields must have glossary entries.
7. `spec_id` and `spec_name` must be consistent across all four files.
8. No duplicate `(requirement_id, test_spec_id)` pairs in tasks.json traceability.

### Rendering Rules

Rendering applies only to JSON artifacts (requirements.json, test_spec.json, tasks.json). The PRD is already markdown and is not rendered — it is included as-is.

EARS sentences are rendered from decomposed fields using templates (§5.2.1). Rendering is deterministic: same in-memory state produces byte-identical markdown output.

Render targets:
- **Per-file**: One JSON artifact rendered to markdown.
- **Combined**: The PRD markdown (as-is) with the rendered JSON artifacts appended, in order: prd, requirements, test_spec, tasks.

### Lifecycle Rules

Five states: draft, active, sealed, superseded, archived.

- draft: All mutations allowed including Intent edits.
- active: All mutations except Intent section and immutable frontmatter (created_at, spec_id, spec_name). Intent hash is computed and locked at draft-to-active transition.
- sealed: No mutations allowed.
- superseded: No mutations allowed. Deprecation banner added to prd.md.
- archived: No mutations allowed.

Transition graph: draft→active, active→sealed, sealed→superseded, sealed→archived, draft→archived.

### Bootstrap Mode

During creation, files come into existence sequentially. The library operates in bootstrap mode: cross-file validation is deferred until all four files are written. A partially-created spec is in an "incomplete" state, not invalid but not yet valid.

### Automatic Behaviors on Save

Two fields are automatically managed by the library on every save operation:

- **`updated_at`**: Set to the current UTC timestamp (ISO 8601) on every save of `prd.md` frontmatter. The caller does not set this field.
- **`coverage`**: The `coverage` field in `test_spec.json` is computed (not authored). On every save, the library scans test cases, property tests, edge case tests, and smoke tests against the requirements in the same spec to populate `requirements_covered`, `properties_covered`, `paths_covered`, and `gaps`. A non-empty `gaps` array is a validation warning, not a blocking error.

### Intent Hash Computation

The intent hash is a SHA-256 hex digest of the `## Intent` section body after normalization:

1. Extract the text between `## Intent` and the next `##` heading (or end of file).
2. Normalize line endings to LF (`\n`).
3. Collapse multiple consecutive blank lines into a single blank line.
4. Lower-case the entire text.
5. Trim leading and trailing whitespace.
6. Compute SHA-256 of the resulting bytes and store as lowercase hex.

### Spec Root and Discovery

The library must have the concept of a "spec root" — the directory containing spec folders (e.g., `.agent-fox/specs/`). If not provided, it defaults to the current working directory.

The library must provide a discovery function that scans the spec root to:
- Enumerate all valid spec folders (matching the `{NN}_{snake_case_name}` pattern).
- Skip the `archive/` subdirectory.
- Load spec metadata (at minimum: spec_id, spec_name, status) without fully loading all artifacts.
- Build a dependency graph from cross-spec dependency declarations in tasks.json.

This is required because specs can have cross-spec dependencies that must be resolvable.

### ID Format Reference

- Requirement: `{spec_id}-REQ-{N}`
- Acceptance criterion: `{spec_id}-REQ-{N}.{C}`
- Edge case: `{spec_id}-REQ-{N}.E{C}`
- Correctness property: `{spec_id}-PROP-{N}`
- Execution path: `{spec_id}-PATH-{N}`
- Error handling: `{spec_id}-ERR-{N}`
- Test case: `TS-{spec_id}-{N}`
- Property test: `TS-{spec_id}-P{N}`
- Edge case test: `TS-{spec_id}-E{N}`
- Smoke test: `TS-{spec_id}-SMOKE-{N}`

## Design Decisions

1. **Package name**: The Python package is `afspec`, consistent with the project's steering.md. The Go equivalent is `github.com/af/speclib`. Consumers install via `pip install afspec` or `uv add afspec`.
2. **Pydantic models**: All data types use Pydantic `BaseModel` instead of plain dataclasses. This provides built-in JSON serialization, field validation, and immutability control. Pydantic's `model_dump()` and `model_validate()` replace manual marshal/unmarshal.
3. **Python-idiomatic error handling**: I/O and lifecycle errors raise exceptions (`SpecError`, `LoadError`, `SaveError`, `LifecycleError`). Validation functions (`validate_schema`, `validate_cross_file`) return lists of `ValidationError` data objects (not exceptions), consistent with Go's approach of collecting all violations.
4. **Not thread-safe**: The library is documented as not thread-safe, which is standard for Python libraries. Atomic file writes are still used for data integrity during save operations.
5. **No `embed` equivalent**: JSON Schema files are bundled as package data and loaded via `importlib.resources`. This is the Python equivalent of Go's `//go:embed`.
6. **Nullable fields**: Python uses `Optional[str]` (i.e., `str | None`) for nullable fields (`return_contract`, `intent_hash`, `test_path`). `None` is serialized as JSON `null`.
7. **Free-form JSON fields**: Go's `json.RawMessage` for the `input` and `expected` fields in test cases is modeled as `Any` in Python — preserving whatever JSON type was in the file (dict, list, string, number, null).
8. **Deterministic JSON output**: JSON is serialized with `json.dumps(indent=2, sort_keys=False, ensure_ascii=False)` followed by a trailing newline. Field order is controlled by Pydantic model field declaration order (matching Go struct order). Map keys (glossary) are sorted alphabetically via a custom serializer.
9. **YAML handling**: PRD frontmatter is parsed and serialized using PyYAML. Field order is fixed to match Go's output (explicit ordering in the serializer).
10. **Python version**: Python 3.10+ minimum as specified in the project's steering.md.
11. **External dependencies**: `pydantic>=2.0`, `PyYAML>=6.0`, `jsonschema>=4.0`. Standard library for JSON, file I/O, and SHA-256.
12. **Testing framework**: `pytest` for test execution, `hypothesis` for property-based tests. Golden fixture files in `tests/golden/` for cross-library consistency.
13. **Build system**: A `Makefile` provides `check`, `test`, and `lint` targets. `make check` runs lint then all tests. `make test` runs `uv run pytest -q`. `make lint` runs `uv run ruff check` and `uv run mypy`.
14. **Cross-library consistency**: The Python and Go libraries must produce byte-identical output for the same input. Verified via golden fixture files. Each fixture is a complete spec folder with all four artifacts. The library's test suite loads these fixtures, processes them (round-trip, render), and compares output byte-for-byte.
15. **Computed fields on save**: The library automatically computes `coverage` in test_spec.json and sets `updated_at` in PRD frontmatter on every save. Callers do not set these fields manually.
16. **Atomic saves**: Save operations use write-to-temporary-file-then-rename to prevent partial writes on failure. If any file in a multi-file save fails, previously written files in the same save are cleaned up. Lifecycle functions (`transition`, `supersede`, `move_to_archive`) include persistence as part of their operation using an internal save that bypasses the public `save` mutation guard.
17. **Tasks markdown rendering**: The library renders `tasks.json` to markdown using a format consistent with the reference in `docs/tasks-example.md`. Subtask states map to checkbox markers: pending→`[ ]`, queued→`[~]`, in_progress→`[-]`, done→`[x]`, pending_reevaluation→`[?]`. Dropped subtasks are omitted from rendered output. Optional subtasks are marked with `*` after the checkbox.
18. **Deprecation banner scope**: When transitioning to superseded, the library adds a deprecation banner to the top of `prd.md` only (not to all four files).
19. **Schema from_group fix**: The `from_group` field in `tasks.v1.json` schema uses `minimum: 0` (not `minimum: 1`) to support the sentinel value `0`.
20. **JSON key ordering**: Pydantic model fields are serialized in declaration order (matching Go struct order). Glossary dict keys are sorted alphabetically. This produces deterministic output matching the Go implementation.
21. **Coverage gaps as warnings**: The `coverage.gaps` array in `test_spec.json` is computed on every save. A non-empty `gaps` array is a validation warning, not a blocking error.
22. **Compound lifecycle operations**: `transition` and `supersede` accept a directory path and persist the result to disk as part of their operation. `move_to_archive` loads, transitions (if needed), saves, and moves the folder.
23. **Enum implementation**: All constrained values (Status, EARSPattern, SubtaskState, TaskGroupKind) use `str, Enum` mixins for direct JSON serialization.
24. **Exception hierarchy**: `SpecError` is the base exception. Subclasses: `LoadError` (file I/O during load), `SaveError` (file I/O during save), `LifecycleError` (illegal transitions, mutation guards), `IntentError` (missing/modified intent section), `BootstrapError` (incomplete bootstrap finalization).

## Source

Source: /Users/candlekeep/devel/workspace/speclib-go/.agent-fox/specs/01_speclib
