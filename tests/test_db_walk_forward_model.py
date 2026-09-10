from datetime import date

from backend.app.db.base import Base
from backend.app.db.models import Experiment, WalkForwardFold, WalkForwardRun
from backend.app.db.session import build_database


def test_walk_forward_run_persists_fold_metadata() -> None:
    database = build_database("sqlite:///:memory:")
    Base.metadata.create_all(database.engine)

    experiment = Experiment(
        symbol="AAPL",
        task="regression",
        model_name="lstm",
        target_name="future_return_1",
        forecast_horizon=1,
        feature_count=10,
        status="completed",
    )
    with database.create_session() as session:
        session.add(experiment)
        session.flush()
        run = WalkForwardRun(
            experiment_id=experiment.id,
            symbol="AAPL",
            model_name="lstm",
            task="regression",
            window_type="expanding",
            initial_train_size=100,
            validation_size=20,
            test_size=20,
            step_size=20,
            gap=1,
            forecast_horizon=1,
        )
        session.add(run)
        session.flush()
        session.add(
            WalkForwardFold(
                run_id=run.id,
                fold_number=1,
                train_start=date(2020, 1, 1),
                train_end=date(2020, 5, 1),
                validation_start=date(2020, 5, 2),
                validation_end=date(2020, 6, 1),
                test_start=date(2020, 6, 2),
                test_end=date(2020, 7, 1),
                train_count=100,
                validation_count=20,
                test_count=20,
                best_epoch=4,
                fold_metrics={"rmse": 0.05, "mae": None},
            )
        )
        session.commit()
        loaded = session.get(WalkForwardRun, run.id)
        assert loaded is not None
        assert loaded.window_type == "expanding"
        assert len(loaded.folds) == 1
        assert loaded.folds[0].fold_number == 1
        assert loaded.folds[0].fold_metrics == {"rmse": 0.05, "mae": None}

    database.engine.dispose()
