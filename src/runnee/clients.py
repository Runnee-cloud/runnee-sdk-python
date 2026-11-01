# Generated ergonomic clients for the public OpenAPI operations.
from __future__ import annotations
import builtins
from typing import Any, AsyncIterator, Iterator, Literal, cast
from types import TracebackType
import httpx
from . import types as T
from ._http import SyncHTTP, AsyncHTTP, RequestOptions
from .errors import RunneeResponseError


class Executions:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def list(
        self,
        *,
        before: str | None = None,
        status: Literal["success", "failed"] | None = None,
        mode: Literal["dry-run", "live"] | None = None,
        options: RequestOptions | None = None,
    ) -> T.ExecutionPage:
        return cast(
            T.ExecutionPage,
            self._http.request(
                "executions.list", {"before": before, "status": status, "mode": mode}, None, options
            ),
        )

    def get(self, id: str, *, options: RequestOptions | None = None) -> T.ExecutionDetail:
        return cast(T.ExecutionDetail, self._http.request("executions.get", {"id": id}, None, options))

    def iterate(
        self,
        *,
        status: Literal["success", "failed"] | None = None,
        mode: Literal["dry-run", "live"] | None = None,
        before: str | None = None,
        options: RequestOptions | None = None,
    ) -> Iterator[T.Execution]:
        seen: set[str] = set()
        while True:
            page = self.list(status=status, mode=mode, before=before, options=options)
            for item in page["items"]:
                yield item
            cursor = page["nextCursor"]
            if cursor is None:
                break
            if cursor in seen:
                raise RunneeResponseError("Runnee returned a repeated pagination cursor.")
            seen.add(cursor)
            before = cursor


class Scripts:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def list(self, *, options: RequestOptions | None = None) -> T.ScriptList:
        return cast(T.ScriptList, self._http.request("scripts.list", {}, None, options))

    def create(self, *, name: str, code: str, options: RequestOptions | None = None) -> T.Script:
        return cast(T.Script, self._http.request("scripts.create", {}, {"name": name, "code": code}, options))

    def get(self, id: str, *, options: RequestOptions | None = None) -> T.ScriptDetail:
        return cast(T.ScriptDetail, self._http.request("scripts.get", {"id": id}, None, options))

    def update(
        self, id: str, *, name: str, code: str, expected_version: int, options: RequestOptions | None = None
    ) -> T.Script:
        return cast(
            T.Script,
            self._http.request(
                "scripts.update",
                {"id": id},
                {"name": name, "code": code, "expectedVersion": expected_version},
                options,
            ),
        )

    def delete(self, id: str, *, options: RequestOptions | None = None) -> T.Deleted:
        return cast(T.Deleted, self._http.request("scripts.delete", {"id": id}, None, options))

    def get_version(self, id: str, version: int, *, options: RequestOptions | None = None) -> T.ScriptVersion:
        return cast(
            T.ScriptVersion,
            self._http.request("scripts.getVersion", {"id": id, "version": version}, None, options),
        )

    def restore(
        self, id: str, *, version: int, expected_version: int, options: RequestOptions | None = None
    ) -> T.Script:
        return cast(
            T.Script,
            self._http.request(
                "scripts.restore",
                {"id": id},
                {"version": version, "expectedVersion": expected_version},
                options,
            ),
        )

    def storage(self, *, options: RequestOptions | None = None) -> T.Storage:
        return cast(T.Storage, self._http.request("scripts.storage", {}, None, options))


