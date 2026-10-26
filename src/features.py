"""Shared property feature construction. Author: Tinashe Clifford Makandise."""
import numpy as np
import pandas as pd

CORE_NUMERIC = ["Gr Liv Area", "Bedroom AbvGr", "Full Bath", "Half Bath", "AgeAtSale", "Garage Cars"]
EXPANDED_NUMERIC = CORE_NUMERIC + ["Overall Qual", "Overall Cond"]
CATEGORICAL = ["Neighborhood"]
RAW_CORE = ["Gr Liv Area", "Bedroom AbvGr", "Full Bath", "Half Bath", "Year Built", "Yr Sold", "Garage Cars", "Neighborhood"]

def build_features(frame):
    """Derive age at sale and select supported inputs without learning statistics."""
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("Pass a pandas DataFrame with named property columns.")
    missing = sorted(set(RAW_CORE) - set(frame.columns))
    if missing:
        raise ValueError(f"Required columns missing: {missing}")
    out = frame.copy()
    numeric = [c for c in RAW_CORE if c != "Neighborhood"]
    numeric += [c for c in ["Overall Qual", "Overall Cond"] if c in out.columns]
    for col in numeric:
        original = out[col]
        converted = pd.to_numeric(original, errors="coerce")
        invalid = original.notna() & converted.isna()
        if invalid.any():
            raise ValueError(f"Non-numeric values in {col}")
        if np.isinf(converted).any():
            raise ValueError(f"Infinite values in {col}")
        out[col] = converted.astype(float)
    out["AgeAtSale"] = (out["Yr Sold"] - out["Year Built"]).where(out["Yr Sold"] >= out["Year Built"])
    nonnegative = ["Bedroom AbvGr", "Full Bath", "Half Bath", "Garage Cars"]
    if out[nonnegative].lt(0).any().any() or out["Gr Liv Area"].le(0).any():
        raise ValueError("Area must be positive; counts and age must be nonnegative.")
    for col in ["Overall Qual", "Overall Cond"]:
        if col in out and (~out[col].between(1, 10) & out[col].notna()).any():
            raise ValueError(f"{col} must be between 1 and 10.")
    out["Neighborhood"] = out["Neighborhood"].map(
        lambda v: np.nan if pd.isna(v) or str(v).strip() in ("", "NA") else str(v).strip()
    )
    selected = CORE_NUMERIC + [c for c in ["Overall Qual", "Overall Cond"] if c in out] + CATEGORICAL
    return out[selected]
