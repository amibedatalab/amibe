from django.contrib import admin
from apps.gym_hub.models import MasterRate, DataUploadTask, ChannelPartner
from django_celery_beat.models import (
    IntervalSchedule,
    CrontabSchedule,
    SolarSchedule,
    ClockedSchedule,
    PeriodicTask
)
from django_celery_results.models import TaskResult,GroupResult


class MasterRateAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'product_code', 'rule_name', 'year_from','is_active')
    list_filter = ('year_from', 'is_staff', 'product_name',
                   'product_code', 'rule_name','is_active')
    search_fields = ("rule_name__startswith", 'product_name',
                     'product_code', 'year_from', 'is_staff')
    exclude = ('created_by', 'approved_by', 'modified_by','data_id',
               'apporved_on', 'is_approved','approved_on','action')


# Unregister the Celery Beat models from the admin site
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(TaskResult)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
# admin.site.unregister(GroupResult)




class CustomChannelPartnerAdmin(admin.ModelAdmin):
    list_display = ('channel_code', 'plan_code', 'rule_name','is_active')
    list_filter = ('channel_code', 'plan_code', 'rule_name',)
    search_fields = ('channel_code__startswith', 'plan_code', 'rule_name',)


admin.site.register(MasterRate, MasterRateAdmin)
admin.site.register(ChannelPartner, CustomChannelPartnerAdmin)
