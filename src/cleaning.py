"""Data cleaning steps from the King County notebook, as reusable functions."""

import numpy as np
import pandas as pd

MAX_PLAUSIBLE_BEDROOMS = 20


def load_data(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def drop_implausible_rows(
    df: pd.DataFrame, max_bedrooms: int = MAX_PLAUSIBLE_BEDROOMS
) -> pd.DataFrame:
    """Drop data-entry errors (the notebook's 33-bedroom house)."""
    return df[df["bedrooms"] <= max_bedrooms].copy()


def rebuild_sqft_basement(df: pd.DataFrame) -> pd.DataFrame:
    """Recompute `sqft_basement` as living area minus above-ground area (removes the '?' values)."""
    df = df.copy()
    df["sqft_basement"] = df["sqft_living"] - df["sqft_above"]
    return df


def fill_missing_with_zero(
    df: pd.DataFrame, columns: tuple[str, ...] = ("view", "waterfront")
) -> pd.DataFrame:
    """Fill missing values with 0, the dominant value of these columns."""
    df = df.copy()
    df[list(columns)] = df[list(columns)].fillna(0)
    return df


def add_last_known_change(df: pd.DataFrame) -> pd.DataFrame:
    """Combine `yr_built` and `yr_renovated` into `last_known_change` and drop both."""
    df = df.copy()
    not_renovated = df["yr_renovated"].isna() | (df["yr_renovated"] == 0)
    df["last_known_change"] = np.where(
        not_renovated, df["yr_built"], df["yr_renovated"]
    ).astype(int)
    return df.drop(columns=["yr_renovated", "yr_built"])


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """The full cleaning step, run on the whole dataset before the train/test split.

    Nothing here is learned from the data, so it cannot leak test information.
    """
    df = drop_implausible_rows(df)
    df = rebuild_sqft_basement(df)
    df = fill_missing_with_zero(df)
    return add_last_known_change(df)
