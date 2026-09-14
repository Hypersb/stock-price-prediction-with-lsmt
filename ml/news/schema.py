"""Structured news article schema for research ingestion."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class Article:
    """Normalized article record returned by a ``NewsProvider``."""

    article_id: str
    provider: str
    headline: str
    summary: str
    url: str
    published_at: datetime
    symbols: tuple[str, ...] = ()
    source: str = ""
    retrieved_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def __post_init__(self) -> None:
        if not self.article_id.strip():
            raise ValueError("article_id must be non-empty")
        if not self.provider.strip():
            raise ValueError("provider must be non-empty")
        if not self.headline.strip():
            raise ValueError("headline must be non-empty")
        object.__setattr__(
            self,
            "symbols",
            tuple(s.strip().upper() for s in self.symbols if str(s).strip()),
        )
