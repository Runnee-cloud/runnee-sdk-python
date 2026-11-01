import asyncio
import json
import threading
import httpx
import pytest
from runnee import (
    Runnee,
    AsyncRunnee,
    RequestOptions,
    RunneeAuthenticationError,
    RunneePermissionError,
    RunneeRateLimitError,
    RunneeConflictError,
    RunneeValidationError,
    RunneeNetworkError,
    RunneeTimeoutError,
    RunneeResponseError,
    RunneeCancelledError,
)

KEY = "rne_" + "T" * 43


def response(data, status=200, **headers):
    return httpx.Response(status, json=data, headers={"x-request-id": "req-test", **headers})


def client(handler, **kwargs):
    return Runnee(api_key=KEY, transport=httpx.MockTransport(handler), **kwargs)


def test_remote_execution_and_headers():
    requests = []

    def handler(request):
        requests.append(request)
        return response(
            {
                "success": True,
                "executionResult": {
                    "durationMs": 1,
                    "instructions": 4,
                    "returnValue": 30,
                    "replies": {"count": 0},
                },
            }
        )

    with client(handler) as c:
        r = c.execute(code="function main(){return 30;}")
    assert r["executionResult"]["returnValue"] == 30
    assert str(requests[0].url) == "https://api.runnee.cloud/api/runtime/execute"
    assert requests[0].headers["authorization"] == "Bearer " + KEY
    assert requests[0].headers["user-agent"].startswith("runnee-python/")
    assert json.loads(requests[0].content)["mode"] == "dry-run"


@pytest.mark.parametrize(
    "status,error",
    [
        (401, RunneeAuthenticationError),
        (403, RunneePermissionError),
        (409, RunneeConflictError),
        (429, RunneeRateLimitError),
    ],
)
def test_typed_errors_without_sensitive_bodies(status, error):
    calls = []
    with client(lambda r: calls.append(r) or response({"message": KEY}, status)) as c:
        with pytest.raises(error) as caught:
            c.execute(code="function main(){}")
        assert caught.value.request_id == "req-test"
        assert KEY not in str(caught.value)
    assert len(calls) == 1


def test_read_retry_and_execution_receipt():
    calls = []

    def handler(request):
        calls.append(request)
        return (
            response({}, 503, **{"retry-after": "0"})
            if len(calls) == 1
            else response({"success": True, "replayed": True, "originalResultOmitted": True})
        )

    with client(handler) as c:
        r = c.execute(code="function main(){}", options=RequestOptions(idempotency_key="order-123456"))
    assert r["originalResultOmitted"] is True
    assert [r.headers["idempotency-key"] for r in calls] == ["order-123456"] * 2


def test_uncertain_execution_is_not_retried():
    calls = []

    def handler(request):
        calls.append(request)
        raise httpx.ConnectError("network " + KEY)

    with client(handler) as c:
        with pytest.raises(RunneeNetworkError):
            c.execute(code="function main(){}")
        with pytest.raises(RunneeValidationError):
            c.execute(code="function main(){}", options=RequestOptions(max_retries=1))
    assert len(calls) == 1


@pytest.mark.parametrize("payload", [{}, {"success": "true"}])
def test_response_validation(payload):
    with client(lambda r: response(payload)) as c:
        with pytest.raises(RunneeResponseError):
            c.execute(code="function main(){}")


def test_pagination_and_metadata():
    urls = []

    def handler(request):
        urls.append(str(request.url))
        return response(
            {
                "items": [
                    {
                        "id": str(len(urls)),
                        "mode": "live",
                        "status": "success",
                        "durationMs": 1,
                        "instructionsUsed": 1,
                        "createdAt": "2026-01-01T00:00:00Z",
                    }
                ],
                "nextCursor": "12" if len(urls) == 1 else None,
                "policy": {},
            }
        )

    metadata = []
    with client(handler) as c:
        assert [
            r["id"]
            for r in c.executions.iterate(
                status="success", options=RequestOptions(on_response=metadata.append)
            )
        ] == ["1", "2"]
    assert "before=12" in urls[1] and "status=success" in urls[1]
    assert metadata[0].request_id == "req-test"


