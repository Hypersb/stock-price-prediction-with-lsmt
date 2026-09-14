"""Tests for keyword sentiment and leakage-safe aggregation."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from ml.news.schema import Article
from ml.nlp import FinancialKeywordSentiment, aggregate_sentiment_before


def test_keyword_sentiment_positive_and_negative() -> None:
    analyzer = FinancialKeywordSentiment()
    pos = analyzer.analyze("Company beats estimates with strong growth and profit")
    neg = analyzer.analyze("Shares plunge after loss and downgrade")
    assert pos.model_version == "keyword_lexicon_v1"
    assert pos.label == "pos"
    assert neg.label == "neg"


def test_aggregate_excludes_articles_at_or_after_prediction_time() -> None:
    cutoff = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)
    before = Article(
        article_id="old",
        provider="test",
        headline="rally and upgrade",
        summary="",
        url="https://example.com/old",
        published_at=cutoff - timedelta(hours=1),
    )
    after = Article(
        article_id="new",
        provider="test",
        headline="plunge and loss",
        summary="",
        url="https://example.com/new",
        published_at=cutoff,
    )
    agg = aggregate_sentiment_before([before, after], cutoff)
    assert agg.n_articles == 1
    assert agg.label == "pos"
    # If leakage occurred, the post-cutoff negative article would flip the mean.
    assert agg.mean_scores["neg"] < agg.mean_scores["pos"]


def test_prediction_time_must_be_timezone_aware() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        aggregate_sentiment_before(
            [],
            datetime(2024, 1, 1),
        )
