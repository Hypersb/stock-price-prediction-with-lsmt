"""Keyword-lexicon financial sentiment baseline (NOT state-of-the-art).

This analyzer uses an explicit positive/negative lexicon for local, offline
scoring. It does not download large transformer models and must not be treated
as production-grade NLP or investment advice.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

SentimentLabel = Literal["pos", "neu", "neg"]

_MODEL_VERSION = "keyword_lexicon_v1"

_POSITIVE = frozenset(
    {
        "beat",
        "beats",
        "bullish",
        "gain",
        "gains",
        "growth",
        "improve",
        "improved",
        "improvement",
        "outperform",
        "outperforms",
        "profit",
        "profits",
        "rally",
        "record",
        "rise",
        "rises",
        "strong",
        "surge",
        "upgrade",
        "upgraded",
    }
)
_NEGATIVE = frozenset(
    {
        "bearish",
        "cut",
        "cuts",
        "decline",
        "declines",
        "downgrade",
        "downgraded",
        "fall",
        "falls",
        "loss",
        "losses",
        "miss",
        "misses",
        "plunge",
        "risk",
        "risks",
        "selloff",
        "slump",
        "weak",
        "weakness",
        "worry",
    }
)

_TOKEN_RE = re.compile(r"[a-zA-Z]+")


@dataclass(frozen=True)
class SentimentResult:
    """Lexicon sentiment scores for a single text."""

    label: SentimentLabel
    scores: dict[str, float]
    model_version: str = _MODEL_VERSION


class FinancialKeywordSentiment:
    """Baseline keyword-count sentiment for headlines/summaries.

    Documented limitation: this is a transparent lexicon baseline, not SOTA.
    """

    model_version = _MODEL_VERSION

    def analyze(self, text: str) -> SentimentResult:
        tokens = [t.lower() for t in _TOKEN_RE.findall(text or "")]
        if not tokens:
            return SentimentResult(
                label="neu",
                scores={"pos": 0.0, "neu": 1.0, "neg": 0.0},
                model_version=self.model_version,
            )
        pos_hits = sum(1 for t in tokens if t in _POSITIVE)
        neg_hits = sum(1 for t in tokens if t in _NEGATIVE)
        total = pos_hits + neg_hits
        if total == 0:
            return SentimentResult(
                label="neu",
                scores={"pos": 0.0, "neu": 1.0, "neg": 0.0},
                model_version=self.model_version,
            )
        pos = pos_hits / total
        neg = neg_hits / total
        neu = max(0.0, 1.0 - pos - neg)
        if pos > neg:
            label: SentimentLabel = "pos"
        elif neg > pos:
            label = "neg"
        else:
            label = "neu"
        return SentimentResult(
            label=label,
            scores={"pos": float(pos), "neu": float(neu), "neg": float(neg)},
            model_version=self.model_version,
        )
