from djangocms_helper.base_test import BaseTestCase
from djangocms_link.fields import PageSearchField
from djangocms_link.fields_select2 import Select2PageSearchField


class FieldTestCase(BaseTestCase):
    def test_field_with_django_select2_extension(self):
        self.assertEqual(PageSearchField, Select2PageSearchField)
