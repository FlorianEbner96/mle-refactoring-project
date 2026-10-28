"""The full pipeline: load -> clean -> train/test split -> features -> model."""

from sklearn.compose import TransformedTargetRegressor
from sklearn.linear_model import ElasticNet
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, PolynomialFeatures, StandardScaler

from src.cleaning import clean_data, load_data
from src.features import WaterDistance, add_center_distance, drop_non_features


def build_feature_pipeline() -> Pipeline:
    """Takes a cleaned train/test frame (incl. price) and returns the final feature set."""
    return Pipeline(
        [
            ("center_distance", FunctionTransformer(add_center_distance)),
            ("water_distance", WaterDistance()),
            ("select_features", FunctionTransformer(drop_non_features)),
        ]
    )


def build_model() -> GridSearchCV:
    """Polynomial features + ElasticNet, tuned with 5-fold grid search (as in the notebook)."""
    elastic_pipeline = Pipeline(
        [
            ("polynomial", PolynomialFeatures(2, include_bias=False)),
            ("scaler", StandardScaler()),
            (
                "model",
                TransformedTargetRegressor(
                    regressor=ElasticNet(
                        max_iter=5000, tol=1e-4, precompute=True),
                    transformer=StandardScaler(),
                ),
            ),
        ]
    )
    param_grid = {
        "model__regressor__alpha": [0.01, 0.1, 1],
        "model__regressor__l1_ratio": [0.2, 0.5, 0.8],
    }
    return GridSearchCV(elastic_pipeline, param_grid, cv=5, scoring="r2", n_jobs=1)


def run_pipeline(path: str, test_size: float = 0.3, random_state: int = 42) -> dict:
    # 1. Load and clean the whole dataset
    df = clean_data(load_data(path))

    # 2. Train/test split
    df_train, df_test = train_test_split(
        df, test_size=test_size, random_state=random_state
    )
    y_train, y_test = df_train["price"], df_test["price"]

    # 3. Feature engineering, fitted on the training data only
    feature_pipeline = build_feature_pipeline()
    X_train = feature_pipeline.fit_transform(df_train)
    X_test = feature_pipeline.transform(df_test)

    # 4. Model training and evaluation
    model = build_model().fit(X_train, y_train)

    return {
        "feature_pipeline": feature_pipeline,
        "model": model,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "test_r2": model.score(X_test, y_test),
    }


if __name__ == "__main__":
    results = run_pipeline("data/King_County_House_prices_dataset.csv")
    print(f"Test R^2: {results['test_r2']:.4f}")
