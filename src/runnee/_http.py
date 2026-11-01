from __future__ import annotations
import asyncio
import json
import math
import os
import random
import threading
import time
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from typing import Any, Callable
from urllib.parse import quote, urlsplit
import httpx
from ._validation import CONTRACTS, validate
from .errors import (
    RunneeAuthenticationError,
    RunneeCancelledError,
    RunneeConflictError,
    RunneeError,
    RunneeNetworkError,
    RunneeNotFoundError,
    RunneePermissionError,
    RunneeRateLimitError,
    RunneeResponseError,
    RunneeServerError,
    RunneeTimeoutError,
    RunneeValidationError,
)


@dataclass(frozen=True)
class ResponseMetadata:
    status: int
    request_id: str | None
    rate_limit_remaining: int | None


@dataclass(frozen=True)
class RequestOptions:
    timeout: float | None = None
    max_retries: int | None = None
    idempotency_key: str | None = None
    cancel_event: threading.Event | None = None
    on_response: Callable[[ResponseMetadata], None] | None = None


def _range(value: float, low: float, high: float, name: str) -> float:
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not math.isfinite(value)
        or not low <= value <= high
    ):
        raise RunneeValidationError(name + " is outside the supported range.")
    return value


def _retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        result = float(value)
        if math.isfinite(result) and result >= 0:
            return result
    except ValueError:
        pass
    try:
        return max(0.0, parsedate_to_datetime(value).timestamp() - time.time())
    except (ValueError, TypeError, OverflowError):
        return None


