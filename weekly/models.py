# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from datetime import date as _date, datetime, timedelta
from xlutils.copy import copy
from xlwt import easyxf
from xlrd import open_workbook
from ftplib import FTP
from daily.models import User, FtpInfo, get_team_by_name


class WeeklyReport(models.Model):
    year = models.IntegerField(verbose_name='年份')
    week = models.IntegerField(verbose_name="周数")
    name = models.TextField(verbose_name="姓名")
    work_plan = models.TextField(verbose_name="本周工作计划")
    work_summary = models.TextField(verbose_name="本周工作总结")
    next_work = models.TextField(verbose_name="下周工作计划")
    create_ip = models.GenericIPAddressField(verbose_name="填寫IP")
    update_datetime = models.DateTimeField(verbose_name="更新時間")
    user = models.ForeignKey(User, verbose_name="用戶信息表中對應的人")

    def __unicode__(self):
        return str(self.week) + self.name

    def get_ordered_value(self):
        return self.name, self.work_plan, self.work_summary, self.next_work, self.create_ip


def get_weekly_report_by_name(name, year=_date.today().isocalendar()[0], week=_date.today().isocalendar()[1]):
    report = WeeklyReport.objects.filter(name=name, year=year, week=week).first()
    return report


def get_weekly_reports_by_week(year=_date.today().isocalendar()[0], week=_date.today().isocalendar()[1]):
    reports = WeeklyReport.objects.filter(year=year, week=week).order_by('user__order').all()
    return reports


def get_team_weekly_reports_by_week(team, year=_date.today().isocalendar()[0], week=_date.today().isocalendar()[1]):
    reports = WeeklyReport.objects.filter(year=year, week=week, user__team=team).order_by('user__order').all()
    return reports


def get_team_month_weekly_reports_by_week(team, year=_date.today().isocalendar()[0],
                                          week=_date.today().isocalendar()[1]):
    reports = []
    for w in get_month_weeks_by_week(year, week):
        reports.append(get_team_weekly_reports_by_week(team, year, w))
    return reports


def weekly_report_add_or_update(name, year, week, post_args, extra_args):
    report = WeeklyReport.objects.filter(name=name, week=week).first()
    if report is None:
        # create
        WeeklyReport.objects.create(
            year=year,
            week=week,
            name=name,
            work_plan=post_args.get('work_plan'),
            work_summary=post_args.get('work_summary'),
            next_work=post_args.get('next_work'),
            create_ip=extra_args.get('create_ip'),
            update_datetime=datetime.now(),
            user_id=User.objects.get(name=name).id
        )
        # process next week
        _next_weekly_report_add_or_update(name, year, week, post_args, extra_args)

    else:
        # update this week
        report.work_summary = post_args.get('work_summary')
        report.next_work = post_args.get('next_work')
        report.create_ip = extra_args.get('create_ip')
        report.update_datetime = datetime.now()
        report.save()
        # process next week
        _next_weekly_report_add_or_update(name, year, week, post_args, extra_args)


def _next_weekly_report_add_or_update(name, year, week, post_args, extra_args):
    # process next week
    year, week = get_next_week(year, week)
    next_report = WeeklyReport.objects.filter(name=name, week=week).first()
    if next_report is None:
        # create
        WeeklyReport.objects.create(
            year=year,
            week=week,
            name=name,
            work_plan=post_args.get('next_work'),
            work_summary="",
            next_work="",
            create_ip=extra_args.get('create_ip'),
            update_datetime=datetime.now(),
            user_id=User.objects.get(name=name).id
        )
    else:
        # update next week
        next_report.work_plan = post_args.get('next_work')
        next_report.create_ip = extra_args.get('create_ip')
        next_report.update_datetime = datetime.now()
        next_report.save()


# date utils
def get_next_week(year, week):
    if week < 52:
        return year, week + 1
    else:
        date = _date(year, 1, 1) + timedelta(weeks=week + 1)
        return date.isocalendar()[0], date.isocalendar()[1]


