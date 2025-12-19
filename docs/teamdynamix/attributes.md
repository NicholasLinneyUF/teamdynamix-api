# `Attributes` Module

**Module:** `teamdynamix.attributes`
**Python Import Path:** `teamdynamix.attributes`
**API Surface:** `/api/attributes/*`
**Primary Client Class:** `Attributes`
**DTOs:** `Attribute`, `AttributeChoice`

The `Attributes` module provides access to the **TeamDynamix Attributes API surface**, including legacy attribute listing endpoints, attribute **choice management**, and **custom attribute** discovery.

This module is endpoint-representative and intentionally minimal. It mirrors TeamDynamix behavior directly without adding workflow abstractions or opinionated logic.

------

## Architectural Notes

This module follows all core architectural guarantees of the `teamdynamix-api` library:

- All HTTP requests flow through `Session → Transport`
- No direct use of `requests`
- Authentication is handled lazily by the session
- Empty responses (`[]`, `{}`, `null`) are valid and expected
- Typed models are **selective views**, not complete schemas

For architectural context, review:

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`

------

## Importing and Instantiation

```python
from teamdynamix import Session
from teamdynamix.attributes import Attributes

session = Session("./config/config.ini")
attributes = Attributes(session)
```

No network calls or authentication occur during construction.

------

## Data Models (DTOs)

### `Attribute`

A **minimal** typed representation of a TeamDynamix attribute.

This DTO exposes only commonly used fields. It is not a full schema.
Use raw methods when full payload access is required.

#### Fields

| Field         | Type          | Description                      |
| ------------- | ------------- | -------------------------------- |
| `ID`          | `int | None`  | Attribute identifier             |
| `Name`        | `str | None`  | Attribute display name           |
| `Description` | `str | None`  | Attribute description            |
| `IsActive`    | `bool | None` | Whether the attribute is active  |
| `IsDefault`   | `bool | None` | Whether the attribute is default |

------

### `AttributeChoice`

A typed representation of an **attribute choice** (selectable option for an attribute).

Fields align with the TeamDynamix API schema as exposed in the Postman collection.

#### Fields

| Field          | Type          | Description                 |
| -------------- | ------------- | --------------------------- |
| `ID`           | `int | None`  | Choice identifier           |
| `Name`         | `str | None`  | Display name                |
| `IsActive`     | `bool | None` | Active status               |
| `DateCreated`  | `str | None`  | Creation timestamp          |
| `DateModified` | `str | None`  | Last modification timestamp |
| `Order`        | `int | None`  | Display order               |

------

## Client Class

### `Attributes`

```python
class Attributes:
    ...
```

The `Attributes` client maps directly to the TeamDynamix Attributes API surface.

It groups endpoints into:

- **Legacy attribute listing endpoints**
- **Attribute choice management**
- **Custom attribute discovery**

No behavior is hidden or abstracted beyond request/response normalization.

------

## Methods

### `list_for_application_component_raw(app_id, component)`

**Endpoint:** `GET /api/applications/{appId}/attributes/{component}`
**Returns:** `list[dict]`

Retrieve attributes scoped to an application and component.

```python
raw = attributes.list_for_application_component_raw(
    app_id=42,
    component="tickets",
)
```

**Behavior notes**

- Returns an empty list when no attributes exist
- Component path is passed through verbatim

------

### `list_for_application_component(app_id, component)`

**Endpoint:** `GET /api/applications/{appId}/attributes/{component}`
**Returns:** `list[Attribute]`

Typed wrapper around `list_for_application_component_raw`.

------

### `list_for_component_raw(component)`

**Endpoint:** `GET /api/attributes/{component}`
**Returns:** `list[dict]`

Retrieve attributes scoped only by component.

------

### `list_for_component(component)`

**Endpoint:** `GET /api/attributes/{component}`
**Returns:** `list[Attribute]`

Typed wrapper around `list_for_component_raw`.

------

### `list_all_raw()`

**Endpoint:** `GET /api/attributes`
**Returns:** `list[dict]`

Retrieve all attributes available to the tenant.

------

### `list_all()`

**Endpoint:** `GET /api/attributes`
**Returns:** `list[Attribute]`

Typed wrapper around `list_all_raw`.

------

### `list_choices_raw(attribute_id)`

**Endpoint:** `GET /api/attributes/{id}/choices`
**Returns:** `list[dict]`

Retrieve all choices for a specific attribute.

------

### `list_choices(attribute_id)`

**Endpoint:** `GET /api/attributes/{id}/choices`
**Returns:** `list[AttributeChoice]`

Typed wrapper around `list_choices_raw`.

------

### `add_choice_raw(attribute_id, choice_payload, *, copy_from_choice_id=None)`

**Endpoint:** `POST /api/attributes/{id}/choices`
**Returns:** `dict`

Create a new attribute choice.

```python
payload = {
    "Name": "New Choice",
    "IsActive": True,
    "Order": 10,
}

created = attributes.add_choice_raw(
    attribute_id=123,
    choice_payload=payload,
)
```

**Parameters**

| Name                  | Type         | Description           |
| --------------------- | ------------ | --------------------- |
| `choice_payload`      | `dict`       | Raw API payload       |
| `copy_from_choice_id` | `int | None` | Optional clone source |

------

### `add_choice(...)`

**Returns:** `AttributeChoice`

Typed wrapper around `add_choice_raw`.

------

### `edit_choice_raw(attribute_id, choice_id, payload)`

**Endpoint:** `PUT /api/attributes/{id}/choices/{choiceId}`
**Returns:** `dict`

Update an existing attribute choice.

------

### `edit_choice(...)`

**Returns:** `AttributeChoice`

Typed wrapper around `edit_choice_raw`.

------

### `delete_choice_raw(attribute_id, choice_id)`

**Endpoint:** `DELETE /api/attributes/{id}/choices/{choiceId}`
**Returns:** `bool`

Delete an attribute choice.

------

### `delete_choice(attribute_id, choice_id)`

Alias for `delete_choice_raw`.

------

### `list_custom_raw(*, component_id=None, associated_type_id=None, app_id=None)`

**Endpoint:** `GET /api/attributes/custom`
**Returns:** `list[dict]`

Retrieve custom attributes filtered by optional parameters.

------

### `list_custom(...)`

**Returns:** `list[Attribute]`

Typed wrapper around `list_custom_raw`.

------

## Raw vs Typed Methods

Raw methods (`*_raw`) return unmodified API dictionaries and lists.

Typed methods return lightweight dataclasses for convenience.

```python
raw = attributes.list_choices_raw(123)
typed = attributes.list_choices(123)
```

Use raw methods when full payload fidelity is required.

------

## Error Handling

- HTTP errors are raised by `Transport`
- Empty responses are valid and do not raise exceptions
- Client methods do not catch or wrap errors

```python
from teamdynamix.exceptions import HttpError

try:
    attributes.list_all()
except HttpError as exc:
    print("Request failed:", exc)
```

------

## Design Intent

This module intentionally does **not**:

- Cache attribute data
- Validate or reshape payloads
- Hide TeamDynamix quirks
- Provide workflow abstractions

It exists to expose the Attributes API surface faithfully and predictably.

------

## Related Documentation

- `ARCHITECTURE.md`
- `DESIGN.md`
- `PATTERNS.md`
- TeamDynamix API Documentation — Attributes