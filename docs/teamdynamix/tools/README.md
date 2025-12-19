# `teamdynamix.tools`

**Python Import Path:** `teamdynamix.tools`  
**Purpose:** Local, script-oriented helper utilities  

The `teamdynamix.tools` subpackage provides **non-HTTP, non-endpoint utilities**
designed to support one-time scripts, migrations, data cleanup, and automation
tasks that interact with TeamDynamix data.

## Design Principles

- No dependency on TeamDynamix Web API endpoints
- No dependency on `Session`, `Auth`, or `Transport`
- Read-focused, predictable behavior
- Script-friendly APIs
- Explicit dependencies (e.g., pandas, sqlite)

## Modules

- `csv_utils` — Load, query, search, and export CSV data for scripts
- `sqlite_utils` — Temporary SQLite databases for batch and migration workflows

## When to use tools vs SDK clients

Use `teamdynamix.tools` when:
- You are preparing or transforming data
- You are writing one-off or migration scripts
- You need local indexing/searching

Use SDK clients when:
- You are calling TeamDynamix Web API endpoints
- You need authenticated HTTP behavior
