import datetime

from django.utils import timezone
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory

from django_admin_lightweight_date_hierarchy.admin import get_date_range_for_hierarchy
from .utils import fake_sub_test
from ..models import Foo


class TestGetDateRangeForHierarchy(TestCase):

    def setUp(self):
        # Python 2.7 does not support subTest, fake it.
        if not hasattr(self, 'subTest'):
            self.subTest = fake_sub_test

    def test(self):
        utc = datetime.timezone.utc

        for  year, month, day,  expected_from_date,                           expected_to_date,                           tz in (      # NOQA
            (2017, 1,     1,    datetime.datetime(2017, 1, 1, tzinfo=utc),    datetime.datetime(2017, 1, 2, tzinfo=utc),  utc),        # NOQA
            (2017, 1,     None, datetime.datetime(2017, 1, 1, tzinfo=utc),    datetime.datetime(2017, 2, 1, tzinfo=utc),  utc),        # NOQA
            (2017, None,  None, datetime.datetime(2017, 1, 1, tzinfo=utc),    datetime.datetime(2018, 1, 1, tzinfo=utc),  utc),        # NOQA
            (2016, None,  None, datetime.datetime(2016, 1, 1, tzinfo=utc),    datetime.datetime(2017, 1, 1, tzinfo=utc),  utc),        # NOQA
            (2017, 2,     28,   datetime.datetime(2017, 2, 28, tzinfo=utc),   datetime.datetime(2017, 3, 1, tzinfo=utc),  utc),        # NOQA
            (2017, 1,     31,   datetime.datetime(2017, 1, 31, tzinfo=utc),   datetime.datetime(2017, 2, 1, tzinfo=utc),  utc),        # NOQA
            (2017, 12,    31,   datetime.datetime(2017, 12, 31, tzinfo=utc),  datetime.datetime(2018, 1, 1, tzinfo=utc),  utc),        # NOQA
            (2017, 12,    None, datetime.datetime(2017, 12, 1, tzinfo=utc),   datetime.datetime(2018, 1, 1, tzinfo=utc),  utc),        # NOQA
            (2017, 1,     1,    datetime.datetime(2017, 1, 1),                datetime.datetime(2017, 1, 2),              None),       # NOQA
            (2017, 1,     None, datetime.datetime(2017, 1, 1),                datetime.datetime(2017, 2, 1),              None),       # NOQA
            (2017, None,  None, datetime.datetime(2017, 1, 1),                datetime.datetime(2018, 1, 1),              None),       # NOQA
        ):
            with self.subTest(year=year, month=month, day=day, timezone=str(tz)):
                date_hierarchy = {
                    'year': year,
                }

                if month is not None:
                    date_hierarchy['month'] = month

                if day is not None:
                    date_hierarchy['day'] = day

                from_date, to_date = get_date_range_for_hierarchy(date_hierarchy, tz=tz)

                self.assertEqual(from_date, expected_from_date)
                self.assertEqual(to_date, expected_to_date)


class TestRangeBasedDateHierarchyListFilter(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        default_timezone = timezone.get_default_timezone()

        # Create test data in all ranges of the hierarchy.
        Foo.objects.bulk_create([
            Foo(id=id, created=datetime.datetime(*t).replace(tzinfo=default_timezone))
            for id, t in [
                (1, (2017, 1, 15, 15)),
                (2, (2017, 1, 16, 15)),
                (3, (2017, 2, 15, 15)),
                (4, (2017, 3, 15, 15)),
                (5, (2017, 12, 31, 23, 59, 59)),
                (6, (2018, 1, 1, 0, 0, 0)),
                (7, (2018, 2, 28, 23, 59, 59)),
                (8, (2018, 3, 1, 1, 0, 0)),
                (9, (2018, 3, 15, 15)),
            ]
        ])
        cls.superuser = User.objects.create_superuser(
            username='foo',
            email='foo@bar.bax',
            password='a321321321',
        )

    def setUp(self):
        self.factory = RequestFactory()

        self.client.force_login(self.superuser)

    def get_results(self, query):
        url = f'/admin/tests/foowithrangebaseddatehierarchylistfilter/?{query}'
        request = self.factory.get(url)
        response = self.client.get(url)
        cl = response.context_data['cl']
        return set(cl.get_queryset(request).values_list('pk', flat=True))

    def test_should_filter_year(self):
        self.assertEqual(self.get_results('created__year=2017'), {1, 2, 3, 4, 5})
        self.assertEqual(self.get_results('created__year=2018'), {6, 7, 8, 9})
        self.assertEqual(self.get_results('created__year=2019'), set())

    def test_should_filter_month(self):
        self.assertEqual(self.get_results('created__year=2018&created__month=2'), {7})
        self.assertEqual(self.get_results('created__year=2018&created__month=3'), {8, 9})
        self.assertEqual(self.get_results('created__year=2019&created__month=1'), set())

    def test_should_filter_day(self):
        self.assertEqual(self.get_results('created__year=2018&created__month=2&created__day=28'), {7})
        self.assertEqual(self.get_results('created__year=2018&created__month=2&created__day=27'), set())
