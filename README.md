# Christ Bot v1.1 - Prototype

**Interstellar Religious Initiative (IRI)**
Flagship of Interstellar Technologies Initiative, LLC (ITI)

**Status:** Phase 2 prototype, pre-development product. This is a working
first version, not a finished product, and not a replacement for clergy,
professional care, or your own conscience.

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

- Scripture is quoted only if it is found in `scripture/corpus.json`.
  If a passage is not there, the engine says so and does not invent it.
  It can work with a passage you paste, labeled clearly as
  user-supplied text, not as retrieved Scripture.
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
    corpus.json             # starter KJV corpus, retrieved only
    README.md               # how to add a fuller verified Bible
  web/
    index.html              # minimal web UI
  tests/
    test_acceptance.py      # 11 handoff acceptance tests + safeguards
  docs/
    handoff_v1.1.md         # binding specification used for this build
    ARCHITECTURE.md         # architecture and data flow
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
3. **A full Bible was not supplied.** The prototype ships a starter
   corpus of 53 KJV passages and a documented path to replace it
   with a fuller verified text. It refuses to fill gaps from memory.
4. **No model was specified.** The prototype ships without a model
   dependency, so it cannot hallucinate Scripture or sermonize. The
   system prompt is preserved for a future adapter, behind the same
   guardrails.

## Known limitations

- The starter corpus is small. Many legitimate passages will return
  "could not retrieve" until a fuller verified Bible is added.
- KJV punctuation follows common editions and may vary slightly by
  printing. Verify against a printed KJV for academic citation.
- The web UI is a local demo. It is not hardened for public deployment,
  authentication, or multi-user use.
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
