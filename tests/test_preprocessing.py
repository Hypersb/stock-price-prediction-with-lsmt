import numpy as np
import pandas as pd

from ml.preprocessing import TrainOnlyScaler


def test_scaler_parameters_use_training_data_only() -> None:
    train = pd.DataFrame({"feature": [1.0, 2.0, 3.0]})
    validation = pd.DataFrame({"feature": [100.0, 200.0]})
    scaler = TrainOnlyScaler.create()

    train_scaled = scaler.fit_transform(train)
    validation_scaled = scaler.transform(validation)

    assert np.isclose(scaler.scaler.mean_[0], 2.0)
    assert np.isclose(train_scaled["feature"].mean(), 0.0)
    assert validation_scaled["feature"].mean() > 100.0