djangocms-link
==============

A Link plugin for django CMS.


Installation
------------

This plugin requires `django CMS` 2.2 or higher to be properly installed and
configured. If you have many pages it supports ajax loading for selecting a page.
To enable this install Django-Select2 3.1.2 or above.

* In your projects `virtualenv`_, run ``pip install djangocms-link``.
* Add ``'djangocms_link'`` to your ``INSTALLED_APPS`` setting.
* Run ``manage.py migrate cmsplugin_disqus``.

If you want to enable the ajax loading:

* In your projects `virtualenv`_, run ``pip install Django-Select2``.
* Add ``'django_select2'`` to your ``INSTALLED_APPS`` settings.
* Add ``url(r'^select2/', include('django_select2.urls')),`` to your main ``urls.py``.

Translations
------------

If you want to help translate the plugin please do it on transifex:

https://www.transifex.com/projects/p/django-cms/resource/djangocms-link/

