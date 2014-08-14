djangocms-link
==============

A Link plugin for django CMS.


Installation
------------

This plugin requires `django CMS` 3.0 or higher to be properly installed and
configured. If you have many pages it supports ajax loading for selecting a page.
To enable this install Django-Select2 3.1.2 or above.

* In your projects `virtualenv`_, run ``pip install djangocms-link``.
* Add ``'djangocms_link'`` to your ``INSTALLED_APPS`` setting.
* If using Django 1.7 add ``'djangocms_link': 'djangocms_link.migrations_django',``
  to ``MIGRATION_MODULES``  (or define ``MIGRATION_MODULES`` if it does not exists);
  when django CMS 3.1 will be released, migrations for Django 1.7 will be moved
  to the standard location and the south-style ones to ``south_migrations``.
* Run ``manage.py migrate djangocms_link``.

If you want to enable the ajax loading:

* In your projects `virtualenv`_, run ``pip install Django-Select2``.
* Add ``'django_select2'`` to your ``INSTALLED_APPS`` settings.
* Add ``url(r'^select2/', include('django_select2.urls')),`` to your main ``urls.py``.


Children
--------

This plugin supports child plugins. If you add an other plugin as a child it will take this content
instead of the link name as the content of the link.

Translations
------------

If you want to help translate the plugin please do it on transifex:

https://www.transifex.com/projects/p/django-cms/resource/djangocms-link/

