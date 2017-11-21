# -*- coding: utf-8 -*-
import datetime
import pytz

from django.test import TestCase

from django_admin_lightweight_date_hierarchy.utils import get_date_hierarchy_drilldown_on_past_dates


class TestGetDateHierarchyDrillDownOnPastDates(TestCase):
    ASOF = pytz.UTC.localize(datetime.datetime(2017, 3, 5, 15, 43, 22))

    def test_should_return_past_years(self):
        dates = get_date_hierarchy_drilldown_on_past_dates(None, None, self.ASOF, 2)
        self.assertEqual(list(dates), [
            datetime.date(2016, 1, 1),
            datetime.date(2017, 1, 1),
        ])

    def test_should_return_past_months_of_current_year(self):
        dates = get_date_hierarchy_drilldown_on_past_dates(2017, None, self.ASOF, 3)
        self.assertEqual(list(dates), [
            datetime.date(2017, 1, 1),
            datetime.date(2017, 2, 1),
            datetime.date(2017, 3, 1),
        ])

    def test_should_return_past_months_of_past_year(self):
        dates = get_date_hierarchy_drilldown_on_past_dates(2016, None, self.ASOF, 3)
        self.assertEqual(list(dates), [
            datetime.date(2016, month, 1) for month in range(1, 13)
        ])

    def test_should_return_nothing_for_future_year(self):
        dates = get_date_hierarchy_drilldown_on_past_dates(2018, None, self.ASOF, 3)
        self.assertEqual(list(dates), [])

    def test_should_return_past_days_of_current_month(self):
        dates = get_date_hierarchy_drilldown_on_past_dates(2017, 3, self.ASOF, 3)
        self.assertEqual(list(dates), [
            datetime.date(2017, 3, day) for day in range(1, 6)
        ])

    def test_should_return_past_days_of_past_month(self):
        dates = get_date_hierarchy_drilldown_on_past_dates(2017, 2, self.ASOF, 3)
        self.assertEqual(list(dates), [
            datetime.date(2017, 2, day) for day in range(1, 29)
        ])

    def test_should_return_nothing_for_future_month(self):
        dates = get_date_hierarchy_drilldown_on_past_dates(2017, 4, self.ASOF, 3)
        self.assertEqual(list(dates), [])
