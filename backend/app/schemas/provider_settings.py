"""
Provider settings API schemas.

TASK-051 exposes only non-secret provider settings and read-only status.
API key fields are intentionally absent and extra request fields are rejected.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict


class ProviderSettingsResponse(BaseModel):
    provider: str
    model: str | None = None
    real_provider_enabled: bool
    llm_chat_enabled: bool
    fallback_to_mock: bool
    key_status: str
    resolved_provider: str
    last_test_status: str
    usage_summary: dict[str, Any] | None = None


class ProviderSettingsUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str | None = None
    model: str | None = None
    real_provider_enabled: bool | None = None
    llm_chat_enabled: bool | None = None
    fallback_to_mock: bool | None = None


class ProviderSettingsNotImplementedResponse(BaseModel):
    status: str
    message: str
