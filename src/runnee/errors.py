"""Safe exceptions: no request, credential or response body is retained."""

from __future__ import annotations


class RunneeError(Exception):
    def __init__(self, message: str, *, status: int | None = None, request_id: str | None = None) -> None:
        super().__init__(message)
        self.status = status
        self.request_id = request_id


class RunneeAuthenticationError(RunneeError):
    pass


class RunneePermissionError(RunneeError):
    pass


class RunneeValidationError(RunneeError):
    pass


class RunneeRateLimitError(RunneeError):
    retry_after: float | None = None


class RunneeTimeoutError(RunneeError):
    pass


class RunneeNetworkError(RunneeError):
    pass


class RunneeServerError(RunneeError):
    pass


class RunneeConflictError(RunneeError):
    pass


class RunneeNotFoundError(RunneeError):
    pass


class RunneeResponseError(RunneeError):
    pass


class RunneeCancelledError(RunneeError):
    pass
