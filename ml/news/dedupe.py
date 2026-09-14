"""Deduplicate news articles by stable identity keys."""

from __future__ import annotations

from ml.news.schema import Article


def dedupe_articles(articles: list[Article]) -> list[Article]:
    """Keep first occurrence; dedupe by URL or (headline, published_at).

    Empty URL falls back to the headline/timestamp key only.
    """
    seen: set[str] = set()
    unique: list[Article] = []
    for article in articles:
        url_key = article.url.strip().lower()
        if url_key:
            key = f"url:{url_key}"
        else:
            key = (
                f"headline:{article.headline.strip().lower()}"
                f"|{article.published_at.isoformat()}"
            )
        if key in seen:
            continue
        seen.add(key)
        unique.append(article)
    return unique
