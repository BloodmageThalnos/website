from django.db import models
from mainApp.models import *

# Create your models here.

class VisitModel(models.Model):
    url = models.CharField(max_length=20)
    v_time = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField()
    user_ip = models.CharField(max_length=16)
    duration = models.IntegerField()
