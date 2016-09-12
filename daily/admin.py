from django.contrib import admin

# Register your models here.
from daily.models import User, DailyReport, FtpInfo


class DailyReportAdmin(admin.ModelAdmin):
    fields = ['date', 'user', 'name', 'pre_work', 'real_work', 'key_result', 'complete_rate', 'tomorrow_work',
              'create_ip', 'update_datetime']
    list_display = ['date', 'name', 'pre_work', 'real_work', 'key_result', 'complete_rate', 'tomorrow_work',
                    'create_ip', 'update_datetime']
    search_fields = ['date', 'user', 'name', 'pre_work', 'real_work', 'key_result', 'complete_rate', 'tomorrow_work',
                     'create_ip']
    ordering = ['-date', 'user']


class FtpInfoAdmin(admin.ModelAdmin):
    list_display = ['team', 'host', 'username', 'password', 'folder1', 'folder2', 'folder3', 'folder4']
    search_fields = ['team', 'host', 'username', 'password', 'folder1', 'folder2', 'folder3', 'folder4']
    ordering = ['team']


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'ip', 'role', 'team', 'order']
    ordering = ['order', 'team', 'role']


admin.site.register(DailyReport, DailyReportAdmin)
admin.site.register(FtpInfo, FtpInfoAdmin)
admin.site.register(User, UserAdmin)
