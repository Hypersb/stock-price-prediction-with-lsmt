import pandas as pd

from ml.validation.preprocessing import preprocess_fold


def test_fold_preprocessing_ignores_large_validation_and_test_values() -> None:
    train = pd.DataFrame({"feature": [1.0, 2.0, 3.0]})
    validation = pd.DataFrame({"feature": [1_000_000.0]})
    test = pd.DataFrame({"feature": [2_000_000.0]})

    result = preprocess_fold(train, validation, test)

    assert result.preprocessor.scaler.mean_[0] == 2.0
    assert result.X_validation.iloc[0, 0] > 100_000