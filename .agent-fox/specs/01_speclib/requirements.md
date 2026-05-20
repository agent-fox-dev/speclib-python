# Requirements Document

## Introduction

The `afspec` package is an idiomatic Python library that provides data structures, validation, file I/O, lifecycle management, and markdown rendering for the agent-fox specification format (v1). It reads and writes spec folders containing four artifacts (`prd.md`, `requirements.json`, `test_spec.json`, `tasks.json`), validates them against JSON Schemas and cross-file integrity rules, enforces a five-state lifecycle, and renders JSON artifacts to deterministic markdown. The library must produce byte-identical output to the Go implementation (`github.com/af/speclib`) for the same input.

## Glossary

| Term | Definition |
|------|-----------|
| Spec | A four-artifact package (`prd.md`, `requirements.json`, `test_spec.json`, `tasks.json`) representing one feature or concern. |
| Spec root | The directory containing spec folders, e.g. `.agent-fox/specs/`. |
| Spec folder | A subdirectory of the spec root matching the naming pattern `{NN}_{snake_case_name}`, containing the four spec artifacts. |
| PRD | Product Requirements Document; the `prd.md` file containing YAML frontmatter and a markdown body. |
| Frontmatter | YAML metadata block at the top of `prd.md`, delimited by `---` lines, containing 12 structured fields. |
| EARS | Easy Approach to Requirements Syntax; a pattern language with six patterns for writing testable requirements. |
| EARS pattern | One of: ubiquitous, event\_driven, complex\_event, state\_driven, unwanted, optional. Determines the required fields on a criterion. |
| Criterion | A single acceptance criterion or edge case expressed as a discriminated union keyed on `ears_pattern`. |
| Intent hash | SHA-256 hex digest of the normalized `## Intent` section body from `prd.md`. Computed at draft-to-active transition and verified on subsequent mutations. |
| Bootstrap mode | A library mode that allows sequential creation of spec artifacts with cross-file validation deferred until `finalize()` is called. |
| Lifecycle state | One of five states: draft, active, sealed, superseded, archived. Stored in `prd.md` frontmatter `status` field. |
| Coverage | A computed object in `test_spec.json` listing which requirements, properties, and paths have corresponding test entries, and which have gaps. |
| Subtask state machine | The six-state state machine (pending, queued, in\_progress, done, pending\_reevaluation, dropped) governing subtask progression. |
| Golden fixture | A complete spec folder in `tests/golden/` used for round-trip and rendering tests. |
| Cross-file integrity | Validation rules that span multiple spec artifacts, ensuring referential consistency. |
| Schema validation | Per-file validation of JSON artifacts against their bundled JSON Schema definitions. |
| Deprecation banner | A blockquote added to the top of `prd.md` when a spec transitions to superseded status. |
| Atomic save | A write strategy using write-to-temporary-file-then-rename to prevent partial writes. |
| Pydantic model | A class inheriting from `pydantic.BaseModel` that provides automatic validation, serialization, and field typing. |
| Criterion builder | A per-EARS-pattern factory function (e.g., `event_driven_criterion`) that sets the correct `ears_pattern` and pattern-specific fields. |
| Collection mutation method | A function (add, get, remove) that modifies or queries a list or dict of child elements with ID uniqueness enforcement. Returns a new model instance. |
| SpecMeta | A lightweight model containing `spec_id`, `spec_name`, `status`, and directory path, loaded during discovery without fully loading all artifacts. |
| Dependency graph | A directed acyclic graph of cross-spec dependencies derived from `tasks.json` dependency declarations. |

## Requirements

### Requirement 1: Data Model Types

**User Story:** As a library consumer, I want complete Python type definitions for all spec artifacts, so that I can represent specs in memory with full type safety.

#### Acceptance Criteria

