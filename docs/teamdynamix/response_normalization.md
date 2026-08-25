# Internal Response Normalization

**Module:** `teamdynamix._response`  
**API Surface:** Internal

TeamDynamix endpoints may return an object, a list, an empty container, `null`,
or occasionally mixed list entries. Client modules use three shared, stateless
helpers to preserve consistent handling:

- `as_list_of_dicts(data)`
- `as_dict(data)`
- `first_dict_or_none(data)`

## Design decision: module functions instead of a mixin

Normalization has no instance state and is not client-specific. Pure functions
keep dependencies explicit at the import site, avoid inheritance and MRO
concerns, and can be tested without constructing a Session or client. Client
modules may import these helpers under their historical private names to avoid
changing behavior while removing duplicate implementations.

The module is internal and is not exported from `teamdynamix.__init__`.
