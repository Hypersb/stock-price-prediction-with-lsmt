from datetime import date

from backend.app.db.base import Base
from backend.app.db.models import Experiment
from backend.app.db.session import build_database


def test_experiment_model_persists_metadata_without_weights() -> None:
    database = build_database("sqlite:///:memory:")
    Base.metadata.create_all(database.engine)

    experiment = Experiment(
        symbol="AAPL",
        task="regression",
        model_name="lstm",
        target_name="future_return_1",
        forecast_horizon=1,
        lookback=60,
        seed=42,
        feature_count=12,
        feature_names=["rsi_14", "macd"],
        model_configuration={"hidden_size": 64},
        training_configuration={"epochs": 10},
        status="completed",
        train_start=date(2020, 1, 1),
        train_end=date(2020, 6, 30),
        validation_start=date(2020, 7, 1),
        validation_end=date(2020, 9, 30),
        test_start=date(2020, 10, 1),
        test_end=date(2020, 12, 31),
        best_epoch=7,
        best_validation_loss=0.0123,
        checkpoint_reference="artifacts/checkpoints/lstm_aapl.pt",
    )

    with database.create_session() as session:
        session.add(experiment)
        session.commit()
        session.refresh(experiment)
        loaded = session.get(Experiment, experiment.id)

    assert loaded is not None
    assert loaded.symbol == "AAPL"
    assert loaded.model_name == "lstm"
    assert loaded.feature_names == ["rsi_14", "macd"]
    assert loaded.model_configuration == {"hidden_size": 64}
    assert loaded.checkpoint_reference.endswith(".pt")
    assert not hasattr(loaded, "weights")
    assert loaded.created_at is not None
    assert loaded.updated_at is not None

    database.engine.dispose()
