# Test Specification: Architecture Support

## Overview

Test cases verify that the `afspec` library correctly handles the optional
`architecture.md` artifact across model construction, I/O, validation,
rendering, and bootstrap. Each test case maps 1:1 to an acceptance
criterion or correctness property.

## Test Cases

### TS-02-1: Spec model has architecture field with default None

**Requirement:** 02-REQ-1.1
**Type:** unit
**Description:** Verify the Spec model accepts an optional architecture field defaulting to None.

**Preconditions:**
- No prior state needed.

**Input:**
- Construct `Spec()` with no architecture argument.
- Construct `Spec(architecture="# Arch")`.

**Expected:**
- Default construction: `spec.architecture` is `None`.
- Explicit construction: `spec.architecture` is `"# Arch"`.

**Assertion pseudocode:**
```
spec_default = Spec()
ASSERT spec_default.architecture IS None

spec_with = Spec(architecture="# Arch")
ASSERT spec_with.architecture == "# Arch"
```

### TS-02-2: load_spec reads architecture.md when present

**Requirement:** 02-REQ-2.1
**Type:** integration
**Description:** Verify load_spec populates architecture field from architecture.md file.

**Preconditions:**
- A valid spec directory with all four required files and an architecture.md file.

**Input:**
- Directory containing prd.md, requirements.json, test_spec.json, tasks.json, architecture.md.
- architecture.md contains `"# Architecture\n\nModule overview."`.

**Expected:**
- Returned Spec has `architecture == "# Architecture\n\nModule overview."`.

**Assertion pseudocode:**
```
write_file(dir / "architecture.md", "# Architecture\n\nModule overview.")
spec = load_spec(dir)
ASSERT spec.architecture == "# Architecture\n\nModule overview."
```

### TS-02-3: load_spec sets architecture to None when absent

**Requirement:** 02-REQ-2.2
**Type:** integration
**Description:** Verify load_spec sets architecture to None when architecture.md is missing.

**Preconditions:**
- A valid spec directory with only the four required files (no architecture.md).

**Input:**
- Directory containing prd.md, requirements.json, test_spec.json, tasks.json.

**Expected:**
- Returned Spec has `architecture is None`.

**Assertion pseudocode:**
```
spec = load_spec(dir)
ASSERT spec.architecture IS None
```

### TS-02-4: save writes architecture.md when architecture is not None

**Requirement:** 02-REQ-3.1
**Type:** integration
**Description:** Verify save writes architecture.md when the Spec has architecture content.

**Preconditions:**
- A valid Spec with architecture set to a non-None string.
- Target directory exists.

**Input:**
- `spec.architecture = "# Architecture\n\nDetails here."`.

**Expected:**
- After save, `architecture.md` exists in the directory.
- File content equals `"# Architecture\n\nDetails here."`.

**Assertion pseudocode:**
```
spec.architecture = "# Architecture\n\nDetails here."
save(spec, dir)
content = read_file(dir / "architecture.md")
ASSERT content == "# Architecture\n\nDetails here."
```

### TS-02-5: save does not write architecture.md when architecture is None

**Requirement:** 02-REQ-3.2
**Type:** integration
**Description:** Verify save does not create architecture.md when architecture is None.

**Preconditions:**
- A valid Spec with architecture set to None.
- Target directory exists with no pre-existing architecture.md.

**Input:**
- `spec.architecture = None`.

**Expected:**
- After save, `architecture.md` does not exist in the directory.

**Assertion pseudocode:**
```
spec.architecture = None
save(spec, dir)
ASSERT NOT exists(dir / "architecture.md")
```

### TS-02-6: _save_internal writes architecture.md when architecture is not None

**Requirement:** 02-REQ-3.3
**Type:** integration
**Description:** Verify _save_internal writes architecture.md when present.

**Preconditions:**
- A valid Spec with architecture set to a non-None string.

**Input:**
- `spec.architecture = "# Internal arch"`.

**Expected:**
- After _save_internal, `architecture.md` exists with correct content.

