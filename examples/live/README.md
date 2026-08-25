# Live endpoint exercises

These scripts perform real, state-changing operations against a configured
TeamDynamix tenant. They are manual examples, not automated tests, and pytest
does not collect or run them.

Before running one, create a tenant-specific configuration file from
`config/sample.config.ini`, review every hard-coded identifier and payload, and
use a sandbox tenant with disposable data.

```bash
python examples/live/people_endpoints.py
python examples/live/ticket_endpoints.py
```

Never commit credentials or tenant configuration files.
