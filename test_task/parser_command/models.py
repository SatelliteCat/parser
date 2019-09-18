from django.db import models


class Log(models.Model):
    """
    Класс описания модели данных лог файла
    """

    id = models.BigAutoField(primary_key=True, unique=True, null=False)
    ip_address = models.CharField(max_length=15, db_index=True)
    date_log = models.DateTimeField()
    http_method = models.CharField(max_length=10, null=True, db_index=True)
    uri_log = models.TextField(null=True)
    num_error = models.IntegerField(null=True)
    size_answer = models.IntegerField(null=True)

    def __str__(self):
        return self.ip_address
