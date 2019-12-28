from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(VisitModel)
class VisitAdmin(admin.ModelAdmin):
    date_hierarchy = 'v_time'
    list_display = ('url', 'v_time', 'user_ip', 'user_id', 'duration', 'b_id')

@admin.register(LifeModel)
class LifeAdmin(admin.ModelAdmin):
    list_display=('user_id','page_id','p_alias','extra')
    list_editable=('p_alias',)


# admin.site.register(VisitModel, VisitAdmin)

