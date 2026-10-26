"""Unfitted model-pipeline factories. Author: Tinashe Clifford Makandise."""
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from .features import build_features, CORE_NUMERIC, EXPANDED_NUMERIC, CATEGORICAL

def make_preprocessor(expanded=False, scale_numeric=True):
    numeric = EXPANDED_NUMERIC if expanded else CORE_NUMERIC
    steps = [("impute", SimpleImputer(strategy="median"))]
    if scale_numeric:
        steps.append(("scale", StandardScaler()))
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("encode", OneHotEncoder(handle_unknown="ignore", drop=None)),
    ])
    return ColumnTransformer([
        ("numeric", Pipeline(steps), numeric),
        ("categorical", categorical, CATEGORICAL),
    ], remainder="drop")

def make_model_pipeline(estimator, expanded=False, scale_numeric=True):
    return Pipeline([
        ("features", FunctionTransformer(build_features, validate=False)),
        ("preprocess", make_preprocessor(expanded, scale_numeric)),
        ("model", estimator),
    ])
