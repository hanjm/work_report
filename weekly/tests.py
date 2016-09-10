# coding = utf-8
from __future__ import unicode_literals
from django.test import TestCase
from models import get_next_week, get_month_weeks_by_week, get_day_range_by_week


# Create your tests here.
class ModelsMethodTest(TestCase):
    def test_get_next_week(self):
        days = get_next_week(year=2016, week=1)
        expect_result = (2016, 2)
        self.assertEquals(days, expect_result)
        days = get_next_week(year=2016, week=52)
        expect_result = (2017, 1)
        self.assertEquals(days, expect_result)

    def test_get_day_range_by_week(self):
        day_range = get_day_range_by_week(year=2016, week=1)
        print(day_range)
        expect_result = "2016年01月04日-2016年01月08日"
        self.assertEquals(day_range, expect_result)
        day_range = get_day_range_by_week(year=2015, week=1)
        print(day_range)
        expect_result = "2014年12月29日-2015年01月02日"
        self.assertEquals(day_range, expect_result)

    def test_get_month_weeks_by_week(self):
        weeks = get_month_weeks_by_week(2015, 50)
        print(weeks)
        expect_result = [49, 50, 51, 52, 53]
        self.assertEquals(weeks, expect_result)
        weeks = get_month_weeks_by_week(2016, 1)
        print(weeks)
        expect_result = [1, 2, 3, 4]
        self.assertEquals(weeks, expect_result)
