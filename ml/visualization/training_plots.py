"""Plots for neural training history."""

import matplotlib.pyplot as plt

from ml.training.history import TrainingHistory


def plot_training_history(history: TrainingHistory) -> tuple[plt.Figure, plt.Axes]:
    """Return a training-versus-validation loss figure without displaying it."""
    frame = history.to_frame()
    figure, axes = plt.subplots()
    axes.plot(frame["epoch"], frame["training_loss"], label="training")
    axes.plot(frame["epoch"], frame["validation_loss"], label="validation")
    axes.set_xlabel("Epoch")
    axes.set_ylabel("Loss")
    axes.set_title("Training history")
    axes.legend()
    return figure, axes