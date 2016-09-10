from django.contrib import admin

# Register your models here.
from daily.models import User, DailyReport, FtpInfo

admin.site.register(DailyReport)
admin.site.register(User)
admin.site.register(FtpInfo)
