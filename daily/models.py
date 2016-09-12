# coding=utf-8
from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from datetime import datetime, timedelta, date as _date
from xlutils.copy import copy
from xlwt import easyxf
from xlrd import open_workbook
from ftplib import FTP


class User(models.Model):
    username = models.OneToOneField(settings.AUTH_USER_MODEL, to_field='username', unique=True,
                                    verbose_name='工號',
                                    help_text="鏈接到授權->用戶中的用戶名，所以，添加用戶前需要先添加一個可登陸用戶")
    name = models.TextField(verbose_name="姓名")
    ip = models.GenericIPAddressField(verbose_name="IP地址")
    role = models.IntegerField(verbose_name="角色", help_text="組長為1，組員為0")
    team = models.TextField(verbose_name="組別")
    order = models.IntegerField(verbose_name="排序權值", help_text="日報主頁顯示的表格按此值降序排列用戶")

    class Meta:
        verbose_name = '用戶信息表'
        verbose_name_plural = verbose_name
        get_latest_by = 'date'

    def __unicode__(self):
        return self.name


def get_user_by_ip(ip):
    return User.objects.get(ip=ip)


def get_user_by_username(username):
    return User.objects.get(username=username)


def get_team_by_name(name):
    return User.objects.get(name=name).team


class DailyReport(models.Model):
    date = models.DateField(verbose_name="日期")
    name = models.TextField(verbose_name="姓名")
    pre_work = models.TextField(verbose_name="今日工作昨日预报")
    real_work = models.TextField(verbose_name="今日實際工作安排")
    key_result = models.TextField(verbose_name="关键結果")
    complete_rate = models.TextField(max_length=5, verbose_name="完成度")
    tomorrow_work = models.TextField(verbose_name="明日工作预报")
    create_ip = models.GenericIPAddressField(verbose_name="填寫IP")
    update_datetime = models.DateTimeField(verbose_name="更新時間")
    user = models.ForeignKey(User, verbose_name="用戶信息表中對應的人")

    class Meta:
        verbose_name = '日報數據表'
        verbose_name_plural = verbose_name
        unique_together = (('date', 'name'),)

    def __unicode__(self):
        return self.date.strftime('%Y-%m-%d ') + self.name

    def get_ordered_value(self):
        return self.name, self.pre_work, self.real_work, self.key_result, self.complete_rate, self.tomorrow_work, \
               self.create_ip


def get_daily_report_by_name(name, date=None):
    if date is None:
        date = _date.today().isoformat()
    report = DailyReport.objects.filter(name=name, date=date).first()
    return report


def get_daily_reports_by_name():
    pass


def get_daily_reports_by_date(date=None):
    if date is None:
        date = _date.today().isoformat()
    reports = DailyReport.objects.filter(date=date).order_by('user__order').all()
    return reports


def get_week_daily_reports_by_date(date=None):
    if date is None:
        date = _date.today().isoformat()
    reports = []
    for day in get_week_days_by_date(date):
        reports.append(get_daily_reports_by_date(day))
    return reports


def get_team_daily_reports_by_date(team, date=None):
    if date is None:
        date = _date.today().isoformat()
    reports = DailyReport.objects.filter(date=date, user__team=team).order_by('user__order').all()
    return reports


# 用戶所在組的所有成員的一周工作內容（主表格）
def get_team_week_daily_reports_by_date(team, date=None):
    if date is None:
        date = _date.today().isoformat()
    reports = []
    for day in get_week_days_by_date(date):
        reports.append(get_team_daily_reports_by_date(team, day))
    return reports


# 個人的一周內容
def get_personal_week_daily_reports_by_week(name, year=None, week=None):
    if year is None:
        year = _date.today().year
    if week is None:
        week = _date.today().isoweekday()[1]
    # 根據year week構造一個日期
    # ISO8601 the first thursday of january is the first week of a year e.g 2016.1.1 is year 2015 week 53
    if int(week) == 53:
        construct_date = datetime.strptime(str(year + 1) + str(1), "%Y%j")
    else:
        if _date(year, 1, 1).isoweekday() >= 4:
            construct_date = datetime.strptime(str(year) + str(week * 7), "%Y%j")
        else:
            construct_date = datetime.strptime(str(year) + str((week - 1) * 7), "%Y%j")
    date = construct_date.strftime("%Y-%m-%d")
    reports = []
    for day in get_week_days_by_date(date):
        reports.append(get_daily_report_by_name(name, day))
    return reports


# 明日工作預報同步至明天的items中
def __tomorrow_report_add_or_update(name, date, post_args, extra_args):
    # process day after date
    date = get_next_day(date)
    tomorrow_report = DailyReport.objects.filter(name=name, date=date).first()
    if tomorrow_report is None:
        # create
        DailyReport.objects.create(
            date=date,
            name=name,
            pre_work=post_args.get('tomorrow_work'),
            real_work="",
            key_result="",
            complete_rate="",
            tomorrow_work="",
            create_ip=extra_args.get('create_ip'),
            update_datetime=datetime.now(),
            user_id=User.objects.get(name=name).id
        )
    else:
        # update day after date
        tomorrow_report.pre_work = post_args.get('tomorrow_work')
        tomorrow_report.create_ip = extra_args.get('create_ip')
        tomorrow_report.update_datetime = datetime.now()
        tomorrow_report.save()


