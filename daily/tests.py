# coding=utf-8
from __future__ import unicode_literals
from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from models import get_week_days_by_date, export_xls
from django.urls import reverse
setup_test_environment()
client = Client()


# test models
class ModelsMethodTest(TestCase):
    def test_get_week_days_by_date(self):
        days = get_week_days_by_date("2016-09-02")
        expect_result = ["2016-08-29", "2016-08-30", "2016-08-31", "2016-09-01", "2016-09-02", "2016-09-03",
                         "2016-09-04"]
        self.assertEquals(days, expect_result)

    def test_export_xls(self):
        filename = export_xls('開發三組', '2016-09-12')
        self.assertEquals(filename, '開發三組日工作報表2016-09-12.xls')


# test views
class ViewsMethodTest(TestCase):
    def test_login(self):
        responses = client.login()

    def test_index(self):
        responses = client.get('/')
        print(responses.status_code)
        self.assertEquals(responses.status_code, 200)
        content = responses.read()
        print(content)
        self.assertContains('工作報告')
