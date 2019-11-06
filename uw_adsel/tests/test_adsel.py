from unittest import TestCase
from restclients_core.exceptions import DataFailureException
from uw_adsel.utilities import fdao_zoom_override
from uw_adsel import AdSel
from datetime import datetime


@fdao_zoom_override
class AdselTest(TestCase):
    adsel = AdSel()

    def test_request_headers(self):
        self.assertEqual(self.adsel._headers(), {'Accept': 'application/json'})

    def test_error(self):
        with self.assertRaises(DataFailureException):
            self.adsel._get_resource("/foobar/")

    def test_get_majors(self):
        majors = self.adsel.get_majors()
        self.assertEqual(len(majors), 2)
        self.assertEqual(majors[0].major_abbr, "BIOL")

    def test_get_quarters(self):
        quarters = self.adsel.get_quarters()
        self.assertEqual(len(quarters), 2)
        self.assertEqual(quarters[0].begin, datetime(2019, 11, 5, 0, 0, 0))

    def test_get_cohorts(self):
        cohorts = self.adsel.get_cohorts_by_qtr(0)
        self.assertEqual(len(cohorts), 4)
        self.assertEqual(cohorts[2].cohort_description, "Second Page Cohort")
