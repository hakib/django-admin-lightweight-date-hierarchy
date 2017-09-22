=============================
django-admin-lightweight-date-hierarchy
=============================

.. image:: https://badge.fury.io/py/django-admin-lightweight-date-hierarchy.svg
    :target: https://badge.fury.io/py/django-admin-lightweight-date-hierarchy

.. image:: https://travis-ci.org/hakib/django-admin-lightweight-date-hierarchy.svg?branch=master
    :target: https://travis-ci.org/hakib/django-admin-lightweight-date-hierarchy

.. image:: https://codecov.io/gh/hakib/django-admin-lightweight-date-hierarchy/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/hakib/django-admin-lightweight-date-hierarchy


Django Admin date_hierarchy with zero queries
----------------------------------------------

The default date_hierarchy tag performs a query on the filtered queryset to find the
dates for which there is data. On large tables this query can be very expensive.

To prevent additional queries set date_hierarchy_drilldown = False on the model admin.
When drill-down is disabled the tag will generate a default range of dates based solely
on the selected hierarchy level without performing a query.

Default options for hierarchy levels:

    Month - all days of the month.
    Year - All months of year.
    None - +-3 years from current year.

When date_hierarchy_drilldown = True or when not set the default behaviour is preserved.


Support
----------

Python 2.7, 3.3, 3.4, 3.5
Django 1.9, 1.10, 1.11


Quickstart
----------

Install django-admin-lightweight-date-hierarchy::

    pip install django-admin-lightweight-date-hierarchy

Add it to your `INSTALLED_APPS`:

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


Documentation
-------------

The full documentation is at https://django-admin-lightweight-date-hierarchy.readthedocs.io.


Running Tests
-------------

::

    source <YOURVIRTUALENV>/bin/activate
    (venv) $ pip install tox
    (venv) $ tox


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
