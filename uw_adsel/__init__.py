"""
This is the interface for interacting with the AdSel Web Service.
"""

import json
import logging
from restclients_core.exceptions import DataFailureException
from uw_adsel.dao import ADSEL_DAO
from uw_adsel.models import Major, Cohort, Quarter
import dateutil.parser
from datetime import datetime


logger = logging.getLogger(__name__)

# max page size 300
PAGE_SIZE = 300


class AdSel(object):
    """
    The AdSel object has methods for interacting with the AdSel API.
    """
    API = '/api/v1'

    def __init__(self, config={}):
        self.DAO = ADSEL_DAO()

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

    def get_cohorts_by_qtr(self, quarter_id, **kwargs):
        url = "{}/cohorts/{}".format(self.API, quarter_id)
        response = self._get_resource(url)
        cohorts = self._cohorts_from_json(response)
        # TODO Confirm how pagination will work
        if response['totalCount'] > 1:
            cohort_page = 2
            while cohort_page <= response['totalCount']:
                page_cohorts = self.get_cohorts_by_qtr_page(quarter_id,
                                                            cohort_page)
                cohorts.extend(page_cohorts)
                cohort_page += 1
        return cohorts

    def get_cohorts_by_qtr_page(self, quarter_id, page, **kwargs):
        url = "{}/cohorts/{}?Page={}".format(self.API, quarter_id, page)
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
        url = "{}/majors/details/{}".format(self.API, quarter_id)
        response = self._get_resource(url)
        majors = self._majors_from_json(response)
        # TODO Confirm how pagination will work
        if response['totalCount'] > 1:
            major_page = 2
            while major_page <= response['totalCount']:
                page_majors = self.get_majors_by_qtr_page(quarter_id,
                                                          major_page)
                majors.extend(page_majors)
                major_page += 1
        return majors

    def get_majors_by_qtr_page(self, quarter_id, page, **kwargs):
        url = "{}/majors/details/{}?Page={}".format(self.API, quarter_id, page)
        response = self._get_resource(url)
        majors = self._majors_from_json(response)
        return majors

    def _majors_from_json(self, response):
        majors = []
        for major_data in response['majors']:
            major = Major()
            major.major_abbr = major_data['majorAbbr']
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

    def _headers(self):
        headers = {"Accept": "application/json"}
        return headers

    def _log_error(self, url, response):
        logger.error("{0} ==> status:{1} data:{2}".format(
            url, response.status, response.data))
