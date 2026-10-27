# Christ Bot, phone version

Single file: `christbot-phone.html` (about 5.6 MB, 88 books, 40,236 Ethiopian verses, 53 King James parallels).

This is the same Phase 1 engine as the desktop Python version, rewritten in JavaScript so it runs in a phone browser with no server, no Python, no account, and no network call after download. It is deterministic and retrieval-only: a passage is quoted only if it is in the file, otherwise it says it could not retrieve it. It listens first, keeps Scripture separate from interpretation, offers the Sacred Pause with exactly the three choices, and overrides to 988, 741741, and 911 on crisis language. It never claims to be God, Jesus, a prophet, or a supernatural being, and it never diagnoses.

Foundation: Ethiopian Orthodox Bible, modern English compilation rooted in the Septuagint and Ge'ez tradition, not an ancient manuscript itself. King James is a separate parallel for shared passages only, never merged. Canon labels: shared, deuterocanonical, Ethiopian-only.

## How to open it

### iPhone (Safari)
1. Download `christbot-phone.html` to Files, for example via the Files app, AirDrop, or email to yourself.
2. In Files, tap the file. It opens in Safari and works.
3. Optional, to make it feel like an app: tap Share, then Add to Home Screen. It will still run from the saved file, offline, with no server.

### Android (Chrome)
1. Download `christbot-phone.html` to Downloads.
2. In Files or Chrome, tap the file to open it in Chrome.
3. Optional: tap the three dots, then Add to Home screen.

## Privacy, phone version

Your conversation lives only in that page, in memory. Closing or reloading the page, or using Clear this session, clears it. Nothing is sent anywhere, because there is no server to send it to. This page does not write a file, use an account, or call a language model.

## Differences from the desktop Python version

- No Python, no terminal, no local server needed.
- Chapter-1 aliases for Susanna, Bel, and Letter of Jeremiah are handled by mapping in code, not by extra lookup keys, so the count shown is 40,236 unique verses.
- Phone improvement: "Bel 1:1" is accepted as shorthand for "Bel and the Dragon 1:1".
- Everything else, including topic detection, interpretations, crisis handling, and the Sacred Pause, follows the desktop engine.
- Rebuild it after any corpus change with: `python3 tools/build_phone.py`

## Known limits

- The file is about 5.6 MB, so it takes a moment to download once, then it works offline.
- The King James parallel is still only 53 passages, so many shared passages show no parallel yet, just like v1.2.
- Ethiopian text quality varies by book, as in the PDF itself. Enoch, Jubilees, and Meqabyan are presented as-is and labeled Ethiopian-only. Spot-check any passage before academic citation.
- This is a local file, not a published app. It is not hardened for public hosting or multi-user use.
