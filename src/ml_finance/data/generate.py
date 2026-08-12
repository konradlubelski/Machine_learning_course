import numpy as np
from numpy.typing import NDArray

def generate_normal_sample(
        seed: int
        ,sample_size: int = 1000
        ,mean: float = 0
        ,standard_deviation: float = 1.0
) -> NDArray[np.float64]:
    if sample_size <= 0:
        raise ValueError("Sample size must be greater than zero.")
    if standard_deviation <= 0:
        raise ValueError("Standard deviation must be greater than zero.")
    
    rng = np.random.default_rng(seed) 

    return rng.normal(loc = mean
                      , scale = standard_deviation
                      , size = sample_size)

if __name__ == "__main__":
    sample = generate_normal_sample(seed=42)

    print(f"Shape: {sample.shape}")
    print(f"First five values: {sample[:5]}")
    print(f"Mean: {sample.mean():.4f}")
    print(f"Standard deviation: {sample.std():.4f}")

