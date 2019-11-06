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
        majors = self.adsel.get_majors_by_qtr(0)
        self.assertEqual(len(majors), 4)
        self.assertEqual(majors[2].major_abbr, "CSE")
        majors_unpaginated = self.adsel.get_majors_by_qtr(1)
        self.assertEqual(len(majors_unpaginated), 2)

    def test_get_quarters(self):
        quarters = self.adsel.get_quarters()
        self.assertEqual(len(quarters), 2)
        self.assertEqual(quarters[0].begin, datetime(2019, 11, 5, 0, 0, 0))

    def test_get_cohorts(self):
        cohorts = self.adsel.get_cohorts_by_qtr(0)
        self.assertEqual(len(cohorts), 4)
        self.assertEqual(cohorts[2].cohort_description, "Second Page Cohort")
        cohorts_unpaginated = self.adsel.get_cohorts_by_qtr(1)
        self.assertEqual(len(cohorts_unpaginated), 2)
