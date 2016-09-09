# -*- coding: utf-8 -*-
import django

from django.core.management import call_command
from django.utils.encoding import force_text
from django.utils.six import StringIO

from cms.api import add_plugin, create_page
from cms.plugin_rendering import PluginContext, render_placeholder

from djangocms_helper.base_test import BaseTestCase


class LinkTestCase(BaseTestCase):

    def test_link(self):

        page = create_page(
            title='help',
            template='page.html',
            language='en',
        )

        plugin = add_plugin(
            page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            external_link='http://example.com'
        )
        self.assertEqual(plugin.get_link(), 'http://example.com')

        plugin = add_plugin(
            page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            external_link='http://example.com',
            anchor='some-h1',
        )
        self.assertEqual(plugin.get_link(), 'http://example.com#some-h1')

        plugin = add_plugin(
            page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            external_link='http://example.com',
            phone='555-123-555',
        )
        self.assertEqual(plugin.get_link(), 'tel:555-123-555')

        plugin = add_plugin(
            page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            external_link='http://example.com',
            mailto='hello@example.com',
        )
        self.assertEqual(plugin.get_link(), 'mailto:hello@example.com')

        plugin = add_plugin(
            page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            internal_link=page,
            external_link='http://example.com',
        )
        self.assertEqual(plugin.get_link(), 'http://example.com')

        plugin = add_plugin(
            page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            internal_link=page,
        )
        self.assertEqual(plugin.get_link(), '/en/')

        plugin = add_plugin(
            page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            internal_link=page,
            anchor='some-h1',
        )
        self.assertEqual(plugin.get_link(), '/en/#some-h1')

        plugin = add_plugin(
            page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            name='some text',
        )
        self.assertEqual(plugin.get_link(), '')
        self.assertEqual(force_text(plugin), 'some text')

    def test_render(self):

        page = create_page(
            title='help',
            template='page.html',
            language='en',
        )
        request = self.get_request(page, 'en')

        plugin = add_plugin(
            page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            external_link='http://example.com',
            name='some text',
        )
        context = PluginContext(
            {'request': request},
            plugin,
            page.placeholders.get(slot='content'),
        )
        output = render_placeholder(
            page.placeholders.get(slot='content'),
            context,
            editable=False,
        )

        # there should never be trailing or leading whitespace from the link.
        # when rendered, it counts as a space in html, which leads to incorrect rendering
        self.assertEqual(output, '<a href="http://example.com">some text</a>')
        plugin.delete()

        plugin = add_plugin(
            page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            external_link='http://example.com',
        )
        add_plugin(
            page.placeholders.get(slot='content'),
            'TextPlugin',
            'en',
            body='text body',
            target=plugin,
        )
        output = render_placeholder(
            page.placeholders.get(slot='content'),
            context,
            editable=False,
        )

        # there should never be trailing or leading whitespace from the link.
        # when rendered, it counts as a space in html, which leads to incorrect rendering
        self.assertEqual(output, '<a href="http://example.com">text body</a>')

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
