from django.contrib import admin

from .models import Sale, SaleWithDrilldown


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    date_hierarchy_drilldown = False


@admin.register(SaleWithDrilldown)
class SaleWithDrilldownAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