1. [01-REQ-1.1] THE `afspec` package SHALL export Pydantic model classes `Spec`, `PRDDocument`, `PRDFrontmatter`, `Requirements`, `TestSpec`, and `Tasks` corresponding to the four spec artifacts defined in `docs/spec-format.md` v1, AND return populated instances of these types from `load_spec`.
2. [01-REQ-1.2] THE `afspec` package SHALL export a `Criterion` Pydantic model supporting six EARS patterns (ubiquitous, event\_driven, complex\_event, state\_driven, unwanted, optional) with pattern-specific fields as defined in `docs/spec-format.md` §5.2.1.
3. [01-REQ-1.3] THE `afspec` package SHALL export a `SubtaskState` enum with six valid values (pending, queued, in\_progress, done, pending\_reevaluation, dropped) and a `valid_transition` function that accepts a current state and target state AND returns `True` if the transition is legal per `docs/spec-format.md` §7.3.1, `False` otherwise.
4. [01-REQ-1.4] THE `afspec` package SHALL export Pydantic model classes `Requirement`, `UserStory`, `CorrectnessProperty`, `ExecutionPath`, `PathStep`, `ErrorHandlingEntry`, `TestCase`, `PropertyTest`, `EdgeCaseTest`, `SmokeTest`, `Coverage`, `TaskGroup`, `Subtask`, `VerificationSubtask`, `TaskDependency`, `TraceabilityEntry`, and `TestCommands`, each with typed fields matching the corresponding JSON schema definitions.
5. [01-REQ-1.5] THE `afspec` package SHALL provide factory functions for all exported model types (`create_spec`, `create_prd_document`, `create_requirements`, `create_test_spec`, `create_tasks`, `create_requirement`, `create_user_story`, `create_correctness_property`, `create_execution_path`, `create_error_handling`, `create_task_group`, `create_subtask`, `create_verification_subtask`, `create_test_case`, `create_property_test`, `create_edge_case_test`, `create_smoke_test`, `create_task_dependency`, `create_traceability_entry`) that accept required fields as parameters AND return populated instances with all other fields at their default values.
6. [01-REQ-1.6] THE `afspec` package SHALL provide six EARS criterion factory functions (`ubiquitous_criterion`, `event_driven_criterion`, `complex_event_criterion`, `state_driven_criterion`, `unwanted_criterion`, `optional_criterion`) that accept the pattern-specific fields as parameters AND return a `Criterion` with the correct `ears_pattern` set, AND a `with_return_contract` method on `Criterion` that accepts a return contract string AND returns a new `Criterion` with the `return_contract` field populated.
7. [01-REQ-1.7] THE `Subtask` model SHALL have a `transition_to` method that accepts a target `SubtaskState` AND returns a new `Subtask` with the updated state if the transition is legal per `valid_transition`, or raises a `LifecycleError` naming the current and target states if the transition is illegal.

#### Edge Cases

1. [01-REQ-1.E1] IF a `Criterion` is serialized to JSON with fields that are incompatible with its declared `ears_pattern` (e.g., a `trigger` field on a `ubiquitous` pattern), THEN THE JSON Schema validation SHALL report the incompatible fields as validation errors.

---

### Requirement 2: File I/O — Load

**User Story:** As a library consumer, I want to load a spec folder from disk into in-memory structures, so that I can inspect, validate, and process specs programmatically.

#### Acceptance Criteria

1. [01-REQ-2.1] WHEN given a valid spec directory path containing all four artifact files, THE `load_spec` function SHALL read `prd.md`, `requirements.json`, `test_spec.json`, and `tasks.json` AND return a populated `Spec` instance.
2. [01-REQ-2.2] WHEN loading `prd.md`, THE library SHALL parse the YAML frontmatter into a `PRDFrontmatter` model and the remaining markdown body into a string field, AND return both within the `PRDDocument` field of `Spec`.
3. [01-REQ-2.3] WHEN loading JSON artifacts, THE library SHALL deserialize each file into its corresponding Pydantic model (`Requirements`, `TestSpec`, `Tasks`) AND return them within `Spec`.

#### Edge Cases

1. [01-REQ-2.E1] IF any of the four artifact files is missing from the spec directory, THEN THE `load_spec` function SHALL raise a `LoadError` identifying which file(s) are missing.
2. [01-REQ-2.E2] IF a JSON artifact contains malformed JSON, THEN THE `load_spec` function SHALL raise a `LoadError` identifying the file and the parse error.
3. [01-REQ-2.E3] IF `prd.md` has missing or unparseable YAML frontmatter, THEN THE `load_spec` function SHALL raise a `LoadError` describing the frontmatter issue.

