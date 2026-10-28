"""Feature engineering from the King County notebook."""

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

# Rough "center of wealth": the Bill Gates residence in Medina.
CENTER_LAT = 47.62774
CENTER_LONG = -122.24194
EARTH_RADIUS_KM = 6378

# Columns that are not model inputs (target, identifier, raw date).
NON_FEATURE_COLUMNS = ["price", "date", "id"]


def distance_km(long, lat, ref_long, ref_lat):
    """Approximate distance in km to a reference location (longitude corrected by cos(lat)).
    """
    delta_long_corr = (long - ref_long) * np.cos(np.radians(ref_lat))
    delta_lat = lat - ref_lat
    return np.hypot(delta_long_corr, delta_lat) * 2 * np.pi * EARTH_RADIUS_KM / 360


def add_center_distance(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["center_distance"] = distance_km(
        df["long"], df["lat"], CENTER_LONG, CENTER_LAT)
    return df


class WaterDistance(BaseEstimator, TransformerMixin):
    """Add `water_distance`: distance to the nearest waterfront house seen during `fit`.

    Fit on training data only, so test and new houses are measured against the
    same reference set.
    """

    def fit(self, X: pd.DataFrame, y=None):
        waterfront = X[X["waterfront"] == 1]
        if waterfront.empty:
            raise ValueError(
                "No waterfront houses to use as reference points.")
        self.ref_long_ = waterfront["long"].to_numpy()
        self.ref_lat_ = waterfront["lat"].to_numpy()
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        distances = distance_km(
            X["long"].to_numpy()[:, None],
            X["lat"].to_numpy()[:, None],
            self.ref_long_[None, :],
            self.ref_lat_[None, :],
        )
        X["water_distance"] = distances.min(axis=1)
        return X


def drop_non_features(df: pd.DataFrame) -> pd.DataFrame:
    """Final feature selection: remove the target, the identifier and the raw date."""
    return df.drop(columns=NON_FEATURE_COLUMNS)
