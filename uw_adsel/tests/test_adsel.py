from unittest import TestCase, mock
from restclients_core.exceptions import DataFailureException
from uw_adsel.utilities import fdao_adsel_override
from uw_adsel import AdSel
from uw_adsel.models import CohortAssignment, MajorAssignment, Application,\
    PurpleGoldApplication, PurpleGoldAssignment
from datetime import datetime


def mocked_get_now():
    dt = datetime(2019, 11, 12, 0, 10, 21)
    return dt


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
        self.assertEqual(majors[1].major_abbr, "CHEM")
        majors_unpaginated = self.adsel.get_majors_by_qtr(1)
        self.assertEqual(len(majors_unpaginated), 2)

    @mock.patch('uw_adsel.AdSel.get_now', side_effect=mocked_get_now)
    def test_get_quarters(self, mock_obj):
        quarters = self.adsel.get_quarters()
        self.assertEqual(len(quarters), 2)
        self.assertEqual(quarters[0].begin, datetime(2019, 11, 5, 0, 0, 0))
        self.assertFalse(quarters[1].is_current)
        self.assertTrue(quarters[0].is_current)

    def test_get_cohorts(self):
        cohorts = self.adsel.get_cohorts_by_qtr(0)
        self.assertEqual(len(cohorts), 2)
        self.assertEqual(cohorts[1].cohort_description,
                         "This is another cohort")
        cohorts_unpaginated = self.adsel.get_cohorts_by_qtr(1)
        self.assertEqual(len(cohorts_unpaginated), 2)

    @mock.patch('uw_adsel.AdSel.get_now', side_effect=mocked_get_now)
    def test_get_now(self, mock_obj):
        self.assertEqual(self.adsel.get_now(),
                         datetime(2019, 11, 12, 0, 10, 21))

    def test_get_activities(self):
        activities = self.adsel.get_activities()
        self.assertEqual(len(activities), 4)
        self.assertEqual(activities[0].user, "javerage")

    def test_get_filtered_activities(self):
        # netid filter
        activities = self.adsel.get_filtered_activities(netid="javerage")
        self.assertEqual(len(activities), 2)
        # No results
        activities = self.adsel.get_filtered_activities(netid="foo")
        self.assertEqual(len(activities), 0)
        # dual filter
        activities = self.adsel.get_filtered_activities(netid="javerage",
                                                        system_key=12345)
        self.assertEqual(len(activities), 4)

    def test_get_application(self):
        applications = self.adsel.get_applications_by_qtr_syskey(0, 123)
        self.assertEqual(len(applications), 4)
        self.assertEqual(applications[0].adsel_id, 1)

    def test_post(self):
        a1 = Application()
        a1.adsel_id = 123
        a1.system_key = 41
        a1.application_number = 1
        a2 = Application()
        a2.adsel_id = 734
        a2.system_key = 34
        a2.application_number = 5

        cohort_assign = CohortAssignment()
        cohort_assign.applicants = [a1, a2]
        cohort_assign.assignment_type = "upload"
        cohort_assign.cohort_number = 1
        cohort_assign.override_protected = True
        cohort_assign.override_previous = False
        cohort_assign.quarter = 0
        cohort_assign.campus = 1
        cohort_assign.comments = "My comment"
        cohort_assign.user = "javerage"

        cohort_json = cohort_assign.json_data()
        self.assertEqual(cohort_json['overridePreviousCohort'], False)
        self.assertEqual(cohort_json['overridePreviousProtectedCohort'], True)

        try:
            submission = self.adsel.assign_cohorts_bulk(cohort_assign)
        except Exception:
            self.fail('assign_cohorts raised an exception')

        major_assign = MajorAssignment()
        major_assign.applicants = [a1, a2]
        major_assign.assignment_type = "upload"
        major_assign.major_code = "CSE"
        major_assign.quarter = 0
        major_assign.campus = 1
        major_assign.comments = "My comment"
        major_assign.user = "javerage"

        major_json = major_assign.json_data()
        self.assertEqual(len(major_json['applicants']), 2)
        self.assertEqual(major_json['applicants'][0]['admissionSelectionId'],
                         123)

        try:
            submission = self.adsel.assign_majors(major_assign)
        except Exception:
            self.fail('assign_majors raised an exception')

    def test_get_all_app(self):
        apps = self.adsel.get_all_applications_by_qtr(0)
        self.assertEqual(len(apps), 4)

    def test_purple_gold_assignment(self):
        a1 = PurpleGoldApplication()
        a1.adsel_id = 123
        a1.system_key = 41
        a1.application_number = 1
        a1.award_amount = 1000
        a2 = PurpleGoldApplication()
        a2.adsel_id = 734
        a2.system_key = 34
        a2.application_number = 5
        a2.award_amount = 2000

        purple_gold_assign = PurpleGoldAssignment()
        purple_gold_assign.applicants = [a1, a2]
        purple_gold_assign.assignment_type = "upload"
        purple_gold_assign.quarter = 0
        purple_gold_assign.campus = 1
        purple_gold_assign.comments = "My comment"
        purple_gold_assign.user = "javerage"

        json_data = purple_gold_assign.json_data()
        self.assertEqual(json_data['applicants'][0]['awardAmount'], 1000)

        try:
            submission = self.adsel.assign_purple_gold(purple_gold_assign)
        except Exception:
            self.fail('assign_purple_gold raised an exception')
