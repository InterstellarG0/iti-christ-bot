# Christ Bot v1.2.8 - Prototype

**v1.2.8, 2026-10-29:** Send freeze fix, no topic, passage, wording, or feature change. On 2026-10-28 the hosted link froze when trying to send on a phone. Cause, in the static phone/hosted engine: every reply rescanned all 40,236 verses, sorting every chapter, on the main thread, with no visible sending state and no guard against repeat taps, so Send looked frozen. Fix: a topic index is built once at startup, in exactly the same corpus order the old scan used, so each reply is now a single lookup and returns the same first passage as before. Send shows Listening, is disabled while a reply is being prepared, ignores repeat taps, and always re-enables, even if preparing or rendering a reply throws. Send starts disabled in the HTML and is enabled only once the handlers are wired, so taps during the initial load cannot silently do nothing. The same index is built once by the Python engine in `load_corpus()`, with a scan fallback for hand-built corpora. The local server UI in `web/index.html` is the only build with a network request, and it now has a 30 second request timeout, the same busy guard, a protected scroll, and the typed message is restored if the request fails. Two claims from the forwarded GPT conversation did not match the hosted static build and were not treated as defects there: it has no `/api/chat` endpoint and no network request, and its scroll call was already wrapped in try/catch. Remaining limit: the single-file phone/hosted build still parses the 5.7 MB corpus synchronously at startup, which was not restructured; Send staying disabled until wiring is the mitigation for taps during that load. Tests: all 30 Python acceptance tests pass, including new test 30 proving the index returns the same first verse as a full scan for every topic, and Node checks on the built phone file prove 49 topics with 0 mismatches against the old scan, 10,000 indexed lookups in 0 ms against 315 ms for 20 old scans, and guilt, money, evidence, John 3:16, and crisis conversations still behave as before. Real phone confirmation by Anthony is still needed; no build is called fixed on a phone until he tests Send there. The hosted public link still serves v1.2.7 until it is shared again, and the hosted v1.2.8 build was verified separately in a live probe.

**v1.2.7, 2026-10-26:** brand colors and Send fixes, phone only, no topic or passage change. Brand palette approved by Anthony: cream #f7f5ef background, deep green #2f5d50 for buttons and title, gold #c9a86a as the brand accent (gold rule under the title, gold Scripture border, gold on button press), dark slate #1d2733 text, crisis red kept only for crisis. Enter now sends in the browser: Enter without Shift sends the message, Shift plus Enter still inserts a newline. Send is more robust: scroll errors no longer kill a reply, a reply error shows a plain fallback message instead of nothing, and if the main chat script fails before wiring Send, a separate fallback script stops the form from reloading the page and shows a diagnosis box telling the user to open the file in Chrome on Android or Safari on iPhone, not in a file preview.

**v1.2.6, 2026-10-26:** phone-only fix, no topic or passage change. The welcome box and version line were previously added by JavaScript only, so on a phone viewer that blocks JavaScript the chat area looked empty and no version showed, while desktop worked. Both are now static HTML in the file itself, so the welcome box and "Phone version v1.2.6" show even before any script runs, and a noscript note tells the user to open the file in Chrome on Android or Safari on iPhone, not in a file preview, if Send does not work. The script no longer adds a second welcome box.

**v1.2.5, 2026-10-26:** adds an evidence topic (50 topics total), built from the 0xSero all-historical-evidence-of-jesus-christ archive, with permission handled by linking and summarizing, not copying. When someone asks about historical evidence, did Jesus exist, or proof outside the Bible, the bot gives a labeled summary (not Scripture, not a passage, not proof on its own), names Josephus, Tacitus, Suetonius, Lucian, Mara bar Serapion, the Talmud, Roman legal documents, church fathers, and archaeology, flags disputed cases (James ossuary, Nazareth inscription provenance, shroud dating) as disputed, and links to the searchable reader and repo. No Ethiopian passage is invented for this topic, and no dossier text is copied into the corpus. Mobile conversation box is larger: on screens up to 600px wide, message text is 19px with 18px padding and taller input (72px), while desktop stays at 17px.

