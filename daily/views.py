# coding= utf-8
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from datetime import date as _date
from django.contrib import messages, sessions
from django.shortcuts import render

try:
    from django.urls import reverse
except ImportError:
    from django.shortcuts.urlresolvers import reverse


def index(request, date=None):
    from models import get_daily_report_by_name, get_team_week_daily_reports_by_date, get_week_days_by_date, \
        get_team_by_name
    from weekly.models import get_weekly_report_by_name, get_leader_weekly_report_by_week
    # get current_user info
    if date is None:
        date = _date.today().isoformat()
    name = get_request_user_name(request)
    today_report = get_daily_report_by_name(name=name, date=date)
    try:
        team = get_team_by_name(name)
    except:
        # team = ''
        messages.info(request, '测试账号：F1670111 密码asdf.2016')
        return HttpResponseRedirect('/login/?next=/')
    reports = get_team_week_daily_reports_by_date(team=team, date=date)
    calendar = _date(int(date.split('-')[0]), int(date.split('-')[1]), int(date.split('-')[2])).isocalendar()
    weekly_report = get_weekly_report_by_name(name, year=calendar[0], week=calendar[1])
    leader_weekly_report = get_leader_weekly_report_by_week(team=team, year=calendar[0], week=calendar[1])
    dates = get_week_days_by_date(date, return_type="date")
    context = {
        "name": name,
        "date": date,
        "day_num": calendar[2],
        "dates": dates,
        "report": today_report,
        "reports": zip(dates, reports),
        'weekly_report': weekly_report,
        'leader_weekly_report': leader_weekly_report,
        "complete_rate_range": range(100, -1, -10)
    }
    return render(request, 'daily_report.html', context)


def add(request, date):
    from models import daily_report_add_or_update
    # get user info
    name = get_request_user_name(request)
    extra_args = dict()
    extra_args['create_ip'] = request.META.get("REMOTE_ADDR")
    try:
        daily_report_add_or_update(name, date, request.POST, extra_args)
        messages.success(request, "ok")
    except Exception as e:
        messages.error(request, "error: " + e.message.decode(errors='ignore'))
    return HttpResponseRedirect(urlresolvers.reverse('daily:view', args=[date]))


def export(request, date):
    from models import export_xls, get_team_by_name
    # get user info
    name = get_request_user_name(request)
    team = get_team_by_name(name)
    filename = export_xls(team, date)
    if request.GET.get('upload'):
        try:
            message = [i + '<br/>'.encode('utf-8') for i in export_xls(team, date, upload=True)]
            return HttpResponse(message)
        except Exception as e:
            return HttpResponse(e.message.decode(errors='ignore'))
    return HttpResponseRedirect('/static/exported_xls/' + filename)


def login(request):
    from django.contrib.auth.views import login as auth_login
    extra_context = {
        'title': '工作报告',
        'site_title': '登录',
        'site_header': '使用工号登录，初始密码为asdf.2016',
    }
    return auth_login(request, template_name='admin/login.html', extra_context=extra_context)


def logout(request):
    from django.contrib.auth.views import logout as auth_logout
    return auth_logout(request, next_page='/')


# get current_user info
def get_request_user_name(request):
    from models import get_user_by_ip, get_user_by_username
    if request.user.is_authenticated():
        try:
            name = get_user_by_username(request.user.username).name
        except Exception as e:
            name = request.META.get("REMOTE_ADDR")
            messages.warning(request, "Warning: Current user does not have corresponding info\
             in table daily_user,your name will be set to your IP address." + e.message.decode(errors='ignore'))
    else:
        try:
            name = get_user_by_ip(request.META.get("REMOTE_ADDR")).name
        except Exception as e:
            name = request.META.get("REMOTE_ADDR")
            # messages.warning(request, "Warning: You haven't logined, and Fail to refer your name by your IP address\
            # ,your name will be set to your IP address. " + e.message.decode(errors='ignore'))
            messages.warning(request,
                             "你没有登录，或者在已注册用户中没有找到你的IP地址，请联系管理员(TEL:XXX)添加一个你的账号" + e.message.decode(errors='ignore'))
    return name
