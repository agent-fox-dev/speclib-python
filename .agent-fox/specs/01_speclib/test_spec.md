# Test Specification: afspec

## Overview

This test specification translates every acceptance criterion, correctness property, edge case, and execution path from the afspec requirements and design documents into concrete, language-agnostic test contracts. Test cases reference Python module and function names from the design interfaces. The coding agent translates these contracts into executable Python tests using `pytest` and `hypothesis` for property tests.

Golden fixture files in `tests/golden/` provide complete spec folders for round-trip and rendering tests. Each fixture contains all four artifacts (`prd.md`, `requirements.json`, `test_spec.json`, `tasks.json`) with known-good content.

## Test Cases

### TS-01-1: Spec type exports all four artifacts

**Requirement:** 01-REQ-1.1
**Type:** unit
**Description:** The Spec model contains fields for all four spec artifacts.

**Preconditions:**
- Module `afspec` is importable.

**Input:**
- Construct a default `afspec.Spec`.

**Expected:**
- The model has fields `prd` (PRDDocument), `requirements` (Requirements), `test_spec` (TestSpec), `tasks` (Tasks).

**Assertion pseudocode:**
```
spec = afspec.Spec()
ASSERT isinstance(spec.prd, PRDDocument)
ASSERT isinstance(spec.requirements, Requirements)
ASSERT isinstance(spec.test_spec, TestSpec)
ASSERT isinstance(spec.tasks, Tasks)
```

### TS-01-2: Criterion supports six EARS patterns

**Requirement:** 01-REQ-1.2
**Type:** unit
**Description:** The Criterion type can represent all six EARS patterns with pattern-specific fields.

**Preconditions:**
- None.

**Input:**
- Create six Criterion values, one per pattern, with correct fields set.

**Expected:**
- Each Criterion serializes to valid JSON matching the schema discriminated union.

**Assertion pseudocode:**
```
for pattern in ["ubiquitous", "event_driven", "complex_event", "state_driven", "unwanted", "optional"]:
    c = new_criterion(pattern, correct_fields)
    json_str = c.model_dump_json()
    ASSERT json_str is valid JSON
    ASSERT json contains "ears_pattern": pattern
    ASSERT only pattern-specific fields are present
```

### TS-01-3: SubtaskState valid_transition

**Requirement:** 01-REQ-1.3
**Type:** unit
**Description:** valid_transition correctly classifies all state transitions.

**Preconditions:**
- None.

**Input:**
- All 30 possible (current, target) state pairs from 6 states.

**Expected:**
- Only the legal transitions return True: pending->queued, pending->dropped, queued->in_progress, queued->pending, queued->dropped, in_progress->done, in_progress->pending_reevaluation, done->pending_reevaluation, pending_reevaluation->pending, pending_reevaluation->dropped.

**Assertion pseudocode:**
```
legal = {("pending", "queued"), ("pending", "dropped"), ("queued", "in_progress"), ("queued", "pending"), ("queued", "dropped"), ("in_progress", "done"), ("in_progress", "pending_reevaluation"), ("done", "pending_reevaluation"), ("pending_reevaluation", "pending"), ("pending_reevaluation", "dropped")}
for (current, target) in all_pairs:
    result = afspec.valid_transition(current, target)
    assert result == ((current, target) in legal)
```

### TS-01-4: All sub-types are exported

**Requirement:** 01-REQ-1.4
**Type:** unit
**Description:** All 17 listed sub-types are exported and have correct field names.

**Preconditions:**
- Module `afspec` is importable.

**Input:**
- Reference each type by name.

**Expected:**
- Each type is accessible and has the fields specified in design.md interfaces.

**Assertion pseudocode:**
```
for type_name in ["Requirement", "UserStory", "CorrectnessProperty", "ExecutionPath", "PathStep", "ErrorHandlingEntry", "TestCase", "PropertyTest", "EdgeCaseTest", "SmokeTest", "Coverage", "TaskGroup", "Subtask", "VerificationSubtask", "TaskDependency", "TraceabilityEntry", "TestCommands"]:
    assert hasattr(afspec, type_name)
    assert type_name has expected fields (runtime check via model_fields)
```

### TS-01-5: load_spec reads all four artifacts

**Requirement:** 01-REQ-2.1
**Type:** integration
**Description:** load_spec loads a valid spec folder and returns a populated Spec.

**Preconditions:**
- A golden fixture folder exists at `tests/golden/valid_spec/` with all four files.

**Input:**
- `afspec.load_spec("tests/golden/valid_spec")`

**Expected:**
- Returns a `Spec` instance (does not raise).
- `spec.prd.frontmatter.spec_id` is non-empty.
- `spec.requirements.spec_id` is non-empty.
- `spec.test_spec.spec_id` is non-empty.
- `spec.tasks.spec_id` is non-empty.

**Assertion pseudocode:**
```
spec = afspec.load_spec("tests/golden/valid_spec")
assert spec is not None
assert spec.prd.frontmatter.spec_id != ""
assert spec.requirements.spec_id != ""
assert spec.test_spec.spec_id != ""
assert spec.tasks.spec_id != ""
```

### TS-01-6: PRD frontmatter and body parsed correctly

**Requirement:** 01-REQ-2.2
**Type:** unit
**Description:** Loading prd.md splits YAML frontmatter from markdown body.

**Preconditions:**
- A prd.md file with known frontmatter fields and body content.

**Input:**
- A prd.md string with `---` delimited frontmatter and a body containing `## Intent`.

**Expected:**
- Frontmatter fields are populated (spec_id, title, status, etc.).
- Body is the markdown content after the closing `---`.

**Assertion pseudocode:**
```
prd = parse_prd(prd_bytes)
assert prd.frontmatter.spec_id == "05"
assert prd.frontmatter.title == "Test Feature"
assert "## Intent" in prd.body
assert "---" not in prd.body
```

### TS-01-7: JSON artifacts unmarshaled correctly

**Requirement:** 01-REQ-2.3
**Type:** unit
**Description:** JSON artifact files deserialize into correct Pydantic models.

**Preconditions:**
- Valid JSON files for requirements, test_spec, and tasks.

**Input:**
- Known-good JSON content for each artifact.

**Expected:**
- Requirements has populated fields (introduction, glossary, requirements list).
- TestSpec has populated fields (test_cases, property_tests).
- Tasks has populated fields (task_groups, traceability).

**Assertion pseudocode:**
```
req = Requirements.model_validate_json(req_json)
assert req.introduction != ""
assert len(req.requirements) > 0
ts = TestSpec.model_validate_json(ts_json)
assert len(ts.test_cases) > 0
tasks = Tasks.model_validate_json(tasks_json)
assert len(tasks.task_groups) > 0
```

### TS-01-8: save writes all four files

**Requirement:** 01-REQ-3.1
**Type:** integration
**Description:** save writes prd.md, requirements.json, test_spec.json, and tasks.json to the target directory.

**Preconditions:**
- A loaded `Spec` from a golden fixture.
- An empty temporary directory.

**Input:**
- `afspec.save(spec, tmpdir)`

**Expected:**
- All four files exist in tmpdir.
- Each file has non-zero size.

**Assertion pseudocode:**
```
spec = afspec.load_spec("tests/golden/valid_spec")
afspec.save(spec, tmpdir)
assert (tmpdir / "prd.md").exists()
assert (tmpdir / "requirements.json").exists()
assert (tmpdir / "test_spec.json").exists()
assert (tmpdir / "tasks.json").exists()
```

### TS-01-9: Deterministic JSON serialization

**Requirement:** 01-REQ-3.2
**Type:** unit
**Description:** JSON output uses 2-space indent, trailing newline, and deterministic key order.

**Preconditions:**
- A known Requirements model with a glossary dict.

**Input:**
- Serialize the model to JSON twice.

**Expected:**
- Both outputs are byte-identical.
- Output uses 2-space indentation.
- Output ends with `}\n`.
- Glossary keys are sorted alphabetically.

**Assertion pseudocode:**
```
req = Requirements(glossary={"zebra": "z", "alpha": "a"})
out1 = afspec.marshal_json(req)
out2 = afspec.marshal_json(req)
assert out1 == out2
assert "  " in out1  # 2-space indent
assert out1.endswith("}\n")
assert out1.index("alpha") < out1.index("zebra")
```

### TS-01-10: Atomic file writes

**Requirement:** 01-REQ-3.3
**Type:** unit
**Description:** Files are written via temp-then-rename for atomicity.

**Preconditions:**
- A target directory with an existing prd.md.

**Input:**
- Save a spec to the directory.

**Expected:**
- No `.tmp` files remain after a successful save.
- The final files are complete (not truncated).

**Assertion pseudocode:**
```
afspec.save(spec, tmpdir)
tmp_files = list(tmpdir.glob("*.tmp*"))
assert len(tmp_files) == 0
content = (tmpdir / "requirements.json").read_text()
assert json.loads(content)  # valid JSON
```

### TS-01-11: updated_at auto-set on save

**Requirement:** 01-REQ-3.4
**Type:** unit
**Description:** save automatically sets updated_at to current UTC time.

**Preconditions:**
- A spec with `updated_at` set to a past time.

**Input:**
- `afspec.save(spec, tmpdir)`

**Expected:**
- The saved prd.md frontmatter has `updated_at` newer than the original value.

**Assertion pseudocode:**
```
spec.prd.frontmatter.updated_at = "2020-01-01T00:00:00Z"
before = datetime.now(timezone.utc)
afspec.save(spec, tmpdir)
reloaded = afspec.load_spec(tmpdir)
assert parse_datetime(reloaded.prd.frontmatter.updated_at) >= before
```

### TS-01-12: Coverage auto-computed on save

**Requirement:** 01-REQ-3.5
**Type:** unit
**Description:** save computes coverage by scanning tests against requirements.

**Preconditions:**
- A spec with test cases covering some but not all requirements.

**Input:**
- `afspec.save(spec, tmpdir)`

**Expected:**
- The saved test_spec.json has coverage.requirements_covered listing covered IDs.
- coverage.gaps lists uncovered IDs.

**Assertion pseudocode:**
```
spec = make_spec_with_partial_coverage()
afspec.save(spec, tmpdir)
reloaded = afspec.load_spec(tmpdir)
assert "05-REQ-1.1" in reloaded.test_spec.coverage.requirements_covered
assert "05-REQ-2.1" in reloaded.test_spec.coverage.gaps
```

### TS-01-13: Schema validation catches violations

**Requirement:** 01-REQ-4.1
**Type:** unit
**Description:** validate_schema returns errors for schema-invalid specs.

**Preconditions:**
- A spec with a missing required field in requirements.json.

**Input:**
- `afspec.validate_schema(invalid_spec)`

**Expected:**
- Returns non-empty error list.
- At least one error references "requirements.json".

**Assertion pseudocode:**
```
spec = make_spec_missing_required_field()
errs = afspec.validate_schema(spec)
assert len(errs) > 0
assert any(e.file == "requirements.json" for e in errs)
```

### TS-01-14: Schemas are bundled and loaded without network

**Requirement:** 01-REQ-4.2
**Type:** unit
**Description:** Schema data is available from bundled package resources.

**Preconditions:**
- None.

**Input:**
- Call `afspec.schemas()`.

**Expected:**
- Returns dict with 4 entries.
- Each value is non-empty and contains valid JSON.

**Assertion pseudocode:**
```
schemas = afspec.schemas()
assert len(schemas) == 4
for name, data in schemas.items():
    assert len(data) > 0
    assert json.loads(data)  # valid JSON
```

### TS-01-15: EARS pattern mismatch detected

**Requirement:** 01-REQ-4.3
**Type:** unit
**Description:** Schema validation rejects criteria with wrong fields for their pattern.

