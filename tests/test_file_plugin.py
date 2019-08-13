# -*- coding: utf-8 -*-
import os

from django.conf import settings

from cms.api import add_plugin, create_page

from djangocms_helper.base_test import BaseTestCase

from .helpers import get_filer_image


class LinkTestCase(BaseTestCase):

    def setUp(self):
        self.page = create_page(
            title="help",
            template="page.html",
            language="en",
        )
        self.image = get_filer_image()

    def tearDown(self):
        self.page.delete()
        self.image.delete()

    def test_file(self):
        plugin = add_plugin(
            self.page.placeholders.get(slot="content"),
            "LinkPlugin",
            "en",
            file_link=self.image
        )
        self.assertIn("test_file.jpg", plugin.get_link())
        self.assertIn("/media/filer_public/", plugin.get_link())
