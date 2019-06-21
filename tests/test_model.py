# -*- coding: utf-8 -*-
from distutils.version import LooseVersion
from unittest import skipIf, skipUnless

from django.core.exceptions import ValidationError
from django.utils.encoding import force_text

from cms import __version__
from cms.api import add_plugin, create_page
from cms.models import StaticPlaceholder, Placeholder

from djangocms_helper.base_test import BaseTestCase

from djangocms_link.models import AbstractLink


CMS_35 = LooseVersion(__version__) >= LooseVersion('3.5')


class LinkTestCase(BaseTestCase):

    def setUp(self):
        self.page = create_page(
            title='help',
            template='page.html',
            language='en',
        )
        self.static_page = create_page(
            title='static-help',
            template='static_placeholder.html',
            language='en',
        )

    def tearDown(self):
        self.page.delete()
        self.static_page.delete()

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
            external_link='/en/home/'
        )
        self.assertEqual(plugin.get_link(), '/en/home/')

        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            external_link='//SEARCHHOST/?q=some+search+string'
        )
        self.assertEqual(plugin.get_link(), '//SEARCHHOST/?q=some+search+string')

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
        AbstractLink.link_is_optional = True

        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
        )
        self.assertIsNone(plugin.clean())

        AbstractLink.link_is_optional = False

        self.assertEqual(AbstractLink.link_is_optional, False)

        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
        )

        # should throw "Please provide a link." error
        with self.assertRaises(ValidationError):
            plugin.clean()

    @skipUnless(CMS_35, "Test relevant only for CMS>=3.5")
    def test_in_placeholders(self):
        plugin = add_plugin(
            self.page.placeholders.get(slot='content'),
            'LinkPlugin',
            'en',
            internal_link=self.page,
        )
        self.assertEqual(plugin.get_link(), '/en/help/')

        placeholder = Placeholder(slot="generated_placeholder")
        placeholder.save()

        plugin = add_plugin(
            placeholder,
            'LinkPlugin',
            'en',
            internal_link=self.static_page,
        )
        # the generated placeholder has no page attached to it, thus:
        self.assertEqual(plugin.get_link(), '//example.com/en/static-help/')

        static_placeholder = StaticPlaceholder.objects.create(
            name='content_static',
            code='content_static',
            site_id=1,
        )
        static_placeholder.save()

        plugin_a = add_plugin(
            static_placeholder.draft,
            'LinkPlugin',
            'en',
            internal_link=self.page,
        )

        plugin_b = add_plugin(
            static_placeholder.public,
            'LinkPlugin',
            'en',
            internal_link=self.static_page,
        )
        # static placeholders will always return the full path
        self.assertEqual(plugin_a.get_link(), '//example.com/en/help/')
        self.assertEqual(plugin_b.get_link(), '//example.com/en/static-help/')
