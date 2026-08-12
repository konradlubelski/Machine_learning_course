import platform
from datetime import datetime, timezone
from typing import Any
import numpy as np
import pandas as pd
from numpy.typing import NDArray
import sklearn
import json
from pathlib import Path

def create_experiment_metadata(
        sample: NDArray[np.float64]
        ,seed: int
) -> dict[str: Any]:
        return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "seed": seed,
        "sample_size": int(sample.size),
        "sample_mean": float(sample.mean()),
        "sample_standard_deviation": float(sample.std()),
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "scikit_learn_version": sklearn.__version__,
    }

def save_experiment_metadata(
    metadata: dict[str, Any],
    output_path: Path,
) -> None:

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
            ensure_ascii=False,
        )
    

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

    experimental_seed = 42

    sample = generate_normal_sample(seed=experimental_seed)

    metadata = create_experiment_metadata(sample = sample
                                          , seed=experimental_seed)
    
    save_experiment_metadata(metadata=metadata
                            ,output_path=Path("reports/experiments/experimental_seed_42.json"))


