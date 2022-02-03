import re
import datetime

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.contrib import admin
from django.utils import timezone


def get_date_range_for_hierarchy(date_hierarchy, tz):
    """Generate date range for date hierarchy.

    date_hierarchy <dict>:
        year (int)
        month (int or None)
        day (int or None)
    tz <timezone or None>:
        The timezone in which to generate the datetimes.
        If None, the datetimes will be naive.

    Returns (tuple):
        from_date (datetime.datetime, aware if tz is set) inclusive
        to_date (datetime.datetime, aware if tz is set) exclusive
    """
    from_date = datetime.datetime(
        date_hierarchy['year'],
        date_hierarchy.get('month', 1),
        date_hierarchy.get('day', 1),
    )

    if tz:
        from_date = from_date.replace(tzinfo=tz)

    if 'day' in date_hierarchy:
        to_date = from_date + datetime.timedelta(days=1)

    elif 'month' in date_hierarchy:
        assert from_date.day == 1
        to_date = (from_date + datetime.timedelta(days=32)).replace(day=1)

    else:
        to_date = from_date.replace(year=from_date.year + 1)

    return from_date, to_date


class RangeBasedDateHierarchyListFilter(admin.ListFilter):
    title = ''

    def __init__(self, request, params, model, model_admin):
        self.date_hierarchy_field = model_admin.date_hierarchy

        if self.date_hierarchy_field is None:
            raise ImproperlyConfigured(
                'RangeBasedDateHierarchyListFilter requires date_hierarchy to be set in the ModelAdmin'
            )

        self.date_hierarchy = {}

        date_hierarchy_field_re = re.compile(fr'^{self.date_hierarchy_field}__(day|month|year)$')

        # Django applies filters one by one on the params requested in the URL's.
        # By poping the date hierarchy from the params list we prevent the
        # default behaviour.
        for param in list(params.keys()):
            match = date_hierarchy_field_re.match(param)
            if match:
                period = match.group(1)
                self.date_hierarchy[period] = int(params.pop(param))

    def has_output(self):
        # Is there a date hierarchy filter?
        return bool(self.date_hierarchy)

    def choices(self, changelist):
        # Required.
        return {}

    def queryset(self, request, queryset):
        tz = timezone.get_default_timezone() if settings.USE_TZ else None
        from_date, to_date = get_date_range_for_hierarchy(self.date_hierarchy, tz)

        return queryset.filter(**{
            f'{self.date_hierarchy_field}__gte': from_date,
            f'{self.date_hierarchy_field}__lt': to_date,
        })
