from datetime import date

from backend.app.db.base import Base
from backend.app.db.models import (
    Experiment,
    OutOfSamplePrediction,
    WalkForwardRun,
)
from backend.app.db.session import build_database


def test_out_of_sample_predictions_persist_with_indexes() -> None:
    database = build_database("sqlite:///:memory:")
    Base.metadata.create_all(database.engine)

    experiment = Experiment(
        symbol="AAPL",
        task="regression",
        model_name="linear_regression",
        target_name="future_return_1",
        forecast_horizon=1,
        feature_count=5,
        status="completed",
    )
    with database.create_session() as session:
        session.add(experiment)
        session.flush()
        run = WalkForwardRun(
            experiment_id=experiment.id,
            symbol="AAPL",
            model_name="linear_regression",
            task="regression",
            window_type="rolling",
            initial_train_size=50,
            validation_size=10,
            test_size=10,
            step_size=10,
            gap=0,
            forecast_horizon=1,
        )
        session.add(run)
        session.flush()
        prediction = OutOfSamplePrediction(
            walk_forward_run_id=run.id,
            experiment_id=experiment.id,
            fold=1,
            model_name="linear_regression",
            task="regression",
            symbol="AAPL",
            prediction_date=date(2020, 8, 3),
            realization_date=date(2020, 8, 4),
            actual_target=0.01,
            predicted_value=0.008,
            sample_kind="out_of_sample",
        )
        session.add(prediction)
        session.commit()
        loaded = session.get(OutOfSamplePrediction, prediction.id)
        assert loaded is not None
        assert loaded.sample_kind == "out_of_sample"
        assert loaded.symbol == "AAPL"
        assert loaded.prediction_date == date(2020, 8, 3)

    index_names = {index.name for index in OutOfSamplePrediction.__table__.indexes}
    assert any("symbol" in (name or "") for name in index_names)
    assert any("prediction_date" in (name or "") for name in index_names)

    database.engine.dispose()
