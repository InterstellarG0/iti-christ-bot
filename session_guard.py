"""Bounded, in-memory conversation sessions for the optional local web server.

No disk persistence, analytics, or external service calls. Thread-safe.
"""
from __future__ import annotations

from collections import OrderedDict
from threading import RLock
from time import monotonic
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class SessionStore(Generic[T]):
    """Expire idle sessions and evict oldest entries to cap memory use.

    The caller supplies the session factory and an opaque session identifier.
    Access refreshes the idle timer. Never log identifiers or message bodies.
    """

    def __init__(self, factory: Callable[[], T], *, max_sessions: int = 128,
                 idle_seconds: float = 3600):
        if max_sessions < 1 or idle_seconds <= 0:
            raise ValueError("Session limits must be positive")
        self._factory = factory
        self._max_sessions = max_sessions
        self._idle_seconds = idle_seconds
        self._items: OrderedDict[str, tuple[float, T]] = OrderedDict()
        self._lock = RLock()

    def get_or_create(self, identifier: str) -> T:
        if not isinstance(identifier, str) or not (1 <= len(identifier) <= 128):
            raise ValueError("Invalid session identifier")
        with self._lock:
            now = monotonic()
            for key, (last_used, _) in list(self._items.items()):
                if now - last_used >= self._idle_seconds:
                    del self._items[key]
            if identifier in self._items:
                _, session = self._items.pop(identifier)
            else:
                session = self._factory()
            self._items[identifier] = (now, session)
            while len(self._items) > self._max_sessions:
                self._items.popitem(last=False)
            return session

    def clear(self, identifier: str) -> bool:
        with self._lock:
            return self._items.pop(identifier, None) is not None

    def clear_all(self) -> None:
        with self._lock:
            self._items.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)