---

### Requirement 3: File I/O — Save

**User Story:** As a library consumer, I want to write in-memory specs back to disk atomically, so that data is never left in a partially-written state.

#### Acceptance Criteria

1. [01-REQ-3.1] WHEN `save` is called with a `Spec` and a directory path, THE library SHALL write all four artifact files (`prd.md`, `requirements.json`, `test_spec.json`, `tasks.json`) to disk AND return without error on success or raise a `SaveError` on failure.
2. [01-REQ-3.2] THE library SHALL serialize JSON artifacts with 2-space indentation and a trailing newline, with model fields in declaration order and dict keys sorted alphabetically, to ensure deterministic byte-identical output for identical in-memory state.
3. [01-REQ-3.3] THE library SHALL write each file atomically using write-to-temporary-file-then-rename within the same directory.
4. [01-REQ-3.4] WHEN saving, THE library SHALL automatically set `updated_at` in the PRD frontmatter to the current UTC time in ISO 8601 format before writing `prd.md`.
5. [01-REQ-3.5] WHEN saving, THE library SHALL automatically compute and populate the `coverage` field in `TestSpec` by scanning test cases, property tests, edge case tests, and smoke tests against the requirements, correctness properties, and execution paths, AND return the `Spec` with updated coverage.

#### Edge Cases

1. [01-REQ-3.E1] IF the target directory does not exist, THEN THE `save` function SHALL raise a `SaveError` without creating any files.
2. [01-REQ-3.E2] IF any file in a multi-file save operation fails to write (e.g., disk full, permission denied), THEN THE library SHALL remove any temporary files already created in the same save operation AND raise a `SaveError`.
3. [01-REQ-3.E3] IF `save` is called concurrently from multiple threads for the same directory, THEN each call SHALL produce a consistent result without file corruption (last writer wins, but no partial files).

---

### Requirement 4: Schema Validation

**User Story:** As a library consumer, I want to validate spec artifacts against their JSON Schemas, so that I can reject malformed inputs early and produce clear error reports.

#### Acceptance Criteria

1. [01-REQ-4.1] WHEN `validate_schema` is called with a `Spec`, THE library SHALL validate each JSON artifact against its bundled JSON Schema (`requirements.v1.json`, `test_spec.v1.json`, `tasks.v1.json`) and the PRD frontmatter against `prd-frontmatter.v1.json`, AND return a list of `ValidationError` values listing all violations found across all files.
2. [01-REQ-4.2] THE library SHALL bundle the four JSON Schema files as package data via `importlib.resources`, AND load them at validation time without network access.
3. [01-REQ-4.3] THE schema validation SHALL enforce the EARS criterion discriminated union by rejecting criteria that have fields not matching their declared `ears_pattern` (e.g., a `trigger` field on a `ubiquitous` criterion).

#### Edge Cases

1. [01-REQ-4.E1] IF a JSON artifact contains unknown fields not defined in the schema, THEN THE validation SHALL report each unknown field as a `ValidationError` with the field path and a descriptive message.
2. [01-REQ-4.E2] IF a criterion has an `ears_pattern` value not in the set (ubiquitous, event\_driven, complex\_event, state\_driven, unwanted, optional), THEN THE validation SHALL report it as a schema error.

---

### Requirement 5: Cross-File Integrity

**User Story:** As a library consumer, I want cross-file consistency checks across all four artifacts, so that I can detect referential integrity violations before they cause runtime failures.

#### Acceptance Criteria

