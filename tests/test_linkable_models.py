from django.test import TestCase, override_settings

from djangocms_link.apps import DjangoCmsLinkConfig
from tests.utils.models import AnotherLinkableModel, ThirdPartyModel


class LinkableModelsTestCase(TestCase):
    """Tests for DJANGOCMS_LINKABLE_MODELS setting"""

    def test_single_linkable_model(self):
        """Test that a single linkable model is properly registered"""
        from djangocms_link import admin as link_admin

        # Save original value
        original_registered = link_admin.REGISTERED_ADMIN.copy()

        try:
            # Simulate app ready with single model
            with override_settings(DJANGOCMS_LINKABLE_MODELS=["utils.thirdpartymodel"]):
                app_config = DjangoCmsLinkConfig("djangocms_link", link_admin)
                app_config.ready()

                # Verify that the admin was registered
                self.assertEqual(len(link_admin.REGISTERED_ADMIN), 1)
                self.assertEqual(link_admin.REGISTERED_ADMIN[0].model, ThirdPartyModel)
        finally:
            # Restore original value
            link_admin.REGISTERED_ADMIN = original_registered

    def test_multiple_linkable_models(self):
        """Test that multiple linkable models are properly registered"""
        from djangocms_link import admin as link_admin

        # Save original value
        original_registered = link_admin.REGISTERED_ADMIN.copy()

        try:
            # Simulate app ready with multiple models
            with override_settings(
                DJANGOCMS_LINKABLE_MODELS=[
                    "utils.thirdpartymodel",
                    "utils.anotherlinkablemodel",
                ]
            ):
                app_config = DjangoCmsLinkConfig("djangocms_link", link_admin)
                app_config.ready()

                # Verify that both admins were registered
                self.assertEqual(len(link_admin.REGISTERED_ADMIN), 2)
                registered_models = [adm.model for adm in link_admin.REGISTERED_ADMIN]
                self.assertIn(ThirdPartyModel, registered_models)
                self.assertIn(AnotherLinkableModel, registered_models)
        finally:
            # Restore original value
            link_admin.REGISTERED_ADMIN = original_registered

    def test_linkable_models_only_registers_once(self):
        """Test that duplicate models don't get registered twice"""
        from djangocms_link import admin as link_admin

        # Save original value
        original_registered = link_admin.REGISTERED_ADMIN.copy()

        try:
            # Simulate app ready with duplicate model entries
            with override_settings(
                DJANGOCMS_LINKABLE_MODELS=[
                    "utils.thirdpartymodel",
                    "utils.thirdpartymodel",
                ]
            ):
                app_config = DjangoCmsLinkConfig("djangocms_link", link_admin)
                app_config.ready()

                # Verify that the admin was only registered once
                self.assertEqual(len(link_admin.REGISTERED_ADMIN), 1)
                self.assertEqual(link_admin.REGISTERED_ADMIN[0].model, ThirdPartyModel)
        finally:
            # Restore original value
            link_admin.REGISTERED_ADMIN = original_registered

    def test_linkable_models_validates_get_absolute_url(self):
        """Test that models without get_absolute_url raise ImproperlyConfigured"""
        from django.core.exceptions import ImproperlyConfigured

        from djangocms_link import admin as link_admin

        # Save original value
        original_registered = link_admin.REGISTERED_ADMIN.copy()

        try:
            # Create a test model without get_absolute_url
            # Import a model that doesn't have get_absolute_url
            with override_settings(
                DJANGOCMS_LINKABLE_MODELS=[
                    "sites.site"
                ]  # Site model doesn't have get_absolute_url
            ):
                app_config = DjangoCmsLinkConfig("djangocms_link", link_admin)
                with self.assertRaises(ImproperlyConfigured) as cm:
                    app_config.ready()
                self.assertIn(
                    "needs to implement get_absolute_url method", str(cm.exception)
                )
        finally:
            # Restore original value
            link_admin.REGISTERED_ADMIN = original_registered

    def test_empty_linkable_models_list(self):
        """Test that an empty linkable models list results in no registered admins"""
        from djangocms_link import admin as link_admin

        # Save original value
        original_registered = link_admin.REGISTERED_ADMIN.copy()

        try:
            with override_settings(DJANGOCMS_LINKABLE_MODELS=[]):
                app_config = DjangoCmsLinkConfig("djangocms_link", link_admin)
                app_config.ready()

                # Verify no admins were registered
                self.assertEqual(len(link_admin.REGISTERED_ADMIN), 0)
        finally:
            # Restore original value
            link_admin.REGISTERED_ADMIN = original_registered
