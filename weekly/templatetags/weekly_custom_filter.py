# coding=utf-8


from django import template
from weekly.models import get_day_range_by_week

register = template.Library()


@register.filter(name='week2range')
def week2range(value, year):
    return get_day_range_by_week(year=int(year), week=value)
