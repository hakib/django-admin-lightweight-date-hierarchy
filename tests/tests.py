#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import pytz
try:
    from unittest import mock
except ImportError:
    import mock

import django
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test import TestCase

from .models import Foo


class TestDateHeirarchyDrilldown(TestCase):

    @classmethod
    def setUpTestData(cls):
        super(TestDateHeirarchyDrilldown, cls).setUpTestData()

        # Create test data in all ranges of the heirarchy.
        Foo.objects.bulk_create([
            Foo(created=pytz.UTC.localize(datetime.datetime(*t)))
            for t in [
                (2017, 1, 15, 15),
                (2017, 1, 16, 15),
                (2017, 2, 15, 15),
                (2017, 3, 15, 15),
                (2018, 3, 15, 15),
            ]
        ])

        cls.superuser = User.objects.create_superuser(
            username='foo',
            email='foo@bar.bax',
            password='a321321321',
        )

    def setUp(self):
        # Django versions < 1.9 does not have client.force_login()
        self.client.post('/admin/login/', {
            'username': self.superuser.username,
            'password': 'a321321321',
        })

    def test_should_preserve_default_behaviour(self):
        # This is basically testing django's date heirarchy...
        for model in (
            # date_hierarchy_drilldown = False
            'foodrilldown',
            # no date_hierarchy_drilldown
            'foodefault',
        ):
            # Year
            response = self.client.get('/admin/tests/{}/?created__year=2017'.format(model))
            for month in (1, 2, 3):
                self.assertContains(response, '?created__month={}&amp;created__year=2017'.format(month))

            # Year + Month
            response = self.client.get('/admin/tests/{}/?created__year=2017&created__month=1'.format(model))
            for day in (15, 16):
                self.assertContains(response, '?created__day={}&amp;created__month=1&amp;created__year=2017'.format(day))

            # Year + Month + Day
            response = self.client.get('/admin/tests/{}/?created__year=2017&created__month=1&created__day=15'.format(model))

            # Back date
            self.assertContains(response, '?created__month=1&amp;created__year=2017')

            # Current selection
            self.assertContains(response, 'January 15')

    @mock.patch('django_admin_lightweight_date_hierarchy.templatetags.admin_list.get_today')
    def test_should_show_years_selection_if_hierarchy_level_not_selected(self, mock_today):
        mock_today.return_value = datetime.date(2017, 1, 1)

        response = self.client.get('/admin/tests/foonodrilldown/')
        for year in range(2014, 2021):
            self.assertContains(response, '?created__year={}'.format(year))

    def test_should_show_years(self):
        response = self.client.get('/admin/tests/foodrilldown/')
        for year in range(2017, 2019):
            self.assertContains(response, '?created__year={}'.format(year))

    def test_should_show_all_months_of_year(self):
        response = self.client.get('/admin/tests/foonodrilldown/?created__year=2017')
        for month in range(1, 13):
            self.assertContains(response, '?created__month={}&amp;created__year=2017'.format(month))

    def test_should_show_all_days_of_month(self):
        response = self.client.get('/admin/tests/foonodrilldown/?created__year=2017&created__month=1')
        for day in range(1, 32):
            self.assertContains(response, '?created__day={}&amp;created__month=1&amp;created__year=2017'.format(day))

    def test_should_only_show_selected_day(self):
        response = self.client.get('/admin/tests/foonodrilldown/?created__year=2017&created__month=1&created__day=15')
        # Back date
        self.assertContains(response, '?created__month=1&amp;created__year=2017')
        # Current selection
        self.assertContains(response, 'January 15')

    def test_should_not_execute_additional_queries_for_date_heirarchy(self):
        for endpoint in (
            '/admin/tests/foonodrilldown/?created__year=2017',
            '/admin/tests/foonodrilldown/?created__year=2017&created__month=1',
            '/admin/tests/foonodrilldown/?created__year=2017&created__month=1&created__day=15',
        ):
            # The 4 queries are:
            #   1. Session
            #   2. User
            #   3. Paginator
            #   4. Results
            with self.assertNumQueries(4):
                self.client.get(endpoint)

    def test_should_apply_custom_drilldown_when_no_filter(self):
        response = self.client.get('/admin/tests/foocustomhierarchy/')
        self.assertContains(response, '?created__year=2018')
        self.assertNotContains(response, '?created__year=2017')

    def test_should_apply_custom_drilldown_for_year(self):
        response = self.client.get('/admin/tests/foocustomhierarchy/?created__year=2017')
        self.assertContains(response, '?created__month=1&amp;created__year=2017')
        self.assertNotContains(response, '?created__month=2&amp;created__year=2017')

    def test_should_apply_custom_drilldown_for_month(self):
        response = self.client.get('/admin/tests/foocustomhierarchy/?created__year=2017&created__month=1')
        self.assertContains(response, '?created__day=1&amp;created__month=1&amp;created__year=2017')
        self.assertContains(response, '?created__day=2&amp;created__month=1&amp;created__year=2017')
        self.assertNotContains(response, '?created__day=3&amp;created__month=1&amp;created__year=2017')
