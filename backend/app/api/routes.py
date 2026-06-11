"""
API routes for dragon-pet-ai backend.

TASK-009 keeps the system mock-only while allowing mock chat to read internal
MVP state before generating a reply.

Safety boundaries:
- /chat does not call any external AI API.
- /chat does not execute shell commands.
- /chat does not read or write user files.
- /chat only writes local conversation history and internal MVP state to SQLite.
"""

import logging
import time

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from pydantic import ValidationError
from sqlmodel import Session

_logger = logging.getLogger(__name__)

from app.core.config import is_memory_injection_enabled
from app.db.database import get_session
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.memory import (
    MemoryContextPreviewResponse,
    MemoryCreateRequest,
    MemoryResponse,
)
from app.schemas.memory_audit import (
    MemoryInjectionAuditListResponse,
    MemoryInjectionAuditResponse,
)
from app.schemas.provider_settings import (
    KeySaveRequest,
    KeyStatusResponse,
    ProviderSettingsResponse,
    ProviderTestConnectionRequest,
    ProviderTestConnectionResponse,
    ProviderSettingsUpdateRequest,
)
from app.services.chat_service import generate_chat_reply
from app.services.conversation_service import get_or_create_default_conversation, store_chat_turn
from app.services.memory_audit_service import (
    create_memory_injection_audit,
    list_memory_injection_audits_paginated,
    normalize_audit_pagination,
    parse_exclusion_summary_json,
    parse_memory_ids_json,
)
from app.services.memory_service import (
    build_approved_memory_context_records,
    build_memory_context_preview,
    create_memory,
    deactivate_memory,
    list_active_memories,
)
from app.services.prompt_service import format_approved_memory_context, normalize_chat_mode
from app.services.provider_test_connection_service import (
    ProviderTestConnectionRequestError,
    check_ollama_server_liveness,
    run_provider_test_connection,
)
from app.services.provider_settings_service import (
    ProviderKeyStorageError,
    ProviderSettingsUpdate,
    clear_provider_api_key,
    get_provider_settings,
    save_provider_api_key,
    update_provider_settings,
)
from app.services.owner_voice_gate_storage import (
    OwnerVoiceGateSettingsUpdate,
    delete_owner_voice_gate_voiceprint,
    enroll_owner_voice_gate_from_files,
    get_owner_voice_gate_status,
    update_owner_voice_gate_settings,
    validate_owner_voice_gate_enroll_fields,
    validate_owner_voice_gate_update_fields,
    validate_owner_voice_gate_verify_fields,
    verify_owner_voice_gate_from_files,
)
from app.services.state_service import get_chat_state_context, update_state_after_chat_turn
from app.services.usage_meter_service import UsageRecord, estimate_text_tokens, record_usage
from app.stt.stt_service import transcribe_audio_bytes, warmup_funasr_sidecar  # TASK-167B / TASK-256
from app.stt.stt_service import _STT_RESOLVED_PROVIDER as _stt_resolved_provider  # TASK-256
from app.ocr.ocr_service import extract_text_from_dataurl, get_ocr_status  # TASK-172A-OCR-BACKEND, TASK-177

router = APIRouter()

_STT_MAX_BYTES = 10 * 1024 * 1024  # 10 MB — guard against runaway uploads
# TASK-245: lock STT language to prevent Whisper auto-detect from misclassifying
# short Chinese speech as Thai / Malay / Indonesian.  Hard-coded here — no UI,
# no persistence, no new IPC channel.  "zh" is the ISO-639-1 code that
# faster-whisper / Whisper accept for Mandarin Chinese (Simplified + Traditional).
_STT_DEFAULT_LANGUAGE = "zh"
_STT_DEFAULT_TASK = "transcribe"  # explicit assertion — never "translate"