def daily_report_add_or_update(name, date, post_args, extra_args):
    report = DailyReport.objects.filter(name=name, date=date).first()
    if report is None:
        # create
        DailyReport.objects.create(
            date=date,
            name=name,
            pre_work=post_args.get('pre_work'),
            real_work=post_args.get('real_work'),
            key_result=post_args.get('key_result'),
            complete_rate=post_args.get('complete_rate'),
            tomorrow_work=post_args.get('tomorrow_work'),
            create_ip=extra_args.get('create_ip'),
            update_datetime=datetime.now(),
            user_id=User.objects.get(name=name).id
        )
        # process day after date
        __tomorrow_report_add_or_update(name, date, post_args, extra_args)

    else:
        # update this day
        report.real_work = post_args.get('real_work')
        report.key_result = post_args.get('key_result')
        report.complete_rate = post_args.get('complete_rate')
        report.tomorrow_work = post_args.get('tomorrow_work')
        report.create_ip = extra_args.get('create_ip')
        report.update_datetime = datetime.now()
        report.save()
        # process day after date
        __tomorrow_report_add_or_update(name, date, post_args, extra_args)


# date function utils
def get_next_day(date_str):
    this_day = datetime.strptime(date_str, "%Y-%m-%d")
    next_day = this_day + timedelta(days=1)
    return next_day.strftime('%Y-%m-%d')


def get_week_days_by_date(date, return_type="str"):
    this_day = datetime.strptime(date, "%Y-%m-%d")
    this_day.weekday()
    monday = this_day - timedelta(this_day.weekday())
    days = []
    if return_type == "date":
        for i in range(7):
            days.append(monday + timedelta(i))
    else:
        for i in range(7):
            days.append((monday + timedelta(i)).strftime("%Y-%m-%d"))
    return days


class FtpInfo(models.Model):
    host = models.GenericIPAddressField(verbose_name="FTP地址")
    username = models.TextField(max_length=10, verbose_name="登錄用戶名")
    password = models.TextField(max_length=26, verbose_name="登錄密碼")
    team = models.TextField(verbose_name="組別", unique=True)
    folder1 = models.TextField(verbose_name="日報上傳文件夾1-組內文件夾")
    folder2 = models.TextField(verbose_name="日報上傳文件夾2-公共文件夾")
    folder3 = models.TextField(verbose_name="週報上傳文件夾1-組內文件夾")
    folder4 = models.TextField(verbose_name="週報上傳文件夾2-公共文件夾")

    class Meta:
        verbose_name = 'FTP公共文件夾登錄信息(用於"導出并上傳至公共文件夾功能")'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.team + self.host + self.username + self.password


# export xls function
def export_xls(team, date=_date.today().isoformat(), upload=False):
    # open xls
    wb = copy(
        open_workbook('daily/static/file/daily_template.xls', encoding_override='utf-8', formatting_info=True))
    sheet = wb.get_sheet(0)
    # cell style
    style = easyxf(
        "font:name PMingLiU,height 240;border:bottom 0x01,right 0x01;align:horz center,vert center,wrap on", "0%")
    # r1c3 date format
    style2 = easyxf("font:name PMingLiU,bold on,height 240;align:horz center,vert center,wrap on")
    # get reports
    reports = get_daily_reports_by_date(date)
    # write reports
    row = 4
    for report in reports:
        tr = [report.name, report.real_work, report.key_result, report.complete_rate, report.name]
        try:
            tr[3] = float(tr[3].strip('%')) / 100
        except:
            pass
        col = 1
        for td in tr:
            sheet.write(row, col, td, style)
            col += 1
        row += 1
    # write team
    sheet.write(1, 2, "組 級 名 稱 ： " + team, style2)
    # write table date
    sheet.write(1, 3, "  時 間： " + date, style2)
    filename = team + '日工作報表' + date + '.xls'
    wb.save('daily/static/exported_xls/' + filename)
    if upload:
        message = []
        try:
            ftp_info = FtpInfo.objects.filter(team=team).first()
            ftp = FTP(ftp_info.host, timeout=20)
            message.append(ftp.getwelcome())
            ftp.login(user=ftp_info.username, passwd=ftp_info.password)
            ftp.cwd(ftp_info.folder1.encode('big5'))
            message.append(ftp.pwd().decode('big5').encode('utf-8'))
            with open('daily/static/exported_xls/' + filename, 'rb') as fp:
                ftp.storbinary(('STOR ' + filename).encode('big5'), fp)
            message.append('上傳成功')
            date_year = date.split('-')[0]
            date_month = date.split('-')[1].lstrip('0')
            date_day = date.split('-')[2].lstrip('0')
            folder2 = ftp_info.folder2 + date_year + '年' + date_month + '月/' + date_month + '月' + date_day + '日'
            try:
                ftp.mkd(folder2.encode('big5'))
            except Exception as e:
                message.append(e.message.decode('big5', errors='ignore').encode('utf-8'))
            ftp.cwd(folder2.encode('big5'))
            message.append(ftp.pwd().decode('big5').encode('utf-8'))
            with open('daily/static/exported_xls/' + filename, 'rb') as fp:
                ftp.storbinary(('STOR ' + filename).encode('big5'), fp)
            message.append('上傳成功')
            ftp.close()
        except Exception as e:
            message.append(e.message)
        finally:
            return message
    return filename
