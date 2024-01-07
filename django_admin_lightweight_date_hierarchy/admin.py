from typing import Any, Dict, Iterator, Optional, Tuple, Type, TYPE_CHECKING
import re
import datetime

import django
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from django.contrib import admin
from django.utils import timezone
from django.http import HttpRequest
from django.db.models import Model, QuerySet
from django.contrib.admin import ModelAdmin


if TYPE_CHECKING:
    from typing_extensions import NotRequired, TypedDict

    class DateHierarchy(TypedDict):
        year: int
        month: NotRequired[int]
        day: NotRequired[int]
else:
    DateHierarchy = dict


def get_date_range_for_hierarchy(
    date_hierarchy: DateHierarchy,
    tz: Optional[datetime.timezone],
) -> Tuple[datetime.datetime, datetime.datetime]:
    """Generate date range for date hierarchy.

    If `tz` is provided, the returned datetimes are aware, otherwise naive.

    Returns:
        [0] from_date - inclusive
        [1] to_date - exclusive
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

    def __init__(
        self,
        request: HttpRequest,
        params: Dict[str, str],
        model: Type[Model],
        model_admin: ModelAdmin,
    ) -> None:
        self.date_hierarchy_field = model_admin.date_hierarchy

        if self.date_hierarchy_field is None:
            raise ImproperlyConfigured(
                'RangeBasedDateHierarchyListFilter requires date_hierarchy to be set in the ModelAdmin'
            )

        self.date_hierarchy: "DateHierarchy" = {}  # type: ignore[typeddict-item]

        date_hierarchy_field_re = re.compile(fr'^{self.date_hierarchy_field}__(day|month|year)$')

        # Django applies filters one by one on the params requested in the URL's.
        # By poping the date hierarchy from the params list we prevent the
        # default behaviour.
        for param in list(params.keys()):
            match = date_hierarchy_field_re.match(param)
            if match:
                period = match.group(1)
                if django.VERSION >= (5, 0):
                    param_values = params.pop(param)
                    if len(param_values) == 1:
                        self.date_hierarchy[period] = int(param_values[0])  # type: ignore[literal-required]
                else:
                    self.date_hierarchy[period] = int(params.pop(param))  # type: ignore[literal-required]

    def has_output(self) -> bool:
        # Is there a date hierarchy filter?
        return bool(self.date_hierarchy)

    def choices(self, changelist: Any) -> Optional[Iterator[Dict[str, Any]]]:
        # Required.
        return iter(())

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        tz = timezone.get_default_timezone() if settings.USE_TZ else None
        from_date, to_date = get_date_range_for_hierarchy(self.date_hierarchy, tz)

        return queryset.filter(**{
            f'{self.date_hierarchy_field}__gte': from_date,
            f'{self.date_hierarchy_field}__lt': to_date,
        })
