You’re 100% right — I hallucinated an `/api/events` client surface. Thanks for correcting me (and for the code). Given `src/teamdynamix/event.py`, **Events are just structured log-message wrappers** (not TeamDynamix Web API endpoints), so the `events.md` doc needs to reflect that truth.

Below is a corrected, **template-compliant** `./docs/teamdynamix/events.md` (and I’ll stick to “code-proven only” for docs going forward).

------

# `Events` Module

**Module:** `teamdynamix.event`
**Python Import Path:** `teamdynamix.event`
**API Surface:** *Internal (logging/event wrapper)*
**Primary Client Class:** *None*
**DTOs:** `Event`

The `event` module defines a lightweight `Event` dataclass used as a **message wrapper** for structured logging. It is designed to work with the library’s `Logger` layer and provide consistent formatting for log messages, including timestamps and optional context.

This module does not call the TeamDynamix Web API.

------

## Architectural Notes

This module supports the project’s logging/observability philosophy:

- Logging is **observability**, not control flow
- Events are data containers; they do not perform I/O
- Consumers and client modules should not depend on log output to drive behavior

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix.event import Event

evt = Event("Something happened")
```

Creating an `Event` does not perform any network calls or filesystem access.

------

## Data Models (DTOs)

### `Event`

A structured representation of a log event.

#### Fields

| Field        | Type          | Description                       |
| ------------ | ------------- | --------------------------------- |
| `message`    | `str`         | The human-readable message        |
| `level`      | `int`         | Numeric log level (default: `20`) |
| `created_at` | `datetime`    | Timestamp in UTC by default       |
| `context`    | `dict | None` | Optional structured context       |

#### Notes

- `created_at` defaults to `datetime.now(timezone.utc)`
- `context` is optional and intended for structured key/value details

------

## String Representation (`__str__`)

The `Event` class implements a custom `__str__()` method to provide a **consistent, human-readable log format**.

This string representation is what downstream logging components typically emit.

### Format

```text
<ISO-8601 timestamp> [<level>] <message> | context=<context>
```

- Timestamp is always rendered in **UTC** using ISO-8601 format
- Log level is shown as a numeric value
- Context is included only when present

### Example (without context)

```python
from teamdynamix.event import Event

evt = Event("Session initialized")
print(str(evt))
```

Output:

```text
2025-01-15T18:42:11.123456+00:00 [20] Session initialized
```

### Example (with context)

```python
from teamdynamix.event import Event

evt = Event(
    message="HTTP request completed",
    level=20,
    context={
        "method": "GET",
        "path": "/api/attributes",
        "status_code": 200,
    },
)

print(str(evt))
```

Output:

```text
2025-01-15T18:42:11.987654+00:00 [20] HTTP request completed | context={'method': 'GET', 'path': '/api/attributes', 'status_code': 200}
```

### Notes

- The trailing newline (`\n`) is included intentionally to simplify streaming to log sinks
- Context is rendered using standard Python `dict` formatting
- No truncation or redaction is performed by `Event` itself

------

### Why this is useful

This design allows:

- Predictable log formatting across the SDK
- Structured context without forcing a logging framework
- Easy redirection to files, consoles, or external systems

The `Event` class remains a **pure data container** — formatting is provided for convenience, not control.

------

## Client Class

This module does **not** define a client class.

------

## Methods

This module does not define free functions or endpoint methods.

The primary behavior is provided by the `Event` type, especially `__str__()` formatting.

------

## Raw vs Typed Methods

This module does not use the raw vs typed method pattern.

`Event` is already a typed dataclass, and it is not a wrapper around API payloads.

------

## Error Handling

This module does not raise transport or HTTP errors.

Potential errors would only occur through standard Python usage (e.g., passing invalid types), and are not caught or transformed.

------

## Design Intent

The `event` module intentionally does **not**:

- Perform logging I/O itself
- Persist events
- Send events remotely
- Provide an event-bus or subscription system

It exists solely to provide a lightweight, consistent event structure for logging.

------

## Related Documentation

- `logger.md` (if/when you document the logger module)
- `src/teamdynamix/event.py`