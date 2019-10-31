from restclients_core import models


class Major(models.Model):
    major_abbr = models.CharField(max_length=32)
    begin_academic_qtr_key_id = models.IntegerField()
    major_pathway = models.IntegerField()
    display_name = models.CharField(max_length=255)
