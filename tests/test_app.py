"""Run with: python -m unittest discover -s tests -v"""
from pathlib import Path
import sys
import unittest
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.app_support import load_artifacts, prepare_property
from streamlit.testing.v1 import AppTest

class ApplicationChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.metadata, cls.coverage, _ = load_artifacts(ROOT)
        cls.values = {'Gr Liv Area': 1500, 'Bedroom AbvGr': 3, 'Full Bath': 2,
            'Half Bath': 1, 'Garage Cars': 2, 'Neighborhood': 'NAmes',
            'Yr Sold': 2009, 'Year Built': 1990, 'Overall Qual': 6, 'Overall Cond': 5}

    def test_validation_and_coverage(self):
        frame, warnings = prepare_property(self.values, self.metadata, self.coverage)
        self.assertTrue(np.isfinite(self.model.predict(frame)).all())
        for change in [{'Year Built': 2010}, {'Bedroom AbvGr': 2.5},
                       {'Gr Liv Area': float('nan')}, {'Neighborhood': 'Unknown'}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                prepare_property(dict(self.values, **change), self.metadata, self.coverage)
        _, warnings = prepare_property(dict(self.values, **{'Gr Liv Area': 9000}), self.metadata, self.coverage)
        self.assertTrue(warnings)

    def test_prediction_and_invalid_form(self):
        app = AppTest.from_file(str(ROOT/'app.py'), default_timeout=30).run()
        self.assertEqual(len(app.exception), 0)
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        result = app.session_state['estimate_result']
        frame, _ = prepare_property(result['inputs'], self.metadata, self.coverage)
        self.assertAlmostEqual(result['estimated_price_usd'], self.model.predict(frame)[0])
        # Future build year must show an error and remove the previous result.
        next(x for x in app.number_input if x.label == 'Year built').set_value(2010)
        next(x for x in app.selectbox if x.label == 'Historical sale year').select(2006)
        app.button[0].click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertGreater(len(app.error), 0)
        self.assertNotIn('estimate_result', app.session_state)

if __name__ == '__main__':
    unittest.main()
