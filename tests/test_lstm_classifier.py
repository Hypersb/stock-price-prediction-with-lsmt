import torch

from ml.neural.lstm import LSTMClassifier


def test_lstm_classifier_returns_logits_and_gradients() -> None:
    model = LSTMClassifier(input_size=3, hidden_size=5, num_layers=2, dropout=0.1)
    sequences = torch.randn(4, 6, 3, requires_grad=True)

    logits = model(sequences)
    logits.sum().backward()

    assert logits.shape == torch.Size([4])
    assert torch.isfinite(logits).all()
    assert all(parameter.grad is not None for parameter in model.parameters())


def test_lstm_classifier_preserves_batch_dimension_for_batch_one() -> None:
    logits = LSTMClassifier(input_size=2)(torch.randn(1, 4, 2))

    assert logits.shape == torch.Size([1])