**v1.2.4, 2026-10-26:** adds 30 topics, for a total of 49. All 25 ready topics from the 53 passage King James set are now detected (anger, peace, trust, wisdom, patience, humility, faith, truth, community, friendship, mercy, comfort, discernment, listening, character, help, freedom, future, mission, dignity, solitude, time, astronomy, origins, life), plus five manually mapped groups verified against the Ethiopian text: guilt and shame to 1 John 1:9, envy and jealousy to Proverbs 14:30, pride to James 4:6, addiction and compulsive behaviors to Romans 7:15, and work, money, and financial stress to Matthew 6:25. Character, help, and mission are mapped to single verses (Galatians 5:22, Psalm 121:1, Matthew 28:19) because their King James entries are ranges. Context switching is disciplined by topic order: existing topics keep priority, generic topics (help, life, money) are last, so a specific concern wins over a generic word in the same sentence, and a new turn replaces last_topic instead of recycling an old passage. The solitude safeguard ("you are my only friend") now runs before topic handling, so the new friendship topic cannot swallow it. Discernment and astronomy/origins were removed from the science and decision phrase lists, so they get their own passages (Psalm 119:105, Psalm 19:1, Genesis 1:1). All 28 acceptance tests pass, including new tests 23 to 28 for all new topics, multi-topic messages, context changes, unknown topics, passage requests, Sacred Pause, and crisis handling.

**v1.2.3, 2026-10-26:** adds a lust topic mapped to 1 Corinthians 10:13, with a non-shaming interpretation, and fixes a stale-topic bug: "find a passage about X" for an unknown X no longer silently reuses an earlier topic's passage, it says so plainly instead.

**v1.2.2, 2026-10-26:** same Ethiopian foundation and corpus as v1.2, plus the v1.2.1 topic fix, plus a verse-request fix. "Show me a verse about this", "find a passage please", and "to look at a retrieved passage together" now actually retrieve a passage for the topic already discussed, instead of looping back to the generic question. Also adds a complaining topic mapped to Philippians 2:14.

**v1.2.1, 2026-10-26:** same Ethiopian foundation and corpus as v1.2, with three fixes and one addition. Topic matching now uses whole words, so "ai" no longer matches "said", "faith", or "again". The phone version is included in `phone/`. `system_prompt.md` is corrected to v1.2.1 with the Ethiopian foundation, and a `.gitignore` keeps `__pycache__` out of the repo.

**Interstellar Religious Initiative (IRI)**
Flagship of Interstellar Technologies Initiative, LLC (ITI)

**Status:** Phase 2 prototype, pre-development product. This is a working
first version, not a finished product, and not a replacement for clergy,
professional care, or your own conscience.

**Foundation, decided 2026-10-26:** Ethiopian Orthodox Bible, modern
English compilation rooted in the Septuagint and Ge'ez tradition, with
King James shown only as a separate parallel, never merged. The PDF
itself is a modern compilation, not an ancient manuscript.

## What this is

Christ Bot is a scripture-centered reflection and discernment companion.
Guiding principle: Ancient Wisdom, Modern Discernment.

It helps users examine the relationship between God, humanity, science,
and increasingly capable machines. It does not claim divine authority,
know God's will, or replace faith, conscience, or human relationships.
Success is honesty, clarity, and usefulness, not controlling belief.

## Run it

No install, no account, no API key. Python 3.10 or later, standard
library only.

CLI:
```
python3 app.py
```

Minimal web UI (same engine, same safeguards):
```
python3 app.py --web
```
Then open http://127.0.0.1:8000

Scripted demo, no typing needed:
```
python3 app.py --demo
```

List every passage this build can actually retrieve:
```
python3 app.py --verses
```

Run the acceptance tests:
```
python3 -m unittest discover -s tests -v
```

## How it works, honestly

This Phase 1 engine is deterministic, not a language model. That is a
deliberate safeguard, not a missing feature:

- Scripture is quoted only if it is found in `scripture/ethiopian_corpus.json`
  (foundation, 40,236 unique verses in 88 books, extracted from the PDF
  Anthony supplied) or, for the KJV parallel, in `scripture/corpus.json`
  (53 passages). If a passage is not there, the engine says so and does
  not invent it.
  It can work with a passage you paste, labeled clearly as
  user-supplied text, not as retrieved Scripture.
- When Scripture is offered, the Ethiopian text comes first, with a
  canon label (shared, deuterocanonical, or Ethiopian-only), then the
  King James parallel in a separate labeled section if one exists.
  Wordings are never merged. If a shared passage has no KJV parallel
  loaded yet, the engine says so, rather than implying it is not in
  the KJV canon.
- The first reply listens. It does not quote Scripture unless you asked
  for a specific passage or your question is explicitly about a text.
- When Scripture is offered, the text, the translation, and any
  interpretation are in separate, labeled sections.
- Sacred Pause is optional, with exactly three choices and no streaks,
  points, or pressure language.
- Crisis language stops reflective mode and gives a short, direct
  redirect to real-world help (988 in the US, Crisis Text Line 741741,
  911 for immediate danger).
- Conversation lives in memory only for one session. Restarting clears it.

