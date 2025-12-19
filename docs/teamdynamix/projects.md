# `Projects` Module

**Module:** `teamdynamix.projects`
**Python Import Path:** `teamdynamix.projects`
**API Surface:** `/api/projects/*`
**Primary Client Class:** `Projects`
**DTOs:** `Project`

The `projects` module provides a thin, endpoint-representative client for working with **TeamDynamix Projects (PPM)**.

It intentionally stays close to the vendor API surface and exposes only minimal typed models. When richer or tenant-specific data is required, raw dictionary payloads are returned.

------

## Architectural Notes

This module follows the core architectural guarantees of `teamdynamix-api`:

- All HTTP calls flow through `Session → Transport`
- Client methods are thin endpoint wrappers
- Empty responses are valid and expected in several endpoints
- Typed models are intentionally minimal
- Response-shape normalization is defensive and conservative

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session
from teamdynamix.projects import Projects

session = Session("./config/config.ini")
projects = Projects(session)
```

No network calls occur during construction.

------

## Data Models (DTOs)

### `Project`

A minimal typed representation of a TeamDynamix Project.

#### Fields

| Field         | Type          | Description         |
| ------------- | ------------- | ------------------- |
| `ID`          | `int | None`  | Project identifier  |
| `Name`        | `str | None`  | Project name        |
| `IsActive`    | `bool | None` | Active status       |
| `Description` | `str | None`  | Project description |
| `ManagerUid`  | `str | None`  | Project manager UID |

#### Notes

- ID normalization accepts `ID`, `Id`, or `id`
- Manager UID normalization accepts `ManagerUid` or `ManagerUID`
- This model is intentionally lean and may be expanded later with proven needs

------

## Client Class

### `Projects`

```python
class Projects:
    ...
```

The `Projects` client exposes the following endpoint groups:

- Core project CRUD-style operations
- Project feed operations
- Project plan and task operations
- Project issue feed operations

------

## Methods

### Core Project Endpoints

#### `search(criteria)`

**Endpoint:** `POST /api/projects/search`
**Returns:** `list[Project]`

Search for projects using a raw criteria payload.

```python
results = projects.search({
    "IsActive": True,
    "MaxResults": 25,
})

for p in results:
    print(p.ID, p.Name)
```

**Behavior notes**

- Returns `[]` when no projects match (valid)
- Only dictionary entries are converted into `Project` objects

------

#### `get(project_id)`

**Endpoint:** `GET /api/projects/{id}`
**Returns:** `Project`

Retrieve a project by ID.

```python
project = projects.get(12345)
print(project.Name, project.IsActive)
```

**Behavior notes**

- Raises `ValueError` if the response is not a JSON object

------

#### `create(project_data, *, notify_new_manager=False, notify_new_alt_managers=False)`

**Endpoint:** `POST /api/projects`
**Returns:** `Project`

Create a new project.

```python
created = projects.create(
    {
        "Name": "New Initiative",
        "IsActive": True,
    },
    notify_new_manager=True,
)
```

**Query parameters**

| Name                   | Type   |
| ---------------------- | ------ |
| `notifyNewManager`     | `bool` |
| `notifyNewAltManagers` | `bool` |

**Behavior notes**

- Query parameters are serialized as lowercase strings
- Raises `ValueError` if response shape is unexpected

------

#### `edit(project_id, updates)`

**Endpoint:** `POST /api/projects/{id}`
**Returns:** `Project`

Edit an existing project.

```python
updated = projects.edit(12345, {"Description": "Updated description"})
```

**Notes**

- TeamDynamix uses `POST` (not `PUT`) for project edits
- Raises `ValueError` on unexpected response shape

------

#### `patch(project_id, operations)`

**Endpoint:** `PATCH /api/projects/{id}`
**Returns:** `Project`

Apply partial updates using JSON Patch semantics.

```python
from teamdynamix.transport import PatchPayload

updated = projects.patch(
    12345,
    [
        PatchPayload.replace("/Name", "Renamed Project"),
    ],
)
```

**Accepted input forms**

- `dict` → converted by `Transport` into patch operations
- `list[PatchPayload]`
- `list[dict]` (assumed RFC-6902 compliant)

**Behavior notes**

- Mixed lists (dict + PatchPayload) are rejected
- Raises `TypeError` for invalid inputs
- Raises `ValueError` for unexpected response shape

------

## Project Feed Endpoints

### `get_feed(project_id)`

**Endpoint:** `GET /api/projects/{id}/feed`
**Returns:** `list[dict]`

Retrieve a project’s activity feed.

```python
feed = projects.get_feed(12345)
```

Returns `[]` when empty (valid).

------

### `add_feed(project_id, body)`

**Endpoint:** `POST /api/projects/{id}/feed`
**Returns:** `dict`

Add a feed entry to a project.

```python
entry = projects.add_feed(12345, "Project kickoff completed.")
```

------

## Plan / Task Endpoints

### `get_plan(project_id, plan_id)`

**Endpoint:** `GET /api/projects/{projectId}/plans/{planId}`
**Returns:** `dict \| None`

Retrieve a project plan.

```python
plan = projects.get_plan(12345, 678)
```

------

### `edit_task(project_id, plan_id, task_id, updates, *, notify_new_resources=False)`

**Endpoint:**
`POST /api/projects/{projectId}/plans/{planId}/tasks/{taskId}/edit`

**Returns:** `dict \| None`

Edit a project task.

```python
projects.edit_task(
    12345,
    678,
    42,
    {"Name": "Updated Task Name"},
    notify_new_resources=True,
)
```

------

## Issue Feed Endpoints

### `get_issue_feed(project_id, issue_id)`

**Endpoint:**
`GET /api/projects/{projectId}/issues/{issueId}/feed`

**Returns:** `list[dict]`

Retrieve issue feed entries.

```python
feed = projects.get_issue_feed(12345, 99)
```

------

### `add_issue_comment(project_id, issue_id, comment_payload)`

**Endpoint:**
`POST /api/projects/{projectId}/issues/{issueId}/feed`

**Returns:** `dict`

Add a comment to an issue feed.

```python
projects.add_issue_comment(
    12345,
    99,
    {"Body": "Investigating root cause."},
)
```

------

## Raw vs Typed Methods

This module uses a **mixed strategy**:

- Core project operations return typed `Project` DTOs
- Feed, plan, task, and issue endpoints return raw `dict` payloads

This reflects the complexity and variability of non-core project schemas.

------

## Error Handling

- HTTP and transport errors are raised by `Transport`
- Empty responses are valid where documented
- Unexpected response shapes raise `ValueError`
- Invalid patch inputs raise `TypeError`

```python
from teamdynamix.exceptions import HttpError

try:
    projects.get(999999)
except HttpError as exc:
    print("HTTP error:", exc.status_code)
```

------

## Design Intent

This module intentionally does **not**:

- Model full project, plan, or task schemas
- Add pagination or caching helpers
- Abstract TeamDynamix workflow logic
- Validate request payload contents

It exists to provide **thin, predictable access** to the TeamDynamix Projects API while remaining flexible for tenant-specific use cases.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`
- `transport.md`
- TeamDynamix API Documentation — Projects