@router.post("/stt/transcribe")
async def stt_transcribe(audio: UploadFile = File(...)):
    """
    TASK-167B: Transcribe a short audio clip using local Whisper.

    Accepts any audio format Whisper supports (webm, wav, ogg, mp4 …).
    Returns {"transcript": str, "status": "ok" | "unavailable" | "empty" | "error",
             "language": str, "languageLocked": bool, "task": str,
             "provider": str | None, "model": str | None, "detectedLanguage": str | None,
             "requestedModel": str | None, "resolvedModel": str | None,
             "modelSource": str | None, "modelFallbackReason": str | None,
             "modelEnv": str | None, "modelLoadStatus": str | None,
             "modelLoadError": str | None,
             "rawTranscript": str | None, "correctedTranscript": str | None,
             "correctionApplied": bool | None, "correctionMode": str | None,
             "correctionReason": str | None, "matchedAlias": str | None,
             "canonicalTerm": str | None,
             "punctuatedTranscript": str | None, "finalTranscript": str | None,
             "punctuationApplied": bool | None, "punctuationMode": str | None,
             "punctuationReason": str | None,
             "sttProviderRequested": str | None, "sttProviderResolved": str | None,
             "sttProviderSource": str | None, "sttProviderLoadStatus": str | None,
             "sttProviderLoadError": str | None, "sttProviderFallbackReason": str | None,
             "sttProviderCandidateNotes": str | None,
             "noSpeechGuardEnabled": bool | None, "noSpeechGuardApplied": bool | None,
             "noSpeechGuardReason": str | None, "audioDurationMs": int | None,
             "audioRms": float | None, "audioPeak": float | None,
             "audioSpeechDetected": bool | None, "sttNoSpeechProbability": float | None,
             "suspiciousTranscriptPattern": str | None}.

    Scope limits (TASK-167B / TASK-245):
    - Local Whisper only — no external STT API calls.
    - No audio persistence — bytes are processed in-memory only.
    - No always-listening, wake-word, TTS, screen capture, or vision logic.
    - /chat handoff is deferred to TASK-167C; this endpoint stops at transcript.
    - Language is locked to _STT_DEFAULT_LANGUAGE ("zh") — no UI or persistence.
    - TASK-STT-001 punctuation restoration adds only conservative local punctuation
      after existing safe-dictionary correction; request schema stays unchanged.
    """
    audio_bytes = await audio.read(_STT_MAX_BYTES + 1)
    if len(audio_bytes) > _STT_MAX_BYTES:
        raise HTTPException(status_code=413, detail="Audio file too large (max 10 MB).")
    mime_type = audio.content_type or "audio/webm"
    result = transcribe_audio_bytes(
        audio_bytes,
        mime_type=mime_type,
        language=_STT_DEFAULT_LANGUAGE,
    )
    # TASK-245: augment with language-lock metadata so the renderer diagnostics
    # panel can surface it without a new endpoint or IPC channel.
    result["language"] = _STT_DEFAULT_LANGUAGE
    result["languageLocked"] = True
    result["task"] = _STT_DEFAULT_TASK
    return result


@router.post("/stt/warmup")
def stt_warmup():
    """
    TASK-256: Best-effort STT sidecar warmup.

    No audio upload. No mic. No disk writes.
    Warms the persistent funasr-local sidecar only.
    Returns skipped for non-funasr-local providers.

    Safety boundaries:
    - Does NOT open the microphone.
    - Does NOT accept or process audio bytes.
    - Does NOT persist anything to disk.
    - Does NOT write chat history.
    - Does NOT trigger Pet Window / TTS / Output Queue.
    """
    provider = _stt_resolved_provider
    if provider != "funasr-local":
        return {
            "status": "skipped",
            "provider": provider,
            "warmupStatus": "skipped",
            "elapsedMs": 0,
            "sidecarMode": None,
            "message": f"unsupported_provider: {provider}",
        }

    t0 = time.monotonic()
    try:
        result = warmup_funasr_sidecar()
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        _logger.warning("TASK-256: STT warmup error: %s", type(exc).__name__)
        return {
            "status": "error",
            "provider": provider,
            "warmupStatus": "error",
            "elapsedMs": elapsed_ms,
            "sidecarMode": "persistent",
            "message": "warmup_error",
        }
    elapsed_ms = int((time.monotonic() - t0) * 1000)
    return {
        "status": result["status"],
        "provider": provider,
        "warmupStatus": result["warmupStatus"],
        "elapsedMs": elapsed_ms,
        "sidecarMode": result.get("sidecarMode"),
        "message": result.get("message", ""),
    }