`system_prompt.md` in this folder is the encoded prompt for any future
language-model adapter. If a model is ever added, it must go through
this engine's guardrails and must never bypass them.

## File structure

```
christbot/
  README.md
  PRIVACY.md
  system_prompt.md          # encoded principles + safeguards
  app.py                    # CLI + minimal web UI
  engine.py                 # conversation rules, safeguards, retrieval
  scripture/
    corpus.json             # KJV starter corpus, parallel only (53 passages)
    ethiopian_corpus.json   # Ethiopian foundation corpus (88 books, 40,236 verses)
    ethiopian_pilot.json    # 4-passage pilot that proved the dual-edition model
    README.md               # how the Ethiopian corpus was extracted and validated
  tools/
    extract_ethiopian.py    # reproducible PDF extraction script, stdlib only
  web/
    index.html              # minimal web UI
  tests/
    test_acceptance.py      # 11 handoff acceptance tests + safeguards + dual-edition tests
  docs/
    handoff_v1.1.md         # binding specification used for this build
    ARCHITECTURE.md         # architecture and data flow
    FOUNDATION.md           # Ethiopian foundation decision and dual-edition model
```

## What is immediate, and what is future

Immediate in this version: listening-first responses, text and
interpretation separation, Sacred Pause, crisis redirect, honest
privacy doc, run instructions, and acceptance tests.

Future, deliberately not in this version: tokens, blockchain, social
features, complex or persistent memory, elaborate rituals, multi-
translation comparison, voice, a full offline model, and richer study
tools. Persistent memory, if added later, needs user controls and a
new privacy statement that matches what is actually built.

## Gaps found while building, and how they were handled

1. **The handoff did not name its five lenses.** The prototype defines
   them explicitly as product labels in `system_prompt.md` (Text;
   History and context; Interpretive traditions; Science and reason;
   Personal discernment), and the engine labels them as such, never as
   Scripture.
2. **Crisis jurisdiction was assumed US.** The prototype keeps 988 as
   the US default, adds Crisis Text Line and 911, and adds a local
   emergency number note for users outside the US. It does not claim
   to know the user's country.
3. **A full Bible was not supplied at v1.1.** At v1.2 the Ethiopian
   Orthodox PDF Anthony supplied was extracted with
   `tools/extract_ethiopian.py` into a verse-level corpus. Validation:
   Genesis 50 chapters / 1,533 verses, Exodus 1,213, Psalms 150 / 2,461,
   Jeremiah 1,364, Ezekiel 1,273, Matthew 1,071, and John 879 all match
   standard verse counts exactly. Susanna is stored as Daniel 13, Bel
   as Daniel 14, and the Song of the Three Children as Daniel 3:24-97,
   as in the PDF, with chapter-1 aliases for Susanna, Bel, and the
   Letter of Jeremiah. The Daniel Greek-portions repeat and the Glossary
   are excluded, so they do not contaminate Daniel or 1 Clement.
4. **No model was specified.** The prototype ships without a model
   dependency, so it cannot hallucinate Scripture or sermonize. The
   system prompt is preserved for a future adapter, behind the same
   guardrails.

## Known limitations

- The KJV parallel is still only 53 passages. A shared passage without
  a loaded parallel will say so, rather than showing a KJV text.
- Ethiopian text quality varies by book, as in the PDF itself. Shared
  books are clean modern English. Enoch and Jubilees use older scholarly
  translations with editorial brackets, which are retained, not cleaned
  silently. Meqabyan I to III use a rough English rendering in the PDF,
  with broken grammar in places, and are presented as-is, labeled
  Ethiopian-only, not polished. Spot-check any passage before academic
  citation, and treat "could not retrieve" as safer than a wrong quote.
- The web UI is a local demo. It is not hardened for public deployment,
  authentication, or multi-user use.
- The single-file phone/hosted build still parses the 5.7 MB corpus
  synchronously at startup, which was not restructured in v1.2.8.
  Send stays disabled until the chat script is wired, so taps during
  that load cannot silently do nothing, but the load itself still
  blocks the page briefly on a slow phone.
- This prototype does not diagnose, counsel, or provide pastoral care.
  It reflects, and it redirects to people and professionals when care
  is needed.

## Safeguards, in short

No divine claims. No fabricated revelation or Scripture. No threats of
divine punishment or spiritual shame. No treating disagreement as
spiritual deficiency. No justifying abuse, violence, or unlawful harm.
No diagnosis, and no framing mental illness as spiritual failure.
No encouraging isolation. No replacing clergy or professional care.
No treating the creator or model as beyond criticism. No invented
sources, quotations, or consensus. No privacy, deletion, or local
storage claims that are not technically true.
