import os

# The API reads DB_CONN at import time. Force an in-memory database so tests
# can never touch a real one, even if a local .env exists.
os.environ["DB_CONN"] = "sqlite://"

import pandas as pd  # noqa: E402
import pytest  # noqa: E402


@pytest.fixture
def raw_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "date": ["10/13/2014"] * 4,
            "price": [200000.0, 500000.0, 750000.0, 300000.0],
            "bedrooms": [3, 4, 33, 2],
            "sqft_living": [1180, 2570, 1620, 900],
            "sqft_above": [1180, 2170, 1620, 700],
            "sqft_basement": ["0.0", "400.0", "?", "200.0"],
            "waterfront": [None, 0.0, 1.0, 1.0],
            "view": [0.0, None, 2.0, 0.0],
            "yr_built": [1955, 1951, 1990, 1980],
            "yr_renovated": [None, 1991.0, 0.0, 2005.0],
            "lat": [47.5112, 47.721, 47.62, 47.65],
            "long": [-122.257, -122.319, -122.24, -122.20],
        }
    )