@router.post("/llm/warmup")
async def llm_warmup():
    """
    TASK-256: Best-effort Ollama model warmup.

    Loads the configured Ollama model into memory without generating a response.
    Uses Ollama's /api/generate with keep_alive and no prompt.

    Safety boundaries:
    - Does NOT write chat history.
    - Does NOT go through the normal /chat flow.
    - Does NOT trigger Pet Window / TTS / Output Queue.
    - Does NOT forward raw Ollama response bodies to the caller.
    - Returns skipped for non-ollama or mock providers.
    - Never returns raw stack traces.
    """
    from app.core.config import get_ollama_base_url, get_ollama_keep_alive
    from app.llm.ollama_provider import DEFAULT_OLLAMA_MODEL

    settings = get_provider_settings()
    provider = settings.get("provider", "mock")
    real_enabled = bool(settings.get("real_provider_enabled", False))

    if provider != "ollama" or not real_enabled:
        return {
            "status": "skipped",
            "provider": provider,
            "model": settings.get("model") or "",
            "warmupStatus": "skipped",
            "elapsedMs": 0,
            "message": "not_applicable",
        }

    model = (settings.get("model") or DEFAULT_OLLAMA_MODEL).strip() or DEFAULT_OLLAMA_MODEL
    base_url = get_ollama_base_url()
    keep_alive = get_ollama_keep_alive()

    t0 = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{base_url}/api/generate",
                json={"model": model, "keep_alive": keep_alive, "stream": False},
            )
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        if resp.status_code < 300:
            return {
                "status": "ok",
                "provider": "ollama",
                "model": model,
                "warmupStatus": "loaded",
                "elapsedMs": elapsed_ms,
                "message": "model loaded",
            }
        return {
            "status": "error",
            "provider": "ollama",
            "model": model,
            "warmupStatus": "error",
            "elapsedMs": elapsed_ms,
            "message": "ollama_error",
        }
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = int((time.monotonic() - t0) * 1000)
        _logger.warning("TASK-256: LLM warmup error: %s", type(exc).__name__)
        return {
            "status": "error",
            "provider": "ollama",
            "model": model,
            "warmupStatus": "error",
            "elapsedMs": elapsed_ms,
            "message": "warmup_error",
        }


@router.post("/ocr/extract")
async def ocr_extract(request: Request):
    """
    TASK-172A-OCR-BACKEND: Extract text from a base64 image dataUrl using local OCR.

    Accepts: {"image": "<data:image/...;base64,...>"}
    Returns: {"ok": true, "text": "..."} or {"ok": false, "error": "reason-code"}

    Privacy: image decoded in memory; no disk write; no external upload; no /chat call.
    Error codes: missing-image, invalid-dataurl, unsupported-mime, payload-too-large,
                 ocr-unavailable, ocr-failed, no-text.
    Never returns raw tracebacks or provider internals.
    """
    try:
        body = await request.json()
    except Exception:
        return {"ok": False, "error": "invalid-dataurl"}

    image_dataurl = body.get("image") if isinstance(body, dict) else None
    if not image_dataurl:
        return {"ok": False, "error": "missing-image"}

    # String-length guard before decoding (20 MB as base64 string ≈ 26.7 MB decoded)
    if len(image_dataurl) > 26 * 1024 * 1024:
        return {"ok": False, "error": "payload-too-large"}

    return extract_text_from_dataurl(image_dataurl)


@router.get("/ocr/status")
async def ocr_status_check():
    """
    TASK-177: Return OCR language availability and Tesseract diagnostic info.

    Returns: {
      "tesseract_available": bool,
      "chi_tra_available": bool,
      "eng_available": bool,
      "selected_lang": str | null,
      "fallback_reason": str | null
    }

    Never exposes Python tracebacks or provider internals.
    Cached: probed once on first call, result reused for the process lifetime.
    """
    return get_ocr_status()


@router.get("/health")
def health_check():
    """
    Liveness check endpoint.
    Returns ok status if the backend is running.
    """
    return {"status": "ok", "service": "dragon-pet-ai"}