**Preconditions:**
- A criterion with ears_pattern "ubiquitous" but a non-empty "trigger" field.

**Input:**
- Validate spec containing the invalid criterion.

**Expected:**
- Validation error for the criterion.

**Assertion pseudocode:**
```
spec = make_spec_with_mismatched_criterion()
errs = afspec.validate_schema(spec)
assert any("trigger" in e.path and e.file == "requirements.json" for e in errs)
```

### TS-01-16: Cross-file validates all eight rules

**Requirement:** 01-REQ-5.1
**Type:** integration
**Description:** validate_cross_file checks all eight integrity rules.

**Preconditions:**
- A valid golden fixture spec.

**Input:**
- `afspec.validate_cross_file(valid_spec)`

**Expected:**
- Returns empty error list for a valid spec.

**Assertion pseudocode:**
```
spec = afspec.load_spec("tests/golden/valid_spec")
errs = afspec.validate_cross_file(spec)
assert len(errs) == 0
```

### TS-01-17: Dangling requirement reference detected

**Requirement:** 01-REQ-5.2
**Type:** unit
**Description:** Cross-file validation catches test cases referencing non-existent requirements.

**Preconditions:**
- A spec where a test case references "99-REQ-99.1" which does not exist in requirements.

**Input:**
- `afspec.validate_cross_file(spec)`

**Expected:**
- Error list contains violation for "99-REQ-99.1".

**Assertion pseudocode:**
```
spec = make_spec_with_dangling_ref("99-REQ-99.1")
errs = afspec.validate_cross_file(spec)
assert any("99-REQ-99.1" in e.message for e in errs)
```

### TS-01-18: Missing test coverage detected

**Requirement:** 01-REQ-5.3
**Type:** unit
**Description:** Cross-file validation catches requirements without test cases.

**Preconditions:**
- A spec with a requirement "05-REQ-1.1" that has at least one acceptance criterion (e.g., `Criterion(ears_pattern="when", system="sys", trigger="event", action="verify result")`), but no test case in `test_spec.json` covering that criterion.

**Input:**
- `afspec.validate_cross_file(spec)`

**Expected:**
- Error mentions "05-REQ-1.1" has an acceptance criterion with no corresponding test case.

**Assertion pseudocode:**
```
criterion = Criterion(ears_pattern="when", system="sys", trigger="event", action="verify result")
spec = make_spec_with_untested_requirement("05-REQ-1.1", acceptance_criteria=[criterion])
errs = afspec.validate_cross_file(spec)
assert any(e.rule == "cross-file-2" and "05-REQ-1.1" in e.message for e in errs)
```

### TS-01-19: Dangling test_spec_id detected

**Requirement:** 01-REQ-5.4
**Type:** unit
**Description:** Cross-file validation catches traceability entries referencing non-existent test spec IDs.

**Preconditions:**
- A spec where traceability references "TS-05-999" which does not exist.

**Input:**
- `afspec.validate_cross_file(spec)`

**Expected:**
- Error mentions "TS-05-999".

**Assertion pseudocode:**
```
spec = make_spec_with_dangling_test_ref("TS-05-999")
errs = afspec.validate_cross_file(spec)
assert any("TS-05-999" in e.message for e in errs)
```

### TS-01-20: Glossary cross-check

**Requirement:** 01-REQ-5.5
**Type:** unit
**Description:** Backtick-wrapped terms in requirements fields must have glossary entries.

**Preconditions:**
- A requirement with action containing `` `SpaceManager` `` but no glossary entry for "SpaceManager".

**Input:**
- `afspec.validate_cross_file(spec)`

**Expected:**
- Error about missing glossary entry for "SpaceManager".

**Assertion pseudocode:**
```
spec = make_spec_with_unglossaried_term("SpaceManager")
errs = afspec.validate_cross_file(spec)
assert any(e.rule == "cross-file-6" and "SpaceManager" in e.message for e in errs)
```

### TS-01-21: Spec ID/name consistency check

**Requirement:** 01-REQ-5.6
**Type:** unit
**Description:** Cross-file validation detects spec_id/spec_name mismatches across files.

**Preconditions:**
- A spec where prd.md has spec_id "05" but requirements.json has spec_id "06".

**Input:**
- `afspec.validate_cross_file(spec)`

**Expected:**
- Error about spec_id mismatch.

**Assertion pseudocode:**
```
spec = make_spec_with_id_mismatch()
errs = afspec.validate_cross_file(spec)
assert any(e.rule == "cross-file-7" for e in errs)
```

### TS-01-22: Legal lifecycle transitions succeed

**Requirement:** 01-REQ-6.1
**Type:** unit
**Description:** All four Transition-legal transitions succeed. Superseded requires supersede.

**Preconditions:**
- Specs in appropriate initial states.

**Input:**
- Call `transition` for each legal pair (excluding superseded).

**Expected:**
- All succeed without raising.

**Assertion pseudocode:**
```
for (current, target) in [("draft", "active"), ("active", "sealed"), ("sealed", "archived"), ("draft", "archived")]:
    spec = make_spec_in_state(current)
    afspec.transition(spec, target, tmpdir)  # does not raise
    assert spec.prd.frontmatter.status == target
    reloaded = afspec.load_spec(tmpdir)
    assert reloaded.prd.frontmatter.status == target
```

### TS-01-23: Transition updates status

**Requirement:** 01-REQ-6.2
**Type:** unit
**Description:** After successful transition, the spec status is updated.

**Preconditions:**
- A spec in draft state.

**Input:**
- `afspec.transition(spec, "active", tmpdir)`

**Expected:**
- `spec.prd.frontmatter.status` is `"active"`.

**Assertion pseudocode:**
```
spec = make_spec_in_state("draft")
afspec.transition(spec, "active", tmpdir)
assert spec.prd.frontmatter.status == "active"
```

### TS-01-24: Draft-to-active computes intent hash

**Requirement:** 01-REQ-6.3
**Type:** unit
**Description:** Transitioning draft->active computes and stores the intent hash.

**Preconditions:**
- A spec in draft state with a known `## Intent` section.

**Input:**
- `afspec.transition(spec, "active", tmpdir)`

**Expected:**
- `spec.prd.frontmatter.intent_hash` is not None and equals the expected SHA-256 hex digest.

**Assertion pseudocode:**
```
spec = make_spec_in_state("draft")
spec.prd.body = "## Intent\n\nBuild a thing.\n\n## Goals\n..."
afspec.transition(spec, "active", tmpdir)
assert spec.prd.frontmatter.intent_hash is not None
expected_hash = sha256_hex(normalize("build a thing."))
assert spec.prd.frontmatter.intent_hash == expected_hash
reloaded = afspec.load_spec(tmpdir)
assert reloaded.prd.frontmatter.intent_hash == expected_hash
```

### TS-01-25: Active state rejects intent modification

**Requirement:** 01-REQ-6.4
**Type:** unit
**Description:** save rejects specs in active state where intent hash has changed.

**Preconditions:**
- A spec transitioned to active with a locked intent hash.
- The intent section body is then modified.

**Input:**
- Modify spec.prd.body intent section, then call `afspec.save(spec, dir)`.

**Expected:**
- save raises an IntentError about intent modification.

**Assertion pseudocode:**
```
spec = make_active_spec()
spec.prd.body = replace_intent(spec.prd.body, "Different intent")
with pytest.raises(IntentError, match="intent"):
    afspec.save(spec, tmpdir)
```

### TS-01-26: Sealed/superseded/archived rejects all mutations

**Requirement:** 01-REQ-6.5
**Type:** unit
**Description:** save raises an error for sealed, superseded, or archived specs.

**Preconditions:**
- Specs in sealed, superseded, and archived states.

**Input:**
- `afspec.save(spec, dir)` for each.

**Expected:**
- All raise LifecycleError.

**Assertion pseudocode:**
```
for status in ["sealed", "superseded", "archived"]:
    spec = make_spec_in_state(status)
    with pytest.raises(LifecycleError, match=status):
        afspec.save(spec, tmpdir)
```

### TS-01-27: supersede adds deprecation banner with spec ID and persists to disk

**Requirement:** 01-REQ-6.6
**Type:** unit
**Description:** supersede prepends a deprecation banner containing the superseding spec ID and saves the result to disk.

**Preconditions:**
- A spec in sealed state saved to a temp directory.

**Input:**
- `afspec.supersede(spec, "02", tmpdir)`

**Expected:**
- `spec.prd.frontmatter.status` is `"superseded"`.
- `spec.prd.body` starts with `> **SUPERSEDED** by spec 02`.
- Reloading the spec from disk shows the same status and banner.

**Assertion pseudocode:**
```
spec = make_spec_in_state("sealed")
afspec.supersede(spec, "02", tmpdir)
assert spec.prd.frontmatter.status == "superseded"
assert spec.prd.body.startswith("> **SUPERSEDED** by spec 02")
reloaded = afspec.load_spec(tmpdir)
assert reloaded.prd.frontmatter.status == "superseded"
assert reloaded.prd.body.startswith("> **SUPERSEDED** by spec 02")
```

### TS-01-28: BootstrapSpec returns usable handle

**Requirement:** 01-REQ-7.1
**Type:** unit
**Description:** BootstrapSpec creates a bootstrap handle for incremental population.

**Preconditions:**
- None.

**Input:**
- `afspec.BootstrapSpec("05", "my_feature")`

**Expected:**
- Returns a `BootstrapSpec` instance.

**Assertion pseudocode:**
```
bs = afspec.BootstrapSpec("05", "my_feature")
assert bs is not None
```

### TS-01-29: BootstrapSpec set methods accept artifacts

**Requirement:** 01-REQ-7.2
**Type:** unit
**Description:** Each set method stores the artifact without running cross-file validation.

**Preconditions:**
- A BootstrapSpec instance.

**Input:**
- Call set_prd, set_requirements, set_test_spec, set_tasks with valid artifacts.

**Expected:**
- No exception. Artifacts are stored for later finalization.

**Assertion pseudocode:**
```
bs = afspec.BootstrapSpec("05", "my_feature")
bs.set_prd(valid_prd)
bs.set_requirements(valid_req)
bs.set_test_spec(valid_ts)
bs.set_tasks(valid_tasks)
# no exception raised
```

### TS-01-30: Finalize validates and returns Spec

**Requirement:** 01-REQ-7.3
**Type:** integration
**Description:** Finalize on a fully-populated BootstrapSpec returns a valid Spec.

**Preconditions:**
- A BootstrapSpec with all four artifacts set from a golden fixture.

**Input:**
- `bs.finalize()`

**Expected:**
- Returns a `Spec` instance and empty validation error list.

**Assertion pseudocode:**
```
bs = afspec.BootstrapSpec("05", "my_feature")
bs.set_prd(golden_prd)
bs.set_requirements(golden_req)
bs.set_test_spec(golden_ts)
bs.set_tasks(golden_tasks)
spec, errs = bs.finalize()
assert spec is not None
assert len(errs) == 0
```

### TS-01-31: render_requirements produces markdown

**Requirement:** 01-REQ-8.1
**Type:** unit
**Description:** render_requirements produces markdown with all sections.

**Preconditions:**
- A Requirements value with introduction, glossary, requirements, properties, paths, and error handling.

**Input:**
- `afspec.render_requirements(req)`

**Expected:**
- Output contains "## Glossary", requirement headings, EARS sentences, property sections, path sections, error handling table.

**Assertion pseudocode:**
```
md = afspec.render_requirements(golden_req)
assert "## Glossary" in md
assert "## Requirements" in md
assert "## Correctness Properties" in md
assert "## Execution Paths" in md
assert "## Error Handling" in md
assert "SHALL" in md
```

### TS-01-32: EARS sentences rendered from fields

