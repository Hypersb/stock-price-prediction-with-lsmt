"""News ingestion contracts (no fabricated headlines)."""

from ml.news.dedupe import dedupe_articles
from ml.news.null_provider import NullNewsProvider
from ml.news.provider import NewsProvider
from ml.news.schema import Article

__all__ = [
    "Article",
    "NewsProvider",
    "NullNewsProvider",
    "dedupe_articles",
]