@router.get("/owner-voice-gate/status")
def owner_voice_gate_status_route():
    """
    TASK-261: Return safe Owner Voice Gate storage-stub status.

    This endpoint does not accept audio, does not load speaker models, does not
    call STT, does not call /chat, and never returns raw audio or embeddings.
    """
    return get_owner_voice_gate_status()


@router.post("/owner-voice-gate/settings")
async def owner_voice_gate_settings_route(request: Request):
    """
    TASK-261: Update safe Owner Voice Gate stub settings only.

    Allowed fields: enabled, threshold, safetyNoticeAccepted.
    Real enrollment and embedding persistence are intentionally unavailable.
    """
    try:
        body = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid json body") from exc
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="request body must be an object")
    try:
        validate_owner_voice_gate_update_fields(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    update = OwnerVoiceGateSettingsUpdate(
        enabled=body["enabled"] if "enabled" in body else None,
        threshold=body["threshold"] if "threshold" in body else None,
        safetyNoticeAccepted=(
            body["safetyNoticeAccepted"] if "safetyNoticeAccepted" in body else None
        ),
    )
    return update_owner_voice_gate_settings(update)


@router.post("/owner-voice-gate/delete")
def owner_voice_gate_delete_route():
    """
    TASK-261: Reset the Owner Voice Gate storage stub.

    There is no real voiceprint in this task. Delete resets the placeholder
    state to defaults and removes the stub file if it exists.
    """
    return delete_owner_voice_gate_voiceprint()


@router.post("/owner-voice-gate/enroll-files")
async def owner_voice_gate_enroll_files_route(request: Request):
    """
    TASK-263: Enroll owner voice from existing local WAV file paths.

    This endpoint accepts file paths only. It never accepts audio bytes,
    base64 audio, transcripts, waveforms, or embedding vectors from the
    renderer. It delegates embedding extraction to the .venv-funasr enrollment
    sidecar and stores only the final centroid in backend-owned storage.
    """
    try:
        body = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid json body") from exc
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="request body must be an object")
    try:
        validate_owner_voice_gate_enroll_fields(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    paths = body.get("paths")
    if not isinstance(paths, list) or not all(isinstance(path, str) for path in paths):
        raise HTTPException(status_code=400, detail="paths must be a list of strings")
    threshold = body.get("threshold", 0.65)
    safety_notice_accepted = bool(body.get("safetyNoticeAccepted", False))
    try:
        result = enroll_owner_voice_gate_from_files(
            paths=paths,
            threshold=threshold,
            safety_notice_accepted=safety_notice_accepted,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        _logger.warning("TASK-263: owner voice enrollment failed: %s", type(exc).__name__)
        raise HTTPException(status_code=503, detail="owner voice enrollment unavailable") from exc
    return result


@router.post("/owner-voice-gate/verify-files")
async def owner_voice_gate_verify_files_route(request: Request):
    """
    TASK-265: Verify existing WAV files against the stored owner voice centroid.

    Accepts file paths only. Never accepts audio bytes, base64 audio,
    transcripts, waveforms, or embedding vectors from the renderer. Delegates
    embedding extraction to the .venv-funasr verification sidecar and compares
    candidate embeddings against the stored centroid only.

    Safety boundaries (TASK-265):
    - No microphone access.
    - No raw audio persistence.
    - No candidate embedding persistence.
    - Stored centroid vector never appears in the response.
    - No runtime wiring to Conversation Mode, STT pipeline, or chat endpoint.
    """
    try:
        body = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid json body") from exc
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="request body must be an object")
    try:
        validate_owner_voice_gate_verify_fields(body)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    paths = body.get("paths")
    if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
        raise HTTPException(status_code=400, detail="paths must be a list of strings")
    threshold = body.get("threshold")
    if threshold is not None and not isinstance(threshold, (int, float)):
        raise HTTPException(status_code=400, detail="threshold must be a number")
    try:
        result = verify_owner_voice_gate_from_files(paths=paths, threshold=threshold)
    except Exception as exc:  # noqa: BLE001
        _logger.warning("TASK-265: owner voice verification failed: %s", type(exc).__name__)
        raise HTTPException(status_code=503, detail="owner voice verification unavailable") from exc
    return result


@router.get("/provider/health")
def provider_health_check():
    """
    TASK-197: Narrow local provider liveness check for Full App startup.

    For Ollama (when real_provider_enabled=True): performs a single
    GET /api/tags to confirm the local server is reachable.  Does NOT load
    a model, does NOT call /api/chat, does NOT write any data.

    Returns:
      provider      — configured provider name
      ollama_reachable — True/False for Ollama; null for non-Ollama providers
      status        — "ok" | "unavailable" | "not_applicable"
    """
    settings = get_provider_settings()
    provider = settings.get("provider", "mock")
    real_enabled = bool(settings.get("real_provider_enabled", False))

    if provider != "ollama" or not real_enabled:
        return {
            "provider": provider,
            "ollama_reachable": None,
            "status": "not_applicable",
        }

    reachable = check_ollama_server_liveness()
    return {
        "provider": "ollama",
        "ollama_reachable": reachable,
        "status": "ok" if reachable else "unavailable",
    }


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    """
    Mock chat endpoint.

    The route adapts the API request/response, reads internal local state for
    mock phrasing, optionally builds approved memory context (feature-flagged),
    stores the turn, and updates state afterward.

    Response schema is always: reply / mood / source
    Memory content is never returned to the caller.

    TASK-020: MEMORY_INJECTION_ENABLED (default False) gates memory context
    building and audit log creation. When disabled, behaviour is identical to
    TASK-019 and earlier. When enabled, the approved context is built and an
    audit row is written, but the formatted context is not yet passed to the
    mock reply generator (no real LLM connected yet).

    TASK-023: Two-layer safety model. Approved memory context is used only when
    BOTH the backend global gate (MEMORY_INJECTION_ENABLED=true) AND the
    per-request toggle (request.use_memory=true) are true.  Either gate being
    False means no injection and no audit row.
    """
    mode = normalize_chat_mode(request.mode)
    state_context = get_chat_state_context(session)

    # ?? Two-layer memory context gate (TASK-023) ???????????????????????????
    # Layer 1 ??backend global gate: MEMORY_INJECTION_ENABLED env var (default False)
    # Layer 2 ??per-request toggle:  request.use_memory (default False)
    #
    # Only when BOTH are True may /chat build approved memory context and
    # write a MemoryInjectionAudit row.  Either gate being False means no
    # memory injection and no audit row ??identical to pre-TASK-020 behaviour.
    #
    # Memory content is NEVER placed in the response returned to the caller.
    memory_enabled = is_memory_injection_enabled()
    memory_requested = request.use_memory is True
    should_use_memory = memory_enabled and memory_requested
    formatted_context: str | None = None

    if should_use_memory:
        # Obtain conversation_id before store_chat_turn so the audit row can
        # reference the same default conversation.
        conversation = get_or_create_default_conversation(session)
        conversation_id: int | None = conversation.id

        selected_records = build_approved_memory_context_records(session)
        selected_ids = [record.id for record in selected_records if record.id is not None]
        entries = [record.content.strip() for record in selected_records]
        formatted_context = format_approved_memory_context(entries)

        # exclusion_summary is not yet computed by the builder ??tracked in
        # TASKS.md TASK-020 implementation notes for follow-up.
        create_memory_injection_audit(
            session=session,
            conversation_id=conversation_id,
            selected_memory_ids=selected_ids,
            total_context_chars=len(formatted_context),
            feature_flag_enabled=True,
            exclusion_summary=None,
        )
        # NOTE: formatted_context is safe-delimited approved memory context.
        # It is passed to chat_service only; it is never returned to clients.

    response_data = generate_chat_reply(
        request.message,
        request.mode,
        state_context,
        memory_context=formatted_context,
        include_usage_metadata=True,
    )
    usage_metadata = response_data.pop("_usage", {})

    # ?? Usage meter recording (TASK-050) ??????????????????????????????????
    # Record only safe aggregate metadata. Raw message text, prompt text,
    # memory context text, provider response body, and API key are NEVER
    # stored. Only integer token-length estimates and safe identifiers.
    _source = response_data["source"]
    record_usage(UsageRecord(
        source=_source,
        provider=usage_metadata.get("provider"),
        model=usage_metadata.get("model"),
        estimated_input_tokens=estimate_text_tokens(request.message),
        estimated_output_tokens=estimate_text_tokens(response_data["reply"]),
        fallback_used=bool(usage_metadata.get("fallback_used")),
        memory_used=should_use_memory,
        error_category=usage_metadata.get("error_category"),
    ))

    store_chat_turn(
        session=session,
        user_message=request.message,
        assistant_reply=response_data["reply"],
        mode=mode,
        mood=response_data["mood"],
        source=response_data["source"],
    )
    update_state_after_chat_turn(
        session=session,
        mood=response_data["mood"],
        mode=mode,
    )
    return ChatResponse(**response_data)


@router.get("/provider/settings", response_model=ProviderSettingsResponse)
def get_provider_settings_route() -> ProviderSettingsResponse:
    """
    Return safe non-secret provider settings and aggregate usage metadata.

    This endpoint never reads or returns an API key.
    """
    return ProviderSettingsResponse(**get_provider_settings())


@router.patch("/provider/settings", response_model=ProviderSettingsResponse)
async def update_provider_settings_route(
    request: Request,
) -> ProviderSettingsResponse:
    """
    Update non-secret provider settings only.

    API key fields are not part of the schema and extra fields are rejected by
    Pydantic before this handler runs.
    """
    try:
        body = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid json body") from exc
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="request body must be an object")

    allowed_fields = set(ProviderSettingsUpdateRequest.model_fields)
    unsupported_fields = set(body) - allowed_fields
    if unsupported_fields:
        raise HTTPException(status_code=400, detail="unsupported setting field")

    try:
        update_request = ProviderSettingsUpdateRequest(**body)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail="invalid provider settings") from exc
    # Preserve partial PATCH semantics: fields omitted by the caller must not be
    # converted into explicit None values that can later overwrite persisted
    # settings.
    update = ProviderSettingsUpdate(**update_request.model_dump(exclude_unset=True))
    try:
        settings = update_provider_settings(update)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ProviderSettingsResponse(**settings)


