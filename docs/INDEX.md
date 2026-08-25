# Documentation Index

This directory is the documentation home for the **TeamDynamix API Python SDK**.

These pages describe the `pre-alpha/11` implementation: the final baseline
derived from the legacy TeamDynamix Postman corpus. They do not claim alignment
with the subsequently published Swagger/OpenAPI specification; that work is
scheduled for `pre-alpha/12`.

- Core philosophy: Session is the facade, Transport is the HTTP boundary, client modules are thin endpoint wrappers.
- Docs style: “JavaDocs-style” module pages under `docs/teamdynamix/`.

---

## Core Architecture & Concepts

- [Architecture](ARCHITECTURE.md)
- [Design](DESIGN.md)
- [Patterns](PATTERNS.md)

---

## Core Runtime Modules

- [`session`](teamdynamix/session.md)
  - `Session(...)`
  - `authenticate()`, `auth_header()`, `request(...)`
  - (Includes short “Config Overrides” section)
- [`config`](teamdynamix/config.md)
- [`auth`](teamdynamix/auth.md)
- [`transport`](teamdynamix/transport.md)
- [`logger`](teamdynamix/logger.md)
- [`event`](teamdynamix/events.md)
- [`exceptions`](teamdynamix/exceptions.md)
- [Internal response normalization](teamdynamix/response_normalization.md)

---

## API Clients

- [`accounts`](teamdynamix/accounts.md)
  - `Accounts.get(...)`, `Accounts.search(...)`, `Accounts.list_all(...)`
- [`applications`](teamdynamix/applications.md)
  - `Applications.list(...)`, `Applications.get(...)`
- [`attributes`](teamdynamix/attributes.md)
  - Attribute choices: `list_choices(...)`, `add_choice(...)`, `edit_choice(...)`, `delete_choice(...)`
  - Custom attributes: `list_custom(...)`
- [`people`](teamdynamix/people.md)
  - `People.get(...)`, `People.get_raw(...)`, `People.search(...)`, `People.user_list(...)`, `People.create(...)`, `People.update(...)`
  - Functional roles: `list_functional_roles(...)`, `add_functional_role(...)`, `remove_functional_role(...)`
- [`groups`](teamdynamix/groups.md)
  - `Groups.get(...)`, `Groups.search(...)`, `Groups.list_all(...)`
- [`functional_roles`](teamdynamix/functional_roles.md)
  - `FunctionalRoles.create(...)`, `FunctionalRoles.edit(...)`, `FunctionalRoles.search(...)`
- [`projects`](teamdynamix/projects.md)
  - `Projects.search(...)`, `Projects.get(...)`, `Projects.create(...)`, `Projects.edit(...)`, `Projects.patch(...)`
  - Feeds: `get_feed(...)`, `add_feed(...)`, issue feeds
  - Plans/tasks: `get_plan(...)`, `edit_task(...)`
- [`tickets`](teamdynamix/tickets.md)
  - `Tickets.get(...)`, `Tickets.search(...)`, `Tickets.create(...)`, `Tickets.update(...)`
  - Feed: `get_feed(...)`, `add_feed_entry(...)`
  - Metadata: `TicketPriorities`, `TicketTypes`, `TicketStatuses`, `TicketSources`
- [`service_catalog`](teamdynamix/service_catalog.md)
  - `ServiceCatalog.list(...)`, `get(...)`, `create(...)`, `update(...)`, `delete(...)`

---

## Script Utilities (`teamdynamix.tools`)

- [Tools overview](teamdynamix/tools/README.md)
- [`data_utils`](teamdynamix/tools/data_utils.md)
- [`script_utils`](teamdynamix/tools/script_utils.md)
- [`csv_utils`](teamdynamix/tools/csv_utils.md)
- [`sqlite_utils`](teamdynamix/tools/sqlite_utils.md)
- [`migration_utils`](teamdynamix/tools/migration_utils.md)
