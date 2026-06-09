# speclib-python example: Audit Hub

This example demonstrates the speclib-python (afspec) construction and
validation API by programmatically building a complete specification (the
"Audit Hub" spec) in memory and writing it to disk.

The program exercises the full afspec API surface:

- Creating a spec with PRD, requirements (EARS criteria, correctness
  properties, execution paths, error handling), test spec (unit, edge-case,
  property, and smoke tests with coverage), tasks (groups, subtasks,
  traceability), and architecture.
- Saving the spec to disk as Markdown and JSON files.

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Running

From this directory:

```
uv sync
uv run python main.py
```

The program writes the generated spec files to `01_audit_hub_output/` and
prints summary statistics to stdout.

## Verifying results

The program uses the afspec `save()` function, which serializes models
through Pydantic validation. Any schema-level errors would surface as
exceptions during construction or saving.

A successful run produces five files in `01_audit_hub_output/`:

| File | Format | Content |
|------|--------|---------|
| `prd.md` | Markdown with YAML frontmatter | Product requirements document |
| `requirements.json` | JSON | Requirements, correctness properties, execution paths |
| `test_spec.json` | JSON | Test cases, edge cases, property tests, smoke tests |
| `tasks.json` | JSON | Task groups, subtasks, traceability matrix |
| `architecture.md` | Markdown | Architecture overview and diagrams |

You can inspect the output files to confirm they contain valid structured
data. The JSON files conform to the speclib v1 schema.
