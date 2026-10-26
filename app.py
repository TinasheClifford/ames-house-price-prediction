"""Historical Ames house price demo. Author: Tinashe Clifford Makandise."""
from pathlib import Path
import json
import numpy as np
import streamlit as st
from src.app_support import load_artifacts, prepare_property

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='Ames House Price Estimator', page_icon='🏠', layout='wide')

@st.cache_resource
def get_resources():
    return load_artifacts(ROOT)

st.title('🏠 Ames House Price Estimator')
st.caption('A machine learning portfolio project by Tinashe Clifford Makandise')
st.info('Explore historical sale prices in Ames, Iowa (2006–2010). Estimates are in historical USD and do not represent current market values.')
try:
    model, metadata, coverage, locations = get_resources()
except (OSError, ValueError, KeyError) as exc:
    st.error(f'Unable to load the application: {exc}')
    st.stop()

estimate_tab, performance_tab = st.tabs(['Estimate a property', 'Model performance'])
with estimate_tab:
    st.subheader('Property details')
    st.write('Enter above-ground living area and room counts. Garage capacity measures spaces inside a garage.')
    with st.form('property_form'):
        left, right = st.columns(2)
        with left:
            area = st.number_input('Above-ground living area (sq ft)', min_value=1.0, value=1500.0, step=50.0)
            bedrooms = st.number_input('Above-ground bedrooms', min_value=0, value=3, step=1)
            full = st.number_input('Above-ground full bathrooms', min_value=0, value=2, step=1)
            half = st.number_input('Above-ground half bathrooms', min_value=0, value=1, step=1)
            garage = st.number_input('Garage capacity (cars)', min_value=0, value=2, step=1)
        with right:
            neighborhood = st.selectbox('Ames neighbourhood code', metadata['supported_neighborhoods'], index=metadata['supported_neighborhoods'].index('NAmes'))
            st.caption('Codes follow the Ames dataset. NAmes means North Ames.')
            sale_year = st.selectbox('Historical sale year', metadata['sale_year_options'], index=3)
            built = st.number_input('Year built', min_value=1, max_value=2010, value=1990, step=1)
            quality = st.slider('Overall material and finish quality', min_value=1, max_value=10, value=6)
            condition = st.slider('Overall condition', min_value=1, max_value=10, value=5)
            st.caption('Ratings: 1 = very poor, 5 = average, 10 = very excellent. Use the original data dictionary for definitions.')
        submitted = st.form_submit_button('Estimate historical price', type='primary')
    if submitted:
        st.session_state.pop('estimate_result', None)
        values = {'Gr Liv Area': area, 'Bedroom AbvGr': bedrooms, 'Full Bath': full,
                  'Half Bath': half, 'Garage Cars': garage, 'Neighborhood': neighborhood,
                  'Yr Sold': sale_year, 'Year Built': built, 'Overall Qual': quality, 'Overall Cond': condition}
        try:
            frame, cautions = prepare_property(values, metadata, coverage)
            prediction = float(model.predict(frame)[0])
            if not np.isfinite(prediction) or prediction <= 0:
                raise ValueError('This property did not produce a valid positive estimate.')
            count = int(locations.set_index('Neighborhood').loc[neighborhood, 'training_count'])
            if count < 20:
                cautions.append(f'This neighbourhood has only {count} training sales; evidence is limited.')
            st.session_state['estimate_result'] = {'inputs': values, 'estimated_price_usd': prediction,
                'age_at_sale': sale_year-built, 'training_neighborhood_count': count, 'cautions': cautions,
                'scope': metadata['scope'], 'author': metadata['author']}
        except ValueError as exc:
            st.error(str(exc))
    if 'estimate_result' in st.session_state:
        result = st.session_state['estimate_result']
        st.divider()
        st.subheader('Last submitted estimate')
        st.metric('Estimated historical sale price', f"${result['estimated_price_usd']:,.0f} USD")
        st.caption(f"Submitted property: {result['inputs']['Neighborhood']} · sale year {result['inputs']['Yr Sold']} · age at sale {result['age_at_sale']} years")
        for caution in result['cautions']:
            st.warning(caution)
        st.write('The held-out average absolute error was about $19,311. Individual errors can be much larger; this is not a guaranteed range or a prediction interval.')
        with st.expander('Review the submitted inputs'):
            st.json(result['inputs'])
        st.download_button('Download this estimate (JSON)', data=json.dumps(result, indent=2),
                           file_name='ames_property_estimate.json', mime='application/json')

with performance_tab:
    st.subheader('Held-out evaluation')
    a, b, c = st.columns(3)
    a.metric('Mean absolute error', f"${metadata['test_metrics']['mae']:,.0f}")
    b.metric('Root mean squared error', f"${metadata['test_metrics']['rmse']:,.0f}")
    c.metric('R²', f"{metadata['test_metrics']['r2']:.3f}")
    st.write(f"Random Forest with quality and condition features. Trained on {metadata['train_rows']:,} properties and evaluated on {metadata['test_rows']:,} separate properties. The test set was not used to fit the exported model.")
    st.write(f"MAE was {metadata['holdout_mae_improvement_percent']:.1f}% lower than a baseline predicting the training median. R² is not a percentage of predictions that are correct.")
    chart = ROOT / 'reports/figures/05_test_diagnostics.png'
    if chart.exists():
        st.image(str(chart), caption='Held-out predictions and residual diagnostics')
    st.subheader('Scope and limitations')
    for limitation in metadata['limitations']:
        st.write('• ' + limitation)
    st.write('The app has no calibrated prediction interval. It has not been validated for current prices, other cities, South Africa or Zimbabwe.')
    st.markdown('[Original Ames Housing study](https://jse.amstat.org/v19n3/decock.pdf) · [Data dictionary](https://jse.amstat.org/v19n3/decock/DataDocumentation.txt)')
