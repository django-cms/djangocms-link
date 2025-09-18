from django.template import Context, Template
from django.test import TestCase, override_settings
from django.utils.crypto import get_random_string

from filer.models import File

from djangocms_link.helpers import LinkDict
from djangocms_link.models import Link
from tests.utils.models import ThirdPartyModel


class LinkDictTestCase(TestCase):
    def test_link_dict_is_a_dict(self):
        some_dict = {get_random_string(5): get_random_string(5) for _ in range(5)}

        self.assertEqual(LinkDict(some_dict), some_dict)
        self.assertEqual(LinkDict(some_dict).url, "")
        self.assertEqual(LinkDict(), dict())
        self.assertEqual(LinkDict().url, "")
        self.assertEqual(LinkDict().type, "")
        self.assertEqual(LinkDict(1), dict())

    def test_external_link(self):
        link1 = LinkDict({"external_link": "https://www.example.com"})
        link2 = LinkDict("https://www.django-cms.org")

        self.assertEqual(link1.url, "https://www.example.com")
        self.assertEqual(link2.url, "https://www.django-cms.org")
        self.assertEqual(str(link1), "https://www.example.com")
        self.assertEqual(str(link2), "https://www.django-cms.org")
        self.assertEqual(link1.type, "external_link")
        self.assertEqual(link2.type, "external_link")

    def test_relative_link(self):
        link1 = LinkDict({"relative_link": "/some/path"})
        link2 = LinkDict("/other/path")

        self.assertEqual(link1.url, "/some/path")
        self.assertEqual(link2.url, "/other/path")
        self.assertEqual(str(link1), "/some/path")
        self.assertEqual(str(link2), "/other/path")
        self.assertEqual(link1.type, "relative_link")
        self.assertEqual(link2.type, "relative_link")

    def test_file_link(self):
        file = File.objects.create(file=get_random_string(5))
        link1 = LinkDict({"file_link": file.pk})
        link2 = LinkDict(file)

        self.assertEqual(link1, link2)
        self.assertEqual(link1.url, file.url)
        self.assertEqual(link2.url, file.url)
        self.assertEqual(str(link1), file.url)
        self.assertEqual(str(link2), file.url)
        self.assertEqual(link1.type, "file_link")
        self.assertEqual(link2.type, "file_link")

    def test_internal_link(self):
        obj = ThirdPartyModel.objects.create(
            name=get_random_string(5), path=get_random_string(5)
        )
        link1 = LinkDict(
            {"internal_link": f"{obj._meta.app_label}.{obj._meta.model_name}:{obj.pk}"}
        )
        link2 = LinkDict(obj)
        link3 = LinkDict(obj, anchor="#test")

        self.assertEqual(link1.url, obj.get_absolute_url())
        self.assertEqual(link2.url, obj.get_absolute_url())
        self.assertEqual(link3.url, f"{obj.get_absolute_url()}#test")
        self.assertEqual(str(link1), obj.get_absolute_url())
        self.assertEqual(str(link2), obj.get_absolute_url())
        self.assertEqual(str(link3), f"{obj.get_absolute_url()}#test")
        self.assertEqual(link1.type, "internal_link")
        self.assertEqual(link2.type, "internal_link")
        self.assertEqual(link3.type, "internal_link")

    def test_no_internal_link(self):
        obj = ThirdPartyModel.objects.create(
            name=get_random_string(5), path=""
        )
        link1 = LinkDict(
            {"internal_link": f"{obj._meta.app_label}.{obj._meta.model_name}:{obj.pk}"}
        )
        link2 = LinkDict(obj)
        link3 = LinkDict(obj, anchor="#test")

        self.assertEqual(link1.url, "")
        self.assertEqual(link2.url, "")
        self.assertEqual(link3.url, "")
        self.assertEqual(str(link1), "")
        self.assertEqual(str(link2), "")
        self.assertEqual(str(link3), "")
        self.assertEqual(link1.type, "internal_link")
        self.assertEqual(link2.type, "internal_link")
        self.assertEqual(link3.type, "internal_link")

    def test_link_types(self):
        anchor = LinkDict("#test")
        external = LinkDict("https://www.example.com")
        phone = LinkDict("tel:+1234567890")
        mail = LinkDict("mailto:info@django-cms.org")

        self.assertEqual(anchor.type, "anchor")
        self.assertEqual(external.type, "external_link")
        self.assertEqual(phone.type, "tel")
        self.assertEqual(mail.type, "mailto")

    def test_db_queries(self):
        obj = ThirdPartyModel.objects.create(
            name=get_random_string(5), path=get_random_string(5)
        )
        link = LinkDict(obj)
        with self.assertNumQueries(0):
            self.assertEqual(link.url, obj.get_absolute_url())
            self.assertEqual(str(link), obj.get_absolute_url())

    def test_cache_no_written_to_db(self):
        obj = ThirdPartyModel.objects.create(
            name=get_random_string(5), path=get_random_string(5)
        )
        link = Link.objects.create(
            link=LinkDict(obj)
        )
        self.assertEqual(link.link.url, link.link["__cache__"])  # populates cache
        link.save()

        link = Link.objects.get(pk=link.pk)  # load from db

        # Cache not saved to db
        self.assertNotIn("__cache__", link.link)

    def test_get_obj_link_in_template(self):
        from django.contrib.sites.models import Site

        from cms.api import create_page

        Site.objects.get_or_create(id=2, domain="mysite.com", name="My Site")
        page = create_page(
            title="Test Page",
            template="page.html",
            slug="test-page",
            language="en",
        )

        template = Template("""{% load djangocms_link_tags %}{{ page|to_url }}""")

        rendered = template.render(Context({"page": page}))
        self.assertEqual(rendered, page.get_absolute_url())

        with override_settings(SITE_ID=2):
            rendered = template.render(Context({"page": page}))
        self.assertEqual(rendered, f"//example.com{page.get_absolute_url()}")

        rendered = template.render(Context({"page": None}))  # Illegal value: fail silently
        self.assertEqual(rendered, "")

        rendered = template.render(Context({"page": LinkDict("tel:+1234567890")}))
        self.assertEqual(rendered, "tel:+1234567890")