def get_month_weeks_by_week(year, week):
    year_first_day = _date(year, 1, 1)
    if year_first_day.weekday() < 4:  # ISO8601 星期算法
        some_day = year_first_day + timedelta(weeks=week - 1)
        if some_day.year != year:  # 如果year_first_day + timedelta(weeks=week - 1) 导致跨年，说明week大于52或53，直接让month=12
            month = 12
        else:
            month = some_day.month
    else:
        some_day = year_first_day + timedelta(weeks=week)
        if some_day.year != year:  # 如果year_first_day + timedelta(weeks=week) 导致跨年，说明week大于52或53，直接让month=12
            month = 12
        else:
            month = some_day.month
    if month == 12:
        month_last_day = _date(year + 1, 1, 1) + timedelta(days=-1)
    else:
        month_last_day = _date(year, month + 1, 1) + timedelta(days=-1)
    month_first_week = _date(year, month, 1).isocalendar()[1]
    if month_first_week == 53:  # ISO8601 星期算法
        month_first_week = 1
    month_last_week = month_last_day.isocalendar()[1]
    return range(month_first_week, month_last_week + 1)


def get_day_range_by_week(year, week):
    year_first_day = _date(year, 1, 1)
    if year_first_day.weekday() < 4:  # ISO8601 星期算法
        day = year_first_day + timedelta(weeks=week - 1)
    else:
        day = year_first_day + timedelta(weeks=week)
    monday = day - timedelta(day.weekday())
    friday = monday + timedelta(4)
    return (monday.strftime(b'%Y年%m月%d日') + b'-' + friday.strftime(b'%Y年%m月%d日')).decode('utf-8', 'ignore')


# export xls function
def export_xls(name, year=_date.today().isocalendar()[0], week=_date.today().isocalendar()[1], upload=False):
    # open xls
    wb = copy(
        open_workbook('weekly/static/file/template.xls', encoding_override='utf-8', formatting_info=True))
    sheet = wb.get_sheet(0)
    # cell style
    style = easyxf(
        "font:name PMingLiU,height 240;border:bottom 0x01,right 0x01;align:horz center,vert center,wrap on", "0%")
    # r1c3 date format
    style2 = easyxf("font:name PMingLiU,bold on,height 240;align:horz center,vert center,wrap on")
    # get reports
    team = get_team_by_name(name)
    reports = get_team_weekly_reports_by_week(team, year, week)
    # write reports
    row = 4
    for report in reports:
        tr = [report.name, report.work_plan, report.work_summary, report.next_work, report.name]
        col = 1
        for td in tr:
            sheet.write(row, col, td, style)
            col += 1
        row += 1
    # write team
    sheet.write(1, 2, "組 級 名 稱 ： " + team, style2)
    # write table date
    sheet.write(1, 3, "  時 間： " + get_day_range_by_week(year, week), style2)
    filename = team + '周工作報表-第' + unicode(week) + '周.xls'
    wb.save('weekly/static/exported_xls/' + filename)
    if upload:
        message = []
        try:
            ftp_info = FtpInfo.objects.filter(team=team).first()
            ftp = FTP(ftp_info.host, timeout=20)
            message.append(ftp.getwelcome())
            ftp.login(user=ftp_info.username, passwd=ftp_info.password)
            ftp.cwd(ftp_info.folder1.encode('big5'))
            message.append(ftp.pwd().decode('big5').encode('utf-8'))
            with open('weekly/static/exported_xls/' + filename, 'rb') as fp:
                ftp.storbinary(('STOR ' + filename).encode('big5'), fp)
            message.append('上傳成功')
            folder2 = ftp_info.folder2
            try:
                ftp.mkd(folder2.encode('big5'))
            except Exception as e:
                message.append(e.message.decode('big5', errors='ignore').encode('utf-8'))
            ftp.cwd(folder2.encode('big5'))
            message.append(ftp.pwd().decode('big5').encode('utf-8'))
            with open('weekly/static/exported_xls/' + filename, 'rb') as fp:
                ftp.storbinary(('STOR ' + filename).encode('big5'), fp)
            message.append('上傳成功')
            ftp.close()
        except Exception as e:
            message.append(e.message)
        finally:
            return message
    return filename
