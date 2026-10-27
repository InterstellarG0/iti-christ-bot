# Christ Bot - Architecture and Data Flow (Phase 1)

## Components

- `app.py` - entry point. CLI loop, scripted demo, passage list, and a
  minimal web server built on Python's standard `http.server`. No
  framework, no database, no external service.
- `engine.py` - the product rules. Topic detection, listening-first
  flow, Scripture retrieval, interpretation separation, Sacred Pause,
  crisis override, identity guard, solitude safeguard, and disagreement
  handling. All deterministic.
- `scripture/corpus.json` - the only source of quoted Scripture.
- `web/index.html` - a single page that calls `/api/chat` and renders
  sections with their labels intact. It adds no engagement mechanics.
- `system_prompt.md` - the prompt for a future model adapter, kept
  behind the same guardrails. It is not executed by this prototype.

## Data flow

```
User input (CLI or web)
  -> app.py (no file write, no network call except the local web UI)
  -> engine.respond(session, text)
       1. Commands (/help, /privacy, /pause, /reset, and others)
       2. Crisis check (overrides everything else)
       3. Identity check (never claim divinity)
       4. User-supplied verse (labeled as not retrieved)
       5. Explicit passage request (retrieval only, or honest failure)
       6. Listening-first rule (first turn: reflect, do not quote)
       7. Topic turn (reflect, retrieve, separate interpretation)
       8. Disagreement, science/AI, and solitude safeguards
       9. Generic reflective turn (listen, ask, do not sermonize)
  -> Response with labeled sections
  -> Display only. Nothing is persisted.
```

## Session state

A `Session` holds only: turn count, last topic, last reflection,
whether Scripture was offered, whether a mental-health care note was
given, and the in-memory history of user messages for the current
session. `reset()` clears all of it. Process exit clears all of it.

## What is deliberately absent

- No language-model call, so no parametric Scripture generation.
- No database, file log, or analytics.
- No authentication, because there is no stored account to protect.
- No background job, token, or social feature.

## Future adapter rule

If a language model is added later, it must sit behind `engine.py`:
the engine must still own crisis detection, Scripture retrieval,
Sacred Pause, and the text/interpretation separation, and must reject
any model output that violates a safeguard in `system_prompt.md`.
A model must never be allowed to quote Scripture directly.