class _Base:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30,
        max_retries: int = 2,
        allow_insecure_http: bool = False,
    ) -> None:
        import re

        key = api_key if api_key is not None else os.environ.get("RUNNEE_API_KEY")
        if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z0-9_-]{8,512}", key):
            raise RunneeAuthenticationError("Set RUNNEE_API_KEY or provide api_key.")
        raw_url = base_url or os.environ.get("RUNNEE_BASE_URL", "https://api.runnee.cloud")
        try:
            if not isinstance(raw_url, str):
                raise ValueError
            url = urlsplit(raw_url)
            if (
                not url.hostname
                or url.username
                or url.password
                or url.query
                or url.fragment
                or url.path not in ("", "/")
                or url.scheme not in ("https", "http")
                or (
                    url.scheme == "http"
                    and url.hostname not in ("localhost", "127.0.0.1", "::1")
                    and not allow_insecure_http
                )
            ):
                raise ValueError
            self._base_url = raw_url.rstrip("/")
        except ValueError:
            raise RunneeValidationError(
                "base_url requires an HTTPS origin; HTTP is limited to local development."
            ) from None
        self._key = key
        self._timeout = _range(timeout, 0.001, 300, "timeout")
        _range(max_retries, 0, 5, "max_retries")
        if not isinstance(max_retries, int):
            raise RunneeValidationError("max_retries must be an integer.")
        self._retries = max_retries

    def _prepare(
        self, operation: str, params: dict[str, Any], body: Any, options: RequestOptions
    ) -> tuple[dict[str, Any], str, dict[str, str], int, float]:
        import re

        op = next((item for item in CONTRACTS["operations"] if item["id"] == operation), None)
        if not op:
            raise RunneeValidationError("Unsupported SDK operation.")
        pathname = op["path"]
        query: dict[str, str] = {}
        for key, value in params.items():
            if value is None:
                continue
            marker = "{" + key + "}"
            if marker in pathname:
                text = str(value)
                if not text or text in (".", "..") or re.search(r"[/\\\x00-\x1f]", text):
                    raise RunneeValidationError("Invalid resource identifier.")
                pathname = pathname.replace(marker, quote(text, safe=""))
            else:
                query[key] = str(value)
        if "{" in pathname:
            raise RunneeValidationError("Missing resource identifier.")
        if op["request"]:
            validate(body, op["request"])
            try:
                encoded = json.dumps(body, allow_nan=False, ensure_ascii=False)
                if len(encoded.encode("utf-8")) > 102400:
                    raise ValueError
            except (ValueError, TypeError, RecursionError, UnicodeError):
                raise RunneeValidationError("Request data must be bounded, serializable JSON.") from None
        if options.idempotency_key is not None and (
            operation != "execute" or not re.fullmatch(r"[A-Za-z0-9_.:-]{8,128}", options.idempotency_key)
        ):
            raise RunneeValidationError("Use an 8–128 character idempotency_key only for execute.")
        safe = op["method"] == "GET" or operation == "execute" and bool(options.idempotency_key)
        retries = options.max_retries if options.max_retries is not None else self._retries if safe else 0
        _range(retries, 0, 5, "max_retries")
        if not isinstance(retries, int) or retries and not safe:
            raise RunneeValidationError("Automatic retries require reads or idempotent execution.")
        timeout = _range(
            options.timeout if options.timeout is not None else self._timeout, 0.001, 300, "timeout"
        )
        from urllib.parse import urlencode

        return (
            op,
            self._base_url + pathname + ("?" + urlencode(query) if query else ""),
            query,
            retries,
            timeout,
        )

    def _headers(self, options: RequestOptions) -> dict[str, str]:
        headers = {
            "Authorization": "Bearer " + self._key,
            "Accept": "application/json",
            "User-Agent": "runnee-python/0.1.0",
        }
        if options.idempotency_key:
            headers["Idempotency-Key"] = options.idempotency_key
        return headers

    @staticmethod
    def _check(deadline: float, options: RequestOptions) -> float:
        if options.cancel_event and options.cancel_event.is_set():
            raise RunneeCancelledError("Request cancelled. Remote execution may still complete.")
        left = deadline - time.monotonic()
        if left <= 0:
            raise RunneeTimeoutError(
                "Request timed out. Reuse its idempotency key or inspect history before submitting again."
            )
        return left

    @staticmethod
    def _response(response: httpx.Response, options: RequestOptions) -> None:
        if options.on_response:
            remaining = response.headers.get("x-ratelimit-remaining", "")
            options.on_response(
                ResponseMetadata(
                    response.status_code,
                    response.headers.get("x-request-id"),
                    int(remaining) if remaining.isdigit() else None,
                )
            )

    @staticmethod
    def _decode(response: httpx.Response, data: bytes, schema: str) -> Any:
        request_id = response.headers.get("x-request-id")
        if not 200 <= response.status_code < 300:
            classes: dict[int, type[RunneeError]] = {
                401: RunneeAuthenticationError,
                403: RunneePermissionError,
                404: RunneeNotFoundError,
                409: RunneeConflictError,
                429: RunneeRateLimitError,
            }
            error_cls = classes.get(
                response.status_code,
                RunneeServerError if response.status_code >= 500 else RunneeValidationError,
            )
            message = (
                "Request conflicts with existing state. An execution may already be admitted; inspect history."
                if response.status_code == 409
                else "Invalid, expired or revoked Runnee API key."
                if response.status_code == 401
                else "The API key scope or resource policy does not permit this operation."
                if response.status_code == 403
                else f"Runnee API request failed (HTTP {response.status_code})."
            )
            error = error_cls(message, status=response.status_code, request_id=request_id)
            if isinstance(error, RunneeRateLimitError):
                error.retry_after = _retry_after(response.headers.get("retry-after"))
            raise error
        content_type = response.headers.get("content-type", "").split(";")[0].strip().lower()
        if content_type != "application/json" and not content_type.endswith("+json"):
            raise RunneeResponseError(
                "Runnee returned a non-JSON response.", status=response.status_code, request_id=request_id
            )
        try:
            value = json.loads(data)
        except (ValueError, UnicodeError):
            raise RunneeResponseError(
                "Runnee returned invalid JSON.", status=response.status_code, request_id=request_id
            ) from None
        validate(value, schema, True, request_id)
        return value

    @staticmethod
    def _delay(status: int, headers: httpx.Headers, attempt: int, retries: int) -> float | None:
        after = _retry_after(headers.get("retry-after"))
        if status in (429, 500, 502, 503, 504) and attempt < retries and (after is None or after <= 60):
            return after if after is not None else min(10, 0.25 * 2**attempt) * random.uniform(0.5, 1)
        return None


