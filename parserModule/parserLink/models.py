from django.db import models


class dbLog(models.Model):
    ipAddress = models.CharField(max_length=15, db_index=True)
    dateLog = models.DateTimeField()
    httpMethod = models.CharField(max_length=10, db_index=True)
    uriLog = models.TextField()
    numError = models.IntegerField()
    sizeAnswer = models.IntegerField()

    def __str__(self):
        return self.ipAddress