class Secrets:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def list(self, *, options: RequestOptions | None = None) -> T.SecretList:
        return cast(T.SecretList, self._http.request("secrets.list", {}, None, options))

    def create(
        self,
        *,
        name: str,
        value: str,
        allow_inline: bool = False,
        script_ids: builtins.list[str] | None = None,
        options: RequestOptions | None = None,
    ) -> T.Secret:
        return cast(
            T.Secret,
            self._http.request(
                "secrets.create",
                {},
                {"name": name, "value": value, "allowInline": allow_inline, "scriptIds": script_ids or []},
                options,
            ),
        )

    def get(self, name: str, *, options: RequestOptions | None = None) -> T.Secret:
        return cast(T.Secret, self._http.request("secrets.get", {"name": name}, None, options))

    def update(
        self,
        name: str,
        *,
        value: str | None = None,
        allow_inline: bool | None = None,
        script_ids: builtins.list[str] | None = None,
        options: RequestOptions | None = None,
    ) -> T.Secret:
        return cast(
            T.Secret,
            self._http.request(
                "secrets.update",
                {"name": name},
                {
                    k: v
                    for k, v in {"value": value, "allowInline": allow_inline, "scriptIds": script_ids}.items()
                    if v is not None
                },
                options,
            ),
        )

    def delete(self, name: str, *, options: RequestOptions | None = None) -> T.Deleted:
        return cast(T.Deleted, self._http.request("secrets.delete", {"name": name}, None, options))


class Usage:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def get(self, *, options: RequestOptions | None = None) -> T.BillingStatus:
        return cast(T.BillingStatus, self._http.request("usage.get", {}, None, options))

    def summary(self, *, options: RequestOptions | None = None) -> T.UsageSummary:
        return cast(T.UsageSummary, self._http.request("usage.summary", {}, None, options))

    def history(
        self, days: Literal[7, 30, 90] = 7, *, options: RequestOptions | None = None
    ) -> T.UsageHistory:
        return cast(T.UsageHistory, self._http.request("usage.history", {"days": days}, None, options))


class Sandbox:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def get(self, *, options: RequestOptions | None = None) -> T.Sandbox:
        return cast(T.Sandbox, self._http.request("sandbox.get", {}, None, options))


class Billing:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def plans(self, *, options: RequestOptions | None = None) -> T.Plans:
        return cast(T.Plans, self._http.request("billing.plans", {}, None, options))


class Telemetry:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def record_execution(
        self, input: T.TelemetryExecution, *, options: RequestOptions | None = None
    ) -> T.TelemetryRecorded:
        return cast(T.TelemetryRecorded, self._http.request("telemetry.recordExecution", {}, input, options))

    def record_event(self, input: T.TelemetryEvent, *, options: RequestOptions | None = None) -> T.Accepted:
        return cast(T.Accepted, self._http.request("telemetry.recordEvent", {}, input, options))


class Health:
    def __init__(self, http: SyncHTTP) -> None:
        self._http = http

    def get(self, *, options: RequestOptions | None = None) -> T.Health:
        return cast(T.Health, self._http.request("health.get", {}, None, options))


