=========
Changelog
=========

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