**Requirement:** 01-REQ-8.2
**Type:** unit
**Description:** Each EARS pattern renders to the correct sentence template.

**Preconditions:**
- One criterion per pattern.

**Input:**
- `afspec.render_ears_sentence(criterion)` for each.

**Expected:**
- Matches the template for each pattern.

**Assertion pseudocode:**
```
c_event = Criterion(ears_pattern="event_driven", trigger="the user clicks submit", system="the form", action="validate all fields")
result = afspec.render_ears_sentence(c_event)
assert result == "WHEN the user clicks submit, THE the form SHALL validate all fields"

c_ubiq = Criterion(ears_pattern="ubiquitous", system="the system", action="log all requests")
result = afspec.render_ears_sentence(c_ubiq)
assert result == "THE the system SHALL log all requests"
```

### TS-01-33: render_test_spec produces markdown

**Requirement:** 01-REQ-8.3
**Type:** unit
**Description:** render_test_spec produces markdown with test cases, property tests, edge case tests, smoke tests, and coverage.

**Preconditions:**
- A TestSpec value with entries in all categories.

**Input:**
- `afspec.render_test_spec(ts)`

**Expected:**
- Output contains section headings for each category.

**Assertion pseudocode:**
```
md = afspec.render_test_spec(golden_ts)
assert "## Test Cases" in md
assert "## Property Tests" in md
assert "## Edge Case Tests" in md
assert "## Smoke Tests" in md
assert "## Coverage" in md
```

### TS-01-34: render_tasks produces markdown

**Requirement:** 01-REQ-8.4
**Type:** unit
**Description:** render_tasks produces markdown with test commands, dependencies, task groups with checkboxes, and traceability.

**Preconditions:**
- A Tasks value with groups, subtasks, and traceability.

**Input:**
- `afspec.render_tasks(tasks)`

**Expected:**
- Output contains test commands, task groups with checkbox syntax, and traceability table.

**Assertion pseudocode:**
```
md = afspec.render_tasks(golden_tasks)
assert "## Test Commands" in md
assert "## Tasks" in md
assert "- [ ]" in md or "- [x]" in md
assert "## Traceability" in md
```

### TS-01-35: render_combined concatenates all sections

**Requirement:** 01-REQ-8.5
**Type:** integration
**Description:** render_combined produces PRD body followed by rendered JSON artifacts.

**Preconditions:**
- A complete golden fixture Spec.

**Input:**
- `afspec.render_combined(spec)`

**Expected:**
- Output starts with the PRD body text.
- Requirements section appears after PRD.
- Test spec section appears after requirements.
- Tasks section appears after test spec.

**Assertion pseudocode:**
```
md = afspec.render_combined(golden_spec)
prd_end = md.index("---")
req_start = md.index("# Requirements")
ts_start = md.index("# Test Specification")
tasks_start = md.index("# Implementation Plan")
assert prd_end < req_start < ts_start < tasks_start
```

### TS-01-36: Deterministic rendering

**Requirement:** 01-REQ-8.6
**Type:** unit
**Description:** Same input produces byte-identical output on repeated calls.

**Preconditions:**
- A golden fixture Spec.

**Input:**
- Call each render function twice with the same input.

**Expected:**
- Both outputs are byte-identical.

**Assertion pseudocode:**
```
out1 = afspec.render_combined(spec)
out2 = afspec.render_combined(spec)
assert out1 == out2
```

### TS-01-37: discover_specs finds spec folders

**Requirement:** 01-REQ-9.1
**Type:** integration
**Description:** discover_specs finds folders matching the naming pattern and skips archive/.

**Preconditions:**
- A temp directory with `01_foo/`, `02_bar/`, `archive/03_old/`, and `readme.md`.
- Each spec folder has a valid prd.md.

**Input:**
- `afspec.discover_specs(tmproot)`

**Expected:**
- Returns 2 SpecMeta entries (01_foo, 02_bar).
- archive/03_old is not included.

**Assertion pseudocode:**
```
metas = afspec.discover_specs(tmproot)
assert len(metas) == 2
ids = [m.spec_id for m in metas]
assert "01" in ids and "02" in ids
assert "03" not in ids
```

### TS-01-38: SpecMeta loaded from frontmatter

**Requirement:** 01-REQ-9.2
**Type:** unit
**Description:** SpecMeta contains spec_id, spec_name, status, and directory path.

**Preconditions:**
- A spec folder with prd.md containing known frontmatter.

**Input:**
- `afspec.discover_specs(root)`

**Expected:**
- SpecMeta has correct spec_id, spec_name, status, and dir fields.

**Assertion pseudocode:**
```
metas = afspec.discover_specs(root)
m = metas[0]
assert m.spec_id == "01"
assert m.spec_name == "foo"
assert m.status == "draft"
assert m.dir.endswith("/01_foo")
```

### TS-01-39: build_dependency_graph constructs graph

**Requirement:** 01-REQ-9.3
**Type:** integration
**Description:** build_dependency_graph parses dependencies from tasks.json and returns a graph.

**Preconditions:**
- Two spec folders where spec 02 depends on spec 01.

**Input:**
- `afspec.build_dependency_graph(metas, root)`

**Expected:**
- Graph has an edge from "01" to "02".
- topological_sort returns ["01", "02"].

**Assertion pseudocode:**
```
graph = afspec.build_dependency_graph(metas, root)
edges = graph.edges()
assert any(e.from_spec == "01" and e.to_spec == "02" for e in edges)
order = graph.topological_sort()
assert order.index("01") < order.index("02")
```

### TS-01-40: Intent hash normalization

**Requirement:** 01-REQ-10.1
**Type:** unit
**Description:** compute_intent_hash normalizes line endings, case, whitespace, and blank lines.

**Preconditions:**
- A PRD body with mixed line endings, uppercase text, and multiple blank lines in the intent section.

**Input:**
- `afspec.compute_intent_hash(body)`

**Expected:**
- Returns a 64-character lowercase hex string.
- Returns the same hash as a body with the same content but LF line endings, lowercase, and collapsed blank lines.

**Assertion pseudocode:**
```
body_crlf = "## Intent\r\n\r\nBuild A Thing.\r\n\r\n\r\n## Goals\r\n"
body_lf = "## Intent\n\nBuild A Thing.\n\n\n## Goals\n"
hash1 = afspec.compute_intent_hash(body_crlf)
hash2 = afspec.compute_intent_hash(body_lf)
assert hash1 == hash2
assert len(hash1) == 64
```

### TS-01-41: compute_intent_hash public function signature

**Requirement:** 01-REQ-10.2
**Type:** unit
**Description:** compute_intent_hash is public and returns a hex string.

**Preconditions:**
- A valid PRD body string.

**Input:**
- `afspec.compute_intent_hash(body)`

**Expected:**
- Returns a hex string for valid input.

**Assertion pseudocode:**
```
hash_val = afspec.compute_intent_hash("## Intent\n\nDo things.\n")
assert len(hash_val) == 64
assert all(c in "0123456789abcdef" for c in hash_val)
```

### TS-01-50: DependencyGraph dependencies returns direct dependencies

**Requirement:** 01-REQ-9.4
**Type:** unit
**Description:** dependencies returns the direct dependency edges for a given spec.

**Preconditions:**
- A dependency graph where spec 02 depends on spec 01, and spec 03 depends on both 01 and 02.

**Input:**
- `graph.dependencies("03")`

**Expected:**
- Returns 2 DependencyEdge values (from 01->03 and 02->03).

**Assertion pseudocode:**
```
graph = build_graph_with(01<-02, 01<-03, 02<-03)
deps = graph.dependencies("03")
assert len(deps) == 2
dep_specs = [d.from_spec for d in deps]
assert "01" in dep_specs and "02" in dep_specs
```

### TS-01-51: DependencyGraph dependents returns direct dependents

**Requirement:** 01-REQ-9.5
**Type:** unit
**Description:** dependents returns the specs that directly depend on a given spec.

**Preconditions:**
- A dependency graph where spec 02 and 03 both depend on spec 01.

**Input:**
- `graph.dependents("01")`

**Expected:**
- Returns 2 DependencyEdge values (01->02 and 01->03).

**Assertion pseudocode:**
```
graph = build_graph_with(01<-02, 01<-03)
deps = graph.dependents("01")
assert len(deps) == 2
dep_specs = [d.to_spec for d in deps]
assert "02" in dep_specs and "03" in dep_specs
```

### TS-01-52: Task group structural rules enforced by schema

**Requirement:** 01-REQ-4.1
**Type:** unit
**Description:** Schema validation catches violations of task group structural rules: group 1 must have kind "tests", the final group must have kind "wiring_verification".

**Preconditions:**
- A valid tasks.json with known task groups.

**Input:**
- Modify group 1 to have kind "standard" instead of "tests".
- Modify the final group to have kind "standard" instead of "wiring_verification".

**Expected:**
- Schema validation returns errors for each structural violation.

**Assertion pseudocode:**
```
tasks = load_valid_tasks()
tasks.task_groups[0].kind = "standard"  # group 1 should be "tests"
errs = afspec.validate_schema(tasks, "tasks")
assert len(errs) > 0
assert any("kind" in e.message for e in errs)

tasks2 = load_valid_tasks()
last = len(tasks2.task_groups) - 1
tasks2.task_groups[last].kind = "standard"  # final group should be "wiring_verification"
errs = afspec.validate_schema(tasks2, "tasks")
assert len(errs) > 0
assert any("kind" in e.message for e in errs)
```

### TS-01-53: Traceability duplicate pair rejected by cross-file validation

**Requirement:** 01-REQ-5.7
**Type:** unit
**Description:** Cross-file validation rejects duplicate `(requirement_id, test_spec_id)` pairs in the traceability table.

**Preconditions:**
- A valid spec with a traceability table.

**Input:**
- Add a duplicate `(requirement_id, test_spec_id)` pair to the traceability table.
- Run `afspec.validate_cross_file(spec)`.

**Expected:**
- Returns error identifying the duplicate pair.

**Assertion pseudocode:**
```
spec = load_valid_spec()
entry = TraceabilityEntry(requirement_id="01-REQ-1.1", test_spec_id="TS-01-1", task_id="1.1")
spec.tasks.traceability = [entry, entry]  # duplicate
errs = afspec.validate_cross_file(spec)
assert len(errs) > 0
assert any("duplicate" in e.message and "traceability" in e.message for e in errs)
```

### TS-01-42: Constructor functions populate required fields

**Requirement:** 01-REQ-1.5
**Type:** unit
**Description:** Each constructor function populates the required fields and leaves others at default values.

**Preconditions:**
- Module `afspec` is importable.

**Input:**
- Call each constructor with sample required arguments.

**Expected:**
- Returned values have the specified fields populated.
- Non-required fields are at default values.

**Assertion pseudocode:**
```
req = afspec.Requirement(id="01-REQ-1", title="Data Model", user_story=afspec.UserStory(role="dev", action="types", benefit="safety"))
assert req.id == "01-REQ-1"
assert req.title == "Data Model"
assert req.user_story.role == "dev"
assert len(req.acceptance_criteria) == 0
assert len(req.edge_cases) == 0

vs = afspec.VerificationSubtask(id="2.V", checks=["tests pass", "lint clean"])
assert vs.id == "2.V"
assert len(vs.checks) == 2
assert vs.checks[0] == "tests pass"

spec = afspec.create_spec("01", "my_spec")
assert spec.prd.frontmatter.spec_id == "01"
assert spec.prd.frontmatter.spec_name == "my_spec"
assert spec.prd.frontmatter.status == "draft"
assert spec.requirements.spec_id == "01"
assert spec.test_spec.spec_id == "01"
assert spec.tasks.spec_id == "01"
```

