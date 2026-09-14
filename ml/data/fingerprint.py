"""Deterministic dataset fingerprints for provenance (not full blob hashing)."""

from __future__ import annotations

import hashlib
from datetime import date

import pandas as pd

from ml.contracts.dataset import DatasetSpec
from ml.data.schema import REQUIRED_COLUMNS, SCHEMA_VERSION


def fingerprint_ohlcv(frame: pd.DataFrame, *, symbol: str, provider: str) -> str:
    """Content fingerprint from schema version + ordered OHLCV core columns.

    Uses a streaming hash of row values rather than dumping entire frames to
    JSON. Callers should pass already-validated/normalized frames.
    """
    if frame.empty:
        raise ValueError("cannot fingerprint empty market data")
    missing = set(REQUIRED_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"fingerprint requires columns: {sorted(missing)}")

    digest = hashlib.sha256()
    digest.update(SCHEMA_VERSION.encode("utf-8"))
    digest.update(b"|")
    digest.update(provider.strip().lower().encode("utf-8"))
    digest.update(b"|")
    digest.update(symbol.strip().upper().encode("utf-8"))
    digest.update(b"|")

    ordered = frame.loc[:, list(REQUIRED_COLUMNS)].sort_values("date", kind="stable")
    for row in ordered.itertuples(index=False, name=None):
        digest.update(repr(row).encode("utf-8"))
        digest.update(b"\n")
    return digest.hexdigest()[:32]


def build_dataset_spec(
    frame: pd.DataFrame,
    *,
    symbol: str,
    provider: str,
    adjustment_policy: str = "unadjusted",
    classification: str = "raw",
    feature_set_id: str | None = None,
    target_definition: str | None = None,
) -> DatasetSpec:
    """Construct a DatasetSpec with a content-derived dataset_id."""
    dates = pd.to_datetime(frame["date"])
    start = dates.min().date()
    end = dates.max().date()
    # end_date on DatasetSpec is exclusive half-open convention for ranges;
    # for identity we store inclusive last observed date + 1 day when equal
    # would violate start < end. Prefer inclusive last bar as end_date and
    # bump by one day if needed for the contract invariant.
    end_exclusive = end if end > start else date.fromordinal(end.toordinal() + 1)
    fingerprint = fingerprint_ohlcv(frame, symbol=symbol, provider=provider)
    dataset_id = f"{provider.lower()}:{normalize_id(symbol)}:{fingerprint}"
    return DatasetSpec(
        dataset_id=dataset_id,
        symbol=symbol.strip().upper(),
        provider=provider.strip().lower(),
        start_date=start,
        end_date=end_exclusive,
        frequency="1d",
        classification=classification,
        adjustment_policy=adjustment_policy,
        feature_set_id=feature_set_id,
        target_definition=target_definition,
        source_metadata=f"schema={SCHEMA_VERSION};rows={len(frame)};last={end.isoformat()}",
    )


def normalize_id(symbol: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in symbol.strip().upper())
