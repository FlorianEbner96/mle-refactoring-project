import numpy as np
import pandas as pd
import pytest

from src.features import (
    CENTER_LAT,
    CENTER_LONG,
    WaterDistance,
    add_center_distance,
    distance_km,
    drop_non_features,
)


def test_distance_km_zero_for_same_point():
    assert distance_km(-122.2, 47.6, -122.2, 47.6) == 0


def test_distance_km_one_degree_latitude_is_about_111_km():
    assert distance_km(-122.0, 48.6, -122.0,
                       47.6) == pytest.approx(111.3, abs=0.5)


def test_distance_km_is_symmetric_in_latitude():
    assert distance_km(-122.0, 47.0, -122.0, 48.0) == pytest.approx(
        distance_km(-122.0, 49.0, -122.0, 48.0)
    )


def test_distance_km_broadcasts():
    result = distance_km(
        np.array([[-122.0], [-122.1]]),
        np.array([[47.0], [47.1]]),
        np.array([[-122.0, -122.2]]),
        np.array([[47.0, 47.2]]),
    )
    assert result.shape == (2, 2)


def test_add_center_distance_is_zero_at_center():
    df = pd.DataFrame({"lat": [CENTER_LAT], "long": [CENTER_LONG]})
    assert add_center_distance(
        df)["center_distance"].iloc[0] == pytest.approx(0)


def test_add_center_distance_grows_with_distance():
    df = pd.DataFrame(
        {"lat": [CENTER_LAT, CENTER_LAT + 0.5], "long": [CENTER_LONG] * 2}
    )
    result = add_center_distance(df)["center_distance"]
    assert result.iloc[1] > result.iloc[0]


def test_add_center_distance_does_not_mutate_input():
    df = pd.DataFrame({"lat": [47.5], "long": [-122.3]})
    add_center_distance(df)
    assert "center_distance" not in df.columns


@pytest.fixture
def water_df():
    return pd.DataFrame(
        {
            "waterfront": [1, 0, 0],
            "lat": [47.60, 47.60, 47.70],
            "long": [-122.30, -122.30, -122.30],
        }
    )


def test_water_distance_is_zero_for_waterfront_reference(water_df):
    result = WaterDistance().fit(water_df).transform(water_df)
    assert result["water_distance"].iloc[0] == 0


def test_water_distance_measures_nearest_reference(water_df):
    result = WaterDistance().fit(water_df).transform(water_df)
    # 0.1 degrees latitude north of the single reference point
    assert result["water_distance"].iloc[2] == pytest.approx(11.13, abs=0.1)


def test_water_distance_uses_references_from_fit_not_transform(water_df):
    transformer = WaterDistance().fit(water_df)
    # a new waterfront house far from the reference must not become its own reference
    new = pd.DataFrame({"waterfront": [1], "lat": [47.90], "long": [-122.30]})
    assert transformer.transform(new)["water_distance"].iloc[0] > 30


def test_water_distance_fit_without_waterfront_raises(water_df):
    with pytest.raises(ValueError):
        WaterDistance().fit(water_df.assign(waterfront=0))


def test_water_distance_does_not_mutate_input(water_df):
    WaterDistance().fit(water_df).transform(water_df)
    assert "water_distance" not in water_df.columns


def test_drop_non_features_removes_price_date_and_id(raw_df):
    result = drop_non_features(raw_df)
    for col in ("price", "date", "id"):
        assert col not in result.columns
    assert "bedrooms" in result.columns
