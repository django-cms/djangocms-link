from django.apps import apps

from cms.test_utils.testcases import CMSTestCase


class CMSConfigTestCase(CMSTestCase):
    def setUp(self):
        self.app = apps.get_app_config("djangocms_link")

    def test_config_recognized(self):
        self.assertFalse(hasattr(self.app, "cms_config"))
        self.assertTrue(hasattr(self.app, "cms_extension"))

    def test_cms_extension(self):
        cms_ext = self.app.cms_extension

        self.assertEqual(cms_ext.link_url_endpoint, "/en/admin/djangocms_link/link/urls")
