from unittest import TestCase
from uw_adsel import AdSelAzure
from uw_adsel.models import CohortAssignment


class AdselTest(TestCase):
    adsel = AdSelAzure()

    def test_assign_cohort(self):
        cohort = CohortAssignment(cohort_number=1, campus=2)
        submit = self.adsel.assign_cohorts_manual(cohort)
        self.assertEqual(submit['response']['summaryPostStatus'],
                         "AzureSubmitSuccess")
