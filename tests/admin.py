# -*- coding: utf-8 -*-
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