def test_secrets_and_validation():
    requests = []
    record = {
        "name": "EXTERNAL_API_KEY",
        "allowInline": True,
        "scriptIds": [],
        "version": 1,
        "createdAt": "2026-01-01T00:00:00Z",
        "updatedAt": "2026-01-01T00:00:00Z",
    }

    def handler(request):
        requests.append(request)
        return response(
            {"deleted": True}
            if request.method == "DELETE"
            else {"items": [record]}
            if request.method == "GET" and request.url.path.endswith("/secrets")
            else record
        )

    with client(handler) as c:
        assert c.secrets.create(name=record["name"], value="sensitive-value", allow_inline=True) == record
        c.secrets.update(record["name"], value="replacement-value")
        assert c.secrets.list()["items"] == [record]
        assert c.secrets.get(record["name"]) == record
        c.secrets.delete(record["name"])
        with pytest.raises(RunneeValidationError):
            c.secrets.create(name="bad", value="short")
        with pytest.raises(RunneeValidationError):
            c.scripts.get("../admin")
    assert all("sensitive-value" not in str(r.url) for r in requests)


@pytest.mark.parametrize(
    "url", ["http://example.com", "https://example.com/path", "file:///secret", "https://key@example.com"]
)
def test_insecure_configuration(url):
    with pytest.raises(RunneeValidationError):
        Runnee(api_key=KEY, base_url=url)


def test_sync_timeout_and_cancellation():
    with client(lambda r: (_ for _ in ()).throw(httpx.ReadTimeout("timeout"))) as c:
        with pytest.raises(RunneeTimeoutError):
            c.execute(code="function main(){}")
        cancel = threading.Event()
        cancel.set()
        with pytest.raises(RunneeCancelledError):
            c.execute(code="function main(){}", options=RequestOptions(cancel_event=cancel))


async def test_async_execution_secrets_and_pagination():
    def handler(request):
        if request.url.path.endswith("history"):
            return response({"items": [], "nextCursor": None, "policy": {}})
        if request.url.path.endswith("secrets"):
            return response({"items": []})
        return response({"success": True})

    async with AsyncRunnee(api_key=KEY, transport=httpx.MockTransport(handler)) as c:
        assert (await c.execute(code="function main(){}"))["success"]
        assert (await c.secrets.list())["items"] == []
        assert [item async for item in c.executions.iterate()] == []


async def test_async_timeout_and_task_cancellation():
    async def slow(request):
        await asyncio.sleep(10)
        return response({"success": True})

    async with AsyncRunnee(api_key=KEY, transport=httpx.MockTransport(slow)) as c:
        with pytest.raises(RunneeTimeoutError):
            await c.execute(code="function main(){}", options=RequestOptions(timeout=0.01))
        task = asyncio.create_task(c.execute(code="function main(){}"))
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task


def test_non_json_data_fails_before_io():
    calls = []
    with client(lambda r: calls.append(r) or response({"success": True})) as c:
        for event in ({"invalid": object()}, {"invalid": float("nan")}):
            with pytest.raises(RunneeValidationError):
                c.execute(code="function main(){}", event=event)
    assert calls == []


def test_explicit_positional_key_constructor():
    seen = []
    with Runnee(
        KEY,
        transport=httpx.MockTransport(
            lambda r: seen.append(r.headers["authorization"]) or response({"success": True})
        ),
    ) as c:
        assert c.execute(code="function main(){}")["success"] is True
    assert seen == ["Bearer " + KEY]


async def test_async_positional_key_constructor():
    seen = []
    async with AsyncRunnee(
        KEY,
        transport=httpx.MockTransport(
            lambda r: seen.append(r.headers["authorization"]) or response({"success": True})
        ),
    ) as c:
        assert (await c.execute(code="function main(){}"))["success"] is True
    assert seen == ["Bearer " + KEY]
