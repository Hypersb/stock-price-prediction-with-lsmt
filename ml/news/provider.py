"""Abstract news provider port."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from ml.news.schema import Article


class NewsProvider(ABC):
    """Fetch articles for symbols within an optional time window.

    Implementations must not invent articles. Missing credentials should yield
    empty results (see ``NullNewsProvider``), not fabricated headlines.
    """

    @abstractmethod
    def fetch(
        self,
        symbols: list[str] | tuple[str, ...],
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 50,
    ) -> list[Article]:
        """Return real articles only; empty list when unavailable."""
