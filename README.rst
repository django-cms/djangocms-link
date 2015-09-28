##############
djangocms-link
##############

.. image:: https://img.shields.io/pypi/v/djangocms-link.svg
    :target: https://pypi.python.org/pypi/djangocms-link/
.. image:: https://img.shields.io/pypi/dm/djangocms-link.svg
    :target: https://pypi.python.org/pypi/djangocms-link/
.. image:: https://img.shields.io/badge/wheel-yes-green.svg
    :target: https://pypi.python.org/pypi/djangocms-link/
.. image:: https://img.shields.io/pypi/l/djangocms-link.svg
    :target: https://pypi.python.org/pypi/djangocms-link/


A Link plugin for django CMS.


Installation
~~~~~~~~~~~~


This plugin requires :code:`django CMS` 3.0 or higher to be properly installed and
configured. If you have many pages it supports ajax loading for selecting a page.
To enable this install Django-Select2 3.4 or above.

* In your projects :code:`virtualenv`, run :code:`pip install djangocms-link`.
* Add :code:`'djangocms_link'` to your :code:`INSTALLED_APPS` setting.
* Run ``manage.py migrate djangocms_link``.

.. warning:: If upgrading for versions prior to 1.7, remove `djangocms_link` from
             ``MIGRATION_MODULES`` setting.

.. warning:: If using Django 1.6, you may need to eventually add
             :code:`'djangocms_link': 'djangocms_link.south_migrations',` to
             :code:`SOUTH_MIGRATION_MODULES`

If you want to enable the ajax loading:

* In your projects :code:`virtualenv`, run :code:`pip install Django-Select2`.
* Add :code:`'django_select2'` to your :code:`INSTALLED_APPS` settings.
* Add :code:`url(r'^select2/', include('django_select2.urls')),` to your main ``urls.py``.


Settings
~~~~~~~~

To support environments where non-standard URLs would otherwise work, this
project supports the defining of an additional RegEx pattern for validating the
host-portion of the URL.

For example: ::

    # RFC1123 Pattern:
    DJANGOCMS_LINK_INTRANET_HOSTNAME_PATTERN = r'[a-z,0-9,-]{1,15}'

    # NetBios Pattern:
    DJANGOCMS_LINK_INTRANET_HOSTNAME_PATTERN = r'[a-z,0-9,!@#$%^()\\-\'{}.~]{1,15}'

Either of these might accept a URL such as: ::

    http://SEARCHHOST/?q=some+search+string

If left undefined, the normal Django URLValidator will be used.


Children
~~~~~~~~

This plugin supports child plugins. If you add an other plugin as a child it will take this content
instead of the link name as the content of the link.

Translations
~~~~~~~~~~~~

If you want to help translate the plugin please do it on transifex:

https://www.transifex.com/projects/p/djangocms-link/resource/djangocms-link/