### TS-01-43: EARS criterion constructors set correct pattern and fields

**Requirement:** 01-REQ-1.6
**Type:** unit
**Description:** Each EARS criterion constructor sets the correct ears_pattern and pattern-specific fields.

**Preconditions:**
- None.

**Input:**
- Call each of the six EARS criterion constructors with sample arguments.

**Expected:**
- Each returned Criterion has the correct ears_pattern value.
- Pattern-specific fields are populated.
- Non-pattern fields are empty.

**Assertion pseudocode:**
```
c = afspec.new_event_driven_criterion("01-REQ-1.1", "user clicks", "the form", "validate")
assert c.ears_pattern == "event_driven"
assert c.id == "01-REQ-1.1"
assert c.trigger == "user clicks"
assert c.system == "the form"
assert c.action == "validate"
assert c.state == ""
assert c.feature == ""
assert c.error_condition == ""
assert c.condition == ""

c2 = afspec.new_state_driven_criterion("01-REQ-1.2", "active state", "the system", "log events")
assert c2.ears_pattern == "state_driven"
assert c2.state == "active state"
```

### TS-01-44: with_return_contract returns criterion with return_contract set

**Requirement:** 01-REQ-1.6
**Type:** unit
**Description:** with_return_contract returns a new Criterion with the return_contract field populated.

**Preconditions:**
- An EARS criterion created via a constructor.

**Input:**
- Call `with_return_contract("the list of items")` on the criterion.

**Expected:**
- Returns a new Criterion (copy) with return_contract set.
- Original criterion is unchanged.

**Assertion pseudocode:**
```
c1 = afspec.new_event_driven_criterion("01-REQ-1.1", "submit", "system", "process")
c2 = c1.with_return_contract("the list of items")
assert c2.return_contract is not None
assert c2.return_contract == "the list of items"
assert c1.return_contract is None  # original unchanged
assert c2.ears_pattern == c1.ears_pattern
assert c2.id == c1.id
```

### TS-01-45: Subtask transition_to succeeds for legal transitions

**Requirement:** 01-REQ-1.7
**Type:** unit
**Description:** transition_to updates the subtask state for legal transitions.

**Preconditions:**
- A Subtask in pending state.

**Input:**
- Call `transition_to("queued")`.

**Expected:**
- Does not raise.
- subtask.state is now "queued".

**Assertion pseudocode:**
```
s = afspec.Subtask(id="1.1", title="Do thing")
assert s.state == "pending"
s.transition_to("queued")
assert s.state == "queued"
```

### TS-01-46: Add methods append and reject duplicates

**Requirement:** 01-REQ-11.1
**Type:** unit
**Description:** Add methods append unique entries and raise error for duplicates.

**Preconditions:**
- A Requirements value with one existing requirement.

**Input:**
- Add a new requirement with a unique ID. Then add one with a duplicate ID.

**Expected:**
- First add succeeds, collection grows by one.
- Second add raises SpecError, collection unchanged.

**Assertion pseudocode:**
```
r = afspec.Requirements(spec_id="01", spec_name="test", introduction="intro")
req1 = afspec.Requirement(id="01-REQ-1", title="First", user_story=afspec.UserStory(role="a", action="b", benefit="c"))
r.add_requirement(req1)
assert len(r.requirements) == 1

req2 = afspec.Requirement(id="01-REQ-2", title="Second", user_story=afspec.UserStory(role="a", action="b", benefit="c"))
r.add_requirement(req2)
assert len(r.requirements) == 2

req_dup = afspec.Requirement(id="01-REQ-1", title="Duplicate", user_story=afspec.UserStory(role="a", action="b", benefit="c"))
with pytest.raises(SpecError):
    r.add_requirement(req_dup)
assert len(r.requirements) == 2
```

### TS-01-47: Get methods return value for existing and None for missing

**Requirement:** 01-REQ-11.2
**Type:** unit
**Description:** Get methods return the correct value or None.

**Preconditions:**
- A Requirements value with one requirement.

**Input:**
- Get the existing requirement by ID. Get a non-existent ID.

**Expected:**
- Existing: returns value.
- Non-existent: returns None.

**Assertion pseudocode:**
```
r = afspec.Requirements(spec_id="01", spec_name="test", introduction="intro")
r.add_requirement(afspec.Requirement(id="01-REQ-1", title="First", user_story=afspec.UserStory(role="a", action="b", benefit="c")))
found = r.get_requirement("01-REQ-1")
assert found is not None
assert found.id == "01-REQ-1"
assert found.title == "First"

missing = r.get_requirement("01-REQ-99")
assert missing is None
```

### TS-01-48: Remove methods return True/False and modify collection

**Requirement:** 01-REQ-11.3
**Type:** unit
**Description:** Remove methods delete existing entries and return True, return False for missing.

**Preconditions:**
- A Requirements value with one requirement.

**Input:**
- Remove the existing requirement. Remove the same ID again.

**Expected:**
- First remove returns True, collection shrinks.
- Second remove returns False, collection unchanged.

**Assertion pseudocode:**
```
r = afspec.Requirements(spec_id="01", spec_name="test", introduction="intro")
r.add_requirement(afspec.Requirement(id="01-REQ-1", title="First", user_story=afspec.UserStory(role="a", action="b", benefit="c")))
assert len(r.requirements) == 1

ok = r.remove_requirement("01-REQ-1")
assert ok is True
assert len(r.requirements) == 0

ok = r.remove_requirement("01-REQ-1")
assert ok is False
```

### TS-01-49: ID generation helpers produce sequential IDs

**Requirement:** 01-REQ-11.5
**Type:** unit
**Description:** next_*_id methods return the next sequential ID based on existing entries.

**Preconditions:**
- A Requirements value with known entries.

**Input:**
- Call next_requirement_id on empty and populated collections.

**Expected:**
- Empty: returns first ID (e.g., "01-REQ-1").
- After adding one: returns next ID (e.g., "01-REQ-2").

**Assertion pseudocode:**
```
r = afspec.Requirements(spec_id="01", spec_name="test", introduction="intro")
assert r.next_requirement_id() == "01-REQ-1"

r.add_requirement(afspec.Requirement(id="01-REQ-1", title="First", user_story=afspec.UserStory(role="a", action="b", benefit="c")))
assert r.next_requirement_id() == "01-REQ-2"

ts = afspec.TestSpec(spec_id="01", spec_name="test")
assert ts.next_test_case_id() == "TS-01-1"
```

## Property Test Cases

### TS-01-P1: Round-trip idempotency

**Property:** Property 1 from design.md
**Validates:** 01-REQ-2.1, 01-REQ-3.1, 01-REQ-3.2
**Type:** property
**Description:** Load-save-load produces identical in-memory state (excluding auto-computed fields).

**For any:** valid golden fixture spec folder
**Invariant:** Loading, saving to a temp dir, then loading from that temp dir yields a Spec whose fields (excluding updated_at and coverage) are deep-equal to the original.

**Assertion pseudocode:**
```
@given(fixture=sampled_from(golden_fixtures))
def test_roundtrip_idempotency(fixture, tmp_path):
    spec1 = afspec.load_spec(fixture)
    afspec.save(spec1, tmp_path)
    spec2 = afspec.load_spec(tmp_path)
    assert deep_equal_ignoring(spec1, spec2, ["prd.frontmatter.updated_at", "test_spec.coverage"])
```

### TS-01-P2: EARS pattern field correctness

**Property:** Property 2 from design.md
**Validates:** 01-REQ-1.2, 01-REQ-4.3
**Type:** property
**Description:** Valid criteria have exactly the required fields for their pattern, no more.

**For any:** randomly generated (pattern, field_set) pair
**Invariant:** Schema validation passes if and only if the field set matches the pattern requirements.

**Assertion pseudocode:**
```
@given(pattern=sampled_from(all_patterns), fields=generated_field_sets())
def test_ears_pattern_field_correctness(pattern, fields):
    criterion = build_criterion(pattern, fields)
    errs = validate_criterion_schema(criterion)
    if fields == required_fields(pattern):
        assert len(errs) == 0
    else:
        assert len(errs) > 0
```

### TS-01-P3: Subtask state machine legality

**Property:** Property 3 from design.md
**Validates:** 01-REQ-1.3
**Type:** property
**Description:** valid_transition returns True only for the 10 legal transitions.

**For any:** pair of SubtaskState values
**Invariant:** valid_transition(current, target) == True iff (current, target) is in the legal set.

**Assertion pseudocode:**
```
legal = {("pending", "queued"), ("pending", "dropped"), ...}

@given(current=sampled_from(all_states), target=sampled_from(all_states))
def test_subtask_state_machine(current, target):
    assert afspec.valid_transition(current, target) == ((current, target) in legal)
```

### TS-01-P4: Schema validation soundness

**Property:** Property 4 from design.md
**Validates:** 01-REQ-4.1, 01-REQ-4.E1, 01-REQ-4.E2
**Type:** property
**Description:** Specs that pass schema validation have all required fields and valid enums.

**For any:** Spec that passes validate_schema
**Invariant:** All required fields are present, all ID patterns match, all enum values are valid.

**Assertion pseudocode:**
```
@given(spec=generated_valid_specs())
def test_schema_validation_soundness(spec):
    errs = afspec.validate_schema(spec)
    if len(errs) == 0:
        assert spec.requirements.spec_id != ""
        assert all(c.ears_pattern in valid_patterns for c in all_criteria(spec))
        assert all(re.match(r"^\w+-REQ-\d+$", r.id) for r in spec.requirements.requirements)
```

### TS-01-P5: Cross-file reference integrity

**Property:** Property 5 from design.md
**Validates:** 01-REQ-5.2, 01-REQ-5.4
**Type:** property
**Description:** Specs passing cross-file validation have consistent references.

**For any:** Spec that passes validate_cross_file
**Invariant:** Every requirement_id in test_spec and traceability exists in requirements.

**Assertion pseudocode:**
```
@given(spec=generated_specs_passing_crossfile())
def test_crossfile_reference_integrity(spec):
    all_req_ids = collect_ids(spec.requirements)
    for tc in spec.test_spec.test_cases:
        assert tc.requirement_id in all_req_ids
    for t in spec.tasks.traceability:
        assert t.requirement_id in all_req_ids
```

### TS-01-P6: Lifecycle transition legality

**Property:** Property 6 from design.md
**Validates:** 01-REQ-6.1, 01-REQ-6.E1, 01-REQ-6.6, 01-REQ-6.E3
**Type:** property
**Description:** transition succeeds iff the (current, target) pair is in transition's legal set. supersede succeeds iff current is sealed.

**For any:** pair of Status values
**Invariant:** transition does not raise iff the pair is in {(draft, active), (active, sealed), (sealed, archived), (draft, archived)}. transition always rejects "superseded". supersede does not raise iff current is sealed.

**Assertion pseudocode:**
```
transition_legal = {("draft", "active"), ("active", "sealed"), ("sealed", "archived"), ("draft", "archived")}

@given(current=sampled_from(all_statuses), target=sampled_from(all_statuses))
def test_lifecycle_transition_legality(current, target, tmp_path):
    spec = make_spec_in_state(current)
    if (current, target) in transition_legal:
        afspec.transition(spec, target, tmp_path)  # does not raise
    else:
        with pytest.raises(LifecycleError):
            afspec.transition(spec, target, tmp_path)

@given(current=sampled_from(all_statuses))
def test_supersede_legality(current, tmp_path):
    spec = make_spec_in_state(current)
    if current == "sealed":
        afspec.supersede(spec, "99", tmp_path)  # does not raise
    else:
        with pytest.raises(LifecycleError):
            afspec.supersede(spec, "99", tmp_path)
```

### TS-01-P7: Atomic save consistency

