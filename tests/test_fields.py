from django.conf import settings
from django.test import TestCase

from djangocms_link.fields import PageSearchField, is_select2_enabled
from djangocms_link.fields_select2 import Select2PageSearchField


class LinkFieldTestCase(TestCase):

    def test_field_with_django_select2_extension(self):
        self.assertTrue('django_select2' in settings.INSTALLED_APPS)
        self.assertTrue(is_select2_enabled())
        settings.INSTALLED_APPS.remove("django_select2")
        self.assertFalse(is_select2_enabled())
        self.assertEqual(PageSearchField, Select2PageSearchField)
