from unittest import TestCase
from uw_adsel.utilities import fdao_zoom_override
from uw_adsel import AdSel
from datetime import datetime


@fdao_zoom_override
class AdselTest(TestCase):
    adsel = AdSel()

    def test_request_headers(self):
        self.assertEqual(self.adsel._headers(), {'Accept': 'application/json'})

    def test_get_majors(self):
        majors = self.adsel.get_majors()
        self.assertEqual(len(majors), 2)
        self.assertEqual(majors[0].major_abbr, "BIOL")

    def test_get_quarters(self):
        quarters = self.adsel.get_quarters()
        self.assertEqual(len(quarters), 2)
        self.assertEqual(quarters[0].begin, datetime(2019, 11, 5, 0, 0, 0))
