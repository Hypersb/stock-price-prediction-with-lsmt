"""Feature engineering application service."""

from __future__ import annotations

import re
from datetime import date

import pandas as pd

from backend.app.core.config import Settings, get_settings
from backend.app.core.errors import BadRequestError
from backend.app.core.json_utils import to_iso_date, to_json_number
from backend.app.schemas.features import FeatureObservation, FeatureResponse
from backend.app.services.market_data import MarketDataService
from ml.data.provider import MarketDataProvider
from ml.features.pipeline import build_features
from ml.features.validation import FeatureValidationError, validate_features

_FORBIDDEN_FEATURE_PATTERN = re.compile(r"(?i)(target|future|direction_|shift_-)")
_OHLCV_COLUMNS = {"open", "high", "low", "close", "volume"}


class FeatureService:
    """Expose leakage-aware feature engineering for research inspection."""

    def __init__(
        self,
        market_data_service: MarketDataService | None = None,
        provider: MarketDataProvider | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        if market_data_service is not None:
            self.market_data_service = market_data_service
        else:
            self.market_data_service = MarketDataService(provider=provider)

    def get_features(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        *,
        limit: int | None = None,
        offset: int | None = None,
    ) -> FeatureResponse:
        if offset is not None and offset < 0:
            raise BadRequestError("offset must be non-negative")

        # Features need the full chronological series for rolling windows; page after.
        market = self.market_data_service.get_ohlcv(
            symbol,
            start_date,
            end_date,
            limit=self.settings.max_market_rows,
            offset=0,
        )
        if market.total > market.returned:
            raise BadRequestError(
                "feature engineering requires the full market series within "
                f"MAX_MARKET_ROWS ({self.settings.max_market_rows}); narrow the date range"
            )

        frame = pd.DataFrame([row.model_dump() for row in market.data])
        try:
            engineered = build_features(frame)
            validate_features(engineered)
        except (TypeError, ValueError, FeatureValidationError) as exc:
            raise BadRequestError(str(exc)) from exc

        feature_names = [
            column
            for column in engineered.columns
            if column != "date" and column not in _OHLCV_COLUMNS
        ]
        forbidden = [
            name for name in feature_names if _FORBIDDEN_FEATURE_PATTERN.search(name)
        ]
        if forbidden:
            raise BadRequestError(f"forbidden feature columns detected: {forbidden}")

        row_limit = limit if limit is not None else self.settings.max_feature_rows
        if row_limit < 1:
            raise BadRequestError("limit must be at least 1")
        row_limit = min(row_limit, self.settings.max_feature_rows)

        total = len(engineered)
        if offset is None:
            # Research-inspection default: latest rows (preserves prior API behavior).
            effective_offset = max(0, total - row_limit)
        else:
            effective_offset = offset
        page = engineered.iloc[effective_offset : effective_offset + row_limit]
        observations: list[FeatureObservation] = []
        for _, row in page.iterrows():
            values = {
                name: to_json_number(row[name])
                for name in feature_names
            }
            observations.append(
                FeatureObservation(
                    date=date.fromisoformat(to_iso_date(row["date"])),
                    values=values,
                )
            )

        return FeatureResponse(
            symbol=market.symbol,
            start_date=market.start_date,
            end_date=market.end_date,
            feature_names=feature_names,
            feature_count=len(feature_names),
            observation_count=total,
            limit=row_limit,
            offset=effective_offset,
            returned_rows=len(observations),
            features=observations,
        )
