"""Tests for news provider contracts (no fabricated articles)."""

from __future__ import annotations

from datetime import datetime, timezone

from ml.news import Article, NullNewsProvider, dedupe_articles


def test_null_provider_returns_empty() -> None:
    provider = NullNewsProvider()
    assert provider.fetch(["AAPL"], limit=10) == []


def test_dedupe_by_url() -> None:
    ts = datetime(2024, 1, 1, tzinfo=timezone.utc)
    a = Article(
        article_id="1",
        provider="test",
        headline="One",
        summary="",
        url="https://example.com/a",
        published_at=ts,
    )
    b = Article(
        article_id="2",
        provider="test",
        headline="Different",
        summary="",
        url="https://example.com/a",
        published_at=ts,
    )
    assert len(dedupe_articles([a, b])) == 1


def test_dedupe_by_headline_and_published_at() -> None:
    ts = datetime(2024, 1, 2, tzinfo=timezone.utc)
    a = Article(
        article_id="1",
        provider="test",
        headline="Same Head",
        summary="",
        url="",
        published_at=ts,
    )
    b = Article(
        article_id="2",
        provider="test",
        headline="Same Head",
        summary="",
        url="",
        published_at=ts,
    )
    c = Article(
        article_id="3",
        provider="test",
        headline="Same Head",
        summary="",
        url="",
        published_at=datetime(2024, 1, 3, tzinfo=timezone.utc),
    )
    out = dedupe_articles([a, b, c])
    assert len(out) == 2
    assert {x.article_id for x in out} == {"1", "3"}
