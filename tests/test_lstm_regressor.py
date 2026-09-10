import torch

from ml.neural.lstm import LSTMRegressor


def test_lstm_regressor_forward_shape_and_gradients() -> None:
    model = LSTMRegressor(input_size=3, hidden_size=5, num_layers=2, dropout=0.1)
    sequences = torch.randn(4, 6, 3, requires_grad=True)

    outputs = model(sequences)
    outputs.sum().backward()

    assert outputs.shape == torch.Size([4])
    assert all(parameter.grad is not None for parameter in model.parameters())


def test_lstm_regressor_preserves_batch_dimension_for_batch_one() -> None:
    model = LSTMRegressor(input_size=2)

    outputs = model(torch.randn(1, 4, 2))

    assert outputs.shape == torch.Size([1])