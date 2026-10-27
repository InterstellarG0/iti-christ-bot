# Christ Bot - Privacy Model, Phase 1

Stated honestly, and matched to what is actually built.

## What happens to your words

- Your conversation is kept in memory only, for one session.
- Nothing is written to a file by `app.py` or `engine.py`.
- No account is required. No analytics, no tracking, no streaks.
- Restarting the program, or using `/reset` in the CLI, clears the session.
- In the web UI, the conversation is kept in server memory only while
  your browser session is active, keyed by a random session id stored
  in your browser's local storage. Restarting the server clears it.

## What this prototype does NOT do

- It does not store conversations on disk.
- It does not encrypt stored conversations, because there are none.
- It does not delete on a schedule, because there is nothing stored
  to delete.
- It is not yet an offline app. The CLI and the local web UI run on
  your machine, but a full offline model, offline packaging, and
  offline distribution are future work, not claims made here.
- It does not send your conversation to a language-model API. There is
  no model call in this version.

## If storage is added later

Any future version that adds persistent memory, accounts, or a remote
model must update this document first, and must only claim the privacy
properties that version actually implements. User controls for memory
would be required before persistent memory ships.

## Crisis conversations

Crisis detection runs in memory, in the same session, for the sole
purpose of redirecting to real-world help in that moment. It does not
create a record, a report, or a stored flag.