1. [01-REQ-5.1] WHEN `validate_cross_file` is called with a complete `Spec`, THE library SHALL check all eight cross-file integrity rules defined in `docs/spec-format.md` §9.2 AND return a list of `ValidationError` values listing all violations.
2. [01-REQ-5.2] THE library SHALL verify that every `requirement_id` referenced in `test_spec.json` test cases, `tasks.json` traceability entries, and `requirements.json` error\_handling entries exists as an acceptance criterion or edge case ID in `requirements.json` (integrity rule 1).
3. [01-REQ-5.3] THE library SHALL verify that every acceptance criterion and edge case in `requirements.json` has a corresponding test case in `test_spec.json`, every correctness property has a property test, and every execution path has a smoke test (integrity rules 2, 3, 4).
4. [01-REQ-5.4] THE library SHALL verify that every `test_spec_id` referenced in `tasks.json` traceability or subtask `test_spec_refs` exists in `test_spec.json` (integrity rule 5).
5. [01-REQ-5.5] THE library SHALL perform a glossary cross-check: every backtick-wrapped term in the checked fields (`action`, `trigger`, `condition`, `error_condition`, `state`, `feature`, `for_any`, `invariant`) of `requirements.json` must have a corresponding entry in the glossary (integrity rule 6).
6. [01-REQ-5.6] THE library SHALL verify that `spec_id` and `spec_name` are identical across `prd.md` frontmatter, `requirements.json`, `test_spec.json`, and `tasks.json` (integrity rule 7).
7. [01-REQ-5.7] THE library SHALL verify that no two entries in the `tasks.json` traceability array share the same `(requirement_id, test_spec_id)` pair (integrity rule 8). Duplicate pairs SHALL be reported as `ValidationError` values.

#### Edge Cases

1. [01-REQ-5.E1] IF `validate_cross_file` is called on a spec where any sub-model (`Requirements`, `TestSpec`, or `Tasks`) has an empty `spec_id` (the sentinel for an unpopulated artifact), THEN THE function SHALL return a `ValidationError` whose message contains "incomplete" and SHALL NOT proceed to cross-file rule checks.

---

### Requirement 6: Lifecycle Management

**User Story:** As a library consumer, I want lifecycle state machine enforcement, so that spec mutations follow the defined transition rules and intent integrity is guaranteed.

#### Acceptance Criteria

1. [01-REQ-6.1] THE library SHALL support five lifecycle states (draft, active, sealed, superseded, archived) with the following legal transitions: draft→active, active→sealed, sealed→archived, draft→archived via `transition(spec, target, dir)`, AND sealed→superseded via the dedicated `supersede(spec, superseding_spec_id, dir)` function.
2. [01-REQ-6.2] WHEN `transition` is called on a `Spec` with a valid target state (draft→active, active→sealed, sealed→archived, draft→archived) and a directory path, THE library SHALL update the spec's status in `PRDFrontmatter`, save the spec to the specified directory using an internal save (bypassing the public `save` mutation guard), AND return the updated `Spec`.
3. [01-REQ-6.3] WHEN transitioning from draft to active, THE library SHALL compute the intent hash from the `## Intent` section of the PRD body and store it in the frontmatter `intent_hash` field.
4. [01-REQ-6.4] WHILE the spec status is active, THE library SHALL reject any save that would alter the `## Intent` section body (detected via intent hash mismatch) or change immutable frontmatter fields (`created_at`, `spec_id`, `spec_name`, `supersedes`), by raising a `LifecycleError`.
5. [01-REQ-6.5] WHILE the spec status is sealed, superseded, or archived, THE public `save` function SHALL reject all mutations by raising a `LifecycleError`. Lifecycle functions (`transition`, `supersede`, `move_to_archive`) use an internal save to persist transitions to these states.
6. [01-REQ-6.6] WHEN `supersede` is called with a `Spec` in sealed state, a `superseding_spec_id` string, and a directory path, THE library SHALL set the status to superseded, prepend a deprecation banner (`> **SUPERSEDED** by spec {superseding_spec_id}. This spec is retained for historical reference only.`) to the top of the PRD body, save the spec to the specified directory using an internal save, AND return the updated `Spec`.
7. [01-REQ-6.7] WHEN `move_to_archive` is called with a spec directory path and a spec root path, THE library SHALL load the spec, transition it to archived status (if not already in a terminal state), save the spec using an internal save, move the spec folder to `{root}/archive/{folder_name}`, create the `archive/` directory if it does not exist, AND return without error. IF the spec is already superseded or archived, THE library SHALL skip the status transition and just move the folder.

