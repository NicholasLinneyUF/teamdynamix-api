# `Logger` Module

**Module:** `teamdynamix.logger`
**Python Import Path:** `teamdynamix.logger`
**API Surface:** *Internal (logging support)*
**Primary Client Class:** `Logger`
**DTOs:** `Event` (from `teamdynamix.event`)

The `logger` module provides a **minimal, thread-safe logging facility** used by the SDK to record operational events.

It is intentionally simple and self-contained:

- Keeps an in-memory list of `Event` objects
- Writes events to a timestamped log file
- Optionally prints events to the console
- Does **not** depend on Python’s `logging` module

------

## Architectural Notes

Logging in `teamdynamix-api` follows these principles:

- Logging is for **observability**, not control flow
- Logging is synchronous and explicit
- Loggers are owned by higher-level components (typically `Session`)
- Logging must not interfere with request/response behavior

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

Most users will **not** instantiate `Logger` directly.
It is typically created and owned by `Session`.

For direct usage or testing, a logger can be instantiated as follows:

```python
from teamdynamix.logger import Logger

logger = Logger(
    log_dir="./logs",
    level="INFO",
    console=True,
)
```

Instantiation creates:

- A log directory (if it does not exist)
- A timestamped log file within that directory

No I/O occurs beyond directory creation.

------

## Data Models (DTOs)

### `Event`

The `Logger` records instances of `Event` (defined in `teamdynamix.event`) for each logged message.

Each event contains:

- Message text
- Numeric log level
- Timestamp (UTC)
- Optional structured context

See `events.md` for full `Event` documentation.

------

## Client Class

### `Logger`

```python
class Logger:
    ...
```

The `Logger` class is responsible for recording events and emitting them to configured outputs.

------

## Methods

### `log(message, level=None, context=None)`

Record a log event.

```python
logger.log("Session initialized")
logger.log(
    "HTTP request completed",
    level=20,
    context={"method": "GET", "status": 200},
)
```

**Parameters**

| Name      | Type          | Description                                      |
| --------- | ------------- | ------------------------------------------------ |
| `message` | `str`         | Log message                                      |
| `level`   | `int | None`  | Numeric log level (defaults to configured level) |
| `context` | `dict | None` | Optional structured context                      |

**Behavior notes**

- If `level` is lower than the configured logger level, the event is ignored
- Accepted level names map internally to numeric values:
  - `CRITICAL` → 50
  - `ERROR` → 40
  - `WARNING` / `WARN` → 30
  - `INFO` → 20
  - `DEBUG` → 10
- When recorded:
  - The event is appended to `logger.events`
  - Printed to console if `console=True`
  - Appended to the log file

------

### `clear_events()`

Clear the in-memory event list.

```python
logger.clear_events()
```

**Behavior notes**

- Does not affect the log file
- Thread-safe
- Intended for test or inspection scenarios

------

## Raw vs Typed Methods

This module does not use the raw/typed method pattern.

`Logger` records typed `Event` objects directly.

------

## Error Handling

The logger is designed to be **non-disruptive**:

- Logging failures should not affect SDK operation
- No SDK-specific exceptions are raised by `Logger`
- Standard Python I/O errors may still propagate in extreme cases (e.g., filesystem permissions)

------

## Design Intent

The `logger` module intentionally does **not**:

- Use or wrap Python’s `logging` module
- Provide log rotation or retention policies
- Perform asynchronous or background logging
- Send logs to remote systems
- Enforce structured logging schemas

It exists to provide a **predictable, dependency-free logging mechanism** suitable for scripts, automation, and SDK diagnostics.

------

## Related Documentation

- `events.md`
- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- `session.md`