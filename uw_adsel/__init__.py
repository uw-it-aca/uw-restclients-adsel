"""
This is the interface for interacting with the AdSel Web Service.
"""

import json
import logging
from restclients_core.exceptions import DataFailureException
from restclients_core.dao import MockDAO
from uw_adsel.dao import ADSEL_DAO
from uw_adsel.models import Major, Cohort, Quarter, Activity, Application
import dateutil.parser
from datetime import datetime
import urllib.parse


logger = logging.getLogger(__name__)

# max page size 300
PAGE_SIZE = 300
MAJOR_TYPE = "major"
COHORT_TYPE = "cohort"


class AdSel(object):
    """
    The AdSel object has methods for interacting with the AdSel API.
    """
    API = '/api/v1'

    def __init__(self, config={}):
        self.DAO = ADSEL_DAO()

    def assign_majors(self, major_assignment):
        url = "{}/assignments/major".format(self.API)
        request = major_assignment.json_data()
        response = self._post_resource(url, request)
        return {"response": response, "request": request}

    def assign_cohorts_bulk(self, cohort_assignment):
        url = "{}/assignments/cohort/bulk".format(self.API)
        request = cohort_assignment.json_data()
        response = self._post_resource(url, request)
        return {"response": response, "request": request}

    def assign_cohorts_manual(self, cohort_assignment):
        url = "{}/assignments/cohort".format(self.API)
        request = cohort_assignment.json_data()
        response = self._post_resource(url, request)
        return {"response": response, "request": request}

    def assign_purple_gold(self, pg_assignments):
        url = "{}/assignments/purpleAndGold".format(self.API)
        request = pg_assignments.json_data()
        response = self._post_resource(url, request)
        return {"response": response, "request": request}

    def get_quarters(self, **kwargs):
        url = "{}/academicqtr".format(self.API)
        response = self._get_resource(url)
        quarters = self._quarters_from_json(response)
        return quarters

    def get_now(self):
        return datetime.now()

    def _quarters_from_json(self, response):
        quarters = []
        for quarter in response:
            qtr = Quarter()
            qtr.id = quarter["academicQtrKeyId"]
            qtr.begin = dateutil.parser.parse(quarter["activeQtrBeginDttm"])
            qtr.end = dateutil.parser.parse(quarter["activeQtrEndDttm"])
            qtr.active_ind = quarter["activeInd"]
            qtr.appl_yr = quarter["appl_yr"]
            qtr.appl_qtr = quarter["appl_qtr"]
            qtr.is_current = (qtr.begin < self.get_now() < qtr.end)
            quarters.append(qtr)
        return quarters

    def get_all_applications_by_qtr(self, quarter_id):
        url = "{}/applications/{}/all".format(self.API, quarter_id)
        response = self._get_resource(url)
        applications = self._get_applications_from_json(response)
        return applications

    def get_applications_by_qtr_syskey(self, quarter_id, syskey):
        url = "{}/applications/{}/{}".format(self.API, quarter_id, syskey)
        response = self._get_resource(url)
        application = self._get_applications_from_json(response)
        return application

    def get_applications_by_qtr_syskey_list(self, quarter_id, syskey_list):
        if isinstance(self.DAO.get_implementation(), MockDAO):
            all_applications = self._get_live_apps_by_qtr_syskey_list(
                quarter_id,
                syskey_list)
            return [app for app in all_applications
                    if app.system_key in syskey_list]
        else:
            return self._get_live_apps_by_qtr_syskey_list(quarter_id,
                                                          syskey_list)

    def _get_live_apps_by_qtr_syskey_list(self, quarter_id, syskey_list):
        url = "{}/applications/SystemKeys/{}".format(self.API, quarter_id)
        response = self._post_resource(url, syskey_list)
        applications = self._get_applications_from_json(response)
        return applications

    def _get_applications_from_json(self, response):
        applications = []
        for app in response:
            application = Application()
            application.adsel_id = app['admissionsSelectionId']
            application.application_number = app['applicationNbr']
            application.system_key = app['systemKey']
            application.campus = app['campus']
            application.quarter_id = app['academicQtrKeyId']
            application.assigned_cohort = app['assignedCohort']
            application.assigned_major = app['assignedMajor']
            application.major_program_code = app['majorProgramCode']
            applications.append(application)
        return applications

    def get_filtered_activities(self,
                                netid=None,
                                assignment_type=None,
                                cohort=None,
                                major=None,
                                start_date=None,
                                end_date=None,
                                system_key=None,
                                adsel_id=None,
                                collection_type=None,
                                assignment_period=None,
                                comment=None):
        url = "{}/activities".format(self.API)
        filters = {}
        if netid is not None:
            filters['netid'] = netid
        if assignment_type is not None:
            filters['assignmentType'] = assignment_type
        if cohort is not None:
            filters['cohort'] = cohort
        if major is not None:
            filters['major'] = major
        if start_date is not None:
            filters['startDate'] = start_date
        if end_date is not None:
            filters['endDate'] = end_date
        if system_key is not None:
            filters['systemKey'] = system_key
        if adsel_id is not None:
            filters['admissionSelectionId'] = adsel_id
        if collection_type is not None:
            filters['collectionType'] = collection_type
        if assignment_period is not None:
            filters['assignmentPeriod'] = assignment_period
        if comment is not None:
            filters['comment'] = comment
        filter_url = urllib.parse.urlencode(filters)
        if len(filter_url) > 0:
            url = url + "?" + filter_url
        try:
            response = self._get_resource(url)
            return self._activities_from_json(response)
        except DataFailureException:
            return []

    def get_activities(self, **kwargs):
        return self.get_filtered_activities()

    def _activities_from_json(self, response):
        activities = []
        for activity in response['decisions']:
            acty = Activity()
            acty.assignment_date = \
                dateutil.parser.parse(activity['assignmentMadeOn'])
            acty.comment = activity['comment']
            acty.user = activity['assignmentMadeBy']
            acty.assignment_type = activity['assignmentType']
            acty.cohort_number = activity['cohortNbr']
            acty.major_abbr = activity['majorAbbr']
            acty.major_program_code = activity['majorProgramCode']
            acty.total_submitted = activity['totalSubmitted']
            acty.total_assigned = activity['totalAssigned']
            activities.append(acty)
        return activities

    def get_cohorts_by_qtr(self, quarter_id, **kwargs):
        url = "{}/cohorts/{}".format(self.API, quarter_id)
        response = self._get_resource(url)
        cohorts = self._cohorts_from_json(response)
        return cohorts

    def _cohorts_from_json(self, response):
        cohorts = []
        for cohort in response['cohorts']:
            cohort_model = Cohort()
            cohort_model.academic_qtr_id = cohort['academicQtrKeyId']
            cohort_model.cohort_number = cohort['cohortNbr']
            cohort_model.cohort_description = cohort['cohortDescription']
            cohort_model.cohort_residency = cohort['cohortResidency']
            cohort_model.admit_decision = cohort['admitDecision']
            cohort_model.protected_group = cohort['protectedGroupInd']
            cohort_model.active_cohort = cohort['activeCohortInd']
            cohort_model.assigned_count = cohort['assignedCount']
            cohorts.append(cohort_model)
        return cohorts

    def get_majors_by_qtr(self, quarter_id, **kwargs):
        majors = self._get_majors_by_page(quarter_id, 1, [])
        return majors

    def _get_majors_by_page(self, quarter_id, page, major_list=[]):
        url = "{}/majors/details/{}?Page={}&Limit=100".format(self.API,
                                                              quarter_id,
                                                              page)
        response = self._get_resource(url)
        majors = self._majors_from_json(response)
        major_list += majors
        if response['nextPage'] is not None:
            self._get_majors_by_page(quarter_id, page+1, major_list)
        return major_list

    def _majors_from_json(self, response):
        majors = []
        for major_data in response['majors']:
            major = Major()
            major.major_abbr = major_data['majorAbbr']
            major.program_code = major_data['majorProgramCode']
            major.academic_qtr_key_id = major_data['academicQtrKeyId']
            major.major_pathway = major_data['majorPathway']
            major.display_name = major_data['displayName']
            major.college = major_data['college']
            major.division = major_data['division']
            major.dtx = major_data['dtx']
            major.assigned_count = major_data['assignedCount']

            majors.append(major)
        return majors

    def _get_resource(self, url):
        response = self.DAO.getURL(url, self._headers())

        if response.status != 200:
            self._log_error(url, response)
            raise DataFailureException(url, response.status, response.data)

        return json.loads(response.data)

    def _post_resource(self, url, request):
        response = self.DAO.postURL(url,
                                    self._post_headers(),
                                    body=json.dumps(request))
        if response.status not in [200, 201]:
            self._log_error(url, response)
            raise DataFailureException(url, response.status, response.data)

        return json.loads(response.data)

    def _headers(self):
        headers = {"Accept": "application/json"}
        return headers

    def _post_headers(self):
        headers = {'Content-Type': 'application/json'}
        return headers

    def _log_error(self, url, response):
        logger.error("{0} ==> status:{1} data:{2}".format(
            url, response.status, response.data))