class Runnee:
    """Server-side Runnee Cloud client. Use a context manager to close connections."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30,
        max_retries: int = 2,
        allow_insecure_http: bool = False,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._http = SyncHTTP(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            allow_insecure_http=allow_insecure_http,
            transport=transport,
        )
        self.executions = Executions(self._http)
        self.scripts = Scripts(self._http)
        self.secrets = Secrets(self._http)
        self.usage = Usage(self._http)
        self.sandbox = Sandbox(self._http)
        self.billing = Billing(self._http)
        self.telemetry = Telemetry(self._http)
        self.health = Health(self._http)

    def execute(
        self,
        code: str,
        *,
        mode: Literal["dry-run", "live"] = "dry-run",
        event: dict[str, Any] | None = None,
        retain_source: bool = False,
        script_name: str | None = None,
        secret_names: builtins.list[str] | None = None,
        script_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> T.ExecuteResponse:
        return cast(
            T.ExecuteResponse,
            self._http.request(
                "execute",
                {},
                {
                    k: v
                    for k, v in {
                        "code": code,
                        "mode": mode,
                        "event": event,
                        "retainSource": retain_source,
                        "scriptName": script_name,
                        "secretNames": secret_names,
                        "scriptId": script_id,
                    }.items()
                    if v is not None
                },
                options,
            ),
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Runnee:
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> None:
        self.close()


class AsyncExecutions:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def list(
        self,
        *,
        before: str | None = None,
        status: Literal["success", "failed"] | None = None,
        mode: Literal["dry-run", "live"] | None = None,
        options: RequestOptions | None = None,
    ) -> T.ExecutionPage:
        return cast(
            T.ExecutionPage,
            await self._http.request(
                "executions.list", {"before": before, "status": status, "mode": mode}, None, options
            ),
        )

    async def get(self, id: str, *, options: RequestOptions | None = None) -> T.ExecutionDetail:
        return cast(T.ExecutionDetail, await self._http.request("executions.get", {"id": id}, None, options))

    async def iterate(
        self,
        *,
        status: Literal["success", "failed"] | None = None,
        mode: Literal["dry-run", "live"] | None = None,
        before: str | None = None,
        options: RequestOptions | None = None,
    ) -> AsyncIterator[T.Execution]:
        seen: set[str] = set()
        while True:
            page = await self.list(status=status, mode=mode, before=before, options=options)
            for item in page["items"]:
                yield item
            cursor = page["nextCursor"]
            if cursor is None:
                break
            if cursor in seen:
                raise RunneeResponseError("Runnee returned a repeated pagination cursor.")
            seen.add(cursor)
            before = cursor


class AsyncScripts:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def list(self, *, options: RequestOptions | None = None) -> T.ScriptList:
        return cast(T.ScriptList, await self._http.request("scripts.list", {}, None, options))

    async def create(self, *, name: str, code: str, options: RequestOptions | None = None) -> T.Script:
        return cast(
            T.Script, await self._http.request("scripts.create", {}, {"name": name, "code": code}, options)
        )

    async def get(self, id: str, *, options: RequestOptions | None = None) -> T.ScriptDetail:
        return cast(T.ScriptDetail, await self._http.request("scripts.get", {"id": id}, None, options))

    async def update(
        self, id: str, *, name: str, code: str, expected_version: int, options: RequestOptions | None = None
    ) -> T.Script:
        return cast(
            T.Script,
            await self._http.request(
                "scripts.update",
                {"id": id},
                {"name": name, "code": code, "expectedVersion": expected_version},
                options,
            ),
        )

    async def delete(self, id: str, *, options: RequestOptions | None = None) -> T.Deleted:
        return cast(T.Deleted, await self._http.request("scripts.delete", {"id": id}, None, options))

    async def get_version(
        self, id: str, version: int, *, options: RequestOptions | None = None
    ) -> T.ScriptVersion:
        return cast(
            T.ScriptVersion,
            await self._http.request("scripts.getVersion", {"id": id, "version": version}, None, options),
        )

    async def restore(
        self, id: str, *, version: int, expected_version: int, options: RequestOptions | None = None
    ) -> T.Script:
        return cast(
            T.Script,
            await self._http.request(
                "scripts.restore",
                {"id": id},
                {"version": version, "expectedVersion": expected_version},
                options,
            ),
        )

    async def storage(self, *, options: RequestOptions | None = None) -> T.Storage:
        return cast(T.Storage, await self._http.request("scripts.storage", {}, None, options))


class AsyncSecrets:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def list(self, *, options: RequestOptions | None = None) -> T.SecretList:
        return cast(T.SecretList, await self._http.request("secrets.list", {}, None, options))

    async def create(
        self,
        *,
        name: str,
        value: str,
        allow_inline: bool = False,
        script_ids: builtins.list[str] | None = None,
        options: RequestOptions | None = None,
    ) -> T.Secret:
        return cast(
            T.Secret,
            await self._http.request(
                "secrets.create",
                {},
                {"name": name, "value": value, "allowInline": allow_inline, "scriptIds": script_ids or []},
                options,
            ),
        )

    async def get(self, name: str, *, options: RequestOptions | None = None) -> T.Secret:
        return cast(T.Secret, await self._http.request("secrets.get", {"name": name}, None, options))

    async def update(
        self,
        name: str,
        *,
        value: str | None = None,
        allow_inline: bool | None = None,
        script_ids: builtins.list[str] | None = None,
        options: RequestOptions | None = None,
    ) -> T.Secret:
        return cast(
            T.Secret,
            await self._http.request(
                "secrets.update",
                {"name": name},
                {
                    k: v
                    for k, v in {"value": value, "allowInline": allow_inline, "scriptIds": script_ids}.items()
                    if v is not None
                },
                options,
            ),
        )

    async def delete(self, name: str, *, options: RequestOptions | None = None) -> T.Deleted:
        return cast(T.Deleted, await self._http.request("secrets.delete", {"name": name}, None, options))


class AsyncUsage:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(self, *, options: RequestOptions | None = None) -> T.BillingStatus:
        return cast(T.BillingStatus, await self._http.request("usage.get", {}, None, options))

    async def summary(self, *, options: RequestOptions | None = None) -> T.UsageSummary:
        return cast(T.UsageSummary, await self._http.request("usage.summary", {}, None, options))

    async def history(
        self, days: Literal[7, 30, 90] = 7, *, options: RequestOptions | None = None
    ) -> T.UsageHistory:
        return cast(T.UsageHistory, await self._http.request("usage.history", {"days": days}, None, options))


class AsyncSandbox:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(self, *, options: RequestOptions | None = None) -> T.Sandbox:
        return cast(T.Sandbox, await self._http.request("sandbox.get", {}, None, options))


class AsyncBilling:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def plans(self, *, options: RequestOptions | None = None) -> T.Plans:
        return cast(T.Plans, await self._http.request("billing.plans", {}, None, options))


class AsyncTelemetry:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def record_execution(
        self, input: T.TelemetryExecution, *, options: RequestOptions | None = None
    ) -> T.TelemetryRecorded:
        return cast(
            T.TelemetryRecorded, await self._http.request("telemetry.recordExecution", {}, input, options)
        )

    async def record_event(
        self, input: T.TelemetryEvent, *, options: RequestOptions | None = None
    ) -> T.Accepted:
        return cast(T.Accepted, await self._http.request("telemetry.recordEvent", {}, input, options))


class AsyncHealth:
    def __init__(self, http: AsyncHTTP) -> None:
        self._http = http

    async def get(self, *, options: RequestOptions | None = None) -> T.Health:
        return cast(T.Health, await self._http.request("health.get", {}, None, options))


class AsyncRunnee:
    """Server-side Runnee Cloud client. Use a context manager to close connections."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str | None = None,
        timeout: float = 30,
        max_retries: int = 2,
        allow_insecure_http: bool = False,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._http = AsyncHTTP(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            allow_insecure_http=allow_insecure_http,
            transport=transport,
        )
        self.executions = AsyncExecutions(self._http)
        self.scripts = AsyncScripts(self._http)
        self.secrets = AsyncSecrets(self._http)
        self.usage = AsyncUsage(self._http)
        self.sandbox = AsyncSandbox(self._http)
        self.billing = AsyncBilling(self._http)
        self.telemetry = AsyncTelemetry(self._http)
        self.health = AsyncHealth(self._http)

    async def execute(
        self,
        code: str,
        *,
        mode: Literal["dry-run", "live"] = "dry-run",
        event: dict[str, Any] | None = None,
        retain_source: bool = False,
        script_name: str | None = None,
        secret_names: builtins.list[str] | None = None,
        script_id: str | None = None,
        options: RequestOptions | None = None,
    ) -> T.ExecuteResponse:
        return cast(
            T.ExecuteResponse,
            await self._http.request(
                "execute",
                {},
                {
                    k: v
                    for k, v in {
                        "code": code,
                        "mode": mode,
                        "event": event,
                        "retainSource": retain_source,
                        "scriptName": script_name,
                        "secretNames": secret_names,
                        "scriptId": script_id,
                    }.items()
                    if v is not None
                },
                options,
            ),
        )

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> AsyncRunnee:
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> None:
        await self.close()
