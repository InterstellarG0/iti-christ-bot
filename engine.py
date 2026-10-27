"""
Christ Bot v1.2.3 - core reflection engine.

Design choices, stated plainly:
- This engine is deterministic and retrieval-only for Scripture. It does
  NOT generate biblical text from a language model. A passage is quoted
  only if it is found in scripture/ethiopian_corpus.json (foundation)
  or, for the KJV parallel, in scripture/corpus.json. If it is not
  found, the engine says so.
- Foundation: Ethiopian Orthodox Bible, modern English compilation in
  the PDF supplied by Anthony, rooted in the Septuagint and Ge'ez
  tradition. It is not an ancient manuscript itself. King James is
  shown only as a separate parallel, never merged into Ethiopian text.
- Every passage carries a canon label: shared, deuterocanonical, or
  ethiopian-only. No tradition is presented as universally accepted.
- There is no persistent memory in Phase 1. A Session lives in memory
  only, for one conversation, and is cleared on reset or restart.
- Crisis language overrides everything else. The engine does not
  continue in reflective mode in that moment.
- The engine never claims to be God, Jesus, a prophet, or a
  supernatural entity, never diagnoses, and never presents one
  interpretive tradition as universally accepted.

Only the Python standard library is used.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

CORPUS_PATH = Path(__file__).resolve().parent / "scripture" / "corpus.json"
ETHIOPIAN_CORPUS_PATH = Path(__file__).resolve().parent / "scripture" / "ethiopian_corpus.json"

ETHIOPIAN_TRANSLATION = (
    "Ethiopian Orthodox Bible, modern English compilation "
    "(Septuagint/Ge'ez tradition)"
)
KJV_TRANSLATION = "KJV (public domain)"

CRISIS_TEXT = (
    "If you feel you may act on thoughts of harming yourself right now, "
    "please reach out for help immediately.\n\n"
    "In the United States, call or text 988 to reach the Suicide and Crisis "
    "Lifeline. You can also text HOME to 741741 for the Crisis Text Line, "
    "or call 911 if you are in immediate danger.\n"
    "If you are outside the United States, please contact your local "
    "emergency number or a trusted crisis service in your country, and "
    "consider telling a trusted person near you right now.\n\n"
    "I am pausing reflective conversation here so you can get real-world "
    "support. I am not a counselor or a replacement for professional care."
)

IDENTITY_TEXT = (
    "I am Christ Bot, a scripture-centered reflection companion built by "
    "the Interstellar Religious Initiative. I am software, not God, Jesus, "
    "a prophet, or a supernatural being. I do not know God's will for you, "
    "and I am not a replacement for clergy, a counselor, or your own "
    "conscience. You are free to disagree with anything I offer."
)

BOOK_ALIASES = {
    "genesis": "Genesis", "gen": "Genesis",
    "exodus": "Exodus", "exod": "Exodus",
    "psalm": "Psalm", "psalms": "Psalm", "ps": "Psalm",
    "proverbs": "Proverbs", "prov": "Proverbs",
    "ecclesiastes": "Ecclesiastes", "eccl": "Ecclesiastes",
    "isaiah": "Isaiah", "isa": "Isaiah",
    "jeremiah": "Jeremiah", "jer": "Jeremiah",
    "lamentations": "Lamentations", "lam": "Lamentations",
    "micah": "Micah", "mic": "Micah",
    "matthew": "Matthew", "matt": "Matthew", "mt": "Matthew",
    "mark": "Mark", "mk": "Mark",
    "luke": "Luke", "lk": "Luke",
    "john": "John", "jn": "John",
    "romans": "Romans", "rom": "Romans",
    "corinthians": "Corinthians",
    "1 corinthians": "1 Corinthians", "1 cor": "1 Corinthians",
    "2 corinthians": "2 Corinthians",
    "galatians": "Galatians", "gal": "Galatians",
    "ephesians": "Ephesians", "eph": "Ephesians",
    "philippians": "Philippians", "phil": "Philippians",
    "colossians": "Colossians", "col": "Colossians",
    "timothy": "Timothy",
    "1 timothy": "1 Timothy", "2 timothy": "2 Timothy",
    "james": "James", "jas": "James",
    "peter": "Peter", "1 peter": "1 Peter",
    "hebrews": "Hebrews", "heb": "Hebrews",
    "joshua": "Joshua", "josh": "Joshua",
    "jubilees": "Jubilees", "enoch": "Enoch", "2 enoch": "2 Enoch",
    "meqabyan i": "Meqabyan I", "meqabyan ii": "Meqabyan II",
    "meqabyan iii": "Meqabyan III", "meqabyan": "Meqabyan I",
    "tobit": "Tobit", "judith": "Judith", "wisdom": "Wisdom",
    "sirach": "Sirach", "baruch": "Baruch", "susanna": "Susanna",
    "prayer of manasses": "Prayer of Manasses",
    "1 esdras": "1 Esdras", "2 esdras": "2 Esdras",
    "1 clement": "1 Clement", "4 baruch": "4 Baruch",
}

REF_RE = re.compile(
    r"\b([1-3]?\s*[A-Za-z]+)\s+(\d+)\s*:\s*(\d+(?:\s*-\s*\d+)?)\b"
)

# Multi-word book names that the single-word pattern cannot capture.
# Listed longest first so "Song of the Three Children" wins over "Song".
MULTIWORD_BOOKS = [
    "Song of the Three Children", "Prayer of Manasses",
    "Bel and the Dragon", "Letter of Jeremiah",
    "Additions to Esther", "Meqabyan I", "Meqabyan II", "Meqabyan III",
    "1 Esdras", "2 Esdras", "1 Clement", "4 Baruch", "2 Enoch",
    "Song of Songs",
]

# Books whose corpus chapter is not the chapter a reader would
# naturally ask for, because the PDF continues Daniel/Baruch numbering.
# Susanna is Daniel 13, Bel is Daniel 14, Letter of Jeremiah is Baruch 6.
CHAPTER_ALIASES = {
    "Susanna": 13,
    "Bel and the Dragon": 14,
    "Letter of Jeremiah": 6,
}

CRISIS_PATTERNS = [
    r"\bkill myself\b", r"\bkill yourself\b", r"\bcommit suicide\b",
    r"\bsuicid\w*\b", r"\bend my life\b", r"\btake my own life\b",
    r"\bi want to die\b", r"\bi don'?t want to live\b",
    r"\bharm myself\b", r"\bhurt myself\b", r"\bcut myself\b",
    r"\bself[- ]harm\b", r"\bno reason to live\b",
]

# keyword phrase -> (topic, reflection sentence)
TOPICS = [
    ("forgiveness", ["forgive", "forgiveness", "can't forgive", "cannot forgive",
                      "someone hurt me", "betrayed", "resentment"],
     "Forgiveness, and what it does and does not require, sounds like it is at the center of this."),
    ("grief", ["grief", "grieving", "lost someone", "died", "death of",
               "mourning", "bereaved", "passed away"],
     "Grief sounds like it is weighing on you right now, and that deserves space before any answers."),
    ("anxiety", ["anxious", "anxiety", "worried", "worry", "stressed",
                 "overwhelmed", "panic", "can't sleep", "cannot sleep"],
     "Anxiety and the weight of what is uncertain sound like they are close to the surface here."),
    ("fear", ["afraid", "fear", "scared", "frightened", "terrified"],
     "Fear sounds like it is shaping how this feels right now."),
    ("doubt", ["doubt", "doubting", "not sure i believe", "struggling to believe",
               "lost faith", "questioning my faith", "unbelief"],
     "Doubt, and wanting to be honest about it rather than pretend, sounds like the real question here."),
    ("decision", ["decision", "decide", "what should i do", "choice",
                  "discern", "discernment", "crossroads"],
     "A decision you want to discern carefully, not rush, sounds like what is in front of you."),
    ("conflict", ["conflict", "argument", "fight with", "angry at", "angry",
                  "disagreement", "someone i love and"],
     "A conflict, and how to respond without doing more harm, sounds like what is on your mind."),
    ("complaining", ["complain", "complaining", "complaints", "complaint",
                      "grumble", "grumbling", "murmur", "murmuring"],
     "Being tired of complaints, whether your own or other people's, sounds like what is weighing on you."),
    ("lust", ["lust", "lustful", "lusting", "temptation", "tempted",
              "porn", "pornography", "sexual desire"],
     "Lust, and wanting help with it rather than just feeling ashamed about it, sounds like what you are bringing here."),
    ("loneliness", ["lonely", "loneliness", "alone", "no one to talk to",
                    "isolated", "no friends"],
     "Loneliness sounds like it is part of this, not just the topic you named."),
    ("science", ["science", "astronomy", "stars", "universe", "evolution",
                 "origins", "big bang", "ai", "artificial intelligence",
                 "machines", "technology"],
     "How faith, science, and increasingly capable machines fit together sounds like the question you are working through."),
    ("creation", ["creation", "created", "nature", "sky", "night sky"],
     "Creation, and what it means to look at it honestly, sounds like part of what you are noticing."),
    ("purpose", ["purpose", "meaning", "why am i here", "direction in life",
                 "calling", "what is my purpose"],
     "Purpose, and what a faithful next step looks like, sounds like the deeper question here."),
    ("hope", ["hopeless", "hope", "give up", "giving up", "despair"],
     "Holding on to hope when it feels thin sounds like what you are asking about."),
    ("love", ["love", "loved", "loving"],
     "Love, what it requires, and where it falls short, sounds like it is at the heart of this."),
    ("prayer", ["pray", "prayer", "praying"],
     "Prayer, and what it is like when it feels dry or uncertain, sounds like part of this."),
    ("rest", ["tired", "exhausted", "rest", "burned out", "burnt out"],
     "Rest, real rest and not just stopping for a moment, sounds like something you need."),
    ("justice", ["justice", "unfair", "injustice", "oppression"],
     "Justice, and what is fair and merciful at the same time, sounds like the tension here."),
    ("strength", ["weak", "strength", "cannot go on", "keep going"],
     "Strength to keep going, and where it comes from, sounds like what you are asking about."),
]

INTERPRETATIONS = {
    "forgiveness": (
        "Interpretation, not Scripture: in many Christian traditions, forgiveness "
        "is described as releasing a debt and refusing to carry revenge as a way of life. "
        "It does not require reconciliation, restored access, or continued contact. "
        "Boundaries and accountability can remain, and in unsafe situations they should. "
        "Other traditions frame this differently, and people disagree in good faith about "
        "how forgiveness and reconciliation relate. You are free to weigh that for yourself."
    ),
    "grief": (
        "Interpretation, not Scripture: grief is often described in Scripture and in "
        "pastoral care as something to be carried, not fixed on a schedule. A passage "
        "about comfort does not mean the pain is small, or that faith removes it."
    ),
    "anxiety": (
        "Interpretation, not Scripture: passages about worry are often read as an "
        "invitation to bring concerns into prayer, not as a diagnosis and not as a "
        "claim that anxiety is a spiritual failure. Persistent distress is a reason "
        "to seek professional and community support, not a reason for shame."
    ),
    "fear": (
        "Interpretation, not Scripture: 'do not fear' passages are often read as "
        "reassurance in the presence of fear, not as a command to never feel afraid. "
        "Fear can also be useful information, especially when a situation is unsafe."
    ),
    "doubt": (
        "Interpretation, not Scripture: doubt is treated very differently across "
        "traditions. Some see it as a normal part of faith, some as a stage to work "
        "through, and some as something to confess. This companion does not treat "
        "doubt as evidence that you are spiritually deficient."
    ),
    "decision": (
        "Interpretation, not Scripture: discernment is often described as slower "
        "than advice. It can include Scripture, counsel from trusted people, attention "
        "to consequences, and time. No passage on its own settles a personal decision "
        "for you, and I will not claim to know what you should choose."
    ),
    "conflict": (
        "Interpretation, not Scripture: peacemaking in Scripture is often paired with "
        "honesty, not with avoiding hard truths or with restoring contact at any cost. "
        "A soft answer and a firm boundary can belong in the same conversation."
    ),
    "complaining": (
        "Interpretation, not Scripture: passages about complaining are often read as "
        "an invitation to notice what is underneath a complaint, not as a ban on honest "
        "lament or on naming a real problem. Scripture also includes laments and honest "
        "complaints to God. The difference people often draw is between a complaint that "
        "names something true and seeks a next step, and a complaint that only circles. "
        "Feeling tired or frustrated is not, on its own, a spiritual failure."
    ),
    "lust": (
        "Interpretation, not Scripture: this passage is often read as saying temptation "
        "is common, not unique to you, and that there is a way through it, not as a claim "
        "that feeling desire makes you spiritually deficient. Desire is treated in Scripture "
        "in different ways, and a single passage does not settle a personal struggle on its "
        "own. If a pattern of behavior is causing real distress or harm, professional and "
        "trusted community support can help alongside reflection here, and this companion "
        "does not diagnose anything."
    ),
    "science": (
        "Interpretation, not Scripture: faith and scientific inquiry are held together "
        "by some people and kept in separate domains by others. A scientific account "
        "of how something works does not, on its own, prove or disprove a theological "
        "claim, and a theological claim does not, on its own, settle a scientific question."
    ),
    "creation": (
        "Interpretation, not Scripture: passages about the heavens are poetry and "
        "wonder as well as theology. They can sit alongside astronomy without being "
        "used as a scientific textbook, and astronomy can be studied seriously without "
        "being treated as a threat to faith."
    ),
}

LENSES_TEXT = (
    "Five lenses, used only when relevant and labeled here as product lenses, not as Scripture:\n"
    "1. Text: what the passage actually says, in the translation named.\n"
    "2. History and context: when and for whom it was written, as far as that is known.\n"
    "3. Interpretive traditions: how different Christian traditions have read it, where they agree and disagree.\n"
    "4. Science and reason: what can be examined, tested, or reasoned about, without manufacturing proof.\n"
    "5. Personal discernment: what this might mean for your own conscience and next step, which only you can decide."
)


def load_corpus(path: Path | None = None) -> dict:
    """Load the dual edition: Ethiopian foundation first, KJV parallel.

    Ethiopian verses are keyed by canonical reference, with "Psalms"
    normalized to "Psalm" and "Psalm 151" stored as "Psalm 151:1"
    (not "Psalm 151 1:1"). Topics are copied from the KJV starter
    corpus where the same reference exists, so topic retrieval keeps
    working with Ethiopian wording.
    """
    # KJV starter corpus, for the parallel only.
    kjv_verses: dict[str, dict] = {}
    kjv_by_ref: dict[str, dict] = {}
    if CORPUS_PATH.exists():
        with open(CORPUS_PATH, encoding="utf-8") as f:
            kjv_data = json.load(f)
        for v in kjv_data.get("verses", []):
            key = canonical_ref(v["reference"])
            kjv_verses[key] = v
            kjv_by_ref[key] = v

    verses: dict[str, dict] = {}
    books: dict[str, str] = {}
    if ETHIOPIAN_CORPUS_PATH.exists():
        with open(ETHIOPIAN_CORPUS_PATH, encoding="utf-8") as f:
            eth = json.load(f)
        for book_raw, book_data in eth.get("books", {}).items():
            canon = book_data.get("canon", "shared")
            book = "Psalm" if book_raw == "Psalms" else book_raw
            books[book] = canon
            for chapter_raw, chapter_verses in book_data.get("chapters", {}).items():
                for verse_raw, verse_text in chapter_verses.items():
                    if book == "Psalm 151":
                        ref = f"Psalm 151:{verse_raw}"
                    else:
                        ref = f"{book} {chapter_raw}:{verse_raw}"
                    entry: dict = {
                        "reference": ref,
                        "text": verse_text,
                        "canon": canon,
                        "topics": list(kjv_by_ref.get(ref, {}).get("topics", [])),
                    }
                    verses[ref] = entry
                    # Chapter aliases for single-chapter books whose
                    # corpus chapter continues Daniel/Baruch numbering.
                    if book in CHAPTER_ALIASES and chapter_raw == str(CHAPTER_ALIASES[book]):
                        alias_ref = f"{book} 1:{verse_raw}"
                        alias_entry = dict(entry)
                        alias_entry["reference"] = alias_ref
                        alias_entry["corpus_reference"] = ref
                        verses[alias_ref] = alias_entry
    # Manual topics for Ethiopian-only passages with no KJV match.
    manual_topics = {
        "Psalm 151:1": ["hope", "strength"],
        "Psalm 151:7": ["hope", "strength"],
        "Jubilees 1:1": ["creation"],
        "Enoch 1:1": ["hope"],
        "Philippians 2:14": ["complaining"],
        "1 Corinthians 10:13": ["lust"],
    }
    for ref, topics in manual_topics.items():
        if ref in verses:
            verses[ref]["topics"] = topics

    return {
        "translation": ETHIOPIAN_TRANSLATION,
        "kjv_translation": KJV_TRANSLATION,
        "note": "Ethiopian foundation, KJV parallel shown separately, never merged.",
        "verses": verses,
        "kjv_verses": kjv_verses,
        "books": books,
        "verse_count": len(verses),
        "kjv_count": len(kjv_verses),
    }


def canonical_ref(raw: str) -> str:
    # Psalm 151 is a book name plus a verse, not chapter 151.
    m151 = re.search(r"\bPsalm\s+151\s*:\s*(\d+(?:\s*-\s*\d+)?)\b", raw, re.IGNORECASE)
    if m151:
        return f"Psalm 151:{re.sub(r'\\s+', '', m151.group(1))}"
    # Multi-word books first.
    for book in MULTIWORD_BOOKS:
        m = re.search(
            rf"\b{re.escape(book)}\s+(\d+)\s*:\s*(\d+(?:\s*-\s*\d+)?)\b",
            raw, re.IGNORECASE,
        )
        if m:
            return f"{book} {m.group(1)}:{re.sub(r'\\s+', '', m.group(2))}"
    m = REF_RE.search(raw)
    if not m:
        return raw.strip()
    book_raw = re.sub(r"\s+", " ", m.group(1).strip().lower())
    book = BOOK_ALIASES.get(book_raw, m.group(1).strip().title())
    chapter = m.group(2)
    verses = re.sub(r"\s+", "", m.group(3))
    return f"{book} {chapter}:{verses}"


def detect_crisis(text: str) -> bool:
    low = text.lower()
    return any(re.search(p, low) for p in CRISIS_PATTERNS)


def detect_topic(text: str) -> tuple[str, str] | None:
    low = text.lower()
    for topic, phrases, reflection in TOPICS:
        for phrase in phrases:
            # Word boundaries, not substrings. The old substring check made
            # "ai" match "said", "faith", and "again", so almost every
            # sentence was misread as the science topic.
            if re.search(r"\b" + re.escape(phrase) + r"\b", low):
                return topic, reflection
    return None


def _is_verse_request(low: str) -> bool:
    """True when the user is asking for a passage in general terms.

    The old code only accepted exact one-word affirmations like "yes",
    so "show me a verse about this", "find a passage please", and
    "to look at a retrieved passage together" all fell through to the
    generic turn, which then offered the same three options again in a loop.
    """
    if any(n in low for n in ("don't want", "do not want", "no passage", "not a passage")):
        return False
    if low.strip() in ("yes", "sure", "ok", "okay", "please", "show me",
                        "go ahead", "yes please", "passage please", "verse please"):
        return True
    phrases = (
        "show me a verse", "show me a passage", "give me a verse",
        "give me a passage", "find a passage", "find a verse",
        "find me a passage", "find me a verse", "show me scripture",
        "show me a scripture", "look at a retrieved passage",
        "look at a passage", "a passage together", "a verse about this",
        "verse about this", "passage about this", "show me one",
    )
    return any(p in low for p in phrases)


def _about_mismatch(low: str) -> str | None:
    """Return the "about X" target if X is not a known topic, else None.

    Without this, "find a passage about lust" before lust was a topic
    silently returned the previous topic's passage, complaining, which
    looked like the bot was ignoring the new question. "About this",
    "about that", and "about it" mean the previous topic, so they are
    not a mismatch.
    """
    if "about" not in low:
        return None
    cleaned = re.sub(r"\s+please\s*$", "", low.strip())
    m = re.search(r"\babout\s+([a-z]+(?:\s+[a-z]+)?)\s*$", cleaned)
    if not m:
        return None
    target = m.group(1).strip()
    if target in ("this", "that", "it", "this topic", "that topic"):
        return None
    for _topic, phrases, _reflection in TOPICS:
        for phrase in phrases:
            if re.search(r"\b" + re.escape(phrase) + r"\b", target):
                return None
    return target


def extract_ref(text: str) -> str | None:
    m151 = re.search(r"\bPsalm\s+151\s*:\s*(\d+(?:\s*-\s*\d+)?)\b", text, re.IGNORECASE)
    if m151:
        return f"Psalm 151:{re.sub(r'\\s+', '', m151.group(1))}"
    for book in MULTIWORD_BOOKS:
        m = re.search(
            rf"\b{re.escape(book)}\s+(\d+)\s*:\s*(\d+(?:\s*-\s*\d+)?)\b",
            text, re.IGNORECASE,
        )
        if m:
            return f"{book} {m.group(1)}:{re.sub(r'\\s+', '', m.group(2))}"
    m = REF_RE.search(text)
    if not m:
        return None
    return canonical_ref(m.group(0))


class Session:
    """Session-only state. Nothing here is written to disk by the engine."""

    def __init__(self, corpus: dict):
        self.corpus = corpus
        self.turns = 0
        self.history: list[dict] = []
        self.last_topic: str | None = None
        self.last_reflection: str | None = None
        self.paused = False
        self.mental_health_note_given = False
        self.offered_scripture = False

    def reset(self) -> None:
        self.turns = 0
        self.history = []
        self.last_topic = None
        self.last_reflection = None
        self.paused = False
        self.mental_health_note_given = False
        self.offered_scripture = False


def _sections_to_text(sections: list[tuple[str, str]]) -> str:
    out = []
    for label, body in sections:
        if label:
            out.append(f"{label}\n{body}")
        else:
            out.append(body)
    return "\n\n".join(out)


def _ethiopian_text_for_ref(corpus: dict, ref: str) -> tuple[str, str] | None:
    """Return (display_ref, text) for a single verse or a verse range.

    Ranges are built verse by verse from the Ethiopian corpus, so a
    range is never quoted from memory. If any verse in the range is
    missing, the whole range is treated as not retrieved.
    """
    canon_ref = canonical_ref(ref)
    # Psalm 151 range handling: "Psalm 151:1-2" etc.
    if canon_ref.startswith("Psalm 151:") and "-" in canon_ref:
        start_s, end_s = canon_ref.split(":", 1)[1].split("-", 1)
        try:
            start, end = int(start_s), int(end_s)
        except ValueError:
            return None
        parts = []
        for v in range(start, end + 1):
            entry = corpus["verses"].get(f"Psalm 151:{v}")
            if not entry:
                return None
            parts.append(entry["text"])
        return canon_ref, " ".join(parts)
    if "-" in canon_ref and ":" in canon_ref:
        book_chapter, verse_range = canon_ref.rsplit(":", 1)
        if "-" in verse_range:
            start_s, end_s = verse_range.split("-", 1)
            try:
                start, end = int(start_s), int(end_s)
            except ValueError:
                return None
            parts = []
            for v in range(start, end + 1):
                entry = corpus["verses"].get(f"{book_chapter}:{v}")
                if not entry:
                    return None
                parts.append(entry["text"])
            return canon_ref, " ".join(parts)
    entry = corpus["verses"].get(canon_ref)
    if not entry:
        return None
    return canon_ref, entry["text"]


def _canon_label_for_ref(corpus: dict, ref: str) -> str:
    canon_ref = canonical_ref(ref)
    # Book name is everything before the last " chapter:" part.
    # For Psalm 151, the book is Psalm 151 itself.
    if canon_ref.startswith("Psalm 151:"):
        return corpus.get("books", {}).get("Psalm 151", "deuterocanonical")
    m = re.match(r"^(.*?)\s+\d+:", canon_ref)
    if not m:
        return "shared"
    return corpus.get("books", {}).get(m.group(1), "shared")


def _scripture_sections(corpus: dict, ref: str) -> list[tuple[str, str]] | None:
    found = _ethiopian_text_for_ref(corpus, ref)
    if not found:
        return None
    display_ref, eth_text = found
    canon = _canon_label_for_ref(corpus, ref)
    canon_note = {
        "shared": "Canon: shared, in both the Ethiopian Orthodox canon and the 66-book KJV canon.",
        "deuterocanonical": "Canon: deuterocanonical, in Orthodox canons, not in the 66-book KJV canon.",
        "ethiopian-only": "Canon: Ethiopian-only, in the Ethiopian Orthodox canon, not in the Protestant or Catholic canons in that form.",
    }.get(canon, f"Canon: {canon}.")
    sections = [(
        f"Scripture ({corpus['translation']})",
        f'"{eth_text}"\n- {display_ref}\n{canon_note}',
    )]
    kjv = corpus.get("kjv_verses", {}).get(canonical_ref(ref))
    if kjv:
        sections.append((
            "King James Version (parallel, not merged)",
            f'"{kjv["text"]}"\n- {kjv["reference"]}',
        ))
    elif canon == "shared":
        sections.append((
            "King James Version (parallel)",
            "Not yet loaded for this passage. The KJV starter corpus has only "
            "53 passages, so a missing parallel does not mean the passage is "
            "not in the KJV canon. The Ethiopian text above is the foundation, "
            "and no wording has been merged between editions.",
        ))
    else:
        sections.append((
            "King James Version (parallel)",
            "No parallel in the 66-book KJV canon for this passage.",
        ))
    return sections


def respond(session: Session, user_text: str) -> dict:
    """Return a response dict: text, sections, crisis, pause_offered, scripture_ref."""
    text = (user_text or "").strip()
    low = text.lower()
    session.history.append({"user": text, "kind": "user"})

    # --- Commands / meta ---
    if low in ("/help", "help", "/commands"):
        return _info(session, (
            "Commands you can use:\n"
            "/verse John 3:16 - retrieve a passage by reference, if it is in the local corpus\n"
            "/edition - show the foundation edition, KJV parallel, and canon labels\n"
            "/lenses - show the five lenses used here\n"
            "/pause - take a Sacred Pause\n"
            "/continue - continue the conversation\n"
            "/privacy - how this prototype handles your words\n"
            "/reset - clear this session only\n"
            "/quit - leave\n\n"
            "The foundation is the Ethiopian Orthodox Bible, in a modern English "
            "compilation rooted in the Septuagint and Ge'ez tradition. King James "
            "is shown only as a separate parallel, never merged into Ethiopian text. "
            "You can also just talk. I will listen first, and I will not quote "
            "Scripture in my first reply unless you ask for a specific passage."
        ))
    if low in ("/edition", "edition"):
        corpus = session.corpus
        return _info(session, (
            "Foundation edition: Ethiopian Orthodox Bible, modern English compilation "
            "rooted in the Septuagint and Ge'ez tradition. This PDF is a modern "
            "compilation, not an ancient manuscript itself.\n"
            f"Ethiopian passages in this build: {corpus.get('verse_count', len(corpus['verses']))}\n"
            f"King James parallel passages in this build: {corpus.get('kjv_count', len(corpus.get('kjv_verses', {})))}\n"
            "Canon labels: shared (in both the Ethiopian canon and the 66-book KJV canon), "
            "deuterocanonical (in Orthodox canons, not in the 66-book canon), and "
            "ethiopian-only (for example Enoch, Jubilees, and Meqabyan I to III).\n"
            "Susanna is stored as Daniel 13, Bel and the Dragon as Daniel 14, "
            "and the Song of the Three Children as Daniel 3:24-97, as in the PDF. "
            "You can also ask for Susanna 1:1, Bel 1:1, or Letter of Jeremiah 1:1, "
            "and I will map those to the corpus chapters."
        ))
    if low in ("/privacy", "privacy"):
        return _info(session, (
            "Privacy model, Phase 1, stated honestly: this prototype keeps your "
            "conversation in memory only, for this session. Nothing is written to "
            "a file, no account is required, and restarting clears the conversation. "
            "The web version keeps the same session in server memory only while "
            "your browser session is active, and it is not stored after a restart. "
            "This is not yet an offline app, and it does not yet encrypt or delete "
            "anything on a schedule, because no storage exists to delete. If a "
            "future version adds storage, its privacy claims will have to change "
            "to match what is actually built."
        ))
    if low in ("/lenses", "lenses"):
        return _info(session, LENSES_TEXT)
    if low in ("/reset", "reset"):
        session.reset()
        return _info(session, "Session cleared. We can start fresh, whenever you are ready.")
    if low in ("/pause", "pause", "pause and return later", "take a moment to reflect or pray"):
        session.paused = True
        return _info(session, (
            "Paused. There is no pressure to return at a particular time, and "
            "nothing is tracked about this pause. When you are ready, type "
            "/continue, or just write again."
        ), pause_offered=False)
    if low in ("/continue", "continue the conversation"):
        session.paused = False
        return _info(session, "Continuing. What would you like to explore next?", pause_offered=False)

    # --- Crisis override: always first after commands ---
    if detect_crisis(text):
        return {
            "text": CRISIS_TEXT,
            "sections": [("", CRISIS_TEXT)],
            "crisis": True,
            "pause_offered": False,
            "scripture_ref": None,
        }

    # --- Identity / divine-claim guard ---
    if re.search(r"\bare you (god|jesus|a prophet|christ)\b", low) or \
            re.search(r"\bdo you claim to be\b", low):
        return _info(session, IDENTITY_TEXT)

    # --- User-supplied verse: labeled as such, never as retrieved ---
    if "here is a verse" in low or "my verse is" in low or "use this verse" in low:
        supplied = re.sub(r"(?i)^(here is a verse|my verse is|use this verse)[:\s]*", "", text).strip()
        session.turns += 1
        sections = [
            ("Reflection", "Thank you for bringing that text in. Let me reflect on what you shared, rather than replacing it with a passage from my corpus."),
            ("User-supplied text (not retrieved from the local corpus)", supplied or "(no text was included after your note)"),
            ("Interpretation (not Scripture)", "Any reading I offer here is interpretation, and it is yours to test against the text, your conscience, and people you trust. What part of this passage stands out to you, and why?"),
        ]
        return _finish(session, sections, pause_offered=True)

    # --- Explicit passage request ---
    ref = extract_ref(text)
    explicit_verse_ask = bool(ref) or _is_verse_request(low) or "quote" in low
    if ref:
        found = _scripture_sections(session.corpus, ref)
        session.turns += 1
        if not found:
            sections = [
                ("Reflection", "I looked for that passage in the local corpus, and I could not retrieve it."),
                ("Not retrieved", (
                    f"I do not have {canonical_ref(ref)} in the Ethiopian corpus, so I will not quote it from memory. "
                    "You can paste the passage yourself and I will work with it as user-supplied text, "
                    "or I can offer a summary labeled as a summary, not as a quotation."
                )),
                ("Question", "Would you like to paste the passage, or explore a nearby topic from the passages I do have?"),
            ]
            return _finish(session, sections, pause_offered=False)
        topic = None
        verse = session.corpus["verses"].get(canonical_ref(ref))
        if verse is None and "-" in canonical_ref(ref):
            # For a range, take topics from its first verse.
            first_ref = canonical_ref(ref).split("-", 1)[0]
            # first_ref is like "Psalm 121:1" already, or "Psalm 121:1" from "121:1-2"
            verse = session.corpus["verses"].get(first_ref)
            if verse is None:
                # Range form "Psalm 121:1-2": first verse key is book chapter:1
                base = canonical_ref(ref).rsplit(":", 1)[0]
                verse = session.corpus["verses"].get(f"{base}:1")
        if verse is None:
            verse = {"topics": []}
        for t in verse.get("topics", []):
            if t in INTERPRETATIONS:
                topic = t
                break
        sections = [("Reflection", "Here is the passage you asked for, kept separate from any interpretation that follows.")]
        sections.extend(found)
        if topic:
            sections.append(("Interpretation (not Scripture)", INTERPRETATIONS[topic]))
        else:
            sections.append(("Interpretation (not Scripture)", (
                "No specific interpretive note is attached to this passage in this prototype. "
                "Readings differ across Christian traditions, and a single passage does not "
                "settle a personal question on its own. What follows in your own reflection "
                "is interpretation, not part of the quoted text."
            )))
        sections.append(("Question", "What stands out to you in this passage, and what would you like to sit with or question about it?"))
        return _finish(session, sections, pause_offered=True, scripture_ref=canonical_ref(ref))

    # --- Topic detection ---
    found_topic = detect_topic(text)
    if found_topic:
        topic, reflection = found_topic
        session.last_topic = topic
        session.last_reflection = reflection

    # --- Answers to the generic question, so it cannot loop ---
    if "say more" in low:
        session.turns += 1
        return _finish(session, [
            ("Reflection", "Take your time, I am listening."),
            ("Question", "What part of this feels heaviest, or most unresolved, right now?"),
        ], pause_offered=False)
    if "pause here" in low or low.strip() in ("pause",):
        session.paused = True
        return _info(session, (
            "Paused. There is no pressure to return at a particular time, and "
            "nothing is tracked about this pause. When you are ready, type "
            "/continue, or just write again."
        ), pause_offered=False)

    # --- General verse request: use the topic we already have ---
    if _is_verse_request(low) and session.last_topic:
        mismatch = _about_mismatch(low)
        if mismatch:
            session.turns += 1
            return _finish(session, [
                ("Reflection", f"I do not have a retrieved passage specifically tagged for {mismatch} in the local corpus, so I will not substitute a passage from an earlier topic."),
                ("Question", f"Would you like to talk through {mismatch} itself, or give me a reference to look up?"),
            ], pause_offered=False)
        topic = session.last_topic
        verse = _verse_for_topic(session.corpus, topic)
        session.turns += 1
        if not verse:
            return _finish(session, [
                ("Reflection", "I do not have a retrieved passage for that topic in the local corpus, so I will not invent one."),
                ("Question", "Would you like to talk through the question itself, or paste a passage you want to reflect on?"),
            ], pause_offered=False)
        sections = [
            ("Reflection", session.last_reflection or "Here is a retrieved passage on that topic."),
        ]
        sections.extend(_scripture_sections(session.corpus, verse["reference"]) or [])
        if topic in INTERPRETATIONS:
            sections.append(("Interpretation (not Scripture)", INTERPRETATIONS[topic]))
        else:
            sections.append(("Interpretation (not Scripture)", _generic_interpretation()))
        sections.append(("Question", "What do you notice in that passage, and what do you disagree with or want to push back on?"))
        return _finish(session, sections, pause_offered=True, scripture_ref=verse["reference"])
    if _is_verse_request(low):
        session.turns += 1
        return _finish(session, [
            ("Reflection", "I would like to find a passage for you, but I do not have a topic from our conversation yet to pick one from."),
            ("Question", "Could you say what it is about, or give me a reference like John 3:16?"),
        ], pause_offered=False)

    # --- Listening-first: first turn, no explicit scripture request ---
    if session.turns == 0 and not explicit_verse_ask:
        session.turns += 1
        reflection = found_topic[1] if found_topic else (
            "Thank you for sharing that. I want to understand what you are actually "
            "carrying before I offer anything from Scripture."
        )
        sections = [
            ("Reflection", reflection),
            ("Question", "Could you say a little more about what part of this feels heaviest, or most unresolved, right now?"),
            ("Note", "I have not quoted a passage yet on purpose. If you would like one, tell me a reference, or say 'show me a verse about this', and I will retrieve one and keep it separate from interpretation."),
        ]
        session.offered_scripture = True
        return _finish(session, sections, pause_offered=False)

    # --- Affirmation to an offered passage ---
    if low.strip() in ("yes", "sure", "ok", "okay", "please", "show me", "go ahead", "yes please") and session.last_topic:
        topic = session.last_topic
        verse = _verse_for_topic(session.corpus, topic)
        session.turns += 1
        if not verse:
            return _finish(session, [
                ("Reflection", "I do not have a retrieved passage for that topic in the local corpus, so I will not invent one."),
                ("Question", "Would you like to talk through the question itself, or paste a passage you want to reflect on?"),
            ], pause_offered=False)
        sections = [
            ("Reflection", session.last_reflection or "Here is a retrieved passage on that topic."),
        ]
        sections.extend(_scripture_sections(session.corpus, verse["reference"]) or [])
        if topic in INTERPRETATIONS:
            sections.append(("Interpretation (not Scripture)", INTERPRETATIONS[topic]))
        else:
            sections.append(("Interpretation (not Scripture)", _generic_interpretation()))
        sections.append(("Question", "What do you notice in that passage, and what do you disagree with or want to push back on?"))
        return _finish(session, sections, pause_offered=True, scripture_ref=verse["reference"])

    # --- Subsequent topic turn: reflect, then offer scripture with separation ---
    if found_topic:
        topic, reflection = found_topic
        verse = _verse_for_topic(session.corpus, topic)
        session.turns += 1
        sections = [("Reflection", reflection)]
        if verse:
            sections.extend(_scripture_sections(session.corpus, verse["reference"]) or [])
            if topic in INTERPRETATIONS:
                sections.append(("Interpretation (not Scripture)", INTERPRETATIONS[topic]))
            else:
                sections.append(("Interpretation (not Scripture)", _generic_interpretation()))
        else:
            sections.append(("Note", "I do not have a retrieved passage for that topic in the local corpus, so I will not invent one."))
        sections.append(("Question", "Does that reflection match what you meant, or is there a part I missed? You are free to disagree."))
        return _finish(session, sections, pause_offered=True, scripture_ref=verse["reference"] if verse else None)

    # --- Science / AI discussion without manufactured proof ---
    if re.search(r"\bai\b", low) or "artificial intelligence" in low:
        session.turns += 1
        return _finish(session, [
            ("Reflection", "You are asking about machines that can imitate understanding, and what that means for being human. That is a serious question, and it does not have a single settled theological answer."),
            ("Note on lenses", "Text, history, traditions, science, and personal discernment can each add something here, but none of them manufactures scientific proof of a religious claim. What concerns you most: what machines can do, what they should not be trusted with, or what they reveal about us?"),
            ("Question", "Which of those feels most urgent to you right now?"),
        ], pause_offered=True)

    # --- Solitude safeguard ---
    if "only friend" in low or "only person i" in low or "you are all i have" in low:
        session.turns += 1
        return _finish(session, [
            ("Reflection", "I hear how alone that can feel, and I am glad you are talking about it here."),
            ("Important note", "I am not a substitute for human community, and I do not want to become your exclusive confidant. If there is a trusted person, community, or clergy member you can talk with, even briefly, that matters more than a longer conversation with me. I can stay in this conversation, but I should not replace those relationships."),
            ("Question", "Is there someone, even one person, you feel even a little safe talking with about this?"),
        ], pause_offered=True)

    # --- Disagreement: acknowledge it, do not shame it ---
    if "disagree" in low or "don't agree" in low or "do not agree" in low or "not convinced" in low:
        session.turns += 1
        return _finish(session, [
            ("Reflection", "Thank you for saying that plainly. Disagreement is welcome here, and it is not treated as a spiritual failure."),
            ("Question", "Which part do you disagree with most, the passage itself, the interpretation I offered, or something else? I would rather understand your reading than defend mine."),
        ], pause_offered=False)

    # --- Generic reflective turn: listen, do not sermonize ---
    session.turns += 1
    sections = [
        ("Reflection", "I hear you, and I do not want to rush past what you just said into advice or a passage."),
        ("Question", "What would be most useful right now: to say more about this, to look at a retrieved passage together, or to pause here?"),
    ]
    return _finish(session, sections, pause_offered=False)


def _generic_interpretation() -> str:
    return (
        "No specific interpretive note is attached to this passage in this prototype. "
        "Readings differ across Christian traditions, and a single passage does not "
        "settle a personal question on its own. Any reading offered here is "
        "interpretation, not part of the quoted text."
    )


def _verse_for_topic(corpus: dict, topic: str) -> dict | None:
    # Deterministic: first verse in corpus order carrying that topic.
    for ref, verse in corpus["verses"].items():
        if topic in verse.get("topics", []):
            return verse
    return None


def _info(session: Session, body: str, pause_offered: bool = False) -> dict:
    return {
        "text": body,
        "sections": [("", body)],
        "crisis": False,
        "pause_offered": pause_offered,
        "scripture_ref": None,
    }


def _finish(session: Session, sections: list[tuple[str, str]], pause_offered: bool = False, scripture_ref: str | None = None) -> dict:
    # Mental-health note: once per session, never a diagnosis, never spiritual failure.
    low_history = " ".join(h.get("user", "").lower() for h in session.history[-3:])
    if not session.mental_health_note_given and any(
        w in low_history for w in ("depress", "anxiety", "panic", "mental illness", "therapist", "counselor")
    ):
        sections.append(("Care note (not a diagnosis)", (
            "I am not diagnosing anything, and mental distress is not a spiritual failure. "
            "If distress persists, please consider professional care and trusted people "
            "around you, alongside any reflection here."
        )))
        session.mental_health_note_given = True

    if pause_offered:
        sections.append(("Sacred Pause (optional)", (
            "You can choose, with no pressure and no judgment attached to any choice:\n"
            "- Continue the conversation\n"
            "- Take a moment to reflect or pray\n"
            "- Pause and return later\n"
            "I do not pray on your behalf, and continuing is not spiritually superior to pausing."
        )))

    text = _sections_to_text(sections)
    return {
        "text": text,
        "sections": sections,
        "crisis": False,
        "pause_offered": pause_offered,
        "scripture_ref": scripture_ref,
    }


def list_verses(corpus: dict) -> list[str]:
    return list(corpus["verses"].keys())
