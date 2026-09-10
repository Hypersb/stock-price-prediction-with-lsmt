import random

import numpy as np
import pytest
import torch

from ml.neural.reproducibility import set_random_seed


def test_random_seed_repeats_python_numpy_and_torch_values() -> None:
    set_random_seed(42)
    first = (random.random(), np.random.rand(), torch.rand(1).item())
    set_random_seed(42)
    second = (random.random(), np.random.rand(), torch.rand(1).item())

    assert first == second


def test_random_seed_requires_integer() -> None:
    with pytest.raises(ValueError, match="integer"):
        set_random_seed("42")