#### Edge Cases

1. [01-REQ-6.E1] IF `transition` is called with a target state that is not reachable from the current state (e.g., draft→sealed), or with `superseded` as the target (must use `supersede` instead), THEN THE library SHALL raise a `LifecycleError` naming the current state and the invalid target state.
2. [01-REQ-6.E2] IF the intent hash check detects that the `## Intent` section has been modified while in active state, THEN THE library SHALL raise a `LifecycleError` indicating intent modification is forbidden in active state.
3. [01-REQ-6.E3] IF `supersede` is called on a spec that is not in sealed state, THEN THE library SHALL raise a `LifecycleError` naming the current state and indicating that only sealed specs can be superseded.
4. [01-REQ-6.E4] IF `move_to_archive` is called with a spec directory that does not exist, THEN THE library SHALL raise a `LifecycleError`. IF the spec is in `active` state (the only non-terminal state from which `archived` is not reachable via a single legal transition), THEN THE library SHALL raise a `LifecycleError` naming the current state.
5. [01-REQ-6.E5] IF `move_to_archive` is called on a spec that is already in the `archive/` subdirectory, THEN THE library SHALL raise a `LifecycleError` indicating the spec is already archived.

---

### Requirement 7: Bootstrap Mode

**User Story:** As a library consumer, I want to create specs incrementally (file by file), so that I can build specs during an authoring workflow without premature validation failures.

#### Acceptance Criteria

1. [01-REQ-7.1] WHEN `BootstrapSpec` is constructed with a `spec_id` and `spec_name`, THE library SHALL return a `BootstrapSpec` instance that allows setting each artifact independently, AND return it to the caller for sequential population.
2. [01-REQ-7.2] THE `BootstrapSpec` SHALL provide `set_prd`, `set_requirements`, `set_test_spec`, and `set_tasks` methods, each accepting the corresponding artifact model, that store the artifact without running cross-file validation.
3. [01-REQ-7.3] WHEN `finalize` is called on a fully-populated `BootstrapSpec`, THE library SHALL run schema validation and cross-file integrity checks AND return either a valid `Spec` or raise a `BootstrapError` containing the list of `ValidationError` values.

#### Edge Cases

1. [01-REQ-7.E1] IF `finalize` is called before all four artifacts have been set, THEN THE library SHALL raise a `BootstrapError` listing the missing artifact(s) by name.
2. [01-REQ-7.E2] IF the same artifact is set more than once on a `BootstrapSpec`, THEN THE library SHALL accept the latest value, overwriting the previous one.

---

### Requirement 8: Markdown Rendering

**User Story:** As a library consumer, I want deterministic markdown output from spec JSON data, so that I can generate human-readable documentation and verify rendering consistency across implementations.

#### Acceptance Criteria

1. [01-REQ-8.1] WHEN `render_requirements` is called with a `Requirements` value, THE library SHALL produce a markdown string containing the introduction, glossary table, each requirement with EARS-rendered acceptance criteria and edge cases, correctness properties, execution paths, and error handling table, AND return the markdown string.
2. [01-REQ-8.2] THE library SHALL render EARS sentences from the decomposed criterion fields using the six templates defined in `docs/spec-format.md` §5.2.1 (e.g., event\_driven: `WHEN {trigger}, THE {system} SHALL {action}`).
3. [01-REQ-8.3] WHEN `render_test_spec` is called with a `TestSpec` value, THE library SHALL produce a markdown string containing test cases, property tests, edge case tests, smoke tests, and a coverage summary, AND return the markdown string.
4. [01-REQ-8.4] WHEN `render_tasks` is called with a `Tasks` value, THE library SHALL produce a markdown string containing test commands, dependencies table, task groups with checkbox-formatted subtasks, and a traceability table, AND return the markdown string.
5. [01-REQ-8.5] WHEN `render_combined` is called with a `Spec`, THE library SHALL produce a single markdown string containing the PRD body (as-is) followed by rendered requirements, test spec, and tasks (in that order), AND return the combined markdown string.
6. [01-REQ-8.6] THE library SHALL produce byte-identical markdown output for identical in-memory state (deterministic rendering), AND return the same string on repeated calls with the same input.

