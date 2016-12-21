===============
django CMS Link
===============


|pypi| |build| |coverage|

**django CMS Link** is a plugin for `django CMS <http://django-cms.org>`_ that
allows you to add links on your site.

This plugin supports child plugins. If you add an other plugin as a
child it will take this content instead of the link name as the content of the link.

This addon is compatible with `Divio Cloud <http://divio.com>`_ and is also available on the
`django CMS Marketplace <https://marketplace.django-cms.org/en/addons/browse/djangocms-link/>`_
for easy installation.

.. image:: preview.gif


Contributing
============

This is a an open-source project. We'll be delighted to receive your
feedback in the form of issues and pull requests. Before submitting your
pull request, please review our `contribution guidelines
<http://docs.django-cms.org/en/latest/contributing/index.html>`_.

One of the easiest contributions you can make is helping to translate this addon on
`Transifex <https://www.transifex.com/projects/p/djangocms-link/>`_.


Documentation
=============

See ``REQUIREMENTS`` in the `setup.py <https://github.com/divio/djangocms-link/blob/master/setup.py>`_
file for additional dependencies:

* Python 2.7, 3.3 or higher
* Django 1.8 or higher


Installation
------------

For a manual install:

* run ``pip install djangocms-link``
* add ``djangocms_link`` to your ``INSTALLED_APPS``
* run ``python manage.py migrate djangocms_link``


Configuration
-------------

Note that the provided templates are very minimal by design. You are encouraged
to adapt and override them to your project's requirements.

This addon provides a ``default`` template for all instances. You can provide
additional template choices by adding a ``DJANGOCMS_LINK_TEMPLATES``
setting::

    DJANGOCMS_LINK_TEMPLATES = [
        ('feature', _('Featured Version')),
    ]

You'll need to create the `feature` folder inside ``templates/djangocms_link/``
otherwise you will get a *template does not exist* error. You can do this by
copying the ``default`` folder inside that directory and renaming it to
``feature``.

To support environments where non-standard URLs would otherwise work, this
project supports the defining of an additional RegEx pattern for validating the
host-portion of the URL.

For example: ::

    # RFC1123 Pattern:
    DJANGOCMS_LINK_INTRANET_HOSTNAME_PATTERN = r'[a-z,0-9,-]{1,15}'

Either of these might accept a URL such as: ::

    http://SEARCHHOST/?q=some+search+string

If left undefined, the normal Django URLValidator will be used.


Django Select2
~~~~~~~~~~~~~~

This plugin supports `django-select2 <https://github.com/applegrew/django-select2#installation>`_
for simpler use of internal links. You need to manually enable it by:

* run ``pip install django-select2``
* add ``django_select2`` to your ``INSTALLED_APPS``
* add ``url(r'^select2/', include('django_select2.urls')),`` to your ``urls.py``
* set ``DJANGOCMS_LINK_USE_SELECT2 = True`` in your ``settings.py``


Running Tests
-------------

You can run tests by executing::

    virtualenv env
    source env/bin/activate
    pip install -r tests/requirements.txt
    python setup.py test


.. |pypi| image:: https://badge.fury.io/py/djangocms-link.svg
    :target: http://badge.fury.io/py/djangocms-link
.. |build| image:: https://travis-ci.org/divio/djangocms-link.svg?branch=master
    :target: https://travis-ci.org/divio/djangocms-link
.. |coverage| image:: https://codecov.io/gh/divio/djangocms-link/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/divio/djangocms-link
