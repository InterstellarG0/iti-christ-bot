# Christ Bot - Foundation Decision (2026-10-26)

Decision by Anthony: the Ethiopian Orthodox Bible he found is the
foundation of the app, with King James infused in it, because
chronologically the Ethiopian Orthodox edition is older.

## What "older" means, stated precisely

The lineage is older, not the PDF itself.

- The Septuagint, the Greek translation behind much of this tradition,
  dates to roughly the 3rd to 2nd centuries BC.
- The Ge'ez translation used by the Ethiopian church is traditionally
  dated to the Aksumite period, centuries before the King James Version.
- The King James Version was published in 1611.
- The PDF Anthony found is a modern English compilation in that
  tradition. It is not an ancient manuscript, and it must never be
  presented as one.

In the app, the source label will therefore read, in full, as a modern
English Ethiopian Orthodox compilation rooted in the Septuagint and
Ge'ez tradition, not simply as "the ancient Ethiopian Bible".

## Dual-edition model: foundation plus infusion, never a blend

"Infused" does not mean merging wordings into a single hybrid text.
That would break the Scripture Integrity Protocol, because the result
would be a text no edition actually contains.

The model is:

1. **Primary text: Ethiopian Orthodox edition.** Shown first when a
   passage exists in it. This is the foundation.
2. **Parallel text: King James Version.** Shown in a separate, labeled
   block only when the same book and reference exist in the 66-book
   KJV canon. It is a parallel, not a correction and not a merge.
3. **Canon label on every passage.** One of:
   - `shared`: in both the Ethiopian canon and the 66-book KJV canon.
   - `deuterocanonical`: in Orthodox canons, not in the 66-book canon.
   - `ethiopian-only`: in the Ethiopian canon, for example Enoch,
     Jubilees, and Meqabyan I to III, and not in the Protestant or
     Catholic canons in that form.
4. **No silent substitution.** If a passage has no KJV parallel, the
   app says so. If a passage has no Ethiopian text in the corpus yet,
   the app says so. It never fills a gap from memory.

## Why this fits the handoff

The handoff requires Scripture to be presented accurately, the
translation to be named, text to be distinguished from interpretation,
and no single tradition to be presented as universally accepted when
legitimate disagreement exists. A dual-edition display does that work
in the open: the user sees which tradition a passage belongs to, and
sees where traditions agree and where they do not.

## Extraction status

The PDF is extractable. A full text extraction is 78,324 lines,
about 5.7 MB, with book headings that are machine detectable. Genesis
is clean modern English with inline verse numbers. Enoch and Jubilees
use older scholarly translations with editorial brackets and notes,
so they need slower, manual checking and cannot be bulk parsed the
same way as Genesis.

Pilot file: `scripture/ethiopian_pilot.json`. It demonstrates the
model with four passages only. At v1.2 that model is now wired into
`engine.py`: the full Ethiopian corpus is the primary retrieval source,
with a KJV parallel section and a canon label on every passage.
`python3 app.py --verses` reports 40,415 lookup keys, which is 40,236
unique verses plus 179 alias keys for Susanna, Bel, and the Letter of
Jeremiah chapter-1 forms.

## Verification rule for the full build

Before any passage from the PDF is treated as verified, it must be
spot checked against the extracted PDF text, and passages with OCR
errors, broken verse numbers, or editorial brackets must be either
cleaned with a note or left out. "Could not retrieve" remains safer
than a wrong quotation.
