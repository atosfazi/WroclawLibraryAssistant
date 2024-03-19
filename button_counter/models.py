from django.db import models

class ClickCounter(models.Model):
    count = models.IntegerField(default=0)