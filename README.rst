=============================
Django Admin lightweight date hierarchy
=============================

.. image:: https://badge.fury.io/py/django-admin-lightweight-date-hierarchy.svg
    :target: https://badge.fury.io/py/django-admin-lightweight-date-hierarchy

.. image:: https://travis-ci.org/hakib/django-admin-lightweight-date-hierarchy.svg?branch=master
    :target: https://travis-ci.org/hakib/django-admin-lightweight-date-hierarchy

.. image:: https://codecov.io/gh/hakib/django-admin-lightweight-date-hierarchy/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/hakib/django-admin-lightweight-date-hierarchy


Django Admin date_hierarchy with zero queries
----------------------------------------------

The built-in `date_hierarchy`_ tag performs a query to find the dates for which there is data.
On large tables this query can be very expensive.

To prevent additional queries, set ``date_hierarchy_drilldown = False`` on the ``ModelAdmin``.
When drill-down is disabled the tag will generate a default range of dates based solely
on the selected hierarchy level - without performing a query.

Default options for hierarchy levels:

- None - +-3 years from current year.
- Year - all months of the selected year.
- Month - all days of the selected month.

When ``date_hierarchy_drilldown = True`` or when not set the default behaviour is preserved.

.. _`date_hierarchy`: https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#django.contrib.admin.ModelAdmin.date_hierarchy


Support
----------

Python 2.7, 3.4, 3.5, 3.6

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

Add the following to any ``ModelAdmin`` with ``date_hierarchy`` to prevent the default drill-down behaviour:

.. code-block:: python

    @admin.register(MyModel)
    class MyModelAdmin(admin.ModelAdmin):
        date_hierarchy = 'created'
        date_hierarchy_drilldown = False


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
