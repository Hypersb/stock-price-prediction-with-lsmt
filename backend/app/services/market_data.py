"""Market-data application service wrapping ingestion domain logic."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from backend.app.core.cache import TtlCache
from backend.app.core.config import Settings, get_settings
from backend.app.core.errors import BadRequestError, NotFoundError
from backend.app.core.json_utils import to_iso_date, to_json_number
from backend.app.schemas.market_data import MarketDataResponse, OhlcvObservation
from ml.data.ingestion import MarketDataIngestionService
from ml.data.provider import MarketDataProvider
from ml.data.requests import MarketDataRequest
from ml.data.validation import MarketDataValidationError


def _default_provider() -> MarketDataProvider:
    from ml.data.yahoo import YahooFinanceProvider

    return YahooFinanceProvider()


class MarketDataService:
    """Adapt validated API requests to the existing ingestion service."""

    def __init__(
        self,
        provider: MarketDataProvider | None = None,
        settings: Settings | None = None,
        cache: TtlCache[list[OhlcvObservation]] | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.provider = provider or _default_provider()
        self.ingestion = MarketDataIngestionService(self.provider)
        self._cache = cache or TtlCache[list[OhlcvObservation]](
            max_size=self.settings.market_data_cache_max_size,
            ttl_seconds=self.settings.market_data_cache_ttl_seconds,
        )

    def get_ohlcv(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> MarketDataResponse:
        try:
            request = MarketDataRequest.create(symbol, start_date, end_date)
        except (TypeError, ValueError) as exc:
            raise BadRequestError(str(exc)) from exc

        span_days = (request.end_date - request.start_date).days
        if span_days > self.settings.max_market_data_days:
            raise BadRequestError(
                "requested date range exceeds configured maximum of "
                f"{self.settings.max_market_data_days} days"
            )
        if offset < 0:
            raise BadRequestError("offset must be non-negative")

        row_limit = self.settings.max_market_rows if limit is None else limit
        if row_limit < 1:
            raise BadRequestError("limit must be at least 1")
        row_limit = min(row_limit, self.settings.max_market_rows)

        cache_key = (request.symbol, request.start_date, request.end_date)
        observations = self._cache.get(cache_key)
        if observations is None:
            observations = self._fetch_observations(request)
            self._cache.set(cache_key, observations)

        total = len(observations)
        page = observations[offset : offset + row_limit]
        return MarketDataResponse(
            symbol=request.symbol,
            start_date=request.start_date,
            end_date=request.end_date,
            total=total,
            count=len(page),
            limit=row_limit,
            offset=offset,
            returned=len(page),
            data=page,
        )

    def _fetch_observations(self, request: MarketDataRequest) -> list[OhlcvObservation]:
        try:
            frame = self.ingestion.ingest(
                request.symbol, request.start_date, request.end_date
            )
        except MarketDataValidationError as exc:
            message = str(exc)
            if "must not be empty" in message:
                raise NotFoundError(
                    f"no market data found for symbol {request.symbol}"
                ) from exc
            raise BadRequestError(message) from exc
        except ValueError as exc:
            raise BadRequestError(str(exc)) from exc

        return [
            OhlcvObservation(
                date=date.fromisoformat(to_iso_date(row["date"])),
                open=float(to_json_number(row["open"])),
                high=float(to_json_number(row["high"])),
                low=float(to_json_number(row["low"])),
                close=float(to_json_number(row["close"])),
                volume=float(to_json_number(row["volume"])),
            )
            for _, row in frame.iterrows()
        ]


def default_market_data_service() -> MarketDataService:
    """Factory used by FastAPI dependency injection."""
    return MarketDataService()


def ensure_default_end_date(end_date: date | None) -> date:
    """Default the exclusive-style end bound to tomorrow when omitted."""
    if end_date is not None:
        return end_date
    return datetime.now(timezone.utc).date() + timedelta(days=1)
