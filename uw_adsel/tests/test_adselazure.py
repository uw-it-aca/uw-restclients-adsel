from unittest import TestCase
from uw_adsel import AdSelAzure
from uw_adsel.models import (CohortAssignment, MajorAssignment,
                             PurpleGoldAssignment)


class AdselTest(TestCase):
    adsel = AdSelAzure()

    def test_bulk_assign(self):
        cohort = CohortAssignment(cohort_number=1, campus=2)
        submit = self.adsel.assign_cohorts_bulk(cohort)
        self.assertEqual(submit["response"], {'string_response': ''})

    def test_pugo_assign(self):
        pugo = PurpleGoldAssignment(pugo_code="12345", campus=2)
        submit = self.adsel.assign_pugo(pugo)
        test_id = submit["response"]['Applicants'][0]['AdmissionSelectionId']
        self.assertEqual(test_id, 281620)

    def test_major_assign(self):
        major = MajorAssignment(major_code="0_BIOL_1", campus=2)
        submit = self.adsel.assign_majors(major)
        test_id = submit["response"]['Applicants'][0]['AdmissionSelectionId']
        self.assertEqual(test_id, 321620)
