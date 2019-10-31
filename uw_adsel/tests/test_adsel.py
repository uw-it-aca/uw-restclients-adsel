from unittest import TestCase
from uw_adsel.utilities import fdao_zoom_override
from uw_adsel import AdSel


@fdao_zoom_override
class AdselTest(TestCase):
    def test_request_headers(self):
        adsel = AdSel()
        self.assertEqual(adsel._headers(), {'Accept': 'application/json'})

    def test_get_majors(self):
        adsel = AdSel()
        majors = adsel.get_majors()
        self.assertEqual(len(majors), 2)
        self.assertEqual(majors[0].major_abbr, "BIOL")
