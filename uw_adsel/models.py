from restclients_core import models


class Major(models.Model):
    major_abbr = models.CharField(max_length=32)
    program_code = models.CharField(max_length=128)
    academic_qtr_key_id = models.IntegerField()
    major_pathway = models.IntegerField()
    display_name = models.CharField(max_length=255)
    college = models.CharField(max_length=255)
    division = models.CharField(max_length=255)
    dtx = models.CharField(max_length=255)
    assigned_count = models.IntegerField()
    assigned_resident = models.IntegerField(null=True)
    assigned_nonresident = models.IntegerField(null=True)
    assigned_international = models.IntegerField(null=True)


class Cohort(models.Model):
    academic_qtr_id = models.IntegerField()
    cohort_number = models.IntegerField()
    cohort_description = models.TextField()
    cohort_residency = models.CharField(max_length=255)
    admit_decision = models.CharField(max_length=255)
    protected_group = models.BooleanField()
    active_cohort = models.BooleanField()
    assigned_count = models.IntegerField()


class Decision(models.Model):
    academic_qtr_id = models.IntegerField()
    display_name = models.CharField(max_length=255)
    assigned_count = models.IntegerField()
    decision_id = models.CharField(max_length=128)


class Quarter(models.Model):
    id = models.IntegerField()
    begin = models.DateTimeField()
    end = models.DateTimeField()
    active_ind = models.CharField(max_length=32)
    appl_yr = models.CharField(max_length=4)
    appl_qtr = models.CharField(max_length=1)
    is_current = models.BooleanField()


class Activity(models.Model):
    assignment_date = models.DateTimeField()
    comment = models.TextField()
    user = models.CharField(max_length=12)
    assignment_type = models.TextField()
    cohort_number = models.IntegerField()
    major_abbr = models.CharField(max_length=32)
    major_program_code = models.CharField(max_length=32)
    total_submitted = models.IntegerField()
    total_assigned = models.IntegerField()


class Application(models.Model):
    adsel_id = models.IntegerField()
    application_number = models.IntegerField()
    system_key = models.IntegerField()
    campus = models.IntegerField()
    quarter_id = models.IntegerField()
    assigned_cohort = models.IntegerField()
    assigned_major = models.CharField(max_length=32)
    major_program_code = models.CharField(max_length=255)

    def json_data(self):
        return {'admissionSelectionId': int(self.adsel_id),
                'applicationNbr': self.application_number,
                'systemKey': int(self.system_key)}


class PurpleGoldApplication(Application):
    award_amount = models.IntegerField()

    def json_data(self):
        return {'admissionSelectionId': int(self.adsel_id),
                'awardAmount': self.award_amount}


class Assignment(models.Model):
    assignment_type = models.CharField()
    quarter = models.IntegerField()
    campus = models.IntegerField()
    comments = models.TextField()
    user = models.CharField(max_length=12)
    applicants = []


class CohortAssignment(Assignment):
    cohort_number = models.IntegerField()
    override_previous = models.BooleanField()
    override_protected = models.BooleanField()

    def json_data(self):
        applicant_json = []
        for application in self.applicants:
            applicant_json.append(application.json_data())
        return {'applicants': applicant_json,
                'cohortNbr': int(self.cohort_number),
                'overridePreviousCohort': self.override_previous,
                'overridePreviousProtectedCohort': self.override_protected,
                'assignmentDetail': {'assignmentType': self.assignment_type,
                                     'academicQtrKeyId': self.quarter,
                                     'campus': int(self.campus),
                                     'comments': self.comments,
                                     'decisionImportUser': self.user}
                }


class MajorAssignment(Assignment):
    major_code = models.CharField()

    def json_data(self):
        applicant_json = []
        for application in self.applicants:
            applicant_json.append(application.json_data())
        return {'applicants': applicant_json,
                'majorProgramCode': self.major_code,
                'assignmentDetail': {'assignmentType': self.assignment_type,
                                     'academicQtrKeyId': self.quarter,
                                     'campus': int(self.campus),
                                     'comments': self.comments,
                                     'decisionImportUser': self.user}
                }


class PurpleGoldAssignment(Assignment):
    def json_data(self):
        applicant_json = []
        for application in self.applicants:
            applicant_json.append(application.json_data())
        return {'applicants': applicant_json,
                'assignmentDetail': {'assignmentType': self.assignment_type,
                                     'academicQtrKeyId': self.quarter,
                                     'comments': self.comments,
                                     'decisionImportUser': self.user}
                }
