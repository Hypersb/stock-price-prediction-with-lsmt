"""Structured training-history tracking and visualization."""

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class TrainingHistory:
    """Record training and validation losses by epoch."""

    records: list[dict[str, float]] = field(default_factory=list)

    def append(self, epoch: int, training_loss: float, validation_loss: float) -> None:
        self.records.append(
            {"epoch": epoch, "training_loss": training_loss, "validation_loss": validation_loss}
        )

    def to_frame(self) -> pd.DataFrame:
        """Return history as a simple visualization-friendly DataFrame."""
        return pd.DataFrame(self.records, columns=["epoch", "training_loss", "validation_loss"])