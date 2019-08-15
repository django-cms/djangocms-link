# -*- coding: utf-8 -*-
from django.conf import settings
from django.test import TestCase


class LinkFieldTestCase(TestCase):

    def test_field_with_django_select2_extension(self):
        self.assertTrue('django_select2' in settings.INSTALLED_APPS)
        self.assertTrue(settings.DJANGOCMS_LINK_USE_SELECT2)
        settings.DJANGOCMS_LINK_USE_SELECT2 = False

        from djangocms_link.fields import ENABLE_SELECT2
        self.assertFalse(settings.DJANGOCMS_LINK_USE_SELECT2)

        from djangocms_link.fields import PageSearchField
        from djangocms_link.fields_select2 import Select2PageSearchField
        self.assertEqual(PageSearchField, Select2PageSearchField)
