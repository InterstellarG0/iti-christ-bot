# Scripture corpus, v1.2

## Foundation corpus

`ethiopian_corpus.json` is the foundation: 88 books, 40,236 unique
verses, extracted from the Ethiopian Orthodox Bible PDF Anthony
supplied (`ethiopianorthodoxbible_0_wj1b.pdf`, 2,151 pages).

Extraction, reproducible, standard library only:

```
pdftotext -layout ethiopianorthodoxbible_0_wj1b.pdf ethiopian.txt
python3 tools/extract_ethiopian.py ethiopian.txt scripture/ethiopian_corpus.json
```

The extractor uses sequential chapter and verse parsing, with
handling for chapter numbers that appear inline, verse numbers
followed by quotes, capitals, parentheses, or lowercase continuations,
unnumbered verse-1 headings, and Psalms book divisions. It does not
force books that do not follow that pattern into verse form, and it
stops at the Daniel Greek-portions repeat and at the Glossary, so
those sections do not contaminate Daniel or 1 Clement.

Validation, standard verse counts matched exactly for: Genesis
50 chapters / 1,533 verses, Exodus 1,213, Psalms 150 / 2,461, Jeremiah
1,364, Ezekiel 1,273, Matthew 1,071, John 879, Romans 433, Leviticus
859, Job 1,070, and others.

Special numbering, as in the PDF: Susanna is Daniel 13, Bel and the
Dragon is Daniel 14, the Song of the Three Children is Daniel 3:24-97,
and the Letter of Jeremiah is Baruch 6. The engine maps Susanna 1:1,
Bel 1:1, and Letter of Jeremiah 1:1 to those corpus chapters, so a
reader asking in single-chapter form still gets the passage.

Canon labels in the corpus: shared, deuterocanonical, or
ethiopian-only. See `docs/FOUNDATION.md` for what each label means.

Quality notes, as in the PDF itself: shared books are clean modern
English. Enoch and Jubilees use older scholarly translations with
editorial brackets, retained not cleaned. Meqabyan I to III use a
rough English rendering, with broken grammar in places, presented
as-is and labeled Ethiopian-only. Spot-check any passage before
academic citation.

## KJV parallel corpus

`corpus.json` is the King James parallel only: 53 passages, public
domain, with topic tags. The engine copies those topic tags onto the
matching Ethiopian verses, so topic retrieval works with Ethiopian
wording. A shared passage with no KJV parallel loaded yet says so
plainly; a missing parallel does not mean the passage is not in the
KJV canon.

## Pilot file

`ethiopian_pilot.json` was the 4-passage pilot that proved the
dual-edition model before the full extraction. It is kept for
reference. The live engine uses `ethiopian_corpus.json`, not the pilot.

## Integrity rule, unchanged

The engine never generates Scripture. If a reference is not in these
files, the engine must say "could not retrieve" and must not quote it
from memory. If you are unsure about a passage, leave it out: the
engine's "could not retrieve" answer is safer than a wrong quotation.
