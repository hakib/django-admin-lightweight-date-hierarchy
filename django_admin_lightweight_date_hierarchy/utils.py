import datetime
import calendar


def get_date_hierarchy_drilldown_on_past_dates(year_lookup, month_lookup, asof, past_years=3):
    """Drill-down only on past dates.

    year_lookup (int or None)
    month_lookup (int or None)
    asof (datetime.datetime aware):
        Current date.
    past_years (int):
        Number of past years to return for year drilldown.

    Yields (datetime.date):
        List of dates to drill down on.
    """
    today = asof.date()

    if year_lookup is None and month_lookup is None:
        return (
            datetime.date(y, 1, 1)
            for y in range(today.year - past_years + 1, today.year + 1)
        )

    elif year_lookup is not None and month_lookup is None:
        # Past months of selected year.
        this_month = today.replace(day=1)
        return (
            month for month in (
                datetime.date(int(year_lookup), m, 1)
                for m in range(1, 13)
            ) if month <= this_month
        )

    elif year_lookup is not None and month_lookup is not None:
        # Past days of selected month.
        days_in_month = calendar.monthrange(year_lookup, month_lookup)[1]
        return (
            day for day in (
                datetime.date(year_lookup, month_lookup, d + 1)
                for d in range(days_in_month)
            ) if day <= today
        )
