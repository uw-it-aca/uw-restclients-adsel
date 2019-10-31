"""
This is the interface for interacting with the Group Web Service.
"""

import json
import logging
from restclients_core.exceptions import DataFailureException
from uw_adsel.dao import ADSEL_DAO
from uw_adsel.models import Major


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

    def get_majors(self, **kwargs):
        url = "{}/majors".format(self.API)
        response = self._get_resource(url)
        majors = self._majors_from_json(response)
        return majors

    def _majors_from_json(self, response):
        majors = []
        for major_data in response:
            major = Major()
            major.major_abbr = major_data['majorAbbr']
            major.begin_academic_qtr_key_id = \
                major_data['beginAcademicQtrKeyId']
            major.major_pathway = major_data['majorPathway']
            major.display_name = major_data['displayName']
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
