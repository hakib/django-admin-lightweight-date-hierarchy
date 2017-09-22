=====
Usage
=====

To use django-admin-lightweight-date-hierarchy in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_admin_lightweight_date_hierarchy',
        ...
    )

Add the following to any model admin with date hierarchy to prevent the default drill-down behaviour:

.. code-block:: python

    @admin.register(MyModel)
    class MyModelAdmin(admin.ModelAdmin):
        date_hierarchy = 'created'
        date_hierarchy_drilldown = False
