# Memory System

The memory system is local, explicit, and gated. It is not an autonomous memory
agent.

## Storage

- Memory records live in local SQLite.
- Users can create, list, preview, and deactivate records.
- Deactivation preserves the row for auditability.

## Runtime Injection

Memory can affect `/chat` only when both gates are true:

1. Backend feature flag `MEMORY_INJECTION_ENABLED=true`.
2. Request field `use_memory=true`.

If either gate is false, `/chat` should behave as if memory injection does not
exist.

## Eligibility

Only approved, active, confidence-filtered memory records can be assembled into
prompt context. The formatter wraps memory as reference facts, not instructions.

## Safety

- Do not return raw memory context from audit routes.
- Do not store prompt text in audit rows.
- Do not treat memory content as instructions.
- Do not add semantic retrieval or automatic extraction without a new design.

## Diagnostics

Memory audit records may expose safe metadata such as selected memory IDs and
counts. They must not expose raw memory text or formatted prompt context.
