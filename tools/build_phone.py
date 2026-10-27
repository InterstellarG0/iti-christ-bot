#!/usr/bin/env python3
"""Build the single-file Christ Bot phone version from the v1.2 corpora."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / "phone" / "christbot-phone.html"
TEMPLATE = BASE / "phone" / "christbot-phone.template.html"

eth = json.loads((BASE / "scripture" / "ethiopian_corpus.json").read_text(encoding="utf-8"))
kjv = json.loads((BASE / "scripture" / "corpus.json").read_text(encoding="utf-8"))

compact = {}
for raw_book, book_data in eth["books"].items():
    book = "Psalm" if raw_book == "Psalms" else raw_book
    compact[book] = [book_data.get("canon", "shared"), book_data["chapters"]]

kjv_map = {}
topics = {}
for v in kjv.get("verses", []):
    kjv_map[v["reference"]] = v["text"]
    if v.get("topics"):
        topics[v["reference"]] = v["topics"]
topics.update({
    "Psalm 151:1": ["hope", "strength"],
    "Psalm 151:7": ["hope", "strength"],
    "Jubilees 1:1": ["creation"],
    "Enoch 1:1": ["hope"],
    "Philippians 2:14": ["complaining"],
    "1 Corinthians 10:13": ["lust"],
    "1 John 1:9": ["guilt"],
    "Proverbs 14:30": ["envy"],
    "James 4:6": ["pride"],
    "Romans 7:15": ["addiction"],
    "Matthew 6:25": ["money"],
    "Galatians 5:22": ["character"],
    "Psalm 121:1": ["help"],
    "Matthew 28:19": ["mission"],
})

def safe_json(obj):
    # Escape </ so embedded JSON can never close the script tag early.
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

template = TEMPLATE.read_text(encoding="utf-8")
out = template.replace("__ETH__", safe_json(compact))
out = out.replace("__KJV__", safe_json(kjv_map))
out = out.replace("__TOPICS__", safe_json(topics))
assert "__ETH__" not in out and "__KJV__" not in out and "__TOPICS__" not in out
OUT.write_text(out, encoding="utf-8")
print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")
print(f"Books: {len(compact)}, KJV parallels: {len(kjv_map)}, topic refs: {len(topics)}")