@router.post(
    "/provider/settings/key",
    response_model=KeyStatusResponse,
)
async def save_provider_key_route(request: Request) -> KeyStatusResponse:
    """
    Save a provider API key through the key storage abstraction.

    The key is write-only: never returned, logged, or stored in SQLite.
    """
    try:
        body = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid json body") from exc
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="request body must be an object")

    allowed_fields = set(KeySaveRequest.model_fields)
    unsupported_fields = set(body) - allowed_fields
    if unsupported_fields:
        raise HTTPException(status_code=400, detail="unsupported key field")

    try:
        key_request = KeySaveRequest(**body)
        result = save_provider_api_key(
            provider=key_request.provider,
            api_key=key_request.api_key,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail="invalid key settings") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ProviderKeyStorageError as exc:
        raise HTTPException(
            status_code=503,
            detail="secure key storage is unavailable",
        ) from exc

    return KeyStatusResponse(**result)


@router.delete(
    "/provider/settings/key",
    response_model=KeyStatusResponse,
)
def clear_provider_key_route(provider: str = "anthropic") -> KeyStatusResponse:
    """
    Clear a provider API key through the key storage abstraction.

    The operation is idempotent when storage is available.
    """
    try:
        result = clear_provider_api_key(provider)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ProviderKeyStorageError as exc:
        raise HTTPException(
            status_code=503,
            detail="secure key storage is unavailable",
        ) from exc
    return KeyStatusResponse(**result)