**Property:** Property 7 from design.md
**Validates:** 01-REQ-3.3, 01-REQ-3.E2
**Type:** property
**Description:** Failed saves leave no temp files behind.

**For any:** save operation that encounters a write failure
**Invariant:** No `.tmp` files remain in the target directory after the error.

**Assertion pseudocode:**
```
@given(failure_point=sampled_from(["file_1", "file_2", "file_3", "file_4"]))
def test_atomic_save_consistency(failure_point, tmp_path):
    inject_write_failure(tmp_path, failure_point)
    with pytest.raises(SaveError):
        afspec.save(spec, tmp_path)
    tmp_files = list(tmp_path.glob("*.tmp*"))
    assert len(tmp_files) == 0
```

### TS-01-P8: Deterministic rendering

**Property:** Property 8 from design.md
**Validates:** 01-REQ-8.6
**Type:** property
**Description:** Same input always produces the same output.

**For any:** valid Spec value
**Invariant:** Two calls to the same render function produce byte-identical output.

**Assertion pseudocode:**
```
@given(spec=generated_valid_specs())
def test_deterministic_rendering(spec):
    out1 = afspec.render_combined(spec)
    out2 = afspec.render_combined(spec)
    assert out1 == out2
```

### TS-01-P9: Intent hash stability

**Property:** Property 9 from design.md
**Validates:** 01-REQ-10.1
**Type:** property
**Description:** Intent hash is invariant under line ending, whitespace, and case variations.

**For any:** PRD body string with an `## Intent` section
**Invariant:** Normalizing the intent content then hashing produces the same result regardless of original line endings, whitespace, or casing.

**Assertion pseudocode:**
```
@given(intent_text=text(min_size=1))
def test_intent_hash_stability(intent_text):
    body_lf = "## Intent\n" + intent_text + "\n## Goals\n"
    body_crlf = "## Intent\r\n" + intent_text.replace("\n", "\r\n") + "\r\n## Goals\r\n"
    body_upper = body_lf.upper()
    h1 = afspec.compute_intent_hash(body_lf)
    h2 = afspec.compute_intent_hash(body_crlf)
    h3 = afspec.compute_intent_hash(body_upper)
    assert h1 == h2 == h3
```

### TS-01-P10: Coverage computation correctness

**Property:** Property 10 from design.md
**Validates:** 01-REQ-3.5
**Type:** property
**Description:** compute_coverage produces exact coverage sets.

**For any:** valid TestSpec and Requirements pair
**Invariant:** requirements_covered contains exactly the IDs with test entries; gaps contains exactly the IDs without.

**Assertion pseudocode:**
```
@given(ts_req=generated_test_req_pairs())
def test_coverage_computation_correctness(ts_req):
    ts, req = ts_req
    cov = afspec.compute_coverage(ts, req)
    all_ids = collect_all_criterion_ids(req) + collect_property_ids(req) + collect_path_ids(req)
    tested_ids = collect_tested_ids(ts)
    assert set(cov.requirements_covered + cov.properties_covered + cov.paths_covered) == tested_ids
    assert set(cov.gaps) == all_ids - tested_ids
```

### TS-01-P11: Constructor completeness

**Property:** Property 11 from design.md
**Validates:** 01-REQ-1.5, 01-REQ-1.6
**Type:** property
**Description:** Constructor functions populate exactly the required fields, leaving others at default values.

**For any:** constructor function and set of required arguments
**Invariant:** The returned value has the specified fields populated with the provided values, and all other fields at their default/empty values.

**Assertion pseudocode:**
```
@given(constructor=sampled_from(all_constructors))
def test_constructor_completeness(constructor):
    args = generate_valid_args(constructor)
    result = constructor(**args)
    for required_field in constructor.required_fields:
        assert getattr(result, required_field) == args[required_field]
    for other_field in set(result.model_fields) - set(constructor.required_fields):
        assert getattr(result, other_field) == type(result).model_fields[other_field].default
```

### TS-01-P12: Collection mutation idempotency

**Property:** Property 12 from design.md
**Validates:** 01-REQ-11.1, 01-REQ-11.2
**Type:** property
**Description:** Adding items with unique IDs then getting each returns the exact value added.

**For any:** sequence of items with unique IDs
**Invariant:** get returns the exact value added for every ID in the sequence, and None for any ID not in the sequence.

**Assertion pseudocode:**
```
@given(items=lists(generated_requirements(), unique_by=lambda r: r.id))
def test_collection_mutation_idempotency(items):
    r = afspec.Requirements(spec_id="01", spec_name="test", introduction="intro")
    for item in items:
        r.add_requirement(item)
    for item in items:
        found = r.get_requirement(item.id)
        assert found is not None
        assert found == item
    assert r.get_requirement("nonexistent") is None
```

## Edge Case Tests

### TS-01-E1: Criterion with mismatched fields

**Requirement:** 01-REQ-1.E1
**Type:** unit
**Description:** Schema validation catches criteria with fields incompatible with their EARS pattern.

**Preconditions:**
- A criterion with ears_pattern "ubiquitous" and a non-empty trigger field.

**Input:**
- Validate the criterion against the schema.

**Expected:**
- Validation error for the trigger field.

**Assertion pseudocode:**
```
c = Criterion(ears_pattern="ubiquitous", system="sys", action="act", trigger="event")
spec = make_spec_with_criterion(c)
errs = afspec.validate_schema(spec)
assert len(errs) > 0
```

### TS-01-E2: load_spec with missing file

**Requirement:** 01-REQ-2.E1
**Type:** unit
**Description:** load_spec raises LoadError when a file is missing.

**Preconditions:**
- A directory with only prd.md and requirements.json (missing test_spec.json and tasks.json).

**Input:**
- `afspec.load_spec(dir)`

**Expected:**
- Raises LoadError whose message identifies both missing files.

**Assertion pseudocode:**
```
with pytest.raises(LoadError, match="test_spec.json") as exc_info:
    afspec.load_spec(dir_missing_files)
assert "tasks.json" in str(exc_info.value)
```

### TS-01-E3: load_spec with malformed JSON

**Requirement:** 01-REQ-2.E2
**Type:** unit
**Description:** load_spec raises LoadError for invalid JSON.

**Preconditions:**
- A directory with a requirements.json containing invalid JSON (`{broken`).

**Input:**
- `afspec.load_spec(dir)`

**Expected:**
- Raises LoadError mentioning requirements.json and the parse error.

**Assertion pseudocode:**
```
(dir / "requirements.json").write_text("{broken")
with pytest.raises(LoadError, match="requirements.json"):
    afspec.load_spec(dir)
```

### TS-01-E4: load_spec with bad frontmatter

**Requirement:** 01-REQ-2.E3
**Type:** unit
**Description:** load_spec raises LoadError for invalid YAML frontmatter.

**Preconditions:**
- A prd.md with no `---` delimiters (no frontmatter).

**Input:**
- `afspec.load_spec(dir)`

**Expected:**
- Raises LoadError about missing or invalid frontmatter.

**Assertion pseudocode:**
```
(dir / "prd.md").write_text("# No frontmatter here\n## Intent\nStuff.\n")
with pytest.raises(LoadError, match="frontmatter"):
    afspec.load_spec(dir)
```

### TS-01-E5: save to non-existent directory

**Requirement:** 01-REQ-3.E1
**Type:** unit
**Description:** save raises SaveError when target directory doesn't exist.

**Preconditions:**
- A valid Spec.

**Input:**
- `afspec.save(spec, "/nonexistent/path")`

**Expected:**
- Raises SaveError, no files created.

**Assertion pseudocode:**
```
with pytest.raises(SaveError):
    afspec.save(spec, "/nonexistent/path")
```

### TS-01-E6: save partial failure cleanup

**Requirement:** 01-REQ-3.E2
**Type:** unit
**Description:** If a write fails mid-save, temp files are cleaned up.

**Preconditions:**
- A directory where writing the third file will fail (e.g., injected error or read-only filesystem mock).

**Input:**
- `afspec.save(spec, dir)`

**Expected:**
- Raises SaveError.
- No `.tmp` files remain in the directory.

**Assertion pseudocode:**
```
inject_failure_on_third_write(dir)
with pytest.raises(SaveError):
    afspec.save(spec, dir)
assert len(list(dir.glob("*.tmp*"))) == 0
```

### TS-01-E7: Concurrent saves don't corrupt

**Requirement:** 01-REQ-3.E3
**Type:** integration
**Description:** Concurrent saves to the same directory produce consistent results.

**Preconditions:**
- A valid Spec and a temporary directory.

**Input:**
- Launch 10 threads each calling `afspec.save(spec, dir)`.

**Expected:**
- All complete without exception.
- Final files on disk are valid JSON.

**Assertion pseudocode:**
```
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
    futures = [pool.submit(afspec.save, spec, dir) for _ in range(10)]
    concurrent.futures.wait(futures)
content = (dir / "requirements.json").read_text()
assert json.loads(content)  # valid JSON
```

### TS-01-E8: Unknown fields in JSON

**Requirement:** 01-REQ-4.E1
**Type:** unit
**Description:** Schema validation reports unknown fields.

**Preconditions:**
- A valid spec whose requirements artifact is serialized to a dict, then mutated to include an unknown field before JSON Schema validation.

**Input:**
- Validate the mutated dict against the requirements JSON Schema.

**Expected:**
- Error mentioning the unknown field.

**Assertion pseudocode:**
```
import importlib.resources, json, jsonschema
schema = json.loads(importlib.resources.read_text("afspec.schemas", "requirements.schema.json"))
req_dict = spec.requirements.model_dump()
req_dict["unknown_field"] = "value"
validator = jsonschema.Draft202012Validator(schema)
errors = list(validator.iter_errors(req_dict))
assert any("unknown_field" in e.message or "additional" in e.message for e in errors)
```

### TS-01-E9: Invalid ears_pattern value

**Requirement:** 01-REQ-4.E2
**Type:** unit
**Description:** Schema validation rejects unrecognized ears_pattern values.

**Preconditions:**
- A criterion with ears_pattern "invalid_pattern".

**Input:**
- `afspec.validate_schema(spec)`

**Expected:**
- Error about invalid ears_pattern.

**Assertion pseudocode:**
```
c = Criterion(ears_pattern="invalid_pattern", system="sys", action="act")
spec = make_spec_with_criterion(c)
errs = afspec.validate_schema(spec)
assert any("ears_pattern" in e.path for e in errs)
```

### TS-01-E10: Cross-file validation on incomplete spec

**Requirement:** 01-REQ-5.E1
**Type:** unit
**Description:** validate_cross_file returns error on incomplete spec.

**Preconditions:**
- A Spec with only prd and requirements set (test_spec and tasks are default).

**Input:**
- `afspec.validate_cross_file(incomplete_spec)`

**Expected:**
- Error indicating the spec is incomplete.

**Assertion pseudocode:**
```
spec = Spec(prd=valid_prd, requirements=valid_req)
errs = afspec.validate_cross_file(spec)
assert len(errs) > 0
assert any("incomplete" in e.message for e in errs)
```

### TS-01-E11: Illegal lifecycle transition

**Requirement:** 01-REQ-6.E1
**Type:** unit
**Description:** transition raises LifecycleError for illegal state changes and for "superseded".

**Preconditions:**
- A spec in draft state. A spec in sealed state.

**Input:**
- `afspec.transition(spec, "sealed", tmpdir)` (draft->sealed is not allowed).
- `afspec.transition(spec, "superseded", tmpdir)` (must use supersede).

**Expected:**
- Both raise LifecycleError.