class SyncHTTP(_Base):
    def __init__(self, *, transport: httpx.BaseTransport | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client = httpx.Client(transport=transport, follow_redirects=False, trust_env=False)

    def close(self) -> None:
        self._client.close()

    def _wait(self, delay: float, deadline: float, options: RequestOptions) -> None:
        left = self._check(deadline, options)
        duration = min(delay, left)
        if options.cancel_event:
            options.cancel_event.wait(duration)
        else:
            time.sleep(duration)
        self._check(deadline, options)

    def request(
        self, operation: str, params: dict[str, Any], body: Any, options: RequestOptions | None = None
    ) -> Any:
        options = options or RequestOptions()
        op, url, _, retries, timeout = self._prepare(operation, params, body, options)
        deadline = time.monotonic() + timeout
        for attempt in range(retries + 1):
            delay: float | None = None
            try:
                with self._client.stream(
                    op["method"],
                    url,
                    headers=self._headers(options),
                    json=body,
                    timeout=self._check(deadline, options),
                ) as response:
                    self._response(response, options)
                    delay = self._delay(response.status_code, response.headers, attempt, retries)
                    if delay is None:
                        chunks: list[bytes] = []
                        size = 0
                        if response.is_success:
                            for chunk in response.iter_bytes():
                                self._check(deadline, options)
                                size += len(chunk)
                                if size > 5 * 1024 * 1024:
                                    raise RunneeResponseError("Runnee response exceeds the SDK size limit.")
                                chunks.append(chunk)
                        return self._decode(response, b"".join(chunks), op["response"])
            except httpx.TimeoutException:
                raise RunneeTimeoutError(
                    "Request timed out. An execution may still have completed."
                ) from None
            except httpx.HTTPError:
                if attempt >= retries:
                    raise RunneeNetworkError(
                        "Unable to reach Runnee. Inspect history before resubmitting an uncertain execution."
                    ) from None
                delay = min(10, 0.25 * 2**attempt) * random.uniform(0.5, 1)
            if delay is not None:
                self._wait(delay, deadline, options)
        raise RunneeNetworkError("Runnee request could not be completed.")


class AsyncHTTP(_Base):
    def __init__(self, *, transport: httpx.AsyncBaseTransport | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._client = httpx.AsyncClient(transport=transport, follow_redirects=False, trust_env=False)

    async def close(self) -> None:
        await self._client.aclose()

    async def request(
        self, operation: str, params: dict[str, Any], body: Any, options: RequestOptions | None = None
    ) -> Any:
        options = options or RequestOptions()
        op, url, _, retries, timeout = self._prepare(operation, params, body, options)
        deadline = time.monotonic() + timeout
        try:
            async with asyncio.timeout(timeout):
                for attempt in range(retries + 1):
                    delay: float | None = None
                    try:
                        async with self._client.stream(
                            op["method"],
                            url,
                            headers=self._headers(options),
                            json=body,
                            timeout=self._check(deadline, options),
                        ) as response:
                            self._response(response, options)
                            delay = self._delay(response.status_code, response.headers, attempt, retries)
                            if delay is None:
                                chunks: list[bytes] = []
                                size = 0
                                if response.is_success:
                                    async for chunk in response.aiter_bytes():
                                        self._check(deadline, options)
                                        size += len(chunk)
                                        if size > 5 * 1024 * 1024:
                                            raise RunneeResponseError(
                                                "Runnee response exceeds the SDK size limit."
                                            )
                                        chunks.append(chunk)
                                return self._decode(response, b"".join(chunks), op["response"])
                    except httpx.TimeoutException:
                        raise RunneeTimeoutError(
                            "Request timed out. An execution may still have completed."
                        ) from None
                    except httpx.HTTPError:
                        if attempt >= retries:
                            raise RunneeNetworkError(
                                "Unable to reach Runnee. Inspect history before resubmitting an uncertain execution."
                            ) from None
                        delay = min(10, 0.25 * 2**attempt) * random.uniform(0.5, 1)
                    if delay is not None:
                        self._check(deadline, options)
                        await asyncio.sleep(delay)
                raise RunneeNetworkError("Runnee request could not be completed.")
        except TimeoutError:
            raise RunneeTimeoutError(
                "Request timed out. Reuse its idempotency key or inspect history."
            ) from None
