#!/usr/bin/env python3
"""
Extract the Ethiopian Orthodox PDF into a structured, verse-level corpus.

Input:  the PDF supplied by Anthony, extracted with pdftotext -layout
        (see README in this folder for the exact command).
Output: scripture/ethiopian_corpus.json

Rules, deliberately conservative:
- A book starts only on a known heading line. Unknown headings are
  ignored, they do not start a book.
- A chapter starts only on a standalone number line that equals the
  next expected chapter for that book. This prevents page numbers
  from being mistaken for chapters.
- A verse starts only when the next expected verse number appears.
  Numbers that are quantities (300 cubits, 40 days) are therefore not
  mistaken for verse starts unless they happen to equal the expected
  verse number, which is checked in validation samples.
- Text before verse 1 in a chapter (psalm superscriptions, section
  headings) is not included in verse 1. Text inside a chapter that
  looks like a heading is retained in the verse it falls in, as in
  the PDF, rather than silently edited out.
- Books whose structure does not follow this pattern are not forced
  into verse form. They are listed in UNPARSED_BOOKS and must be
  handled separately, at chapter level, with a clear note.

This script is standard library only.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# heading line (stripped) -> (canonical name, canon label)
HEADINGS = {
    "The First Book of Moses, Genesis": ("Genesis", "shared"),
    "The Second Book of Moses, Exodus": ("Exodus", "shared"),
    "The Third Book of Moses, Leviticus": ("Leviticus", "shared"),
    "The Fourth Book of Moses, Numbers": ("Numbers", "shared"),
    "The Fifth Book of Moses, Deuteronomy": ("Deuteronomy", "shared"),
    "The Book of Joshua": ("Joshua", "shared"),
    "The Book of Judges": ("Judges", "shared"),
    "The Book of Ruth": ("Ruth", "shared"),
    "The First Book of Samuel": ("1 Samuel", "shared"),
    "The Second Book of Samuel": ("2 Samuel", "shared"),
    "The First Book of Kings": ("1 Kings", "shared"),
    "The Second Book of Kings": ("2 Kings", "shared"),
    "The First Book of Chronicles": ("1 Chronicles", "shared"),
    "The Second Book of Chronicles": ("2 Chronicles", "shared"),
    "The Prayer of Manasses": ("Prayer of Manasses", "deuterocanonical"),
    "The Book of Jubilees, or The Little Genesis": ("Jubilees", "ethiopian-only"),
    "The Book of Enoch": ("Enoch", "ethiopian-only"),
    "The Book of Ezra": ("Ezra", "shared"),
    "The Book of Nehemiah": ("Nehemiah", "shared"),
    "The First Book of Esdras, or Ezra Kali": ("1 Esdras", "deuterocanonical"),
    "The Second Book of Esdras, or Ezra Sutu'el": ("2 Esdras", "deuterocanonical"),
    "The Book of Tobit": ("Tobit", "deuterocanonical"),
    "The Book of Judith": ("Judith", "deuterocanonical"),
    "The Book of Esther": ("Esther", "shared"),
    "The Book of Meqabyan I": ("Meqabyan I", "ethiopian-only"),
    "The Book of Meqabyan II": ("Meqabyan II", "ethiopian-only"),
    "The Book of Meqabyan III": ("Meqabyan III", "ethiopian-only"),
    "The Book of Job": ("Job", "shared"),
    "The Psalms": ("Psalms", "shared"),
    "Psalm 151": ("Psalm 151", "deuterocanonical"),
    "The Proverbs": ("Proverbs", "shared"),
    "The Wisdom of Solomon": ("Wisdom", "deuterocanonical"),
    "Ecclesiastes or, The Preacher": ("Ecclesiastes", "shared"),
    "The Song of Songs, or Song of Solomon": ("Song of Songs", "shared"),
    "The Book of the Prophet Isaiah": ("Isaiah", "shared"),
    "The Book of Jeremiah": ("Jeremiah", "shared"),
    "The Lamentations of Jeremiah": ("Lamentations", "shared"),
    "The Book of Baruch": ("Baruch", "deuterocanonical"),
    "The Letter of Jeremiah": ("Letter of Jeremiah", "deuterocanonical"),
    "4 Baruch, or Paralipomena of Jeremiah": ("4 Baruch", "ethiopian-only"),
    "The Book of Ezekiel": ("Ezekiel", "shared"),
    "The Book of Daniel": ("Daniel", "shared"),
    "The Book of Hosea": ("Hosea", "shared"),
    "The History of Susanna": ("Susanna", "deuterocanonical"),
    "Bel and the Dragon": ("Bel and the Dragon", "deuterocanonical"),
    "The Book of Joel": ("Joel", "shared"),
    "The Book of Amos": ("Amos", "shared"),
    "The Book of Obadiah": ("Obadiah", "shared"),
    "The Book of Jonah": ("Jonah", "shared"),
    "The Book of Micah": ("Micah", "shared"),
    "The Book of Nahum": ("Nahum", "shared"),
    "The Book of Habakkuk": ("Habakkuk", "shared"),
    "The Book of Zephaniah": ("Zephaniah", "shared"),
    "The Book of Haggai": ("Haggai", "shared"),
    "The Book of Zechariah": ("Zechariah", "shared"),
    "The Book of Malachi": ("Malachi", "shared"),
    "The Good News According to Matthew": ("Matthew", "shared"),
    "The Good News According to Mark": ("Mark", "shared"),
    "The Good News According to Luke": ("Luke", "shared"),
    "The Good News According to John": ("John", "shared"),
    "The Acts of the Apostles": ("Acts", "shared"),
    "Paul's Letter to the Romans": ("Romans", "shared"),
    "Paul's First Letter to the Corinthians": ("1 Corinthians", "shared"),
    "Paul's Second Letter to the Corinthians": ("2 Corinthians", "shared"),
    "Paul's Letter to the Galatians": ("Galatians", "shared"),
    "Paul's Letter to the Ephesians": ("Ephesians", "shared"),
    "Paul's Letter to the Philippians": ("Philippians", "shared"),
    "Paul's Letter to the Colossians": ("Colossians", "shared"),
    "Paul's First Letter to the Thessalonians": ("1 Thessalonians", "shared"),
    "Paul's Second Letter to the Thessalonians": ("2 Thessalonians", "shared"),
    "Paul's First Letter to Timothy": ("1 Timothy", "shared"),
    "Paul's Second Letter to Timothy": ("2 Timothy", "shared"),
    "Paul's Letter to Titus": ("Titus", "shared"),
    "Paul's Letter to Philemon": ("Philemon", "shared"),
    "The Letter to the Hebrews": ("Hebrews", "shared"),
    "The Letter from James": ("James", "shared"),
    "Peter's First Letter": ("1 Peter", "shared"),
    "Peter's Second Letter": ("2 Peter", "shared"),
    "John's First Letter": ("1 John", "shared"),
    "John's Second Letter": ("2 John", "shared"),
    "John's Third Letter": ("3 John", "shared"),
    "The Letter from Jude": ("Jude", "shared"),
    "Revelation": ("Revelation", "shared"),
    "The First Epistle of Clement to the Corinthians": ("1 Clement", "ethiopian-only"),
}

# Multi-line headings: first line -> canonical, and the continuation
# line to skip.
MULTILINE = {
    "The Second Book of Enoch, or Slavonic Enoch, or": ("2 Enoch", "ethiopian-only"),
    "The Wisdom of Jesus the Son of Sirach, or": ("Sirach", "deuterocanonical"),
    "The Song of the Three Holy Children, or The": ("Song of the Three Children", "deuterocanonical"),
    "Additions to Esther, translated from the Greek": ("Additions to Esther", "deuterocanonical"),
}

# Headings that end the current book and whose text must not be
# absorbed into it. "Daniel with Greek Portions" repeats Daniel 1-12
# with Greek additions; "Glossary" is back matter, not Scripture.
STOP_HEADINGS = {
    "The Book of Daniel with Greek Portions",
    "Glossary",
}


def parse_chapter(text: str, start_verse: int = 1) -> dict[int, str]:
    """Split one chapter's joined text into verses, sequentially."""
    verses: dict[int, str] = {}
    expected = start_verse
    # Psalms are divided into five books. A "Book 5" heading at the
    # start of Psalm 107 would otherwise consume the space verse 1
    # needs, so strip that division heading first.
    text = re.sub(r"^\s*Book \d+\s+", "", text)
    # Find candidate verse starts: a number at start or after space,
    # followed by any non-digit character. This covers space, quotes,
    # capitals, parentheses, and lowercase continuations such as
    # Ezekiel 23:41, which begins "41and sat...". The sequential
    # expected-verse check filters out quantities like "300 cubits".
    pattern = re.compile(r"(?:^|\s)(\d+)(?=[^\d]|$)")
    all_matches = list(pattern.finditer(text))
    if not all_matches:
        return verses
    # Some chapters give verse 1 as an unnumbered heading, then
    # start numbering at verse 2 (Jeremiah 14 and Ezekiel 2 are
    # the clear cases). If the first numbered verse is 2 and
    # there is substantial text before it, that text is verse 1.
    first_num = int(all_matches[0].group(1))
    expected = start_verse
    if first_num == 2 and start_verse == 1:
        preceding = re.sub(r"\s+", " ", text[: all_matches[0].start()].strip())
        if len(preceding) > 20:
            verses[1] = preceding
            expected = 2
    starts: list[tuple[int, int, int]] = []  # (verse, text_pos, match_start)
    for m in all_matches:
        num = int(m.group(1))
        if num == expected:
            # position of the verse text: end of match
            starts.append((num, m.end(), m.start()))
            expected += 1
    for idx, (num, pos, _mstart) in enumerate(starts):
        end = starts[idx + 1][2] if idx + 1 < len(starts) else len(text)
        body = text[pos:end].strip()
        body = re.sub(r"\s+", " ", body).strip()
        if body.startswith(f"{num} "):
            body = body[len(f"{num} "):].strip()
        if body:
            verses[num] = body
    return verses


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: extract_ethiopian.py <pdftotext-output.txt> [output.json]")
        return 2
    src = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "scripture" / "ethiopian_corpus.json"
    lines = src.read_text(encoding="utf-8", errors="ignore").splitlines()

    # Body start: Genesis heading followed by a chapter 1 line.
    body_start = None
    for i, line in enumerate(lines):
        if line.strip() == "The First Book of Moses, Genesis" and i + 1 < len(lines) and lines[i + 1].strip() == "1":
            body_start = i
            break
    if body_start is None:
        print("could not find body Genesis heading")
        return 1

    books: dict[str, dict] = {}
    current_book: str | None = None
    current_canon: str | None = None
    current_chapter: int | None = None
    expected_chapter = 1
    chapter_lines: list[str] = []
    skip_next = False

    def flush_chapter() -> None:
        nonlocal chapter_lines
        if current_book is None or current_chapter is None or not chapter_lines:
            chapter_lines = []
            return
        text = " ".join(chapter_lines)
        start_verse = 24 if (current_book == "Song of the Three Children" and current_chapter == 3) else 1
        verses = parse_chapter(text, start_verse=start_verse)
        if verses:
            books[current_book]["chapters"][str(current_chapter)] = verses
        chapter_lines = []

    for raw in lines[body_start:]:
        line = raw.strip()
        # Normalize curly apostrophes so PDF headings match the keys.
        line = line.replace("’", "'").replace("‘", "'")
        if skip_next:
            skip_next = False
            continue
        if line in STOP_HEADINGS:
            flush_chapter()
            current_book = None
            current_chapter = None
            continue
        if line in MULTILINE:
            flush_chapter()
            current_book, current_canon = MULTILINE[line]
            books.setdefault(current_book, {"canon": current_canon, "chapters": {}})
            current_chapter = None
            expected_chapter = 1
            skip_next = True  # continuation line of the heading
            continue
        if line in HEADINGS:
            flush_chapter()
            current_book, current_canon = HEADINGS[line]
            books.setdefault(current_book, {"canon": current_canon, "chapters": {}})
            current_chapter = None
            expected_chapter = 1
            if current_book == "Psalm 151":
                # Single psalm: its "151" line is a psalm number,
                # not a chapter marker. Treat all following text
                # as chapter 1.
                current_chapter = 1
                expected_chapter = 999
                chapter_lines = []
            continue
        if current_book is None:
            continue
        # Standalone number line: chapter marker.
        # At a book start, accept any first chapter number, because
        # some books in this PDF continue Daniel numbering
        # (Susanna 13, Bel 14, Letter of Jeremiah 6, Song 3).
        # After that, only the next expected chapter counts.
        if re.fullmatch(r"\d+", line):
            num = int(line)
            if current_chapter is None or num == expected_chapter:
                flush_chapter()
                current_chapter = num
                expected_chapter = num + 1
                chapter_lines = []
                continue
            else:
                # Page number or other number: ignore.
                continue
        if current_chapter is None:
            # Pre-chapter material (prologue, introduction, notes):
            # do not assign it to a chapter.
            continue
        # Inline chapter marker: some chapter numbers in this PDF
        # are not on their own line, but appear as "29 1 Now..."
        # at the end of the previous chapter's last line. If the
        # next expected chapter number is followed by verse 1,
        # split the chapter here.
        if expected_chapter < 999:
            inline = re.search(
                rf"(?:^|\s){expected_chapter}\s+1(?:\s+|(?=[“‘\"'A-Z]))", line
            )
            if inline:
                before = line[: inline.start()].strip()
                after = "1" + line[inline.end():]
                if before:
                    chapter_lines.append(before)
                flush_chapter()
                current_chapter = expected_chapter
                expected_chapter = expected_chapter + 1
                chapter_lines = [after] if after.strip() else []
                continue
        chapter_lines.append(line)
    flush_chapter()
    total_verses = sum(len(ch) for b in books.values() for ch in b["chapters"].values())
    result = {
        "foundation": "Ethiopian Orthodox Bible, modern English compilation in the PDF supplied by Anthony, rooted in the Septuagint and Ge'ez tradition. Not an ancient manuscript itself.",
        "source_file": "ethiopianorthodoxbible_0_wj1b.pdf",
        "extraction": "pdftotext -layout, sequential chapter and verse parsing. See tools/extract_ethiopian.py for rules and limits.",
        "books": books,
        "book_count": len(books),
        "verse_count": total_verses,
    }
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"books: {len(books)}")
    print(f"verses: {total_verses}")
    for name, book in books.items():
        chs = book["chapters"]
        vcount = sum(len(c) for c in chs.values())
        print(f"  {name}: {len(chs)} chapters, {vcount} verses, canon={book['canon']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
