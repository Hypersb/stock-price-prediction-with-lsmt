"""Bounded in-process TTL cache for non-sensitive research reads."""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from collections.abc import Hashable
from typing import Generic, TypeVar

T = TypeVar("T")


class TtlCache(Generic[T]):
    """Thread-safe LRU cache with per-entry time-to-live."""

    def __init__(self, *, max_size: int = 64, ttl_seconds: float = 60.0) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._entries: OrderedDict[Hashable, tuple[float, T]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: Hashable) -> T | None:
        now = time.monotonic()
        with self._lock:
            item = self._entries.get(key)
            if item is None:
                return None
            expires_at, value = item
            if expires_at <= now:
                del self._entries[key]
                return None
            self._entries.move_to_end(key)
            return value

    def set(self, key: Hashable, value: T) -> None:
        expires_at = time.monotonic() + self.ttl_seconds
        with self._lock:
            if key in self._entries:
                del self._entries[key]
            self._entries[key] = (expires_at, value)
            while len(self._entries) > self.max_size:
                self._entries.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)
