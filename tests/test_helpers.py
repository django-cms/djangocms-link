from django.test import TestCase
from django.utils.crypto import get_random_string

from djangocms_link.helpers import get_rel_obj
from tests.utils.models import ThirdPartyModel


class GetRelObjTestCase(TestCase):
    def test_get_rel_obj_with_valid_object(self):
        """Test that get_rel_obj returns the correct object for valid internal link"""
        obj = ThirdPartyModel.objects.create(
            name=get_random_string(5), path=get_random_string(5)
        )
        internal_link = f"{obj._meta.app_label}.{obj._meta.model_name}:{obj.pk}"

        result = get_rel_obj(internal_link)

        self.assertEqual(result, obj)
        self.assertIsInstance(result, ThirdPartyModel)

    def test_get_rel_obj_with_non_existing_app(self):
        """Test that get_rel_obj returns None for non-existing app"""
        internal_link = "nonexistentapp.model:1"

        result = get_rel_obj(internal_link)

        self.assertIsNone(result)

    def test_get_rel_obj_with_non_existing_model(self):
        """Test that get_rel_obj returns None for non-existing model"""
        internal_link = "utils.nonexistentmodel:1"

        result = get_rel_obj(internal_link)

        self.assertIsNone(result)

    def test_get_rel_obj_with_non_existing_pk(self):
        """Test that get_rel_obj returns None for non-existing pk"""
        internal_link = "utils.thirdpartymodel:999999"

        result = get_rel_obj(internal_link)

        self.assertIsNone(result)

    def test_get_rel_obj_with_invalid_format(self):
        """Test that get_rel_obj returns None for invalid format (no colon)"""
        internal_link = "utils.thirdpartymodel"

        result = get_rel_obj(internal_link)

        self.assertIsNone(result)

    def test_get_rel_obj_with_malformed_model_name(self):
        """Test that get_rel_obj returns None for malformed model name (no dot)"""
        internal_link = "thirdpartymodel:1"

        result = get_rel_obj(internal_link)

        self.assertIsNone(result)
