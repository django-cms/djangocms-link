# -*- coding: utf-8 -*-
from cms.api import create_page, add_plugin
from cms.plugin_rendering import render_placeholder
from django.template import RequestContext
from django.utils.encoding import force_text
from djangocms_helper.base_test import BaseTestCase


class LinkTestCase(BaseTestCase):

    def get_context(self, page, context_vars={}):
        request = self.get_request(page, 'en')
        context_vars['request'] = request
        return RequestContext(request, context_vars)

    def test_link(self):

        page = create_page(title='hellp', template='page.html', language='en')

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', url='http://example.com')
        self.assertEqual(plugin.link(), 'http://example.com')

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', url='http://example.com', anchor='some-h1')
        self.assertEqual(plugin.link(), 'http://example.com#some-h1')

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', url='http://example.com', phone='555-123-555')
        self.assertEqual(plugin.link(), 'tel://555-123-555')

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
        context = self.get_context(page)

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', url='http://example.com', name='some text')
        output = render_placeholder(page.placeholders.get(slot='content'), context, editable=False)
        self.assertEqual(output, '<a href="http://example.com">some text</a>')
        plugin.delete()

        plugin = add_plugin(page.placeholders.get(slot='content'), 'LinkPlugin', 'en', url='http://example.com')
        add_plugin(page.placeholders.get(slot='content'), 'TextPlugin', 'en', body='text body', target=plugin)
        output = render_placeholder(page.placeholders.get(slot='content'), context, editable=False)
        self.assertEqual(output, '<span class="plugin_link"><a href="http://example.com">text body</a></span>')
