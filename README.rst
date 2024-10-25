===============
django CMS Link
===============

|pypi| |build| |coverage|

**django CMS Link** is a plugin for `django CMS <https://django-cms.org>`_ that
allows you to add links on your site.

This plugin supports child plugins. If you add an other plugin as a
child it will take this content instead of the link name as the content of the link.

This addon is compatible with `Divio Cloud <http://divio.com>`_.

.. image:: preview.gif


Contributing
============

This is a an open-source project. We'll be delighted to receive your
feedback in the form of issues and pull requests. Before submitting your
pull request, please review our `contribution guidelines
<http://docs.django-cms.org/en/latest/contributing/index.html>`_.

We're grateful to all contributors who have helped create and maintain this package.
Contributors are listed at the `contributors <https://github.com/divio/djangocms-link/graphs/contributors>`_
section.

One of the easiest contributions you can make is helping to translate this addon on
`Transifex <https://www.transifex.com/projects/p/djangocms-link/>`_.


Documentation
=============

See ``REQUIREMENTS`` in the `setup.py <https://github.com/divio/djangocms-link/blob/master/setup.py>`_
file for additional dependencies:

|python| |django| |djangocms|

* Django Filer 1.7 or higher

If `django Filer <http://django-filer.readthedocs.io/en/latest/installation.html>`_
is installed and configured appropriately, django CMS Link will allow linking
files.


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
setting:

.. code-block:: python

    DJANGOCMS_LINK_TEMPLATES = [
        ('feature', _('Featured Version')),
    ]

You'll need to create the ``feature`` folder inside ``templates/djangocms_link/``
otherwise you will get a *template does not exist* error. You can do this by
copying the ``default`` folder inside that directory and renaming it to
``feature``.

To support environments where non-standard URLs would otherwise work, this
project supports the defining of an additional RegEx pattern for validating the
host-portion of the URL.

For example:

.. code-block:: python

    # RFC1123 Pattern:
    DJANGOCMS_LINK_INTRANET_HOSTNAME_PATTERN = r'[a-z,0-9,-]{1,15}'

Either of these might accept a URL such as:

.. code-block:: html

    http://SEARCHHOST/?q=some+search+string

If left undefined, the normal Django URLValidator will be used.


Link fields
-----------

As of version 5, django CMS Link provides a re-usable link model field,
form field and form widget. This allows you to use the link field in your own
models or forms.

.. code-block:: python

    from djangocms_link.fields import LinkField, LinkFormField, LinkWidget

    class MyModel(models.Model):
        link = LinkField()

    class MyForm(forms.Form):
        link = LinkFormField(required=False)

``LinkField`` is a subclass of ``JSONField`` and stores the link data as dict.
To render the link field in a template, use the new template tags::

    {% load djangocms_link_tags %}
    <a href="{{ obj.link|to_url }}">Link</a>

    {% get_url obj.link as url %}
    {% if url %}
        <a href="{{ url }}">Link available</a>
    {% endif %}

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

.. |python| image:: https://img.shields.io/badge/python-3.5+-blue.svg
    :target: https://pypi.org/project/djangocms-link/
.. |django| image:: https://img.shields.io/badge/django-2.2,%203.0,%203.1-blue.svg
    :target: https://www.djangoproject.com/
.. |djangocms| image:: https://img.shields.io/badge/django%20CMS-3.7%2B-blue.svg
    :target: https://www.django-cms.org/

Updating from version 4 or lower
--------------------------------

django CMS Link 5 is a rewrite of the plugin. If you are updating from
version 4 or lower, you will notice

* the **new re-usable link widget**, greatly simplifying the user interface
* an **improved management of multi-site situations**, essentially avoiding the
  unnecessary additon of the host name to the URL in plugin instances that
  are not in a page placeholder (such as links on aliases or static placeholder)
* a **re-usable admin endpoint** for querying available links which can be used
  by other apps such as djangocms-text.
* Links are generated by template tags or template filters instead of the
  model's ``get_link()`` method. This allows multiple links in future models. The
  ``get_link()`` method is still available for backwards compatibility.

Migrations should automatically existing plugin instances to the new model
fields.

.. warning::

   Migration has worked for some people seamlessly. We strongly recommend to
    backup your database before updating to version 5. If you encounter any
    issues, please report them on
    `GitHub <https://github.com/django-cms/djangocms-link/issues>`_.
