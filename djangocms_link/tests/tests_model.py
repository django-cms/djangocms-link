# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import django
from cms.api import add_plugin, create_page
from cms.plugin_rendering import PluginContext, render_placeholder
from django.core.management import call_command
from django.utils.encoding import force_text
from django.utils.six import StringIO
from djangocms_helper.base_test import BaseTestCase

# Need the copy of unittest2 bundled with Django for @skipIf on Python 2.6.
try:
    from django.utils import unittest
except ImportError:
    import unittest


class LinkTestCase(BaseTestCase):

    def test_link(self):

        page = create_page(title='hellp', template='page.html', language='en')

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', url='http://example.com')
        self.assertEqual(plugin.link(), 'http://example.com')

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', url='http://example.com', anchor='some-h1')
        self.assertEqual(plugin.link(), 'http://example.com#some-h1')

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', url='http://example.com', phone='555-123-555')
        self.assertEqual(plugin.link(), 'tel:555-123-555')

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', url='http://example.com', mailto='hello@example.com')
        self.assertEqual(plugin.link(), 'mailto:hello@example.com')

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', url='http://example.com', page_link=page)
        self.assertEqual(plugin.link(), 'http://example.com')

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', page_link=page)
        self.assertEqual(plugin.link(), '/en/')

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', page_link=page, anchor='some-h1')
        self.assertEqual(plugin.link(), '/en/#some-h1')

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', name='some text')
        self.assertEqual(plugin.link(), '')
        self.assertEqual(force_text(plugin), 'some text')

    def test_render(self):

        page = create_page(title='hellp', template='page.html', language='en')
        request = self.get_request(page, 'en')

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', url='http://example.com', name='some text')
        context = PluginContext({'request': request}, plugin, page.placeholders.get(slot='content'))
        output = render_placeholder(page.placeholders.get(slot='content'), context, editable=False)
        self.assertEqual(output, '<a href="http://example.com" >some text</a>\n')
        plugin.delete()

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', url='http://example.com')
        add_plugin(page.placeholders.get(slot='content'), 'TextPlugin', 'en', body='text body', target=plugin)
        output = render_placeholder(page.placeholders.get(slot='content'), context, editable=False)
        self.assertEqual(output, '<span class="plugin_link"><a href="http://example.com" >text body</a></span>\n')

    @unittest.skipIf(django.VERSION[:2] < (1, 7), 'Skipping Django 1.7 test.')
    def test_makemigrations(self):
        """
        Fail if there are schema changes with no migrations.
        """
        app_name = 'djangocms_link'
        out = StringIO()
        call_command('makemigrations', dry_run=True, noinput=True, stdout=out)
        output = out.getvalue()
        self.assertNotIn(app_name, output, (
            '`makemigrations` thinks there are schema changes without'
            ' migrations.'
        ))
