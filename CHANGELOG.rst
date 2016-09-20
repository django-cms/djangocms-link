=========
Changelog
=========


2.0.1 (2016-20-09)
==================

* Fixed an issues with migrations where Null values caused ``IntegrityError``


2.0.0 (2016-15-08)
==================

* Added additional settings
* Added configuration option for select2
* Cleaned up file structure
* Removed Django < 1.8 support
* Adapted ``README.txt``
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


1.7.2 (2015-03-04)
==================

* fix field name clashes with in Django 1.9


1.7.1 (2015-10-14)
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
