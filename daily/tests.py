from django.test import TestCase
from models import get_week_days_by_date


# Create your tests here.
class ModelsMethodTest(TestCase):
    def test_get_week_days_by_date(self):
        days = get_week_days_by_date("2016-09-02")
        expect_result = ["2016-08-29", "2016-08-30", "2016-08-31", "2016-09-01", "2016-09-02", "2016-09-03",
                         "2016-09-04"]
        self.assertEquals(days, expect_result)
