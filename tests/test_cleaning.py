import pandas as pd

from src.cleaning import (
    add_last_known_change,
    clean_data,
    drop_implausible_rows,
    fill_missing_with_zero,
    rebuild_sqft_basement,
)


def test_drop_implausible_rows_removes_33_bedrooms(raw_df):
    result = drop_implausible_rows(raw_df)
    assert 33 not in result["bedrooms"].values
    assert len(result) == len(raw_df) - 1


def test_drop_implausible_rows_does_not_mutate_input(raw_df):
    drop_implausible_rows(raw_df)
    assert len(raw_df) == 4


def test_rebuild_sqft_basement_replaces_question_mark(raw_df):
    result = rebuild_sqft_basement(raw_df)
    assert result["sqft_basement"].tolist() == [0, 400, 0, 200]
    assert pd.api.types.is_numeric_dtype(result["sqft_basement"])


def test_fill_missing_with_zero(raw_df):
    result = fill_missing_with_zero(raw_df)
    assert result[["view", "waterfront"]].isna().sum().sum() == 0
    assert result["waterfront"].iloc[0] == 0


def test_fill_missing_keeps_existing_values(raw_df):
    result = fill_missing_with_zero(raw_df)
    assert result["view"].iloc[2] == 2.0


def test_last_known_change_uses_renovation_year_when_present(raw_df):
    result = add_last_known_change(raw_df)
    assert result["last_known_change"].iloc[1] == 1991
    assert result["last_known_change"].iloc[3] == 2005


def test_last_known_change_falls_back_to_build_year_for_nan_and_zero(raw_df):
    result = add_last_known_change(raw_df)
    assert result["last_known_change"].iloc[0] == 1955  # NaN
    assert result["last_known_change"].iloc[2] == 1990  # 0


def test_last_known_change_drops_source_columns(raw_df):
    result = add_last_known_change(raw_df)
    assert "yr_built" not in result.columns
    assert "yr_renovated" not in result.columns


def test_clean_data_runs_all_steps(raw_df):
    result = clean_data(raw_df)
    assert len(result) == len(raw_df) - 1  # 33-bedroom row dropped
    assert result.isna().sum().sum() == 0
    assert "last_known_change" in result.columns
    assert "yr_built" not in result.columns
