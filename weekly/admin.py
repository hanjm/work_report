from django.contrib import admin

# Register your models here.
from weekly.models import WeeklyReport


class WeeklyReportAdmin(admin.ModelAdmin):
    fields = ['user', 'year', 'week', 'name', 'work_plan', 'work_summary', 'next_work', 'create_ip', 'update_datetime']
    list_display = ['year', 'week', 'name', 'work_plan', 'work_summary', 'next_work', 'create_ip', 'update_datetime']
    search_fields = ['year', 'week', 'name', 'work_plan', 'work_summary', 'next_work', 'create_ip', 'update_datetime']
    ordering = ['-year', '-week']


admin.site.register(WeeklyReport, WeeklyReportAdmin)
