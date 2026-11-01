# Generated from the public OpenAPI contract.
from __future__ import annotations
from typing import Any, Literal, NotRequired, TypeAlias, TypedDict


class Error(TypedDict):
    statusCode: NotRequired[int]
    message: NotRequired[str | list[str]]
    error: NotRequired[str]
    code: NotRequired[str]


class ExecuteRequest(TypedDict):
    code: str
    mode: NotRequired[Literal["dry-run", "live"]]
    event: NotRequired[dict[str, Any]]
    retainSource: NotRequired[bool]
    scriptName: NotRequired[str]
    secretNames: NotRequired[list[str]]
    scriptId: NotRequired[str]


class Diagnostic(TypedDict):
    code: NotRequired[str]
    message: str
    line: NotRequired[int]
    column: NotRequired[int]
    filename: NotRequired[str]
    snippet: NotRequired[str]


Timings: TypeAlias = dict[str, Any]


class ExecutionResult(TypedDict):
    durationMs: float
    instructions: int
    returnValue: NotRequired[Any]
    replies: dict[str, Any]
    counters: NotRequired[dict[str, Any]]
    explain: NotRequired[dict[str, Any]]


class ExecuteResponse(TypedDict):
    success: bool
    mocked: NotRequired[bool]
    error: NotRequired[Diagnostic]
    executionResult: NotRequired[ExecutionResult]
    replies: NotRequired[list[Any]]
    metrics: NotRequired[dict[str, Any]]
    telemetryRecorded: NotRequired[bool]
    executionId: NotRequired[str | None]
    replayed: NotRequired[bool]
    originalResultOmitted: NotRequired[bool]


Policy: TypeAlias = dict[str, Any]


class Execution(TypedDict):
    id: str
    scriptName: NotRequired[str | None]
    mode: str
    status: str
    durationMs: float
    instructionsUsed: int
    errorCode: NotRequired[str | None]
    httpCalls: NotRequired[int]
    dbOps: NotRequired[int]
    errorMessage: NotRequired[str | None]
    hasSource: NotRequired[bool]
    timings: NotRequired[Timings]
    createdAt: str
    expiresAt: NotRequired[str]


class ExecutionDetail(TypedDict):
    id: str
    scriptName: NotRequired[str | None]
    mode: str
    status: str
    durationMs: float
    instructionsUsed: int
    errorCode: NotRequired[str | None]
    httpCalls: NotRequired[int]
    dbOps: NotRequired[int]
    errorMessage: NotRequired[str | None]
    hasSource: NotRequired[bool]
    timings: NotRequired[Timings]
    createdAt: str
    expiresAt: NotRequired[str]
    sourceCode: NotRequired[str | None]
    outputPreview: NotRequired[str | None]


class ExecutionPage(TypedDict):
    items: list[Execution]
    nextCursor: str | None
    policy: Policy


class Script(TypedDict):
    id: str
    name: str
    currentVersion: int
    createdAt: str
    updatedAt: str


class ScriptDetail(TypedDict):
    id: str
    name: str
    currentVersion: int
    createdAt: str
    updatedAt: str
    code: str
    versions: list[dict[str, Any]]


class ScriptList(TypedDict):
    items: list[Script]
    policy: Policy


class ScriptCreate(TypedDict):
    name: str
    code: str


class ScriptUpdate(TypedDict):
    name: str
    code: str
    expectedVersion: int


class ScriptRestore(TypedDict):
    version: int
    expectedVersion: int


class ScriptVersion(TypedDict):
    version: int
    code: str
    createdAt: str


class Deleted(TypedDict):
    deleted: bool


class Storage(TypedDict):
    policy: Policy
    history: dict[str, Any]
    scripts: dict[str, Any]


class Secret(TypedDict):
    name: str
    allowInline: bool
    scriptIds: list[str]
    version: int
    createdAt: str
    updatedAt: str


class SecretList(TypedDict):
    items: list[Secret]


class SecretCreate(TypedDict):
    name: str
    value: str
    allowInline: NotRequired[bool]
    scriptIds: NotRequired[list[str]]


class SecretUpdate(TypedDict):
    value: NotRequired[str]
    allowInline: NotRequired[bool]
    scriptIds: NotRequired[list[str]]


class SandboxLimits(TypedDict):
    timeoutMs: int
    maxInstructions: int
    maxMemoryMb: int


class Sandbox(TypedDict):
    plan: str
    configurable: bool
    limits: SandboxLimits
    defaults: SandboxLimits
    maxLimits: SandboxLimits


class Plan(TypedDict):
    id: str
    configurable: NotRequired[bool]
    limits: SandboxLimits
    maxLimits: NotRequired[SandboxLimits]
    name: str
    monthlyUsd: NotRequired[float | None]
    yearlyMonthlyUsd: NotRequired[float | None]
    usageUsdPer1k: NotRequired[float]
    executionsPerMonth: int | None
    timeoutMs: NotRequired[int]
    features: NotRequired[list[str]]


class Plans(TypedDict):
    configured: bool
    plans: list[Plan]


class BillingStatus(TypedDict):
    configured: bool
    plan: Plan
    subscription: dict[str, Any] | None
    usage: dict[str, Any]


class UsageSummary(TypedDict):
    windowDays: int
    totalExecutions: int
    successfulExecutions: int
    failedExecutions: int
    averageDurationMs: float
    latest: list[dict[str, Any]]


class UsageHistory(TypedDict):
    days: int
    total: int
    success: int
    failed: int
    successRate: float
    daily: list[dict[str, Any]]
    topScripts: list[dict[str, Any]]
    topScriptsSample: dict[str, Any]
    apiKeys: dict[str, Any]


class TelemetryExecution(TypedDict):
    scriptName: NotRequired[str]
    mode: NotRequired[str]
    status: str
    durationMs: int
    instructionsUsed: int
    memoryUsageKb: NotRequired[int]
    errorCode: NotRequired[str]
    metadata: NotRequired[dict[str, Any]]


class TelemetryEvent(TypedDict):
    eventName: str
    pagePath: NotRequired[str]
    sessionId: NotRequired[str]
    fingerprintHash: NotRequired[str]
    properties: NotRequired[dict[str, Any]]


TelemetryRecorded: TypeAlias = dict[str, Any] | str | None


class Accepted(TypedDict):
    accepted: bool


class Health(TypedDict):
    status: Literal["operational", "degraded"]
    timestamp: str
    services: list[dict[str, Any]]
