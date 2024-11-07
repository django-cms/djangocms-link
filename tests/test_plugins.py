import warnings

from django.core.exceptions import ValidationError

from cms.api import add_plugin, create_page
from cms.models import Placeholder, StaticPlaceholder
from cms.test_utils.testcases import CMSTestCase

from djangocms_link.cms_plugins import LinkPlugin
from djangocms_link.models import AbstractLink

from .fixtures import TestFixture
from .helpers import get_filer_file


class LinkPluginsTestCase(TestFixture, CMSTestCase):
    def setUp(self):
        self.file = get_filer_file()
        self.language = "en"
        self.home = create_page(
            title="home",
            template="page.html",
            language=self.language,
        )
        self.publish(self.home, self.language)
        self.page = create_page(
            title="content",
            template="page.html",
            language=self.language,
        )
        self.publish(self.page, self.language)
        self.static_page = create_page(
            title="static-content",
            template="static_placeholder.html",
            language="en",
        )
        self.placeholder = self.get_placeholders(self.page, self.language).get(
            slot="content"
        )
        self.superuser = self.get_superuser()

    def tearDown(self):
        self.file.delete()
        self.page.delete()
        self.home.delete()
        self.static_page.delete()
        self.superuser.delete()

    def test_link_plugin(self):
        plugin = add_plugin(
            placeholder=self.placeholder,
            plugin_type=LinkPlugin.__name__,
            language=self.language,
            link={"internal_link": f"cms.page:{self.page.pk}"},
        )
        plugin.full_clean()
        self.assertEqual(plugin.plugin_type, "LinkPlugin")

    def test_plugin_structure(self):
        request_url = self.page.get_absolute_url(self.language) + "?toolbar_off=true"

        plugin = add_plugin(
            placeholder=self.placeholder,
            plugin_type=LinkPlugin.__name__,
            language=self.language,
            link={"internal_link": f"cms.page:{self.page.pk}"},
            name="Page link",
        )
        self.publish(self.page, self.language)
        self.assertEqual(plugin.get_plugin_class_instance().name, "Link")

        with self.login_user_context(self.superuser):
            response = self.client.get(request_url)

        self.assertContains(response, '<a href="/en/content/">Page link</a>')

    def test_full_plugin_render(self):
        request_url = self.get_add_plugin_uri(
            placeholder=self.placeholder,
            plugin_type=LinkPlugin.__name__,
            language=self.language,
        )
        from djangocms_link.fields import LinkWidget

        pos = LinkWidget().data_pos["external_link"]

        data = {
            "template": "default",
            "link_0": "external_link",
            f"link_{pos}": "https://www.google.com",
            "name": "External link",
        }

        with self.login_user_context(self.superuser), warnings.catch_warnings():
            # hide the "DontUsePageAttributeWarning" warning when using
            # `get_add_plugin_uri` to get cleaner test results
            warnings.simplefilter("ignore")
            response = self.client.post(request_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="success">')

    def test_optional_link(self):
        AbstractLink.link_is_optional = True

        plugin = add_plugin(
            self.get_placeholders(self.page, self.language).get(slot="content"),
            "LinkPlugin",
            "en",
        )
        self.assertIsNone(plugin.full_clean())

        AbstractLink.link_is_optional = False

        self.assertEqual(AbstractLink.link_is_optional, False)

        plugin = add_plugin(
            self.get_placeholders(self.page, self.language).get(slot="content"),
            "LinkPlugin",
            "en",
        )

        # should throw "Please provide a link." error
        with self.assertRaises(ValidationError):
            plugin.clean()

    def test_in_placeholders(self):
        from djangocms_link.helpers import get_link

        plugin = add_plugin(
            self.get_placeholders(self.page, self.language).get(slot="content"),
            "LinkPlugin",
            "en",
            link={"internal_link": f"cms.page:{self.page.pk}"},
        )
        site = getattr(self.page, "site", self.page.node.site)
        self.assertEqual(get_link(plugin.link, site.id), "/en/content/")

        placeholder = Placeholder(slot="generated_placeholder")
        placeholder.save()

        plugin = add_plugin(
            placeholder,
            "LinkPlugin",
            "en",
            link={"internal_link": f"cms.page:{self.static_page.pk}"},
        )
        # the generated placeholder has no page attached to it, thus:
        self.assertEqual(plugin.get_link(), "/en/static-content/")

        static_placeholder = StaticPlaceholder.objects.create(
            name="content_static",
            code="content_static",
            site_id=1,
        )
        static_placeholder.save()

        plugin_a = add_plugin(
            static_placeholder.draft,
            "LinkPlugin",
            "en",
            link={"internal_link": f"cms.page:{self.page.pk}"},
        )

        plugin_b = add_plugin(
            static_placeholder.public,
            "LinkPlugin",
            "en",
            link={"internal_link": f"cms.page:{self.static_page.pk}"},
        )
        # static placeholders will not return the full path
        self.assertEqual(plugin_a.get_link(0), "//example.com/en/content/")
        self.assertEqual(plugin_b.get_link(), "/en/static-content/")

    def test_file(self):
        plugin = add_plugin(
            self.get_placeholders(self.page, self.language).get(slot="content"),
            "LinkPlugin",
            "en",
            link={"file_link": str(self.file.pk)},
        )
        self.assertIn("test_file.pdf", plugin.get_link())
        self.assertIn("/media/filer_public/", plugin.get_link())

    def test_rendering(self):
        add_plugin(
            self.get_placeholders(self.page, self.language).get(slot="content"),
            "LinkPlugin",
            "en",
            name="Link",
            link={"internal_link": f"cms.page:{self.page.pk}"},
        )
        self.publish(self.page, self.language)

        response = self.client.get(self.page.get_absolute_url(self.language))
        self.assertContains(response, '<a href="/en/content/">Link</a>')

    def test_rendering_fallback(self):
        add_plugin(
            self.get_placeholders(self.page, self.language).get(slot="content"),
            "LinkPlugin",
            "en",
            name="Link",
            link={"internal_link": "cms.page:0"},
        )
        self.publish(self.page, self.language)

        response = self.client.get(self.page.get_absolute_url(self.language))
        self.assertContains(response, "<span>Link</span>")
