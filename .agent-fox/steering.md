The following patterns and guidelines were extracted from Google Cloud SDK documentation at [https://docs.cloud.google.com/go/docs/reference](https://docs.cloud.google.com/python/docs/reference)

# Idiomatic Python SDK Design Patterns

These instructions apply to any Python library that wraps a remote API.
They are technology-agnostic. Apply them regardless of whether the underlying
API is REST, gRPC, GraphQL, or something else.

---

## Principle: Optimise for the Caller, Not the API

The API's shape is an implementation detail. The SDK's job is to make
the caller's code read naturally in Python. If a design decision forces
the caller to think about the wire protocol, it is the wrong decision.

---

## 1. One Entry Point

Expose a single `Client` class. All operations go through it.

```python
client = YourClient(api_key="...", region="us-east-1")
result = client.do_something(...)
```

The client's `__init__` accepts all shared configuration: credentials,
project/tenant identifiers, base URL, default timeout, default retry
policy. Callers should never need to instantiate transport or auth
objects themselves unless they are explicitly overriding defaults.

If the API surface is large enough to warrant sub-clients (e.g. separate
concerns like `storage`, `compute`, `iam`), the main client constructs
and exposes them as attributes:

```python
client.storage.upload(...)
client.iam.grant_role(...)
```

Sub-clients are not imported and instantiated directly. They are accessed
through the main client, which manages their shared state.

---

## 2. Resource Hierarchy: Full Object, Lightweight Reference, List Item

For every named resource in the API, provide three types:

**`Resource`** — the full object, all fields populated, returned from
`get_*` or `create_*` calls.

**`ResourceReference`** — identifiers only, no metadata. Used to address
a remote resource without fetching it. Constructable from a string ID.

**`ResourceListItem`** — a partial object matching what the list API
returns. Distinct from the full `Resource` to make it explicit that a
`get` call is needed for the complete picture.

```python
# Full object — network call
pipeline = client.get_pipeline("pipeline-123")

# Reference — no network call, just an address
ref = PipelineReference(pipeline_id="pipeline-123", project="my-project")

# Caller can pass either to other methods
client.run_pipeline(ref)
client.run_pipeline(pipeline)
client.run_pipeline("pipeline-123")  # plain string also accepted
```

Methods that operate on a resource accept
`Union[Resource, Reference, str]`. A private helper coerces the input
at the top of each method. This is the single most important ergonomic
decision in the SDK.

---

## 3. Separate Config from Action

Operations with more than two or three options, or that run
asynchronously, use a dedicated config object rather than keyword
arguments on the client method.

```python
config = RunConfig(
    timeout_ms=5000,
    retry_on_failure=True,
    output_location="gs://my-bucket/results/",
)
job = client.run_pipeline("pipeline-123", run_config=config)
```

Config objects follow these rules:

- All parameters are keyword-only with default `None`.
- `None` means "use the server default", not "raise an error".
- They are mutable after construction (`config.timeout_ms = 10000`).
- They have a `to_api_repr() -> dict` method that serialises only
  non-`None` fields.
- They have a `classmethod from_api_repr(data: dict)` factory.
- The client method's `run_config` parameter is always optional.

---

## 4. Long-Running Operations Return a Job / Future

If the API reports progress asynchronously (a job ID, a task ARN, an
operation name), model it as a Job object that implements the Future
interface.

Required methods:

```python
job.result(timeout=None)        # block until complete, raise on failure
job.done() -> bool              # non-blocking status check
job.cancel() -> bool            # request cancellation
job.add_done_callback(fn)       # register a callback
```

Required attributes:

```python
job.job_id       # str
job.state        # enum: PENDING, RUNNING, DONE, FAILED, CANCELLED
job.created      # datetime
job.started      # datetime | None
job.ended        # datetime | None
job.errors       # list[Error]
job.metadata     # dict of service-specific statistics
```

The Job object holds a reference to the client so it can poll itself.
The caller does not need to pass the client again to check status.

For truly async codebases, provide async variants: `await job.result_async()`.

---

## 5. Enums for Every Constrained Value

Any parameter or field that accepts a fixed set of string (or integer)
values is an `Enum`. Use `str` as a mixin so the value serialises
directly to JSON.

```python
class RunStatus(str, Enum):
    PENDING   = "PENDING"
    RUNNING   = "RUNNING"
    DONE      = "DONE"
    FAILED    = "FAILED"

class OutputFormat(str, Enum):
    JSON    = "json"
    PARQUET = "parquet"
    CSV     = "csv"
```

Collect all enums in an `enums.py` module. Re-export the most-used ones
from the package root so callers can write `your_sdk.RunStatus.DONE`
rather than `your_sdk.enums.RunStatus.DONE`.

Never use bare string literals in method signatures or config classes
where an enum exists.

---

## 6. Retry and Timeout Are Universal

Every client method that touches the network accepts `retry` and
`timeout` as keyword-only arguments.

```python
result = client.get_pipeline(
    "pipeline-123",
    retry=Retry(predicate=is_transient_error, deadline=60),
    timeout=10.0,
)
```

Define a module-level `DEFAULT_RETRY` with sensible defaults (retry on
429, 500, 503 with exponential backoff). Use it as the default for every
method. Callers can pass `retry=None` to disable retries entirely.

`timeout` is always in seconds, always a plain `float`, always `None`
by default (which means "use the transport's default" or "wait forever",
documented clearly).

---

## 7. Lazy Iterators for List Operations

`list_*` methods return iterators, never lists. Pagination is
transparent.

```python
for pipeline in client.list_pipelines(filter="status=DONE"):
    print(pipeline.pipeline_id)
```

Accept `max_results: Optional[int] = None` to cap results and
`page_token: Optional[str] = None` to resume from a checkpoint. Expose
the current page token on the iterator object for callers who need to
checkpoint manually.

Never load all pages before returning. Never buffer more than one page
in memory unless explicitly requested.

---

## 8. `from_api_repr` / `to_api_repr` on Every Model

Every resource and config class knows how to construct itself from a raw
API response dict and how to serialise itself back.

```python
raw = api_response["pipeline"]
pipeline = Pipeline.from_api_repr(raw)

request_body = config.to_api_repr()
```

The client layer handles only HTTP/gRPC mechanics. It calls
`from_api_repr` on responses and `to_api_repr` on request bodies.
No parsing logic lives in the client.

This separation makes unit testing clean: model classes are tested
against fixture dicts with no HTTP mocking required.

---

## 9. Idiomatic Exception Hierarchy

Define an exception hierarchy rooted at a single base class. Map
API error codes to specific Python exceptions.

```python
YourSdkError             # base, never raised directly
  ApiError               # unexpected HTTP/gRPC error
    NotFoundError        # 404
    PermissionDeniedError# 403
    ConflictError        # 409
    RateLimitError       # 429
    ServerError          # 5xx
  ConfigurationError     # bad client setup, raised before any network call
  TimeoutError           # operation exceeded timeout
  RetryError             # exhausted retry budget
```

Rules:
- All exceptions include the original HTTP status code and response body.
- Never raise the generic base class directly.
- Never swallow API errors silently.
- `NotFoundError` should be raised for `get_*` calls when the resource
  does not exist, not returned as `None`.

---

## 10. Module Structure

```
your_sdk/
  __init__.py        # re-exports Client and the most common types
  client.py          # Client class only — no model logic here
  models/
    resource.py      # Resource, ResourceReference, ResourceListItem
    config.py        # *Config classes
    job.py           # *Job classes
  enums.py           # all Enum classes
  retry.py           # DEFAULT_RETRY, retry predicates
  exceptions.py      # full exception hierarchy
  _transport/        # private — HTTP/gRPC mechanics, not part of public API
```

`__init__.py` re-exports: `Client`, primary resource classes, primary
config classes, primary enums, primary exceptions. Everything else is
importable by path for advanced users.

Prefix private modules with `_`. Never document them as part of the
public API. Do not import from them in user-facing examples.

---

## 11. Idempotent Operation Identity

For any operation that creates or mutates a resource, accept an optional
`idempotency_key` (or `operation_id`, `request_id`) parameter. If the
caller provides one, the SDK passes it to the API so retries do not
create duplicate resources.

```python
job = client.create_pipeline(
    config=pipeline_config,
    idempotency_key="deploy-2026-05-19-v3",
)
```

Generate a random UUID when the caller does not provide one, so that
naive retries in caller code at least fail loudly rather than silently
duplicating work.

---

## 12. Constructor Ergonomics: Accept Strings Everywhere Reasonable

Anywhere the API takes a resource path, ARN, or compound ID, accept a
plain string. Provide a `from_string` classmethod on reference classes
for when the caller wants to parse explicitly.

```python
# All equivalent:
client.get_pipeline("projects/my-project/pipelines/pipeline-123")
client.get_pipeline(PipelineReference.from_string("projects/my-project/pipelines/pipeline-123"))
client.get_pipeline(PipelineReference(project="my-project", pipeline_id="pipeline-123"))
```

Parse resource path strings once, at the boundary of the SDK, using a
private helper. Never require callers to construct path strings manually
by concatenating IDs with `/`.

---

## 13. Consistent Naming Conventions

| Operation type        | Method name pattern                    |
|-----------------------|----------------------------------------|
| Fetch single resource | `get_{resource}(id)`                   |
| Create resource       | `create_{resource}(config)`            |
| Update resource       | `update_{resource}(id, config)`        |
| Delete resource       | `delete_{resource}(id)`                |
| List resources        | `list_{resource}s(filter=None)`        |
| Check existence       | `get_{resource}` + catch `NotFoundError` |
| Async operation       | `run_{operation}` → returns `*Job`     |
| Sync convenience      | `run_{operation}_and_wait` (optional)  |

Properties on resource objects use `snake_case`. Enum member names use
`UPPER_SNAKE_CASE`. Module names use `snake_case`. Class names use
`PascalCase`.

Never abbreviate in public names. `configuration` not `cfg`,
`identifier` not `id` (unless it is literally `id`), `timeout` not `to`.

---

## 14. Provide Sync-and-Wait Convenience Wrappers

For the most common async operations, provide a blocking convenience
method that creates the job and waits for it. Name it clearly.

```python
# Async — caller controls waiting
job = client.run_pipeline("pipeline-123", run_config=config)
result = job.result(timeout=120)

# Sync convenience — one call, blocks until done
result = client.run_pipeline_and_wait("pipeline-123", run_config=config, timeout=120)
```

The convenience method is a thin wrapper: it calls the async method,
calls `.result()`, and returns the result. No special logic.

---