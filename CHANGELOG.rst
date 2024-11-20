=========
Changelog
=========

5.0.0 (unreleased)
==================

* Major refactor
* New re-usable LinkWidget, LinkFormField, and LinkField
* New re-usable JSON endpoint for internal links
* New template tags (``get_url`` tag and ``to_url`` filter) to convert link
  fields into URLs. This allows multiple LinkFields per model
* Fixed cross-site linking which reduces the number situations of the hostname
  needing to be part of a link
* Dropped django-select2 dependency in favor of django admin's autocomplete

4.0.0 (2024-07-22)
==================

* Added support for django CMS 4.1
* Added support for python 3.10 to 3.12
* Dropped support for django < 4.2
* Dropped support for python < 3.10
* fix: Remove deprecated test suite assertEquals
* fix: Remove outdated treebeard dependency

3.1.0 (2022-08-19)
==================

* Added support for Django 4.0
* Display page title instead of menu title


3.0.0 (2020-09-02)
==================

* Added support for Django 3.1
* Dropped support for Python 2.7 and Python 3.4
* Dropped support for Django < 2.2
* Fixed an issue when using django-select2 where jQuery is missing
* Decreased django-select2's ``data-minimum-input-length`` option to 0


2.6.1 (2020-05-12)
==================

* Fixed an issue where 'Page' object has no attribute 'site'


2.6.0 (2020-04-21)
==================

* Added support for Django 3.0
* Added support for Python 3.8
* Pinned ``django-filer`` to 1.5.0
* Added further tests to raise coverage
* Fixed smaller issues found during testing
* Dropped support for django-select2 <= 4
* Dropped support for django-filer <= 1.4


2.5.0 (2019-07-09)
==================

* Added file link support
* Allow link requirement to be changed when another
  CMS plugin inherits from AbstractLink
* Fixed a bug preventing ``HOSTNAME_PATTERN`` to work
* Updated translations


2.4.0 (2019-04-16)
==================

* Added support for Django 2.2 and django CMS 3.7
* Removed support for Django 2.0
* Extended test matrix
* Added isort and adapted imports
* Adapted code base to align with other supported addons


2.3.1 (2018-12-20)
==================

* Fixes an issue when ``cms_page`` is not available (#153)


2.3.0 (2018-12-11)
==================

* Fixed test matrix
* Fixed an issue when ``page.site`` is not available
* Fixed an issue generating ``'Page' object has no attribute 'site'``


2.2.2 (2018-12-03)
==================

* Fixed node attribute error
* Fixed tests for travis and fixed tox file


2.2.1 (2018-11-16)
==================

* Fixed missing on_delete for AbstractLink model


2.2.0 (2018-11-16)
==================

* Added support for Django 1.11, 2.0 and 2.1
* Removed support for Django 1.8, 1.9, 1.10
* Adapted testing infrastructure (tox/travis) to incorporate
  django CMS 3.5 and 4.0
* Fixed a bug where overriding ``Site.__str__`` resulted in invalid urls.


2.1.2 (2017-05-09)
==================

* Fixed a bug which prevented links from working when the page
  referenced is on a different site from the one that contains the plugin.
* Updated translations


2.1.1 (2017-03-02)
==================

* Added compatibility for django 1.10
* Fixed a bug with newer versions of django-select2 which prevented users
  from selecting a page.


2.1.0 (2017-01-18)
==================

* Added compatibility for django 1.10
* Added better validation to set a link
* Added support for django-select2 5.x
* Removed unused ``UserSearchField``
* Updated translations


2.0.3 (2016-11-22)
==================

* Prevent changes to ``DJANGOCMS_LINK_XXX`` settings from requiring new
  migrations
* Changed naming of ``Aldryn`` to ``Divio Cloud``
* Adapted testing infrastructure (tox/travis) to incorporate
  django CMS 3.4 and dropped 3.2
* Removed NetBios Pattern from doccd umentations as its incorrect
* Updated translations


2.0.2 (2016-10-31)
==================

* Fixed an issue with ``target`` attribute


2.0.1 (2016-09-20)
==================

* Fixed an issues with migrations where Null values caused ``IntegrityError``


2.0.0 (2016-09-15)
==================

* Backwards incompatible changes
    * Added ``DJANGOCMS_LINK_TEMPLATES`` setting
    * Added select2 configuration setting ``DJANGOCMS_LINK_USE_SELECT2``
    * Moved template from ``templates/cms/plugins/link.html`` to
      ``templates/djangocms_link/default/link.html``
    * Removed ``name`` and ``target`` context in favour of ``instance.name`` and ``instance.target``
    * Removed Django < 1.8 support
    * Renamed model field ``url`` to ``external_link`` and ``page_link`` to ``internal_link``
* Added adaptions to ``README.txt``
* Fixed an issue where links appear twice
* Updated translations


1.8.3 (2016-09-12)
==================

* Added native Aldryn support


1.8.2 (2016-07-18)
==================

* Fixed styling issues with attributes field
* Pinned djangocms_attributes_field to v0.1.1+
* Fixed a regression where unnecessary whitespace was added to rendered html


1.8.1 (2016-07-05)
==================

* Pinned to djangocms-attributes-field v0.1.0
* Let attributes field be optional


1.8.0 (2016-06-20)
==================

* Adds support for arbitrary HTML attributes on link tag


1.7.2 (2016-03-04)
==================

* fix field name clashes with in Django 1.9


1.7.1 (2015-10-15)
==================

* Pin Django Select2 to >=4.3,<5.0 to preserve Django 1.6 compatibility


1.7.0 (2015-10-12)
==================

* Move migrations to standard location
* Move to djangocms-helper for tests
* PEP-8 / isort code style
* Fix tel field
* Change mailto field length


1.6.2 (2015-06-09)
==================

* Use RST for Readme
* Add repo badges for Travis, PyPI, etc.
* Add support for internal/intranet links using NetBios, NetBEUI or other hostnames
* Allow anchor-only links
* Added clarity to the helptext for the anchor field


1.6.1 (2014-05-07)
==================

* Fix a bug in forms Fix a we refer field.widget.queryset instead field.queryset.
