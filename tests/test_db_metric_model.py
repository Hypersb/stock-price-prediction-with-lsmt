from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.db.base import Base
from backend.app.db.metrics import normalize_metric_value
from backend.app.db.models import Experiment, ExperimentMetric
from backend.app.db.session import build_database


def test_experiment_metrics_are_normalized_and_unique_per_split() -> None:
    database = build_database("sqlite:///:memory:")
    Base.metadata.create_all(database.engine)

    experiment = Experiment(
        symbol="MSFT",
        task="classification",
        model_name="logistic_regression",
        target_name="direction_1",
        forecast_horizon=1,
        feature_count=8,
        status="completed",
        train_start=date(2020, 1, 1),
        train_end=date(2020, 6, 1),
    )

    with database.create_session() as session:
        session.add(experiment)
        session.flush()
        session.add_all(
            [
                ExperimentMetric(
                    experiment_id=experiment.id,
                    split="validation",
                    metric_name="rmse",
                    metric_value=normalize_metric_value(0.12),
                ),
                ExperimentMetric(
                    experiment_id=experiment.id,
                    split="test",
                    metric_name="directional_accuracy",
                    metric_value=normalize_metric_value(0.61),
                ),
                ExperimentMetric(
                    experiment_id=experiment.id,
                    split="test",
                    metric_name="roc_auc",
                    metric_value=normalize_metric_value(float("nan")),
                ),
            ]
        )
        session.commit()
        session.refresh(experiment)
        assert len(experiment.metrics) == 3
        values = {
            (metric.split, metric.metric_name): metric.metric_value
            for metric in experiment.metrics
        }
        assert values[("validation", "rmse")] == pytest.approx(0.12)
        assert values[("test", "roc_auc")] is None

        session.add(
            ExperimentMetric(
                experiment_id=experiment.id,
                split="validation",
                metric_name="rmse",
                metric_value=0.2,
            )
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

    database.engine.dispose()


def test_normalize_metric_value_rejects_non_numeric() -> None:
    with pytest.raises(ValueError, match="numeric"):
        normalize_metric_value("not-a-number")