#### Edge Cases

1. [01-REQ-8.E1] IF a criterion has a non-null `return_contract`, THEN THE rendered EARS sentence SHALL append ` AND return {return_contract}` after the action clause.

---

### Requirement 9: Spec Root Discovery

**User Story:** As a library consumer, I want to enumerate specs in a directory and resolve cross-spec dependencies, so that I can build tooling that operates across multiple specs.

#### Acceptance Criteria

1. [01-REQ-9.1] WHEN `discover_specs` is called with a root directory path, THE library SHALL scan for subdirectories matching the `{NN}_{snake_case_name}` pattern, skip the `archive/` subdirectory, AND return a list of `SpecMeta` values.
2. [01-REQ-9.2] THE library SHALL load each discovered spec's `prd.md` frontmatter to populate `SpecMeta` fields (`spec_id`, `spec_name`, `status`, `dir`) without fully loading all four artifacts, AND return the metadata to the caller.
3. [01-REQ-9.3] WHEN `build_dependency_graph` is called with a list of `SpecMeta` values and the spec root path, THE library SHALL parse `tasks.json` dependency declarations from each spec folder, validate that every `depends_on_spec` value references a spec present in the provided `SpecMeta` list, AND return a `DependencyGraph` representing the directed dependency relationships, or raise a `SpecError` if parsing or validation fails.
4. [01-REQ-9.4] THE `DependencyGraph` type SHALL provide a `dependencies` method that accepts a `spec_id` AND returns the list of `DependencyEdge` values representing the direct dependencies of that spec (specs it depends on).
5. [01-REQ-9.5] THE `DependencyGraph` type SHALL provide a `dependents` method that accepts a `spec_id` AND returns the list of `DependencyEdge` values representing the direct dependents of that spec (specs that depend on it).

#### Edge Cases

1. [01-REQ-9.E1] IF the root directory does not exist, THEN THE `discover_specs` function SHALL raise a `SpecError`.
2. [01-REQ-9.E2] IF a subdirectory does not match the `{NN}_{snake_case_name}` naming pattern, THEN THE library SHALL skip it without error.
3. [01-REQ-9.E3] IF the dependency graph contains a cycle, THEN THE `build_dependency_graph` function SHALL raise a `SpecError` identifying the specs involved in the cycle.
4. [01-REQ-9.E4] IF a `depends_on_spec` value in a spec's `tasks.json` references a spec ID that is not present in the discovered `SpecMeta` list, THEN THE `build_dependency_graph` function SHALL raise a `SpecError` identifying the unknown spec ID and the spec that references it.
5. [01-REQ-9.E5] IF `dependencies` or `dependents` is called with a `spec_id` that has no edges in the graph, THEN THE method SHALL return an empty list (not `None`).

---

### Requirement 10: Intent Hash Computation

**User Story:** As a library consumer, I want the library to compute and verify intent hashes, so that spec intent cannot be silently changed after activation.

#### Acceptance Criteria

1. [01-REQ-10.1] WHEN `compute_intent_hash` is called with a PRD body string, THE library SHALL extract the text between `## Intent` and the next `##` heading (or end of document), normalize line endings to LF, collapse multiple consecutive blank lines into one, lower-case the text, trim leading and trailing whitespace, compute SHA-256, AND return the lowercase hex digest string.
2. [01-REQ-10.2] THE library SHALL expose `compute_intent_hash` as a public function that accepts a PRD body string and returns the hex digest string on success, or raises an `IntentError` on failure.

#### Edge Cases

