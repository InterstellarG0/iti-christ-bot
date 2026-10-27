#!/usr/bin/env python3
"""
Christ Bot v1.2.3 - Phase 2 prototype.

Foundation: Ethiopian Orthodox Bible, modern English compilation
rooted in the Septuagint and Ge'ez tradition, with King James shown
only as a separate parallel, never merged.

Run the CLI (no install, no account, no API key):
    python3 app.py

Run the minimal web UI (same engine, session in server memory only):
    python3 app.py --web
    then open http://127.0.0.1:8000

Run a scripted demo without typing:
    python3 app.py --demo

List the retrieved passages available in this build:
    python3 app.py --verses

Only the Python standard library is used. No conversation is written
to a file by this program. Restarting clears every session.
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine import Session, load_corpus, list_verses, respond  # noqa: E402

ROOT = Path(__file__).resolve().parent
INTRO = """Christ Bot - a scripture-centered reflection companion.
Interstellar Religious Initiative, flagship of Interstellar Technologies Initiative, LLC.

Foundation: Ethiopian Orthodox Bible, modern English compilation rooted in
the Septuagint and Ge'ez tradition, with King James as a separate parallel.
I am software, not God, Jesus, a prophet, or a supernatural being.
I do not know God's will for you, and I am not a replacement for clergy,
a counselor, or your own conscience. You are free to disagree with me.

Privacy in this prototype: your conversation lives in memory only for
this session. Nothing is written to a file. Restarting clears it.

Type /help for commands, /quit to leave.
"""


def run_cli(corpus: dict) -> int:
    session = Session(corpus)
    print(INTRO)
    while True:
        try:
            user = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nPaused. You can return whenever you like. Nothing here is tracked.")
            return 0
        if not user:
            continue
        if user.lower() in ("/quit", "quit", "exit"):
            print("\nThank you for the conversation. Pause and return later, whenever you like.")
            return 0
        result = respond(session, user)
        print(f"\nChrist Bot:\n{result['text']}")
        if result["crisis"]:
            print("\n[Reflective conversation is paused here so you can get real-world support.]")
    return 0


DEMO_SCRIPT = [
    "I have been carrying a lot of worry lately and I am not sure what to do.",
    "yes",
    "I also need to forgive someone, but I do not want to let them back into my life.",
    "show me John 3:16",
    "show me John 99:99",
]


def run_demo(corpus: dict) -> int:
    session = Session(corpus)
    print(INTRO)
    print("--- Scripted demo ---\n")
    for user in DEMO_SCRIPT:
        print(f"You: {user}\n")
        result = respond(session, user)
        print(f"Christ Bot:\n{result['text']}\n")
        print("---\n")
    return 0


def run_web(corpus: dict, port: int) -> int:
    sessions: dict[str, Session] = {}
    web_file = ROOT / "web" / "index.html"

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):  # keep server logs quiet; never log message bodies
            return

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path in ("/", "/index.html"):
                data = web_file.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            parsed = urlparse(self.path)
            if parsed.path != "/api/chat":
                self.send_response(404)
                self.end_headers()
                return
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                payload = json.loads(raw.decode("utf-8"))
            except Exception:
                self.send_response(400)
                self.end_headers()
                return
            sid = payload.get("session") or str(uuid.uuid4())
            message = (payload.get("message") or "").strip()
            if sid not in sessions:
                sessions[sid] = Session(corpus)
            result = respond(sessions[sid], message) if message else {
                "text": "Please write something to begin.",
                "sections": [("", "Please write something to begin.")],
                "crisis": False, "pause_offered": False, "scripture_ref": None,
            }
            body = json.dumps({
                "session": sid,
                "text": result["text"],
                "sections": result["sections"],
                "crisis": result["crisis"],
                "pause_offered": result["pause_offered"],
                "scripture_ref": result["scripture_ref"],
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Christ Bot web UI: http://127.0.0.1:{port}")
    print("Sessions live in server memory only. Restarting this program clears them.")
    print("Press Ctrl-C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped. Sessions cleared.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Christ Bot v1.2.3 prototype")
    parser.add_argument("--web", action="store_true", help="run the minimal web UI")
    parser.add_argument("--port", type=int, default=8000, help="web port (default 8000)")
    parser.add_argument("--demo", action="store_true", help="run a scripted demo conversation")
    parser.add_argument("--verses", action="store_true", help="list retrieved passages in the corpus")
    args = parser.parse_args(argv)

    corpus = load_corpus()
    if args.verses:
        print(f"Foundation: {corpus['translation']}")
        print(f"Ethiopian passages in this build: {corpus.get('verse_count', len(corpus['verses']))}")
        print(f"King James parallel passages: {corpus.get('kjv_count', len(corpus.get('kjv_verses', {})))}")
        print(f"Books in the Ethiopian corpus: {len(corpus.get('books', {}))}")
        print("\nIf a passage is not listed here, the engine will say so rather than invent it.")
        print("Use /verse in the CLI, or ask for a reference, to retrieve a passage.")
        return 0
    if args.demo:
        return run_demo(corpus)
    if args.web:
        return run_web(corpus, args.port)
    return run_cli(corpus)


if __name__ == "__main__":
    raise SystemExit(main())