**Assertion pseudocode:**
```
spec.architecture = "# Internal arch"
_save_internal(spec, dir)
content = read_file(dir / "architecture.md")
ASSERT content == "# Internal arch"
```

### TS-02-7: _save_internal does not write architecture.md when architecture is None

**Requirement:** 02-REQ-3.4
**Type:** integration
**Description:** Verify _save_internal does not create architecture.md when None.

**Preconditions:**
- A valid Spec with architecture set to None.
- No pre-existing architecture.md in the directory.

**Input:**
- `spec.architecture = None`.

**Expected:**
- After _save_internal, `architecture.md` does not exist.

**Assertion pseudocode:**
```
spec.architecture = None
_save_internal(spec, dir)
ASSERT NOT exists(dir / "architecture.md")
```

### TS-02-8: validate_schema does not validate architecture content

**Requirement:** 02-REQ-4.1
**Type:** unit
**Description:** Verify validate_schema ignores architecture field entirely.

**Preconditions:**
- A valid Spec that passes schema validation.

**Input:**
- Set `spec.architecture` to arbitrary content (e.g., invalid JSON, random text).

**Expected:**
- `validate_schema(spec)` returns no additional errors compared to architecture=None.

**Assertion pseudocode:**
```
spec_none = create_valid_spec(architecture=None)
spec_with = create_valid_spec(architecture="not json {{{")
errors_none = validate_schema(spec_none)
errors_with = validate_schema(spec_with)
ASSERT errors_none == errors_with
```

### TS-02-9: validate_cross_file does not check architecture

**Requirement:** 02-REQ-4.2
**Type:** unit
**Description:** Verify validate_cross_file ignores architecture field.

**Preconditions:**
- A valid Spec that passes cross-file validation.

**Input:**
- Set `spec.architecture` to arbitrary content.

**Expected:**
- `validate_cross_file(spec)` returns no additional errors compared to architecture=None.

**Assertion pseudocode:**
```
spec_none = create_valid_spec(architecture=None)
spec_with = create_valid_spec(architecture="anything")
errors_none = validate_cross_file(spec_none)
errors_with = validate_cross_file(spec_with)
ASSERT errors_none == errors_with
```

### TS-02-10: load_spec requires only four files

**Requirement:** 02-REQ-4.3
**Type:** integration
**Description:** Verify load_spec succeeds with only the four required files.

**Preconditions:**
- Directory with only prd.md, requirements.json, test_spec.json, tasks.json.

**Input:**
- Call load_spec on the directory.

**Expected:**
- Returns a valid Spec without error.
- No LoadError raised about missing architecture.md.

**Assertion pseudocode:**
```
spec = load_spec(dir_with_four_files)
ASSERT spec IS NOT None
ASSERT spec.architecture IS None
```

### TS-02-11: render_combined includes architecture between PRD and requirements

**Requirement:** 02-REQ-5.1
**Type:** unit
**Description:** Verify render_combined places architecture content between PRD body and requirements.

**Preconditions:**
- A Spec with all artifacts populated and architecture set to a non-None string.

**Input:**
- `spec.architecture = "# Architecture\n\nOverview content."`.

**Expected:**
- Output contains architecture content after PRD body section and before requirements section.
- Architecture content is separated by `---` horizontal rules.

**Assertion pseudocode:**
```
output = render_combined(spec)
prd_idx = output.index(spec.prd.body.rstrip())
arch_idx = output.index("# Architecture")
req_idx = output.index("# Requirements:")
ASSERT prd_idx < arch_idx < req_idx
ASSERT "---" appears between prd_body_end and arch_start
ASSERT "---" appears between arch_end and req_start
```

### TS-02-12: render_combined without architecture matches current behavior

**Requirement:** 02-REQ-5.2
**Type:** unit
**Description:** Verify render_combined output is unchanged when architecture is None.

**Preconditions:**
- A Spec with architecture set to None.

**Input:**
- Call render_combined on the spec.

**Expected:**
- Output follows the pattern: PRD body → separator → requirements → separator → test_spec → separator → tasks.
- No architecture content appears.