1. [01-REQ-10.E1] IF the PRD body does not contain a `## Intent` section, THEN THE `compute_intent_hash` function SHALL raise an `IntentError` indicating the section is missing.
2. [01-REQ-10.E2] IF the `## Intent` section is empty (whitespace-only after trimming), THEN THE `compute_intent_hash` function SHALL return the SHA-256 hash of an empty byte slice (the well-known empty hash `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).

---

### Requirement 11: Programmatic Construction API

**User Story:** As a library consumer (e.g., an agent or CLI tool), I want typed methods for building specs programmatically, so that I can construct, query, and modify spec artifacts without manually populating model fields.

#### Acceptance Criteria

1. [01-REQ-11.1] WHEN an `add_*` method (`add_requirement`, `add_test_case`, `add_property_test`, `add_edge_case_test`, `add_smoke_test`, `add_correctness_property`, `add_execution_path`, `add_error_handling`, `add_criterion`, `add_edge_case`) is called with a value whose ID already exists in the target collection, THEN THE method SHALL raise a `ValueError` identifying the duplicate ID without modifying the collection, AND return the updated model and append the value when the ID is unique.
2. [01-REQ-11.2] WHEN a `get_*` method (`get_requirement`, `get_criterion`) is called with an ID, THEN THE method SHALL return the matching value if found, or `None` if not found.
3. [01-REQ-11.3] WHEN a `remove_*` method (`remove_requirement`, `remove_glossary_entry`) is called with an ID or key, THEN THE method SHALL return the updated model with the matching entry removed and `True`, or the unchanged model and `False` if no match exists.
4. [01-REQ-11.4] WHEN `set_glossary_entry` is called on a `Requirements` value with a term and definition, THEN THE method SHALL return a new `Requirements` with the glossary entry inserted or overwritten for that term.
5. [01-REQ-11.5] WHEN a `next_*_id` method (`next_requirement_id`, `next_criterion_id`, `next_edge_case_id`, `next_correctness_property_id`, `next_execution_path_id`, `next_error_handling_id`, `next_test_case_id`, `next_property_test_id`, `next_edge_case_test_id`, `next_smoke_test_id`) is called, THEN THE method SHALL return the next sequential ID in the correct format based on the existing entries in the collection AND the `spec_id` of the parent artifact.
6. [01-REQ-11.6] WHEN `add_task_group` is called on a `Tasks` value, THEN THE method SHALL raise a `ValueError` if a group with the same ID exists, or return a new `Tasks` with the group appended. WHEN `add_subtask` is called on a `TaskGroup`, THEN THE method SHALL raise a `ValueError` if a subtask with the same ID exists, or return a new `TaskGroup` with the subtask appended. WHEN `add_dependency` is called on a `Tasks` value, THEN THE method SHALL return a new `Tasks` with the entry appended. WHEN `add_traceability_entry` is called on a `Tasks` value, THEN THE method SHALL raise a `ValueError` if an entry with the same `(requirement_id, test_spec_id)` pair already exists, or return a new `Tasks` with the entry appended.
7. [01-REQ-11.7] WHEN `Spec` is constructed with a `spec_id` and `spec_name`, THEN THE constructor SHALL return a `Spec` with initialized sub-artifacts (`Requirements`, `TestSpec`, `Tasks`) that share the same `spec_id` and `spec_name`, AND a `PRDDocument` with frontmatter fields `spec_id`, `spec_name`, and `status` set to `draft`.

#### Edge Cases

1. [01-REQ-11.E1] IF `add_requirement` is called with a `Requirement` whose ID duplicates an existing entry, THEN THE method SHALL raise a `ValueError` AND the `Requirements.requirements` list SHALL remain unchanged (same length and content as before the call).
2. [01-REQ-11.E2] IF `get_requirement` is called with an ID that does not exist in the collection, THEN THE method SHALL return `None`.
3. [01-REQ-11.E3] IF `next_requirement_id` is called on a `Requirements` value with an empty `requirements` list, THEN THE method SHALL return the first ID in the sequence (e.g., `"{spec_id}-REQ-1"`).
4. [01-REQ-11.E4] IF `add_traceability_entry` is called with a `TraceabilityEntry` whose `(requirement_id, test_spec_id)` pair duplicates an existing entry, THEN THE method SHALL raise a `ValueError` identifying the duplicate pair AND the `Tasks.traceability` list SHALL remain unchanged.
