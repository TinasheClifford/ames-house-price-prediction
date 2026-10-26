"""Reproduce the frozen training run without examining the holdout target.
Author: Tinashe Clifford Makandise
"""
import argparse
import hashlib
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from src.modeling import make_model_pipeline

ROOT = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True, help='Original AmesHousing.txt')
    parser.add_argument('--output', type=Path, default=ROOT/'retrained-output')
    args = parser.parse_args()
    metadata = json.loads((ROOT/'models/model_metadata.json').read_text(encoding='utf-8'))
    selection = json.loads((ROOT/'reports/selected_model_config.json').read_text(encoding='utf-8'))
    if sklearn.__version__ != metadata['versions']['scikit_learn']:
        raise ValueError('Install the pinned scikit-learn version before reproducing training.')
    if hashlib.sha256(args.data.read_bytes()).hexdigest() != metadata['source_sha256']:
        raise ValueError('Source bytes differ from the documented original dataset. Do not reuse published metrics for different data.')
    data = pd.read_csv(args.data, sep='\t', keep_default_na=False, na_values=[''])
    assert data.shape == (2930,82) and data['PID'].is_unique
    training, _ = train_test_split(data, test_size=.2, random_state=42)
    training = training.sort_values('Order').copy()
    c = selection['configuration']
    if c['family'] != 'RandomForestRegressor':
        raise ValueError('This reproduction script supports the frozen Random Forest configuration.')
    model = make_model_pipeline(RandomForestRegressor(n_estimators=c['n_estimators'],
        min_samples_leaf=c['min_samples_leaf'], random_state=c['random_state'], n_jobs=1),
        expanded=c['expanded'], scale_numeric=c['scale_numeric'])
    X = training.drop(columns='SalePrice')
    model.fit(X, training['SalePrice'])
    # Confirm reproduction of the exported reference pipeline on training inputs.
    reference = joblib.load(ROOT/'models/house_price_pipeline.joblib')
    np.testing.assert_allclose(model.predict(X), reference.predict(X), rtol=1e-10, atol=1e-8)
    destination = args.output.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    model_path = destination/'house_price_pipeline.joblib'
    joblib.dump(model, model_path)
    restored = joblib.load(model_path)
    np.testing.assert_allclose(model.predict(X.iloc[:5]),restored.predict(X.iloc[:5]))
    metadata['model_sha256'] = hashlib.sha256(model_path.read_bytes()).hexdigest()
    metadata['reproduction_note'] = 'Recreated frozen training split and settings; published test metrics are reference results from Notebook 5, not recalculated here.'
    (destination/'model_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    print(f'Reproduced training on {len(training):,} rows; reference predictions match.')
    print(f'Saved model and metadata in {destination}. No test target evaluated.')

if __name__ == '__main__':
    main()
