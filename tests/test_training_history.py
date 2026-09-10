import matplotlib

matplotlib.use("Agg")

from ml.training.history import TrainingHistory
from ml.visualization.training_plots import plot_training_history


def test_training_history_records_and_plots_losses() -> None:
    history = TrainingHistory()
    history.append(1, 0.5, 0.6)
    history.append(2, 0.3, 0.4)

    frame = history.to_frame()
    figure, axes = plot_training_history(history)

    assert frame.to_dict("records") == [
        {"epoch": 1.0, "training_loss": 0.5, "validation_loss": 0.6},
        {"epoch": 2.0, "training_loss": 0.3, "validation_loss": 0.4},
    ]
    assert len(axes.lines) == 2
    figure.clear()