@router.post(
    "/provider/settings/test",
    response_model=ProviderTestConnectionResponse,
)
async def test_provider_connection_route(
    request: Request,
) -> ProviderTestConnectionResponse:
    """
    Run one safe provider Test Connection request.

    TASK-059 keeps this mocked-provider only. Runtime default runner does not
    call external providers. No API key, raw prompt, or raw provider body is
    returned to the frontend.
    """
    try:
        body = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid json body") from exc
    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="request body must be an object")

    allowed_fields = set(ProviderTestConnectionRequest.model_fields)
    unsupported_fields = set(body) - allowed_fields
    if unsupported_fields:
        raise HTTPException(status_code=400, detail="unsupported test field")

    try:
        test_request = ProviderTestConnectionRequest(**body)
        result = run_provider_test_connection(
            provider=test_request.provider,
            model=test_request.model,
            explicit_cost_ack=test_request.explicit_cost_ack,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail="invalid test settings") from exc
    except ProviderTestConnectionRequestError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.category) from exc

    return ProviderTestConnectionResponse(**result)


@router.post("/memory", response_model=MemoryResponse)
def create_memory_route(
    request: MemoryCreateRequest,
    session: Session = Depends(get_session),
) -> MemoryResponse:
    """
    Create an explicit local memory record.

    This endpoint is manual-only. It does not perform extraction, retrieval, or
    connect memory to chat responses.
    """
    try:
        memory = create_memory(
            session=session,
            memory_type=request.memory_type,
            content=request.content,
            importance=request.importance,
            confidence=request.confidence,
            source=request.source,
            source_message_id=request.source_message_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MemoryResponse.model_validate(memory)


@router.get("/memory", response_model=list[MemoryResponse])
def list_memory_route(session: Session = Depends(get_session)) -> list[MemoryResponse]:
    """
    List active local memory records.

    This is a plain list endpoint, not semantic retrieval.
    """
    return [
        MemoryResponse.model_validate(memory)
        for memory in list_active_memories(session)
    ]


@router.get("/memory/context-preview", response_model=MemoryContextPreviewResponse)
def memory_context_preview_route(
    session: Session = Depends(get_session),
) -> MemoryContextPreviewResponse:
    """
    Preview active memories as deterministic context text.

    This does not perform semantic retrieval and is not used by /chat.
    """
    preview = build_memory_context_preview(session)
    return MemoryContextPreviewResponse(
        memories=[
            MemoryResponse.model_validate(memory)
            for memory in preview["memories"]
        ],
        context_text=preview["context_text"],
        count=preview["count"],
        source=preview["source"],
    )


@router.get("/memory/audit", response_model=MemoryInjectionAuditListResponse)
def list_audit_route(
    limit: int = 20,
    offset: int = 0,
    session: Session = Depends(get_session),
) -> MemoryInjectionAuditListResponse:
    """
    Read-only audit inspection endpoint.

    Returns safe metadata about past memory injection events: which memory IDs
    were selected, how many, total context chars, and flag state.

    Safety rules:
    - This endpoint is read-only. It does not create rows or modify any table.
    - Raw memory content is never included in any response field.
    - Prompt text and approved memory context text are never returned.
    - selected_memory_ids is a list of integer IDs only.

    TASK-026: supports limit (default 20, max 100) and offset (default 0).
    Results are sorted newest first (id descending).
    """
    norm_limit, norm_offset = normalize_audit_pagination(limit, offset)
    rows = list_memory_injection_audits_paginated(
        session, limit=norm_limit, offset=norm_offset
    )
    items = [
        MemoryInjectionAuditResponse(
            id=row.id,
            created_at=row.created_at,
            conversation_id=row.conversation_id,
            selected_memory_ids=parse_memory_ids_json(row.selected_memory_ids_json),
            selected_count=row.selected_count,
            total_context_chars=row.total_context_chars,
            feature_flag_enabled=row.feature_flag_enabled,
            exclusion_summary=parse_exclusion_summary_json(row.exclusion_summary_json),
        )
        for row in rows
    ]
    return MemoryInjectionAuditListResponse(
        items=items,
        count=len(items),
        limit=norm_limit,
        offset=norm_offset,
    )


@router.delete("/memory/{memory_id}", response_model=MemoryResponse)
def deactivate_memory_route(
    memory_id: int,
    session: Session = Depends(get_session),
) -> MemoryResponse:
    """
    Deactivate a memory record without deleting the database row.
    """
    memory = deactivate_memory(session, memory_id)
    if memory is None:
        raise HTTPException(status_code=404, detail="memory record not found")
    return MemoryResponse.model_validate(memory)