**Assertion pseudocode:**
```
spec = make_spec_in_state("draft")
with pytest.raises(LifecycleError, match="draft.*sealed"):
    afspec.transition(spec, "sealed", tmpdir)

spec2 = make_spec_in_state("sealed")
with pytest.raises(LifecycleError, match="[Ss]upersede"):
    afspec.transition(spec2, "superseded", tmpdir)
```

### TS-01-E12: Intent hash mismatch in active state

**Requirement:** 01-REQ-6.E2
**Type:** unit
**Description:** Library detects intent modification in active state.

**Preconditions:**
- A spec transitioned to active with intent hash locked.
- Intent section body modified after transition.

**Input:**
- Call save or hash check after modifying intent.

**Expected:**
- Raises IntentError about intent hash mismatch.

**Assertion pseudocode:**
```
spec = make_active_spec_with_known_intent()
spec.prd.body = replace_intent(spec.prd.body, "Completely different intent")
with pytest.raises(IntentError, match="intent"):
    afspec.save(spec, tmpdir)
```

### TS-01-E13: Finalize with missing artifacts

**Requirement:** 01-REQ-7.E1
**Type:** unit
**Description:** Finalize returns error listing missing artifacts.

**Preconditions:**
- A BootstrapSpec with only PRD and Requirements set.

**Input:**
- `bs.finalize()`

**Expected:**
- Returns None for spec and error list mentioning test_spec and tasks as missing.

**Assertion pseudocode:**
```
bs = afspec.BootstrapSpec("05", "feat")
bs.set_prd(valid_prd)
bs.set_requirements(valid_req)
spec, errs = bs.finalize()
assert spec is None
assert any("test_spec" in e.message for e in errs)
assert any("tasks" in e.message for e in errs)
```

### TS-01-E14: BootstrapSpec artifact overwrite

**Requirement:** 01-REQ-7.E2
**Type:** unit
**Description:** Setting the same artifact twice uses the latest value.

**Preconditions:**
- A BootstrapSpec.

**Input:**
- Call set_requirements with two different Requirements values.

**Expected:**
- Finalize uses the second value.

**Assertion pseudocode:**
```
bs = afspec.BootstrapSpec("05", "feat")
bs.set_requirements(req_v1)
bs.set_requirements(req_v2)
# ... set other artifacts ...
spec, _ = bs.finalize()
assert spec.requirements == req_v2
```

### TS-01-E15: Return contract appended to EARS sentence

**Requirement:** 01-REQ-8.E1
**Type:** unit
**Description:** Non-None return_contract is appended to the rendered sentence.

**Preconditions:**
- A criterion with a non-None return_contract.

**Input:**
- `afspec.render_ears_sentence(criterion)`

**Expected:**
- Rendered sentence ends with "AND return {return_contract}".

**Assertion pseudocode:**
```
c = Criterion(ears_pattern="event_driven", trigger="items are submitted", system="the system", action="process them", return_contract="the list of created items")
result = afspec.render_ears_sentence(c)
assert result.endswith("AND return the list of created items")
```

### TS-01-E16: discover_specs with non-existent root

**Requirement:** 01-REQ-9.E1
**Type:** unit
**Description:** discover_specs raises SpecError for non-existent directory.

**Preconditions:**
- Root directory does not exist.

**Input:**
- `afspec.discover_specs("/nonexistent")`

**Expected:**
- Raises SpecError.

**Assertion pseudocode:**
```
with pytest.raises(SpecError):
    afspec.discover_specs("/nonexistent")
```

### TS-01-E17: Non-spec directories skipped

**Requirement:** 01-REQ-9.E2
**Type:** unit
**Description:** Directories not matching the naming pattern are skipped.

**Preconditions:**
- Root with subdirectories: `01_valid/`, `docs/`, `.hidden/`, `no_number/`.

**Input:**
- `afspec.discover_specs(root)`

**Expected:**
- Only `01_valid` is returned.

**Assertion pseudocode:**
```
metas = afspec.discover_specs(root)
assert len(metas) == 1
assert metas[0].spec_id == "01"
```

### TS-01-E18: Dependency cycle detected

**Requirement:** 01-REQ-9.E3
**Type:** unit
**Description:** build_dependency_graph raises SpecError for cyclic dependencies.

**Preconditions:**
- Spec 01 depends on spec 02, and spec 02 depends on spec 01.

**Input:**
- `afspec.build_dependency_graph(metas, root)`

**Expected:**
- Raises SpecError identifying the cycle.

**Assertion pseudocode:**
```
# Set up: 01 depends_on 02, 02 depends_on 01
with pytest.raises(SpecError, match="cycle"):
    afspec.build_dependency_graph(metas, root)
```

### TS-01-E19: Missing Intent section

**Requirement:** 01-REQ-10.E1
**Type:** unit
**Description:** compute_intent_hash raises IntentError when Intent section is absent.

**Preconditions:**
- A PRD body without `## Intent`.

**Input:**
- `afspec.compute_intent_hash("# Title\n\n## Goals\nStuff.\n")`

**Expected:**
- Raises IntentError.

**Assertion pseudocode:**
```
with pytest.raises(IntentError, match="Intent"):
    afspec.compute_intent_hash("# Title\n\n## Goals\nStuff.\n")
```

### TS-01-E20: Empty Intent section

**Requirement:** 01-REQ-10.E2
**Type:** unit
**Description:** Empty Intent section returns hash of empty byte slice.

**Preconditions:**
- A PRD body with `## Intent` section containing only whitespace.

**Input:**
- `afspec.compute_intent_hash("## Intent\n   \n\n## Goals\n")`

**Expected:**
- Returns the SHA-256 of empty bytes: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

**Assertion pseudocode:**
```
hash_val = afspec.compute_intent_hash("## Intent\n   \n\n## Goals\n")
assert hash_val == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
```

### TS-01-E21: Add with duplicate ID raises error, collection unchanged

**Requirement:** 01-REQ-11.E1
**Type:** unit
**Description:** Adding an entry with a duplicate ID raises error and does not modify the collection.

**Preconditions:**
- A Requirements value with one requirement (ID "01-REQ-1").

**Input:**
- Call `add_requirement` with a Requirement whose ID is "01-REQ-1".

**Expected:**
- Raises SpecError mentioning "01-REQ-1".
- `len(r.requirements)` is still 1.
- The existing requirement is unchanged.

**Assertion pseudocode:**
```
r = afspec.Requirements(spec_id="01", spec_name="test", introduction="intro")
orig = afspec.Requirement(id="01-REQ-1", title="Original", user_story=afspec.UserStory(role="a", action="b", benefit="c"))
r.add_requirement(orig)
dup = afspec.Requirement(id="01-REQ-1", title="Duplicate", user_story=afspec.UserStory(role="x", action="y", benefit="z"))
with pytest.raises(SpecError, match="01-REQ-1"):
    r.add_requirement(dup)
assert len(r.requirements) == 1
found = r.get_requirement("01-REQ-1")
assert found.title == "Original"
```

### TS-01-E22: Get non-existent returns None

**Requirement:** 01-REQ-11.E2
**Type:** unit
**Description:** Getting an entry with a non-existent ID returns None.

**Preconditions:**
- An empty Requirements value.

**Input:**
- Call `get_requirement("01-REQ-99")`.

**Expected:**
- Returns None.

**Assertion pseudocode:**
```
r = afspec.Requirements(spec_id="01", spec_name="test", introduction="intro")
found = r.get_requirement("01-REQ-99")
assert found is None
```

### TS-01-E23: next_requirement_id on empty returns first ID

**Requirement:** 01-REQ-11.E3
**Type:** unit
**Description:** next_requirement_id on an empty collection returns the first ID in the sequence.

**Preconditions:**
- A Requirements value with no requirements.

**Input:**
- Call `next_requirement_id()`.

**Expected:**
- Returns "01-REQ-1" (using the spec_id from the Requirements value).

**Assertion pseudocode:**
```
r = afspec.Requirements(spec_id="01", spec_name="test", introduction="intro")
assert r.next_requirement_id() == "01-REQ-1"

r2 = afspec.Requirements(spec_id="05", spec_name="feat", introduction="intro")
assert r2.next_requirement_id() == "05-REQ-1"
```

### TS-01-E24: transition_to with illegal transition raises error

**Requirement:** 01-REQ-1.7
**Type:** unit
**Description:** transition_to raises LifecycleError for illegal state transitions.

**Preconditions:**
- A Subtask in pending state.

**Input:**
- Call `transition_to("done")` (pending->done is illegal).

**Expected:**
- Raises LifecycleError naming "pending" and "done".
- State remains pending.

**Assertion pseudocode:**
```
s = afspec.Subtask(id="1.1", title="Do thing")
with pytest.raises(LifecycleError, match="pending.*done"):
    s.transition_to("done")
assert s.state == "pending"
```

### TS-01-E25: set_glossary_entry overwrites existing entry

**Requirement:** 01-REQ-11.4
**Type:** unit
**Description:** set_glossary_entry inserts new entries and overwrites existing ones.

**Preconditions:**
- A Requirements value with no glossary entries.

**Input:**
- Set "Spec" -> "A package". Then set "Spec" -> "Updated definition".

**Expected:**
- After first set: glossary has one entry.
- After second set: glossary still has one entry with updated value.

**Assertion pseudocode:**
```
r = afspec.Requirements(spec_id="01", spec_name="test", introduction="intro")
r.set_glossary_entry("Spec", "A package")
assert r.glossary["Spec"] == "A package"

r.set_glossary_entry("Spec", "Updated definition")
assert r.glossary["Spec"] == "Updated definition"
assert len(r.glossary) == 1
```

### TS-01-E26: Dangling dependency reference detected

**Requirement:** 01-REQ-9.E4
**Type:** unit
**Description:** build_dependency_graph raises SpecError when depends_on_spec references a non-existent spec.

**Preconditions:**
- Spec 01 exists. Spec 02 declares a dependency on spec "99" which does not exist.

**Input:**
- `afspec.build_dependency_graph(metas, root)` where metas only contains specs 01 and 02.

**Expected:**
- Raises SpecError mentioning "99" and "02".

**Assertion pseudocode:**
```
# Set up: spec 02 has dependency on "99" which is not in metas
with pytest.raises(SpecError, match="99"):
    afspec.build_dependency_graph(metas, root)
```

### TS-01-E27: dependencies/dependents with no edges returns empty list

**Requirement:** 01-REQ-9.E5
**Type:** unit
**Description:** dependencies and dependents return empty lists for specs with no edges.

**Preconditions:**
- A dependency graph with spec 01 (no dependencies) and spec 02 depends on 01.

**Input:**
- `graph.dependencies("01")` and `graph.dependents("02")`

**Expected:**
- Both return empty (non-None) lists.

**Assertion pseudocode:**
```
graph = build_graph_with(01<-02)
deps = graph.dependencies("01")
assert deps is not None
assert len(deps) == 0

dependents = graph.dependents("02")
assert dependents is not None
assert len(dependents) == 0
```

### TS-01-E28: supersede called on non-sealed spec

**Requirement:** 01-REQ-6.E3
**Type:** unit
**Description:** supersede raises LifecycleError when spec is not sealed.

**Preconditions:**
- Specs in draft, active, superseded, and archived states.

**Input:**
- `afspec.supersede(spec, "02", tmpdir)` for each.

**Expected:**
- All raise LifecycleError naming the current state.
- Status remains unchanged.

**Assertion pseudocode:**
```
for status in ["draft", "active", "superseded", "archived"]:
    spec = make_spec_in_state(status)
    with pytest.raises(LifecycleError, match=status):
        afspec.supersede(spec, "02", tmpdir)
    assert spec.prd.frontmatter.status == status
```

### TS-01-E29: move_to_archive transitions and moves folder

