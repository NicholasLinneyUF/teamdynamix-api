### Module Docs Template (Authoritative)

Every file under `docs/teamdynamix/*.md` should follow this structure:

1. **Module header**
   - Module name
   - Python import path
   - API surface
   - Primary client class
   - DTOs (if any)
2. **Architectural Notes**
   - Explicitly restate architectural guarantees
   - Reference `ARCHITECTURE.md`, `DESIGN.md`, `PATTERNS.md`
3. **Importing and Instantiation**
   - Show `Session` + client construction
   - Reinforce lazy behavior
4. **Data Models (DTOs)**
   - Explicit field tables
   - Clear statement: *selective, not complete*
5. **Client Class**
   - High-level description of responsibility
   - Explicitly endpoint-representative
6. **Methods**
   For each public method:
   - Endpoint
   - Return type
   - Example usage
   - Parameters table (if applicable)
   - Behavior notes (empty results, tenant variance, etc.)
7. **Raw vs Typed Methods**
   - Explain `_raw` vs typed pattern
   - Example side-by-side usage
8. **Error Handling**
   - What raises
   - What does *not* raise
   - Example
9. **Design Intent**
   - What the module intentionally does *not* do
10. **Related Documentation**

- Cross-links to core docs
