from django.db import models

# Create your models here.
class CaptchaRecord(models.Model):
    id = models.IntegerField(primary_key=True)
    hash = models.CharField(max_length=40)
    user = models.CharField(max_length=30, default="")
    time = models.DateTimeField(auto_now_add=True)
    pic = models.CharField(max_length=30)
    answer = models.CharField(max_length=30)
    wrong_times = models.IntegerField(default=0)
    correct = models.IntegerField(default=0)