**Assertion pseudocode:**
```
output = render_combined(spec_without_arch)
ASSERT "# Architecture" NOT IN output
sections = output.split("---")
ASSERT len(sections) == 4  // PRD, requirements, test_spec, tasks
```

### TS-02-13: BootstrapSpec.set_architecture stores content

**Requirement:** 02-REQ-6.1
**Type:** unit
**Description:** Verify BootstrapSpec provides set_architecture and stores the content.

**Preconditions:**
- A BootstrapSpec instance.

**Input:**
- Call `set_architecture("# Arch content")`.

**Expected:**
- Internal state stores the architecture content for later use by finalize.

**Assertion pseudocode:**
```
bs = BootstrapSpec("02", "test")
bs.set_architecture("# Arch content")
ASSERT bs._architecture == "# Arch content"
```

### TS-02-14: finalize includes architecture when set

**Requirement:** 02-REQ-6.2
**Type:** unit
**Description:** Verify finalize passes architecture content to assembled Spec.

**Preconditions:**
- A fully populated BootstrapSpec with architecture set.

**Input:**
- Call finalize after setting all four required artifacts and architecture.

**Expected:**
- Returned Spec has `architecture` equal to the set content.

**Assertion pseudocode:**
```
bs = BootstrapSpec("02", "test")
bs.set_prd(prd)
bs.set_requirements(req)
bs.set_test_spec(ts)
bs.set_tasks(tasks)
bs.set_architecture("# My Arch")
spec, errors = bs.finalize()
ASSERT spec IS NOT None
ASSERT spec.architecture == "# My Arch"
```

### TS-02-15: finalize sets architecture to None when not set

**Requirement:** 02-REQ-6.3
**Type:** unit
**Description:** Verify finalize produces Spec with architecture=None when set_architecture was not called.

**Preconditions:**
- A fully populated BootstrapSpec without architecture set.

**Input:**
- Call finalize after setting only the four required artifacts.

**Expected:**
- Returned Spec has `architecture` equal to None.

**Assertion pseudocode:**
```
bs = BootstrapSpec("02", "test")
bs.set_prd(prd)
bs.set_requirements(req)
bs.set_test_spec(ts)
bs.set_tasks(tasks)
spec, errors = bs.finalize()
ASSERT spec IS NOT None
ASSERT spec.architecture IS None
```

## Property Test Cases

### TS-02-P1: Architecture round-trip preservation

**Property:** Property 1 from design.md
**Validates:** 02-REQ-2.1, 02-REQ-3.1
**Type:** property
**Description:** Saving and reloading a Spec preserves architecture content exactly.

**For any:** non-None string value for architecture (generated by Hypothesis text strategy)
**Invariant:** `load_spec(dir_after_save).architecture == original_architecture`

**Assertion pseudocode:**
```
FOR ANY arch_content IN text():
    spec = create_valid_spec(architecture=arch_content)
    save(spec, dir)
    reloaded = load_spec(dir)
    ASSERT reloaded.architecture == arch_content
```

### TS-02-P2: None architecture preserves absence

**Property:** Property 2 from design.md
**Validates:** 02-REQ-2.2, 02-REQ-3.2
**Type:** property
**Description:** Saving a Spec with architecture=None and reloading preserves None.

**For any:** valid Spec with architecture=None saved to a clean directory
**Invariant:** `load_spec(dir_after_save).architecture is None`

**Assertion pseudocode:**
```
spec = create_valid_spec(architecture=None)
save(spec, dir)
ASSERT NOT exists(dir / "architecture.md")
reloaded = load_spec(dir)
ASSERT reloaded.architecture IS None
```

### TS-02-P3: Validation neutrality

**Property:** Property 3 from design.md
**Validates:** 02-REQ-4.1, 02-REQ-4.2, 02-REQ-4.E1
**Type:** property
**Description:** Architecture content does not affect validation results.

**For any:** non-None string value for architecture (generated by Hypothesis text strategy)
**Invariant:** `validate(spec_with_arch) == validate(spec_without_arch)`

**Assertion pseudocode:**
```
FOR ANY arch_content IN text():
    spec_none = create_valid_spec(architecture=None)
    spec_with = create_valid_spec(architecture=arch_content)
    ASSERT validate(spec_none) == validate(spec_with)
```

