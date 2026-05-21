# Requirements Document

## Introduction

This specification defines how the `afspec` library supports `architecture.md`
as an optional fifth artifact in a spec package. The file is free-form
markdown with no schema. Its presence or absence does not affect spec
validity. The library must load, save, and render it correctly.

## Glossary

| Term | Definition |
|------|-----------|
| `architecture.md` | Optional free-form markdown file providing architectural context for a spec |
| `Spec` | Top-level Pydantic model containing all spec artifacts (prd, requirements, test_spec, tasks, and optionally architecture) |
| `load_spec` | Function that reads a spec directory and returns a populated `Spec` model |
| `save` | Public function that writes a `Spec` to disk with mutation guards |
| `_save_internal` | Internal save function used by lifecycle transitions, bypasses mutation guards |
| `render_combined` | Function that renders all spec artifacts into a single markdown document |
| `BootstrapSpec` | Helper class for incremental spec creation with deferred validation |
| `_atomic_write` | Internal helper that writes file content atomically via temp-then-rename |
| `architecture` | The optional string field on `Spec` holding the content of `architecture.md` |

## Requirements

### Requirement 1: Spec Model Architecture Field

**User Story:** As a library consumer, I want the `Spec` model to carry
optional architecture content, so that I can work with `architecture.md`
programmatically.

#### Acceptance Criteria

1. [02-REQ-1.1] THE `Spec` model SHALL have an `architecture` field of type `str | None` with a default value of `None`.

#### Edge Cases

1. [02-REQ-1.E1] WHEN a `Spec` is constructed without specifying `architecture`, THE `Spec` SHALL have `architecture` equal to `None`.

### Requirement 2: Load Architecture from Disk

**User Story:** As a library consumer, I want `load_spec` to read
`architecture.md` when it exists, so that I can access architecture
content through the `Spec` model.

#### Acceptance Criteria

1. [02-REQ-2.1] WHEN `load_spec` is called AND `architecture.md` exists in the spec directory, THE `load_spec` function SHALL read the file content as UTF-8 and populate `spec.architecture` with the content AND return the populated `Spec`.
2. [02-REQ-2.2] WHEN `load_spec` is called AND `architecture.md` does not exist in the spec directory, THE `load_spec` function SHALL set `spec.architecture` to `None` AND return the populated `Spec`.

#### Edge Cases

1. [02-REQ-2.E1] WHEN `load_spec` is called AND `architecture.md` exists but is empty, THE `load_spec` function SHALL set `spec.architecture` to an empty string.

### Requirement 3: Save Architecture to Disk

**User Story:** As a library consumer, I want `save` and `_save_internal`
to write `architecture.md` when content is present, so that architecture
content persists to disk.

#### Acceptance Criteria

1. [02-REQ-3.1] WHEN `save` is called AND `spec.architecture` is not `None`, THE `save` function SHALL write `architecture.md` to the target directory using `_atomic_write`.
2. [02-REQ-3.2] WHEN `save` is called AND `spec.architecture` is `None`, THE `save` function SHALL not write, modify, or delete any `architecture.md` file on disk.
3. [02-REQ-3.3] WHEN `_save_internal` is called AND `spec.architecture` is not `None`, THE `_save_internal` function SHALL write `architecture.md` to the target directory using `_atomic_write`.
4. [02-REQ-3.4] WHEN `_save_internal` is called AND `spec.architecture` is `None`, THE `_save_internal` function SHALL not write, modify, or delete any `architecture.md` file on disk.

#### Edge Cases

1. [02-REQ-3.E1] WHEN `save` is called AND `spec.architecture` is an empty string, THE `save` function SHALL write an empty `architecture.md` file (empty string is a valid non-None value).

### Requirement 4: Validation Exclusion

**User Story:** As a library consumer, I want validation to ignore
`architecture.md`, so that its free-form content never causes validation
failures.

#### Acceptance Criteria

1. [02-REQ-4.1] THE `validate_schema` function SHALL NOT validate `architecture.md` content against any JSON schema.
2. [02-REQ-4.2] THE `validate_cross_file` function SHALL NOT include `architecture.md` in cross-file integrity checks.
3. [02-REQ-4.3] WHEN `load_spec` checks for required files, THE `load_spec` function SHALL require only `prd.md`, `requirements.json`, `test_spec.json`, and `tasks.json` (not `architecture.md`).

#### Edge Cases

1. [02-REQ-4.E1] WHEN a `Spec` has `architecture` set to any value (including non-None), THE `validate` function SHALL return the same validation errors as if `architecture` were `None`.

### Requirement 5: Combined Rendering

**User Story:** As a library consumer, I want `render_combined` to include
architecture content in the combined output, so that the full spec is
viewable in one document.

#### Acceptance Criteria

1. [02-REQ-5.1] WHEN `render_combined` is called AND `spec.architecture` is not `None`, THE `render_combined` function SHALL include the architecture content as-is between the PRD body and the rendered requirements, separated by horizontal rules (`---`).
2. [02-REQ-5.2] WHEN `render_combined` is called AND `spec.architecture` is `None`, THE `render_combined` function SHALL render the combined output without any architecture section (same as current behavior).

#### Edge Cases

1. [02-REQ-5.E1] WHEN `render_combined` is called AND `spec.architecture` is an empty string, THE `render_combined` function SHALL include the horizontal rule separators with no content between them.

### Requirement 6: Bootstrap Architecture Support

**User Story:** As a library consumer, I want `BootstrapSpec` to support
setting architecture content during incremental spec creation, so that
architecture can be added during the bootstrap flow.

#### Acceptance Criteria

1. [02-REQ-6.1] THE `BootstrapSpec` class SHALL provide a `set_architecture` method that accepts a `str` parameter and stores the architecture content.
2. [02-REQ-6.2] WHEN `finalize` is called AND architecture has been set via `set_architecture`, THE `finalize` method SHALL include the architecture content in the assembled `Spec` AND return the `Spec` with `architecture` populated.
3. [02-REQ-6.3] WHEN `finalize` is called AND architecture has NOT been set via `set_architecture`, THE `finalize` method SHALL assemble the `Spec` with `architecture` set to `None`.
