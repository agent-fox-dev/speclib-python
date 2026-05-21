# Support Optional architecture.md as Fifth Spec Artifact

## Intent

Add support for `architecture.md` as an optional fifth artifact in a spec
package, as defined in spec-format.md v1.1. The library must recognize,
load, save, and render the file without requiring it for validity.

## Background

The spec format specification (`docs/spec-format.md`) was updated from v1.0
to v1.1 to introduce `architecture.md` as an optional fifth artifact.
Previously, architectural content (module responsibilities, components and
interfaces, data models, technology stack) was placed in `prd.md` optional
sections, making the PRD a grab-bag mixing intent with architecture. The new
format cleanly separates "why/what" (prd.md) from "how" (architecture.md).

## Goals

- Recognize `architecture.md` as a valid file in a spec directory
- Load its content into the `Spec` model when present
- Write it to disk when content is provided
- Include it in combined rendering at the correct position
- Exclude it from all validation (schema and cross-file)
- Ensure it moves with the rest of the directory during archive/supersede

## Non-Goals

- Adding schema validation for `architecture.md` (it is free-form markdown)
- Adding frontmatter parsing for `architecture.md`
- Making `architecture.md` required for spec completeness
- Adding a dedicated `render_architecture` function (the file is already
  markdown)

## Required Changes

### Model

The `Spec` model gains an optional `architecture` field (`str | None`,
default `None`) representing the raw content of `architecture.md`.

### I/O

- `load_spec`: If `architecture.md` exists in the spec directory, read it
  and populate `spec.architecture`. If absent, leave as `None`.
- `save` and `_save_internal`: If `spec.architecture` is not `None`, write
  `architecture.md` atomically. If `None`, do not write or modify any
  existing `architecture.md` on disk.

### Validation

- `architecture.md` is excluded from schema validation (no schema exists).
- `architecture.md` is excluded from cross-file integrity checks.
- Completeness checks continue to require only the four JSON/markdown files.
- No changes to `validation.py` are needed — it already validates only the
  four known artifacts.

### Rendering

- `render_combined`: When `spec.architecture` is not `None`, include the
  architecture content (as-is) between the PRD body and the rendered
  requirements, separated by horizontal rules.

### Bootstrap

- `BootstrapSpec` gains a `set_architecture(content: str)` method.
- `finalize()` passes architecture content through to the assembled `Spec`.
- Architecture is not required for finalization — it remains optional.

### Lifecycle / Archive / Discovery

- No changes needed. `move_to_archive` uses `shutil.move` on the entire
  directory, so `architecture.md` moves with the rest automatically.
- `discover_specs` only reads `prd.md` frontmatter — no changes needed.

## Design Decisions

1. **Save when architecture is None**: `save()` only writes `architecture.md`
   when `spec.architecture` is not `None`. If the field is `None`, the file
   on disk is not touched. This avoids surprising deletion behavior and keeps
   the save function simple — it writes what's in the model, nothing more.

2. **Both save paths handle architecture**: `save()` and `_save_internal()`
   both write `architecture.md` when present, keeping the two paths
   consistent. This ensures lifecycle transitions don't silently drop
   architecture content.

3. **Same atomic write pattern**: `architecture.md` uses the same
   `_atomic_write` helper as the other artifacts. No special error handling
   — if the write fails, `SaveError` is raised, same as for any other file.

4. **BootstrapSpec gets set_architecture**: For API consistency, even though
   architecture is optional. The setter simply stores the content; finalize
   passes it through.

5. **create_spec does NOT gain a parameter**: The architecture field defaults
   to `None` on `Spec`, which is sufficient. Adding a parameter to
   `create_spec` would add complexity for a feature that's truly optional
   and rarely set at creation time.

6. **No new public exports**: The `Spec.architecture` field is the only new
   API surface. No new types, functions, or exceptions are introduced.

7. **UTF-8 encoding**: Same `encoding="utf-8"` pattern as all other file
   operations.

## Source

Source: https://github.com/agent-fox-dev/speclib-python/issues/1
