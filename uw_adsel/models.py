from restclients_core import models


class Major(models.Model):
    major_abbr = models.CharField(max_length=32)
    begin_academic_qtr_key_id = models.IntegerField()
    major_pathway = models.IntegerField()
    display_name = models.CharField(max_length=255)


class Quarter(models.Model):
    id = models.IntegerField()
    begin = models.DateTimeField()
    end = models.DateTimeField()
    active_ind = models.CharField(max_length=32)
    appl_yr = models.CharField(max_length=4)
    appl_qtr = models.CharField(max_length=1)