### TS-02-P4: Combined render ordering

**Property:** Property 4 from design.md
**Validates:** 02-REQ-5.1
**Type:** property
**Description:** Architecture content always appears between PRD body and requirements in combined render.

**For any:** non-None, non-empty string value for architecture
**Invariant:** In `render_combined(spec)`, architecture content appears after PRD body and before requirements heading.

**Assertion pseudocode:**
```
FOR ANY arch_content IN text(min_size=1):
    spec = create_valid_spec(architecture=arch_content)
    output = render_combined(spec)
    arch_pos = output.find(arch_content.rstrip())
    req_pos = output.find("# Requirements:")
    ASSERT arch_pos > 0
    ASSERT arch_pos < req_pos
```

## Edge Case Tests

### TS-02-E1: Spec construction without architecture argument

**Requirement:** 02-REQ-1.E1
**Type:** unit
**Description:** Verify Spec defaults architecture to None when not specified.

**Preconditions:**
- None.

**Input:**
- Construct Spec with only required fields.

**Expected:**
- `spec.architecture` is None.

**Assertion pseudocode:**
```
spec = Spec(prd=PRDDocument(), requirements=Requirements(), test_spec=TestSpec(), tasks=Tasks())
ASSERT spec.architecture IS None
```

### TS-02-E2: load_spec with empty architecture.md

**Requirement:** 02-REQ-2.E1
**Type:** integration
**Description:** Verify load_spec sets architecture to empty string for empty file.

**Preconditions:**
- Directory with four required files and an empty architecture.md.

**Input:**
- architecture.md exists but contains empty string.

**Expected:**
- `spec.architecture == ""`.

**Assertion pseudocode:**
```
write_file(dir / "architecture.md", "")
spec = load_spec(dir)
ASSERT spec.architecture == ""
```

### TS-02-E3: save writes empty architecture.md for empty string

**Requirement:** 02-REQ-3.E1
**Type:** integration
**Description:** Verify save writes architecture.md even when architecture is empty string.

**Preconditions:**
- Spec with architecture set to empty string.

**Input:**
- `spec.architecture = ""`.

**Expected:**
- architecture.md exists on disk with empty content.

**Assertion pseudocode:**
```
spec.architecture = ""
save(spec, dir)
ASSERT exists(dir / "architecture.md")
content = read_file(dir / "architecture.md")
ASSERT content == ""
```

### TS-02-E4: validation unchanged by architecture presence

**Requirement:** 02-REQ-4.E1
**Type:** unit
**Description:** Verify validate returns same errors regardless of architecture value.

**Preconditions:**
- A Spec that passes validation.

**Input:**
- Compare validate results with architecture=None vs architecture="content".

**Expected:**
- Identical error lists.

**Assertion pseudocode:**
```
spec_none = create_valid_spec(architecture=None)
spec_with = create_valid_spec(architecture="# Arch\nContent")
ASSERT validate(spec_none) == validate(spec_with)
```

### TS-02-E5: render_combined with empty architecture string

**Requirement:** 02-REQ-5.E1
**Type:** unit
**Description:** Verify render_combined handles empty architecture string.

**Preconditions:**
- Spec with architecture set to empty string.

**Input:**
- Call render_combined.

**Expected:**
- Output contains the separators but no architecture content between them.

**Assertion pseudocode:**
```
spec = create_valid_spec(architecture="")
output = render_combined(spec)
ASSERT "---" IN output
// Architecture section exists but is empty between separators
```

## Integration Smoke Tests

### TS-02-SMOKE-1: Load-save round-trip with architecture

**Execution Path:** Path 1 and Path 2 from design.md
**Description:** End-to-end load of a spec with architecture.md, followed by save and reload.

**Setup:** Create a temp directory with all four required spec files and an architecture.md file. No mocks.

**Trigger:** `load_spec(dir)` → modify architecture → `save(spec, dir)` → `load_spec(dir)`

