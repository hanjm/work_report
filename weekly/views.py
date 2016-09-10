# coding= utf-8
from __future__ import unicode_literals
from django.shortcuts import render, urlresolvers
from django.http import HttpResponse, HttpResponseRedirect
from datetime import date as _date, datetime
from django.contrib import messages, sessions


def index(request, year=_date.today().isocalendar()[0], week=_date.today().isocalendar()[1]):
    from daily.views import get_request_user_name
    from daily.models import get_team_by_name
    from models import get_weekly_report_by_name, get_team_month_weekly_reports_by_week, get_month_weeks_by_week
    # url里的匹配参数为string 需要转换为int
    year = int(year)
    week = int(week)
    # get current_user info
    name = get_request_user_name(request)
    report = get_weekly_report_by_name(name=name, year=year, week=week)
    reports = get_team_month_weekly_reports_by_week(team=get_team_by_name(name), year=year, week=week)
    weeks = get_month_weeks_by_week(year, week)
    context = {
        "name": name,
        'year': year,
        "week": week,
        "weeks": weeks,
        "week_num": week - weeks[0] + 1,  # 一个月的第几个星期
        "report": report,
        "reports": zip(weeks, reports),
    }
    return render(request, 'weekly_report.html', context)


def add(request, year, week):
    from daily.views import get_request_user_name
    from models import weekly_report_add_or_update
    # url里的匹配参数为string 需要转换为int
    year = int(year)
    week = int(week)
    # get user info
    name = get_request_user_name(request)
    extra_args = dict()
    extra_args['create_ip'] = request.META.get("REMOTE_ADDR")
    try:
        weekly_report_add_or_update(name, year, week, request.POST, extra_args)
        messages.success(request, "ok")
    except Exception as e:
        messages.error(request, "error: " + e.message)
    return HttpResponseRedirect(urlresolvers.reverse('weekly:view', args=[year, week]))


def export(request, year, week):
    from daily.views import get_request_user_name
    from models import export_xls
    # url里的匹配参数为string 需要转换为int
    year = int(year)
    week = int(week)
    # get user info
    name = get_request_user_name(request)
    filename = export_xls(name, year, week)
    if request.GET.get('upload'):
        try:
            message = [i + '<br/>'.encode('utf-8') for i in export_xls(name, year, week, upload=True)]
            return HttpResponse(message)
        except Exception as e:
            return HttpResponse(e.message)
    return HttpResponseRedirect('/static/exported_xls/' + filename)


def view_by_date(request, date):
    date_list = date.split('-')
    view_day = _date(year=int(date_list[0]), month=int(date_list[1]), day=int(date_list[2]))
    return HttpResponseRedirect(
        urlresolvers.reverse('weekly:view', args=[view_day.isocalendar()[0], view_day.isocalendar()[1]]))
