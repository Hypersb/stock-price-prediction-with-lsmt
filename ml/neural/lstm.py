"""Configurable PyTorch LSTM architectures for forecasting."""

import torch
from torch import nn


class LSTMRegressor(nn.Module):
    """Predict one continuous future return from a lookback sequence."""

    def __init__(
        self,
        input_size: int,
        hidden_size: int = 64,
        num_layers: int = 1,
        dropout: float = 0.0,
    ) -> None:
        super().__init__()
        _validate_architecture(input_size, hidden_size, num_layers, dropout)
        recurrent_dropout = dropout if num_layers > 1 else 0.0
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=recurrent_dropout,
            batch_first=True,
        )
        self.output = nn.Linear(hidden_size, 1)

    def forward(self, sequences: torch.Tensor) -> torch.Tensor:
        """Return one scalar regression output per batch item."""
        recurrent_output, _ = self.lstm(sequences)
        final_hidden = recurrent_output[:, -1, :]
        return self.output(final_hidden).squeeze(-1)


def _validate_architecture(input_size: int, hidden_size: int, num_layers: int, dropout: float) -> None:
    if any(isinstance(value, bool) or not isinstance(value, int) or value <= 0 for value in (input_size, hidden_size, num_layers)):
        raise ValueError("input_size, hidden_size, and num_layers must be positive integers")
    if not 0.0 <= dropout < 1.0:
        raise ValueError("dropout must be in the range [0, 1)")