**Requirement:** 01-REQ-6.7
**Type:** integration
**Description:** move_to_archive transitions spec to archived, saves, and moves the folder.

**Preconditions:**
- A temp root with a spec folder `01_feature/` in draft state.

**Input:**
- `afspec.move_to_archive(root / "01_feature", root)`

**Expected:**
- `root/01_feature/` no longer exists.
- `root/archive/01_feature/` exists with all four files.
- The spec in the archive folder has status "archived".

**Assertion pseudocode:**
```
setup_spec_in_root(root, "01_feature", "draft")
afspec.move_to_archive(root / "01_feature", root)
assert not (root / "01_feature").exists()
assert (root / "archive" / "01_feature").exists()
spec = afspec.load_spec(root / "archive" / "01_feature")
assert spec.prd.frontmatter.status == "archived"
```

### TS-01-E30: move_to_archive on non-existent directory

**Requirement:** 01-REQ-6.E4
**Type:** unit
**Description:** move_to_archive raises SpecError for non-existent spec directory.

**Preconditions:**
- Directory does not exist.

**Input:**
- `afspec.move_to_archive("/nonexistent/01_feature", "/nonexistent")`

**Expected:**
- Raises SpecError.

**Assertion pseudocode:**
```
with pytest.raises(SpecError):
    afspec.move_to_archive("/nonexistent/01_feature", "/nonexistent")
```

### TS-01-E31: move_to_archive on non-archivable state

**Requirement:** 01-REQ-6.E4
**Type:** unit
**Description:** move_to_archive raises LifecycleError for specs in active state (the only non-archivable state).

**Preconditions:**
- A spec in active state.

**Input:**
- `afspec.move_to_archive(spec_dir, root)`

**Expected:**
- Raises LifecycleError naming the current state.
- Spec folder is not moved.

**Assertion pseudocode:**
```
setup_spec_in_root(root, "01_feature", "active")
with pytest.raises(LifecycleError, match="active"):
    afspec.move_to_archive(root / "01_feature", root)
assert (root / "01_feature").exists()
assert not (root / "archive" / "01_feature").exists()
```

### TS-01-E32: move_to_archive on already-archived folder

**Requirement:** 01-REQ-6.E5
**Type:** unit
**Description:** move_to_archive raises SpecError when spec is already in the archive directory.

**Preconditions:**
- A spec folder already at `root/archive/01_feature/`.

**Input:**
- `afspec.move_to_archive(root / "archive" / "01_feature", root)`

**Expected:**
- Raises SpecError indicating spec is already archived.

**Assertion pseudocode:**
```
setup_spec_in_archive(root, "01_feature")
with pytest.raises(SpecError, match="already archived"):
    afspec.move_to_archive(root / "archive" / "01_feature", root)
```

### TS-01-E33: move_to_archive on superseded spec succeeds

**Requirement:** 01-REQ-6.E4
**Type:** integration
**Description:** move_to_archive accepts a superseded spec, skips status transition (already terminal), and moves the folder to archive/.

**Preconditions:**
- A spec in superseded state in a temp root.

**Input:**
- `afspec.move_to_archive(root / "01_feature", root)`

**Expected:**
- Does not raise.
- Folder moved to `root/archive/01_feature/`.
- Status remains "superseded" on disk (not changed to "archived").
- Deprecation banner is preserved.

**Assertion pseudocode:**
```
setup_spec_in_root(root, "01_feature", "superseded_with_banner")
afspec.move_to_archive(root / "01_feature", root)
assert not (root / "01_feature").exists()
assert (root / "archive" / "01_feature").exists()
reloaded = afspec.load_spec(root / "archive" / "01_feature")
assert reloaded.prd.frontmatter.status == "superseded"
assert reloaded.prd.body.startswith("> **SUPERSEDED**")
```

### TS-01-E34: add_traceability_entry with duplicate pair raises error

**Requirement:** 01-REQ-11.E4
**Type:** unit
**Description:** add_traceability_entry raises SpecError when a `(requirement_id, test_spec_id)` pair already exists.

**Preconditions:**
- A Tasks value with one traceability entry `("01-REQ-1.1", "TS-01-1", "1.1")`.

**Input:**
- Add another entry with the same `requirement_id` and `test_spec_id` but different `task_id`.

**Expected:**
- Raises SpecError mentioning "duplicate".
- Traceability table is not modified.

**Assertion pseudocode:**
```
tasks = afspec.Tasks(spec_id="01", spec_name="test")
entry1 = afspec.TraceabilityEntry(requirement_id="01-REQ-1.1", test_spec_id="TS-01-1", task_id="1.1")
tasks.add_traceability_entry(entry1)
assert len(tasks.traceability) == 1

entry2 = afspec.TraceabilityEntry(requirement_id="01-REQ-1.1", test_spec_id="TS-01-1", task_id="2.1")
with pytest.raises(SpecError, match="duplicate"):
    tasks.add_traceability_entry(entry2)
assert len(tasks.traceability) == 1
```

## Integration Smoke Tests

### TS-01-SMOKE-1: Load spec from disk end-to-end

**Execution Path:** Path 1 from design.md
**Description:** Full path from load_spec call through parsing to populated Spec.

**Setup:** Golden fixture folder `tests/golden/valid_spec/` with all four artifacts.

**Trigger:** `afspec.load_spec("tests/golden/valid_spec")`

**Expected side effects:**
- Returns `Spec` with all four artifacts populated.
- PRD frontmatter has all 12 fields.
- Requirements has at least one requirement with acceptance criteria.
- TestSpec has at least one test case.
- Tasks has at least one task group.

**Must NOT satisfy with:** No mocking of file I/O or JSON parsing.

**Assertion pseudocode:**
```
spec = afspec.load_spec("tests/golden/valid_spec")
assert spec.prd.frontmatter.spec_id != ""
assert len(spec.requirements.requirements) >= 1
assert len(spec.requirements.requirements[0].acceptance_criteria) >= 1
assert len(spec.test_spec.test_cases) >= 1
assert len(spec.tasks.task_groups) >= 1
```

### TS-01-SMOKE-2: Save spec to disk end-to-end

**Execution Path:** Path 2 from design.md
**Description:** Full path from save through coverage computation, updated_at, serialization, and atomic writes.

**Setup:** Loaded golden fixture Spec. Empty temp directory.

**Trigger:** `afspec.save(spec, tmpdir)`

**Expected side effects:**
- All four files written to tmpdir.
- prd.md has updated `updated_at` field.
- test_spec.json has populated `coverage` field.
- JSON files are valid and deterministic.

**Must NOT satisfy with:** No mocking of file system operations.

**Assertion pseudocode:**
```
spec = afspec.load_spec("tests/golden/valid_spec")
original_updated = spec.prd.frontmatter.updated_at
afspec.save(spec, tmpdir)
reloaded = afspec.load_spec(tmpdir)
assert reloaded.prd.frontmatter.updated_at != original_updated
assert len(reloaded.test_spec.coverage.requirements_covered) > 0
```

### TS-01-SMOKE-3: Validate spec end-to-end

**Execution Path:** Path 3 from design.md
**Description:** Full path from validate through schema and cross-file checks.

**Setup:** Golden fixture Spec (valid). Modified Spec with known violations.

**Trigger:** `afspec.validate(spec)` for both.

**Expected side effects:**
- Valid spec returns empty error list.
- Invalid spec returns non-empty error list with specific violations.

**Must NOT satisfy with:** No mocking of schema loading or validation engine.

**Assertion pseudocode:**
```
valid_spec = afspec.load_spec("tests/golden/valid_spec")
errs = afspec.validate(valid_spec)
assert len(errs) == 0

invalid_spec = mutate_to_invalid(valid_spec)
errs = afspec.validate(invalid_spec)
assert len(errs) > 0
```

### TS-01-SMOKE-4: Lifecycle transition end-to-end

**Execution Path:** Path 4 from design.md
**Description:** Full path from transition through state machine check, intent hash computation, status update, and persistence to disk.

**Setup:** Spec in draft state with a known Intent section saved to a temp directory.

**Trigger:** `afspec.transition(spec, "active", tmpdir)`

**Expected side effects:**
- Status changes to active.
- intent_hash is populated and correct.
- Transition persists the result to disk (compound operation).
- Reloaded spec from disk has the same status and intent hash.
- Modifying intent and saving fails (intent hash mismatch).

**Must NOT satisfy with:** No mocking of intent hash computation.

**Assertion pseudocode:**
```
spec = load_draft_spec()
afspec.transition(spec, "active", tmpdir)
assert spec.prd.frontmatter.status == "active"
assert spec.prd.frontmatter.intent_hash is not None
reloaded = afspec.load_spec(tmpdir)
assert reloaded.prd.frontmatter.status == "active"
assert reloaded.prd.frontmatter.intent_hash == spec.prd.frontmatter.intent_hash
spec.prd.body = replace_intent(spec.prd.body, "changed")
with pytest.raises(IntentError):
    afspec.save(spec, tmpdir)
```

### TS-01-SMOKE-5: Bootstrap spec creation end-to-end

**Execution Path:** Path 5 from design.md
**Description:** Full path from BootstrapSpec through sequential population to finalize.

**Setup:** Individual artifacts from a golden fixture.

**Trigger:** `BootstrapSpec` -> `set_prd` -> `set_requirements` -> `set_test_spec` -> `set_tasks` -> `finalize()`

**Expected side effects:**
- finalize returns a valid `Spec`.
- The Spec passes validate with no errors.

**Must NOT satisfy with:** No mocking of validation.

**Assertion pseudocode:**
```
bs = afspec.BootstrapSpec("05", "my_feature")
bs.set_prd(golden_prd)
bs.set_requirements(golden_req)
bs.set_test_spec(golden_ts)
bs.set_tasks(golden_tasks)
spec, errs = bs.finalize()
assert spec is not None
assert len(errs) == 0
validation_errs = afspec.validate(spec)
assert len(validation_errs) == 0
```

### TS-01-SMOKE-6: Render markdown end-to-end

**Execution Path:** Path 6 from design.md
**Description:** Full path from render_combined through EARS rendering, per-file rendering, and concatenation.

**Setup:** Golden fixture Spec.

**Trigger:** `afspec.render_combined(spec)`

**Expected side effects:**
- Returns non-empty markdown string.
- Contains PRD body content.
- Contains EARS-rendered sentences with "SHALL".
- Contains rendered test cases.
- Contains rendered task groups with checkboxes.

**Must NOT satisfy with:** No mocking of individual render functions.

**Assertion pseudocode:**
```
spec = afspec.load_spec("tests/golden/valid_spec")
md = afspec.render_combined(spec)
assert len(md) > 0
assert spec.prd.body[:50] in md  # first 50 chars of PRD body
assert "SHALL" in md
assert "[ ]" in md or "[x]" in md
```

### TS-01-SMOKE-7: Discover specs end-to-end

**Execution Path:** Path 7 from design.md
**Description:** Full path from discover_specs through directory scanning, metadata loading, and dependency graph construction.

**Setup:** A temp directory with two spec folders (01_alpha, 02_beta) where 02 depends on 01.

**Trigger:** `discover_specs(root)` then `build_dependency_graph(metas, root)`

**Expected side effects:**
- discover_specs returns 2 SpecMeta entries.
- build_dependency_graph returns a graph with one edge.
- topological_sort returns ["01", "02"].

**Must NOT satisfy with:** No mocking of file system or JSON parsing.

**Assertion pseudocode:**
```
setup_spec_folders(root, ["01_alpha", "02_beta_depends_on_01"])
metas = afspec.discover_specs(root)
assert len(metas) == 2
graph = afspec.build_dependency_graph(metas, root)
order = graph.topological_sort()
assert order == ["01", "02"]
```

### TS-01-SMOKE-8: Programmatic spec construction end-to-end

