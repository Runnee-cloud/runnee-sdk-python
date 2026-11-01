# runnee

Official synchronous and asynchronous Python SDK for Runnee Cloud. Remote execution only; no interpreter is distributed. Python 3.11+; one runtime dependency, HTTPX.

## Installation

Release candidate: registry commands apply after publication. Local installation from this repository: pip install .

```sh
pip install runnee
uv add runnee
```

## Quickstart

Create a dashboard API key with scripts:execute and set RUNNEE_API_KEY on your server.

```python
import os
from runnee import Runnee

with Runnee(api_key=os.environ["RUNNEE_API_KEY"]) as client:
    result = client.execute(code="function main() { return 10 + 20; }", mode="dry-run")
    if result["success"] and "executionResult" in result:
        print(result["executionResult"].get("returnValue"))
```

```python
import os
import asyncio
from runnee import AsyncRunnee


async def main():
    async with AsyncRunnee(api_key=os.environ["RUNNEE_API_KEY"]) as client:
        result = await client.execute(code="function main() { return 30; }")
        print(result)


asyncio.run(main())
```

Use AsyncRunnee in FastAPI async routes; Runnee suits synchronous Flask/Django views and jobs. Clients own reusable connection pools; close them or use context managers.

## Configuration

Runnee(api_key=..., base_url="https://api.runnee.cloud", timeout=30, max_retries=2) and AsyncRunnee accept identical configuration. RUNNEE_BASE_URL is an optional fallback. timeout is seconds. HTTP requires loopback or explicit allow_insecure_http development use; redirects and environment proxy inheritance are disabled. Custom HTTPX transports support controlled testing.

RequestOptions(timeout=..., max_retries=..., idempotency_key=..., cancel_event=..., on_response=...) supplies per-call behavior. Async client cancellation uses asyncio task cancellation. Sync cancel_event is checked between attempts and received response chunks; an in-flight socket can wait until its HTTPX timeout. Async timeout bounds the complete operation; sync uses the remaining budget for network timeouts and checks the deadline while receiving chunks and between attempts. A client timeout does not change the script execution budget.

## API reference

- execute(code=..., mode="dry-run", event=..., retain_source=False, script_name=..., secret_names=..., script_id=..., options=...)
- executions.list(before=..., status=..., mode=...), get(id), iterate(...). Use for in sync or async for in async code. Pages contain at most20 items; history retention is3days.
- scripts.list(), create(name=..., code=...), get(id), update(id,name=...,code=...,expected_version=...), delete(id), get_version(id,version), restore(id,version=...,expected_version=...), storage().
- secrets.list(), get(name), create(name=...,value=...,allow_inline=False,script_ids=...), update(name,value=...,allow_inline=...,script_ids=...), delete(name).
- usage.get(), summary(), history(days=7|30|90); sandbox.get(); billing.plans(); health.get().
- telemetry.record_execution(input), record_event(input). External execution records consume quota.

Async methods use the same names with await. Returned dictionaries follow API camelCase names and have generated TypedDict definitions in runnee.types. Arguments follow Python snake_case. SDK API-key issuance/revocation, account/payment mutations and remote execution cancellation are not supported.

## Secret usage

```python
import os
from runnee import Runnee

with Runnee(api_key=os.environ["RUNNEE_API_KEY"]) as client:
    client.secrets.create(name="EXTERNAL_API_KEY", value=os.environ["EXTERNAL_API_KEY"], allow_inline=True)
    result = client.execute(
        code='use("secrets"); function main() { return secrets.has("EXTERNAL_API_KEY"); }',
        secret_names=["EXTERNAL_API_KEY"],
    )
    client.secrets.update("EXTERNAL_API_KEY", value=os.environ["REPLACEMENT_API_KEY"])
    client.secrets.delete("EXTERNAL_API_KEY")
```

Metadata is readable with secrets:read; writes require secrets:write; grants require scripts:execute and secrets:use. Prefer script_ids policies over allow_inline; execute with script_id and the exact current saved source. Secrets remain inaccessible until explicitly named on an execution. Management responses never contain values. See SECURITY.md for disclosure boundaries.

## Reliability and errors

Read requests retry transient network failures and 429/500/502/503/504 with exponential jitter and Retry-After. Auth failures are never retried. Writes are not retried by default. Execute retries require an idempotency_key in RequestOptions. Reuse it after an uncertain network failure. Receipts expire after24hours and replay only summaries, not original output; HTTP409 can mean the original execution is pending. Inspect history before choosing a new key.

RunneeError subclasses: RunneeAuthenticationError, RunneePermissionError, RunneeValidationError, RunneeRateLimitError, RunneeTimeoutError, RunneeNetworkError, RunneeServerError, RunneeConflictError, RunneeNotFoundError, RunneeResponseError, RunneeCancelledError. Errors expose status/request_id; RateLimit exposes retry_after seconds. Script failures return success=False instead of raising an HTTP exception.

## Development

pip install -e '.[dev]'; pytest; mypy; ruff check .; ruff format --check .; python -m build. CI tests supported Python versions and both clients. See CONTRIBUTING.md, CHANGELOG.md and RELEASING.md. MIT licensed. Publication is a separate approved release step.
