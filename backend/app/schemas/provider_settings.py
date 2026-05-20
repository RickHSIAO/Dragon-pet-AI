"""
Provider settings API schemas.

Provider settings responses expose safe metadata only. Key save requests are
write-only and key values are never included in response schemas.
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


class KeySaveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str
    api_key: str


class KeyStatusResponse(BaseModel):
    provider: str
    key_status: str
    message: str


class ProviderTestConnectionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str
    model: str | None = None
    explicit_cost_ack: bool = False


class ProviderTestConnectionResponse(BaseModel):
    status: str
    provider: str
    model: str | None = None
    source: str
    safe_message: str
    error_category: str | None = None
    usage_estimate: dict[str, int] | None = None


class ProviderSettingsNotImplementedResponse(BaseModel):
    status: str
    message: str
