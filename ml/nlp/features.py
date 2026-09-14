"""Leakage-safe sentiment feature aggregation for research pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ml.news.schema import Article
from ml.nlp.sentiment import FinancialKeywordSentiment, SentimentResult


@dataclass(frozen=True)
class AggregatedSentiment:
    """Mean lexicon scores over articles published strictly before cutoff."""

    n_articles: int
    mean_scores: dict[str, float]
    label: str
    model_version: str


def aggregate_sentiment_before(
    articles: list[Article],
    prediction_time: datetime,
    *,
    analyzer: FinancialKeywordSentiment | None = None,
    text_field: str = "headline",
) -> AggregatedSentiment:
    """Aggregate sentiment using only articles with ``published_at < prediction_time``.

    Articles at or after ``prediction_time`` are excluded to avoid look-ahead
    leakage into features available at prediction time.
    """
    if prediction_time.tzinfo is None:
        raise ValueError("prediction_time must be timezone-aware")
    sentiment = analyzer or FinancialKeywordSentiment()
    eligible: list[SentimentResult] = []
    for article in articles:
        published = article.published_at
        if published.tzinfo is None:
            raise ValueError("article.published_at must be timezone-aware")
        if published >= prediction_time:
            continue
        if text_field == "summary":
            text = article.summary
        else:
            text = article.headline
        eligible.append(sentiment.analyze(text))

    if not eligible:
        return AggregatedSentiment(
            n_articles=0,
            mean_scores={"pos": 0.0, "neu": 1.0, "neg": 0.0},
            label="neu",
            model_version=sentiment.model_version,
        )

    keys = ("pos", "neu", "neg")
    means = {
        key: float(sum(r.scores[key] for r in eligible) / len(eligible))
        for key in keys
    }
    label = max(means, key=means.get)  # type: ignore[arg-type]
    return AggregatedSentiment(
        n_articles=len(eligible),
        mean_scores=means,
        label=label,
        model_version=sentiment.model_version,
    )