**Execution Path:** Path 8 from design.md
**Description:** Full path from create_spec through constructor calls, add methods, and validation.

**Setup:** None (constructs everything programmatically).

**Trigger:** Build a complete spec using only constructors and add methods, then validate.

**Expected side effects:**
- `create_spec` returns a Spec with consistent spec_id and spec_name across all artifacts.
- Adding requirements, criteria, test cases, and task groups succeeds.
- The resulting Spec passes `validate` with no errors.
- Saving the Spec to disk and reloading produces the same in-memory state.

**Must NOT satisfy with:** No manual field assignment -- all construction via constructors and add methods.

**Assertion pseudocode:**
```
spec = afspec.create_spec("99", "programmatic_test")
assert spec.prd.frontmatter.spec_id == "99"
assert spec.requirements.spec_id == "99"

story = afspec.UserStory(role="developer", action="construct specs", benefit="programmatic creation")
req = afspec.Requirement(id=spec.requirements.next_requirement_id(), title="Test Feature", user_story=story)
c = afspec.new_event_driven_criterion(req.next_criterion_id(), "data arrives", "the system", "process it")
req.add_criterion(c)
spec.requirements.add_requirement(req)
spec.requirements.set_glossary_entry("system", "the afspec library")

tc = afspec.TestCase(id=spec.test_spec.next_test_case_id(), requirement_id=c.id, type="unit", description="Test the feature")
spec.test_spec.add_test_case(tc)

group = afspec.TaskGroup(group_number=1, kind="standard", title="Implement feature")
sub = afspec.Subtask(id="1.1", title="Write code")
group.add_subtask(sub)
spec.tasks.add_task_group(group)
spec.tasks.add_traceability_entry(afspec.TraceabilityEntry(requirement_id=c.id, test_spec_id=tc.id, task_id="1.1"))

# Validate (schema validation may require more complete data -- this tests the construction path)
afspec.save(spec, tmpdir)
reloaded = afspec.load_spec(tmpdir)
assert reloaded.requirements.spec_id == "99"
```

### TS-01-SMOKE-9: Supersede and archive workflow end-to-end

**Execution Path:** Paths 4a and 4b from design.md
**Description:** Full path from supersede through deprecation banner insertion and persistence, then move_to_archive through folder relocation. Demonstrates the complete supersede->archive workflow.

**Setup:** Two spec folders in a temp root: `01_alpha` (sealed), `02_beta` (sealed).

**Trigger:** `supersede(spec_alpha, "03_gamma", alpha_dir)` then `move_to_archive(alpha_dir, root)` to archive the superseded spec.

**Expected side effects:**
- After supersede: status is superseded, PRD body starts with deprecation banner mentioning "03_gamma", persisted to disk.
- Public save rejects the superseded spec.
- supersede on a non-sealed spec raises LifecycleError.
- move_to_archive on the superseded spec succeeds (superseded is archivable), folder moved to `root/archive/01_alpha`, status remains superseded on disk.
- move_to_archive on a sealed spec: folder moved to `root/archive/02_beta`, status is archived on disk.

**Must NOT satisfy with:** No mocking of file system or lifecycle functions.

**Assertion pseudocode:**
```
# supersede persists to disk
spec_a = load_sealed_spec(root / "01_alpha")
afspec.supersede(spec_a, "03_gamma", root / "01_alpha")
assert spec_a.prd.frontmatter.status == "superseded"
assert spec_a.prd.body.startswith("> **SUPERSEDED** by spec 03_gamma")
reloaded = afspec.load_spec(root / "01_alpha")
assert reloaded.prd.frontmatter.status == "superseded"
assert reloaded.prd.body.startswith("> **SUPERSEDED** by spec 03_gamma")

# Public save rejects superseded
with pytest.raises(LifecycleError):
    afspec.save(spec_a, root / "01_alpha")

# supersede rejects non-sealed
spec_draft = load_draft_spec()
with pytest.raises(LifecycleError):
    afspec.supersede(spec_draft, "99_other", tmpdir)

# move_to_archive on superseded spec succeeds (skip transition, just move)
afspec.move_to_archive(root / "01_alpha", root)
assert (root / "archive" / "01_alpha").exists()
assert not (root / "01_alpha").exists()
reloaded = afspec.load_spec(root / "archive" / "01_alpha")
assert reloaded.prd.frontmatter.status == "superseded"
assert reloaded.prd.body.startswith("> **SUPERSEDED** by spec 03_gamma")

# move_to_archive on sealed spec transitions to archived
afspec.move_to_archive(root / "02_beta", root)
assert (root / "archive" / "02_beta").exists()
assert not (root / "02_beta").exists()
reloaded = afspec.load_spec(root / "archive" / "02_beta")
assert reloaded.prd.frontmatter.status == "archived"
```

## Coverage Matrix

| Requirement | Test Spec Entry | Type |
|-------------|-----------------|------|
| 01-REQ-1.1 | TS-01-1 | unit |
| 01-REQ-1.2 | TS-01-2 | unit |
| 01-REQ-1.3 | TS-01-3 | unit |
| 01-REQ-1.4 | TS-01-4 | unit |
| 01-REQ-1.E1 | TS-01-E1 | unit |
| 01-REQ-2.1 | TS-01-5 | integration |
| 01-REQ-2.2 | TS-01-6 | unit |
| 01-REQ-2.3 | TS-01-7 | unit |
| 01-REQ-2.E1 | TS-01-E2 | unit |
| 01-REQ-2.E2 | TS-01-E3 | unit |
| 01-REQ-2.E3 | TS-01-E4 | unit |
| 01-REQ-3.1 | TS-01-8 | integration |
| 01-REQ-3.2 | TS-01-9 | unit |
| 01-REQ-3.3 | TS-01-10 | unit |
| 01-REQ-3.4 | TS-01-11 | unit |
| 01-REQ-3.5 | TS-01-12 | unit |
| 01-REQ-3.E1 | TS-01-E5 | unit |
| 01-REQ-3.E2 | TS-01-E6 | unit |
| 01-REQ-3.E3 | TS-01-E7 | integration |
| 01-REQ-4.1 | TS-01-13 | unit |
| 01-REQ-4.2 | TS-01-14 | unit |
| 01-REQ-4.3 | TS-01-15 | unit |
| 01-REQ-4.E1 | TS-01-E8 | unit |
| 01-REQ-4.E2 | TS-01-E9 | unit |
| 01-REQ-5.1 | TS-01-16 | integration |
| 01-REQ-5.2 | TS-01-17 | unit |
| 01-REQ-5.3 | TS-01-18 | unit |
| 01-REQ-5.4 | TS-01-19 | unit |
| 01-REQ-5.5 | TS-01-20 | unit |
| 01-REQ-5.6 | TS-01-21 | unit |
| 01-REQ-5.E1 | TS-01-E10 | unit |
| 01-REQ-6.1 | TS-01-22 | unit |
| 01-REQ-6.2 | TS-01-23 | unit |
| 01-REQ-6.3 | TS-01-24 | unit |
| 01-REQ-6.4 | TS-01-25 | unit |
| 01-REQ-6.5 | TS-01-26 | unit |
| 01-REQ-6.6 | TS-01-27 | unit |
| 01-REQ-6.7 | TS-01-E29 | integration |
| 01-REQ-6.E1 | TS-01-E11 | unit |
| 01-REQ-6.E2 | TS-01-E12 | unit |
| 01-REQ-6.E3 | TS-01-E28 | unit |
| 01-REQ-6.E4 | TS-01-E30 | unit |
| 01-REQ-6.E4 | TS-01-E31 | unit |
| 01-REQ-6.E4 | TS-01-E33 | integration |
| 01-REQ-6.E5 | TS-01-E32 | unit |
| 01-REQ-7.1 | TS-01-28 | unit |
| 01-REQ-7.2 | TS-01-29 | unit |
| 01-REQ-7.3 | TS-01-30 | integration |
| 01-REQ-7.E1 | TS-01-E13 | unit |
| 01-REQ-7.E2 | TS-01-E14 | unit |
| 01-REQ-8.1 | TS-01-31 | unit |
| 01-REQ-8.2 | TS-01-32 | unit |
| 01-REQ-8.3 | TS-01-33 | unit |
| 01-REQ-8.4 | TS-01-34 | unit |
| 01-REQ-8.5 | TS-01-35 | integration |
| 01-REQ-8.6 | TS-01-36 | unit |
| 01-REQ-8.E1 | TS-01-E15 | unit |
| 01-REQ-9.1 | TS-01-37 | integration |
| 01-REQ-9.2 | TS-01-38 | unit |
| 01-REQ-9.3 | TS-01-39 | integration |
| 01-REQ-9.E1 | TS-01-E16 | unit |
| 01-REQ-9.E2 | TS-01-E17 | unit |
| 01-REQ-9.4 | TS-01-50 | unit |
| 01-REQ-9.5 | TS-01-51 | unit |
| 01-REQ-9.E3 | TS-01-E18 | unit |
| 01-REQ-9.E4 | TS-01-E26 | unit |
| 01-REQ-9.E5 | TS-01-E27 | unit |
| 01-REQ-10.1 | TS-01-40 | unit |
| 01-REQ-10.2 | TS-01-41 | unit |
| 01-REQ-10.E1 | TS-01-E19 | unit |
| 01-REQ-10.E2 | TS-01-E20 | unit |
| 01-REQ-1.5 | TS-01-42 | unit |
| 01-REQ-1.6 | TS-01-43 | unit |
| 01-REQ-1.6 | TS-01-44 | unit |
| 01-REQ-1.7 | TS-01-45 | unit |
| 01-REQ-1.7 | TS-01-E24 | unit |
| 01-REQ-11.1 | TS-01-46 | unit |
| 01-REQ-11.2 | TS-01-47 | unit |
| 01-REQ-11.3 | TS-01-48 | unit |
| 01-REQ-11.4 | TS-01-E25 | unit |
| 01-REQ-11.5 | TS-01-49 | unit |
| 01-REQ-11.E1 | TS-01-E21 | unit |
| 01-REQ-11.E2 | TS-01-E22 | unit |
| 01-REQ-11.E3 | TS-01-E23 | unit |
| 01-REQ-11.E4 | TS-01-E34 | unit |
| 01-REQ-5.7 | TS-01-53 | unit |
| 01-REQ-4.1 | TS-01-52 | unit |
| 01-REQ-11.6 | TS-01-E34 | unit |
| Property 1 | TS-01-P1 | property |
| Property 2 | TS-01-P2 | property |
| Property 3 | TS-01-P3 | property |
| Property 4 | TS-01-P4 | property |
| Property 5 | TS-01-P5 | property |
| Property 6 | TS-01-P6 | property |
| Property 7 | TS-01-P7 | property |
| Property 8 | TS-01-P8 | property |
| Property 9 | TS-01-P9 | property |
| Property 10 | TS-01-P10 | property |
| Property 11 | TS-01-P11 | property |
| Property 12 | TS-01-P12 | property |
| 01-PATH-1 | TS-01-SMOKE-1 | integration |
| 01-PATH-2 | TS-01-SMOKE-2 | integration |
| 01-PATH-3 | TS-01-SMOKE-3 | integration |
| 01-PATH-4 | TS-01-SMOKE-4 | integration |
| 01-PATH-5 | TS-01-SMOKE-5 | integration |
| 01-PATH-6 | TS-01-SMOKE-6 | integration |
| 01-PATH-7 | TS-01-SMOKE-7 | integration |
| 01-PATH-8 | TS-01-SMOKE-8 | integration |
| 01-PATH-4a | TS-01-SMOKE-9 | integration |
| 01-PATH-4b | TS-01-SMOKE-9 | integration |
