# -*- coding: utf-8 -*-
import datetime

from django.contrib import admin

from .models import Foo


class FooNoDrilldown(Foo):
    class Meta:
        proxy = True


@admin.register(FooNoDrilldown)
class FooNoDrilldownAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    date_hierarchy_drilldown = False
    show_full_result_count = False


class FooDrilldown(Foo):
    class Meta:
        proxy = True


@admin.register(FooDrilldown)
class FooDrilldownAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    date_hierarchy_drilldown = True


class FooDefault(Foo):
    class Meta:
        proxy = True


@admin.register(FooDefault)
class FooDefaultAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'


class FooCustomHierarchy(Foo):
    class Meta:
        proxy = True


@admin.register(FooCustomHierarchy)
class FooCustomHierarchyAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    date_hierarchy_drilldown = False

    def get_date_hierarchy_drilldown(self, year_lookup=None, month_lookup=None):
        if year_lookup is None and month_lookup is None:
            # Year 2018
            return (
                datetime.date(2018, 1, 1),
            )

        elif year_lookup is not None and month_lookup is None:
            # First month of year
            return (
                datetime.date(year_lookup, 1, 1),
            )

        elif year_lookup is not None and month_lookup is not None:
            # First two days of month
            return (
                datetime.date(year_lookup, month_lookup, 1),
                datetime.date(year_lookup, month_lookup, 2),
            )
