from django.db import models
from mainApp.models import *

# Create your models here.

class VisitModel(models.Model):
    url = models.CharField(max_length=20)
    v_time = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField()
    user_ip = models.CharField(max_length=16)
    duration = models.IntegerField()
    b_id = models.CharField(max_length=64)


def id_(str):
    ret = ''
    for i in range(0,len(str),2):
        ret+=chr((ord(str[i])<<5)+ord(str[i|1])-(1623 if str[i|1].isalpha() else 1584)) if str[i]<'e' else 'e' if str[i]<'y' else 'a'
    return ret