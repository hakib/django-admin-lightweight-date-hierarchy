import datetime
import calendar

from django.utils.translation import gettext_lazy as _
from django.contrib.admin.templatetags.admin_list import register
from django.utils.text import capfirst
from django.utils import formats
from django.db import models
from django.contrib.admin.utils import get_fields_from_path


def get_today():
    # Get today's date - used for mocking in tests.
    return datetime.date.today()


def default_date_hierarchy_drilldown(year_lookup=None, month_lookup=None):
    """Generate default drill-down for any level of the hierarchy.

    year_lookup (int or None):
        Year lookup.
        None when no lookup.
    month_lookup (int or None):
        Month lookup (1-12).
        None when lookup by year or when no lookup.

    Returns (generator<datetime.date>):
        Dates to drill-down to.
    """
    if year_lookup is None and month_lookup is None:
        # Three years from each direction.
        today = get_today()
        return (
            datetime.date(y, 1, 1)
            for y in range(today.year - 3, today.year + 3 + 1)
        )

    elif year_lookup is not None and month_lookup is None:
        # All months of selected year.
        return (
            datetime.date(int(year_lookup), month, 1)
            for month in range(1, 13)
        )

    elif year_lookup is not None and month_lookup is not None:
        # All days of month.
        return (
            datetime.date(year_lookup, month_lookup, 1) + datetime.timedelta(days=i)
            for i in range(calendar.monthrange(year_lookup, month_lookup)[1])
        )

    else:
        assert 'date hierarchy drilldown makes no sense.'


@register.inclusion_tag('admin/date_hierarchy.html')
def date_hierarchy(cl):
    """Displays the date hierarchy for date drill-down functionality.

    This tag overrides Django Admin date_hierarchy template tag at
    django/contrib/admin/templatetags/admin_list.py -> date_hierarchy

    The tag prevents additional queries used for generating the date hierarchy.
    The default tag performs a query on the filtered queryset to find the dates
    for which there is data for the level in the hierarchy. On large tables
    this query can be very expensive.

    The additional query is prevented by setting date_hierarchy_drilldown = False
    on the model admin. When drilldown is disabled the tag will generate a default
    range of dates based only on the selected hierarchy level without performing a
    query.

    Hierarchy levels:
        Month - all days of the month.
        Year - All months of year.
        None - +-3 years from current year.

    When date_hierarchy_drilldown = True or when not set the default behaviour
    is preserved.

    Usage:
        class MyModelAdmin(admin.ModelAdmin):
            date_hierarchy = 'created'
            date_hierarchy_drilldown = False
    """
    if cl.date_hierarchy:
        field_name = cl.date_hierarchy
        field = get_fields_from_path(cl.model, field_name)[-1]
        dates_or_datetimes = 'datetimes' if isinstance(field, models.DateTimeField) else 'dates'
        year_field = '%s__year' % field_name
        month_field = '%s__month' % field_name
        day_field = '%s__day' % field_name
        field_generic = '%s__' % field_name
        year_lookup = cl.params.get(year_field)
        month_lookup = cl.params.get(month_field)
        day_lookup = cl.params.get(day_field)

        def link(filters):
            return cl.get_query_string(filters, [field_generic])

        date_hierarchy_drilldown = getattr(cl.model_admin, 'date_hierarchy_drilldown', True)
        date_hierarchy_drilldown_fn = getattr(
            cl.model_admin,
            'get_date_hierarchy_drilldown',
            default_date_hierarchy_drilldown,
        )

        if not (year_lookup or month_lookup or day_lookup):

            # Select appropriate start level.
            if date_hierarchy_drilldown:
                date_range = cl.queryset.aggregate(first=models.Min(field_name), last=models.Max(field_name))
                if date_range['first'] and date_range['last']:
                    if date_range['first'].year == date_range['last'].year:
                        year_lookup = date_range['first'].year
                        if date_range['first'].month == date_range['last'].month:
                            month_lookup = date_range['first'].month

        if year_lookup and month_lookup and day_lookup:
            day = datetime.date(int(year_lookup), int(month_lookup), int(day_lookup))
            return {
                'show': True,
                'back': {
                    'link': link({year_field: year_lookup, month_field: month_lookup}),
                    'title': capfirst(formats.date_format(day, 'YEAR_MONTH_FORMAT'))
                },
                'choices': [{'title': capfirst(formats.date_format(day, 'MONTH_DAY_FORMAT'))}]
            }

        elif year_lookup and month_lookup:

            if date_hierarchy_drilldown:
                days = cl.queryset.filter(**{year_field: year_lookup, month_field: month_lookup})
                days = getattr(days, dates_or_datetimes)(field_name, 'day')

            else:
                days = date_hierarchy_drilldown_fn(int(year_lookup), int(month_lookup))

            return {
                'show': True,
                'back': {
                    'link': link({year_field: year_lookup}),
                    'title': str(year_lookup)
                },
                'choices': [{
                    'link': link({year_field: year_lookup, month_field: month_lookup, day_field: day.day}),
                    'title': capfirst(formats.date_format(day, 'MONTH_DAY_FORMAT'))
                } for day in days]
            }

        elif year_lookup:

            if date_hierarchy_drilldown:
                months = cl.queryset.filter(**{year_field: year_lookup})
                months = getattr(months, dates_or_datetimes)(field_name, 'month')

            else:
                months = date_hierarchy_drilldown_fn(int(year_lookup), None)

            return {
                'show': True,
                'back': {
                    'link': link({}),
                    'title': _('All dates')
                },
                'choices': [{
                    'link': link({year_field: year_lookup, month_field: month.month}),
                    'title': capfirst(formats.date_format(month, 'YEAR_MONTH_FORMAT'))
                } for month in months]
            }

        else:

            if date_hierarchy_drilldown:
                years = getattr(cl.queryset, dates_or_datetimes)(field_name, 'year')

            else:
                years = date_hierarchy_drilldown_fn(None, None)

            return {
                'show': True,
                'choices': [{
                    'link': link({year_field: str(year.year)}),
                    'title': str(year.year),
                } for year in years]
            }
