"""Small in-memory rate limiter for protecting public endpoints."""

from __future__ import annotations

from collections import defaultdict, deque
from threading import Lock
from time import time
from typing import Deque


class InMemoryRateLimiter:
    """Simple fixed-window limiter with per-key tracking."""

    def __init__(self, *, requests: int, window_seconds: int) -> None:
        self._requests = requests
        self._window_seconds = window_seconds
        self._buckets: dict[str, Deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str) -> bool:
        """Return True when the request should be permitted for the given key."""

        now = time()
        window_start = now - self._window_seconds

        with self._lock:
            bucket = self._buckets[key]
            while bucket and bucket[0] <= window_start:
                bucket.popleft()

            if len(bucket) >= self._requests:
                return False

            bucket.append(now)
            return True
