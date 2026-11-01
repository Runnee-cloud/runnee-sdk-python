# Contributing

Thank you for contributing to the official Runnee Cloud SDK. This repository contains the remote API client only. Keep runtime, infrastructure and customer data out of changes.

## Local checks

Use Python 3.11 or later in a virtual environment.

```sh
python -m venv .venv
# Activate .venv using your shell.
python -m pip install -e ".[dev]"
python -m pytest
python -m mypy
python -m ruff check .
python -m ruff format --check .
python -m build
python -m twine check dist/*
```

## Pull requests

Add regression coverage for behavior changes. Keep public names compatible and document changes in CHANGELOG.md. Never commit real API keys, secret values, .env files or customer responses. Tests use synthetic keys and local HTTP mocks; they neither execute customer scripts nor require production credentials. Live API verification belongs in an isolated staging account.

The checked-in openapi.json is the public API contract snapshot. Coordinate API changes with the platform maintainers, then update this snapshot, client types, validation and tests together. Do not add methods for unimplemented endpoints.

## Releases and security

Follow [RELEASING.md](RELEASING.md). Use semantic versioning; breaking public changes require a major release (during 0.x, a new minor release). Security reports follow [SECURITY.md](SECURITY.md), rather than public issue reports.
