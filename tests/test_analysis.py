"""Regression and metamorphic checks for the scientific unit of analysis."""
import sys, unittest, json, zipfile
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from analyze import cohort, cluster_bootstrap_difference, ROOT

class AnalysisChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with zipfile.ZipFile(ROOT/'data/raw/food-enforcement.json.zip') as z:
            cls.records=json.loads(z.read(z.namelist()[0]))['results']
        cls.raw,cls.selected,cls.events=cohort(cls.records)

    def test_no_product_pseudoreplication(self):
        e=self.events.set_index('event_id')
        self.assertEqual(len(e),81)
        self.assertEqual(e.loc['90667','n_products'],77)
        self.assertEqual(int((e.classification=='Class I').sum()),22)

    def test_record_order_invariance(self):
        _,_,e=cohort(list(reversed(self.records)))
        self.assertEqual(self.events.to_json(),e.to_json())

    def test_duplicate_record_cannot_change_estimand(self):
        _,_,e=cohort(self.records+[self.records[0]])
        self.assertEqual(self.events.to_json(),e.to_json())

    def test_conflicting_duplicate_rejected(self):
        r=self.records[0].copy();r['classification']='invalid'
        with self.assertRaises(AssertionError):cohort(self.records+[r])

    def test_calendar_arithmetic_and_expansion(self):
        e=self.events.set_index('event_id')
        self.assertEqual(e.loc['63914','days'],1986)
        self.assertEqual(e.loc['97959','days'],39)
        self.assertTrue((e.days>=0).all())
        self.assertTrue((e.days==e.all_days).all())

    def test_threshold_partitions(self):
        e=self.events
        self.assertEqual(int((e.days<=30).sum()),20)
        self.assertEqual(int((e.days<=60).sum()),52)
        self.assertEqual(int((e.days<=90).sum()),64)
        self.assertAlmostEqual(e.loc[e.classification=='Class II','days'].median()-e.loc[e.classification=='Class I','days'].median(),-1.5)

    def test_bootstrap_reproducibility(self):
        d=self.events[self.events.classification.isin(['Class I','Class II'])]
        self.assertEqual(cluster_bootstrap_difference(d,100),cluster_bootstrap_difference(d,100))

if __name__=='__main__':unittest.main()