**Expected side effects:**
- architecture.md file exists on disk after save
- Reloaded spec has modified architecture content
- All four required files remain valid

**Must NOT satisfy with:** Mocking load_spec, save, or file I/O.

**Assertion pseudocode:**
```
spec = load_spec(dir)
ASSERT spec.architecture IS NOT None
spec = spec.model_copy(update={"architecture": "# Modified"})
save(spec, dir)
reloaded = load_spec(dir)
ASSERT reloaded.architecture == "# Modified"
```

### TS-02-SMOKE-2: Combined rendering end-to-end

**Execution Path:** Path 3 from design.md
**Description:** Load a spec with architecture and verify render_combined output ordering.

**Setup:** Create a temp directory with spec files including architecture.md. No mocks.

**Trigger:** `load_spec(dir)` → `render_combined(spec)`

**Expected side effects:**
- Rendered output contains PRD body, then architecture content, then requirements

**Must NOT satisfy with:** Mocking render_combined or load_spec.

**Assertion pseudocode:**
```
spec = load_spec(dir)
output = render_combined(spec)
prd_end = output.find("---")
arch_pos = output.find(spec.architecture.rstrip())
req_pos = output.find("# Requirements:")
ASSERT prd_end < arch_pos < req_pos
```

### TS-02-SMOKE-3: Bootstrap finalize with architecture

**Execution Path:** Path 4 from design.md
**Description:** Bootstrap a spec with architecture, finalize, save, and reload.

**Setup:** Create valid artifacts programmatically. No mocks.

**Trigger:** Bootstrap → set_architecture → finalize → save → load_spec

**Expected side effects:**
- architecture.md exists on disk after save
- Reloaded spec has architecture content matching what was set in bootstrap

**Must NOT satisfy with:** Mocking BootstrapSpec, save, or load_spec.

**Assertion pseudocode:**
```
bs = BootstrapSpec("02", "test")
bs.set_prd(valid_prd)
bs.set_requirements(valid_req)
bs.set_test_spec(valid_ts)
bs.set_tasks(valid_tasks)
bs.set_architecture("# Bootstrap Arch")
spec, errors = bs.finalize()
ASSERT spec IS NOT None
ASSERT len(errors) == 0
save(spec, dir)
reloaded = load_spec(dir)
ASSERT reloaded.architecture == "# Bootstrap Arch"
```

## Coverage Matrix

| Requirement | Test Spec Entry | Type |
|-------------|-----------------|------|
| 02-REQ-1.1 | TS-02-1 | unit |
| 02-REQ-1.E1 | TS-02-E1 | unit |
| 02-REQ-2.1 | TS-02-2 | integration |
| 02-REQ-2.2 | TS-02-3 | integration |
| 02-REQ-2.E1 | TS-02-E2 | integration |
| 02-REQ-3.1 | TS-02-4 | integration |
| 02-REQ-3.2 | TS-02-5 | integration |
| 02-REQ-3.3 | TS-02-6 | integration |
| 02-REQ-3.4 | TS-02-7 | integration |
| 02-REQ-3.E1 | TS-02-E3 | integration |
| 02-REQ-4.1 | TS-02-8 | unit |
| 02-REQ-4.2 | TS-02-9 | unit |
| 02-REQ-4.3 | TS-02-10 | integration |
| 02-REQ-4.E1 | TS-02-E4 | unit |
| 02-REQ-5.1 | TS-02-11 | unit |
| 02-REQ-5.2 | TS-02-12 | unit |
| 02-REQ-5.E1 | TS-02-E5 | unit |
| 02-REQ-6.1 | TS-02-13 | unit |
| 02-REQ-6.2 | TS-02-14 | unit |
| 02-REQ-6.3 | TS-02-15 | unit |
| Property 1 | TS-02-P1 | property |
| Property 2 | TS-02-P2 | property |
| Property 3 | TS-02-P3 | property |
| Property 4 | TS-02-P4 | property |
| Path 1+2 | TS-02-SMOKE-1 | integration |
| Path 3 | TS-02-SMOKE-2 | integration |
| Path 4 | TS-02-SMOKE-3 | integration |
