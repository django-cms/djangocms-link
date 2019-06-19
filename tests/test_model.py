# -*- coding: utf-8 -*-
from distutils.version import LooseVersion
from unittest import skipIf, skipUnless

from django.utils.encoding import force_text
from django.core.exceptions import ValidationError

import cms
from cms.api import add_plugin, create_page

from djangocms_helper.base_test import BaseTestCase
from djangocms_link.models import AbstractLink


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

    def test_optional_link(self):
        self.assertEqual(AbstractLink.link_is_optional, False)

        plugin1 = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
        )

        # should throw "Please provide a link." error
        with self.assertRaises(ValidationError):
            plugin1.clean()

        AbstractLink.link_is_optional = True

        plugin2 = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
        )
        self.assertIsNone(plugin2.clean())
