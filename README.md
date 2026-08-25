# teamdynamix-api

An experimental Python SDK for the TeamDynamix Web API. The project keeps
authentication, transport, configuration, and logging in a shared `Session`
while exposing endpoint-oriented client modules.

> **Pre-alpha:** APIs may change between releases. The `pre-alpha/11` release
> is the final baseline derived from the legacy TeamDynamix/Postman corpus;
> Swagger/OpenAPI realignment is planned for `pre-alpha/12`.

## Installation

Install the project from a local checkout:

```bash
python -m pip install .
```

Python 3.10 or newer is required.

The release label and Git tag are `0.0.0-pre-alpha.11`. Python distribution
metadata uses the PEP 440 equivalent `0.0.0a11`, which is also exposed as
`teamdynamix.__version__`.

## Session logging

`Session` uses `log-<timestamp>.txt` by default. Scripts can provide a
descriptive prefix so their log files are easy to distinguish:

```python
from teamdynamix import Session

session = Session("./config/config.ini", name_prefix="log-mytool")
```

This produces a filename such as `log-mytool-20260825153000.txt` in the
configured log directory.

See [the documentation index](docs/INDEX.md) for architecture, configuration,
client, and contributor documentation.

## License

This project is available under the [MIT License](LICENSE).
