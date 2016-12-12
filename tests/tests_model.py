# -*- coding: utf-8 -*-
from django.core.management import call_command
from django.utils.encoding import force_text
from django.utils.six import StringIO
from django.utils import translation

from cms.api import add_plugin, create_page

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

    def test_get_link_doesnt_raise_error_on_untranslated_target(self):
        """
        Test that getting the URL of a link to a page that is not translated
        in the current language doesn't raise an exception.
        """
        homepage = create_page(
            title='help',
            template='page.html',
            language='en',
            published=True
        )
        # Make sure this page is not a homepage
        non_homepage = create_page(
            title='Foobar',
            template='page.html',
            language='en',
            published=True
        )

        plugin = add_plugin(
            homepage.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            internal_link=non_homepage
        )

        with translation.override('fr'):
            self.assertEqual(plugin.get_link(), '')

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
