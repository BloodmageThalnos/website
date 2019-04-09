from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(VisitModel)
class VisitAdmin(admin.ModelAdmin):
    date_hierarchy = 'v_time'
    list_display = ('url', 'v_time', 'user_ip', 'duration')


# admin.site.register(VisitModel, VisitAdmin)