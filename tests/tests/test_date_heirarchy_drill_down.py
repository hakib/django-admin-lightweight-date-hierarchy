import datetime
from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Foo


class TestDateHierarchyDrilldown(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        # Create test data in all ranges of the hierarchy.
        Foo.objects.bulk_create([
            Foo(created=datetime.datetime(*t, tzinfo=datetime.timezone.utc))
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
        self.client.force_login(self.superuser)

    def test_should_preserve_default_behaviour(self):
        # This is basically testing django's date hierarchy...
        for model in (
            # date_hierarchy_drilldown = False
            'foodrilldown',
            # no date_hierarchy_drilldown
            'foodefault',
        ):
            # Year
            response = self.client.get(f'/admin/tests/{model}/?created__year=2017')
            for month in (1, 2, 3):
                self.assertContains(response, f'?created__month={month}&amp;created__year=2017')

            # Year + Month
            response = self.client.get(f'/admin/tests/{model}/?created__year=2017&created__month=1')
            for day in (15, 16):
                self.assertContains(
                    response,
                    f'?created__day={day}&amp;created__month=1&amp;created__year=2017'
                )

            # Year + Month + Day
            response = self.client.get(
                f'/admin/tests/{model}/?created__year=2017&created__month=1&created__day=15'
            )

            # Back date
            self.assertContains(response, '?created__month=1&amp;created__year=2017')

            # Current selection
            self.assertContains(response, 'January 15')

    @mock.patch('django_admin_lightweight_date_hierarchy.templatetags.admin_list.get_today')
    def test_should_show_years_selection_if_hierarchy_level_not_selected(self, mock_today):
        mock_today.return_value = datetime.date(2017, 1, 1)

        response = self.client.get('/admin/tests/foonodrilldown/')
        for year in range(2014, 2021):
            self.assertContains(response, f'?created__year={year}')

    def test_should_show_years(self):
        response = self.client.get('/admin/tests/foodrilldown/')
        for year in range(2017, 2019):
            self.assertContains(response, f'?created__year={year}')

    def test_should_show_all_months_of_year(self):
        response = self.client.get('/admin/tests/foonodrilldown/?created__year=2017')
        for month in range(1, 13):
            self.assertContains(response, f'?created__month={month}&amp;created__year=2017')

    def test_should_show_all_days_of_month(self):
        response = self.client.get('/admin/tests/foonodrilldown/?created__year=2017&created__month=1')
        for day in range(1, 32):
            self.assertContains(response, f'?created__day={day}&amp;created__month=1&amp;created__year=2017')

    def test_should_only_show_selected_day(self):
        response = self.client.get('/admin/tests/foonodrilldown/?created__year=2017&created__month=1&created__day=15')
        # Back date
        self.assertContains(response, '?created__month=1&amp;created__year=2017')
        # Current selection
        self.assertContains(response, 'January 15')

    def test_should_not_execute_additional_queries_for_date_hierarchy(self):
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
