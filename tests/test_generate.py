import numpy as np
import pytest

from ml_finance.data.generate import generate_normal_sample

def test_generate_normal_sample_has_expected_size() -> None:
    sample = generate_normal_sample(seed = 42, sample_size = 1000)

    assert sample.shape == (1000,)

def test_same_seed_produces_identical_samples() -> None:
    first_sample = generate_normal_sample(seed = 42)
    second_sample = generate_normal_sample(seed = 42)

    assert np.array_equal(first_sample, second_sample)

def test_different_seeds_produce_different_samples() -> None:
    first_sample = generate_normal_sample(seed=42)
    second_sample = generate_normal_sample(seed=123)

    assert not np.array_equal(first_sample, second_sample)

def test_zero_sample_size_raises_value_error() -> None:
    with pytest.raises(ValueError, match = "Sample size must be greater than zero.",):
        generate_normal_sample(sample_size = 0, seed = 42)

def test_negative_sample_size_raises_value_error() -> None:
    with pytest.raises(ValueError):
        generate_normal_sample(sample_size = -10, seed = 42)

def test_non_positive_standard_deviation_raises_error() -> None:
    with pytest.raises(ValueError, match = "Standard deviation must be greater than zero."):
        generate_normal_sample(seed = 42, standard_deviation = 0.0)
