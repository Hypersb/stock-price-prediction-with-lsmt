"""Null news provider — app works without paid API credentials."""

from __future__ import annotations

from datetime import datetime

from ml.news.provider import NewsProvider
from ml.news.schema import Article


class NullNewsProvider(NewsProvider):
    """Always returns an empty list (no fabricated news)."""

    def fetch(
        self,
        symbols: list[str] | tuple[str, ...],
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int = 50,
    ) -> list[Article]:
        _ = (symbols, start, end, limit)
        return []
