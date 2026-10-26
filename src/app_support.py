"""Input validation and artifact loading for the Streamlit demo."""
from pathlib import Path
import hashlib
import json
import math
import joblib
import pandas as pd
import sklearn


def load_artifacts(root):
    root = Path(root)
    metadata = json.loads((root / 'models/model_metadata.json').read_text(encoding='utf-8'))
    path = root / 'models/house_price_pipeline.joblib'
    if hashlib.sha256(path.read_bytes()).hexdigest() != metadata['model_sha256']:
        raise ValueError('The saved model does not match its metadata. Restore both files from the same export.')
    if sklearn.__version__ != metadata['versions']['scikit_learn']:
        raise ValueError('Install the scikit-learn version in requirements.txt before loading this model.')
    model = joblib.load(path)
    coverage = pd.read_csv(root / 'reports/training_feature_coverage.csv', index_col='feature')
    locations = pd.read_csv(root / 'reports/app_neighborhood_counts.csv')
    return model, metadata, coverage, locations


def prepare_property(values, metadata, coverage):
    """Return a single raw-input row and coverage cautions; reject invalid values."""
    required = metadata['required_raw_inputs']
    missing = sorted(set(required) - set(values))
    if missing:
        raise ValueError('Missing inputs: ' + ', '.join(missing))
    clean = {}
    for key in required:
        if key == 'Neighborhood':
            value = str(values[key]).strip()
            if value not in metadata['supported_neighborhoods']:
                raise ValueError('Choose a neighbourhood represented in the training data.')
            clean[key] = value
            continue
        try:
            value = float(values[key])
        except (ValueError, TypeError):
            raise ValueError(f'{key} must be a number.') from None
        if not math.isfinite(value):
            raise ValueError(f'{key} must be a finite number.')
        if key != 'Gr Liv Area' and not value.is_integer():
            raise ValueError(f'{key} must be a whole number.')
        clean[key] = value
    if clean['Gr Liv Area'] <= 0:
        raise ValueError('Living area must be greater than zero.')
    for key in ['Bedroom AbvGr', 'Full Bath', 'Half Bath', 'Garage Cars']:
        if clean[key] < 0:
            raise ValueError('Room counts and garage capacity cannot be negative.')
    if clean['Yr Sold'] not in metadata['sale_year_options']:
        raise ValueError('Choose a historical sale year from 2006 to 2010.')
    if clean['Year Built'] < 1 or clean['Year Built'] > clean['Yr Sold']:
        raise ValueError('Build year must be positive and no later than the historical sale year.')
    for key in ['Overall Qual', 'Overall Cond']:
        if key in clean and not 1 <= clean[key] <= 10:
            raise ValueError('Quality and condition ratings must be between 1 and 10.')
    frame = pd.DataFrame([clean], columns=required)
    observed = dict(clean, AgeAtSale=clean['Yr Sold']-clean['Year Built'])
    cautions = []
    for key in coverage.index:
        if key in observed:
            lower, upper = coverage.loc[key, ['min', 'max']]
            if observed[key] < lower or observed[key] > upper:
                cautions.append(f'{key}: outside the training range ({lower:g}–{upper:g}).')
    return frame, cautions
