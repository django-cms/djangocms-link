# -*- coding: utf-8 -*-
from unittest import skipIf, skipUnless
from distutils.version import LooseVersion

from django.core.management import call_command
from django.utils.encoding import force_text
from django.utils.six import StringIO

import cms
from cms.api import add_plugin, create_page

from djangocms_helper.base_test import BaseTestCase

CMS_35 = LooseVersion(cms.__version__) >= LooseVersion('3.5')


class LinkTestCase(BaseTestCase):
    def setUp(self):
        self.page = create_page(
            title='help',
            template='page.html',
            language='en',
        )

    def test_link(self):
        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            external_link='http://example.com'
        )
        self.assertEqual(plugin.get_link(), 'http://example.com')

        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            external_link='http://example.com',
            anchor='some-h1',
        )
        self.assertEqual(plugin.get_link(), 'http://example.com#some-h1')

        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            phone='555-123-555',
        )
        self.assertEqual(plugin.get_link(), 'tel:555-123-555')

        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            mailto='hello@example.com',
        )
        self.assertEqual(plugin.get_link(), 'mailto:hello@example.com')

        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            external_link='http://example.com',
        )
        self.assertEqual(plugin.get_link(), 'http://example.com')

        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            name='some text',
        )
        self.assertEqual(plugin.get_link(), '')
        self.assertEqual(force_text(plugin), 'some text')

    @skipUnless(CMS_35, "Test relevant only for CMS>=3.5")
    def test_link_for_cms35(self):
        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            internal_link=self.page,
        )
        self.assertEqual(plugin.get_link(), '/en/help/')

        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            internal_link=self.page,
            anchor='some-h1',
        )
        self.assertEqual(plugin.get_link(), '/en/help/#some-h1')

    @skipIf(CMS_35, "Test relevant only for CMS<3.5")
    def test_link_for_cms_34(self):
        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            internal_link=self.page,
        )
        self.assertEqual(plugin.get_link(), '/en/')

        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            internal_link=self.page,
            anchor='some-h1',
        )
        self.assertEqual(plugin.get_link(), '/en/#some-h1')

    def test_makemigrations(self):
        """
        Fail if there are schema changes with no migrations.
        """
        app_name = 'djangocms_link'
        out = StringIO()
        call_command('makemigrations', dry_run=True, no_input=True, stdout=out)
        output = out.getvalue()
        self.assertNotIn(app_name, output, (
            '`makemigrations` thinks there are schema changes without'
            ' migrations.'
        ))
