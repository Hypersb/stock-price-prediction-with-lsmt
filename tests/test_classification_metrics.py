import numpy as np

from ml.evaluation.classification import evaluate_classification


def test_classification_metrics_and_roc_auc() -> None:
    metrics = evaluate_classification(
        np.array([0, 0, 1, 1]),
        np.array([0, 1, 1, 1]),
        np.array([[0.8, 0.2], [0.4, 0.6], [0.3, 0.7], [0.1, 0.9]]),
    )

    assert metrics["accuracy"] == 0.75
    assert metrics["confusion_matrix"].tolist() == [[1, 1], [0, 2]]
    assert metrics["roc_auc"] == 1.0


def test_classification_metrics_do_not_fabricate_single_class_auc() -> None:
    metrics = evaluate_classification(np.array([0, 0]), np.array([0, 0]), np.array([0.1, 0.2]))

    assert metrics["roc_auc"] is None