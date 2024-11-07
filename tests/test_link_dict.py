from django.test import TestCase
from django.utils.crypto import get_random_string

from filer.models import File

from djangocms_link.helpers import LinkDict
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
        self.assertEqual(link1.type, "external_link")
        self.assertEqual(link2.type, "external_link")

    def test_file_link(self):
        file = File.objects.create(file=get_random_string(5))
        link1 = LinkDict({"file_link": file.pk})
        link2 = LinkDict(file)

        self.assertEqual(link1, link2)
        self.assertEqual(link1.url, file.url)
        self.assertEqual(link2.url, file.url)
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
        link3 = LinkDict(obj, anchor="test")

        self.assertEqual(link1, link2)
        self.assertEqual(link1.url, obj.get_absolute_url())
        self.assertEqual(link2.url, obj.get_absolute_url())
        self.assertEqual(link3.url, f"{obj.get_absolute_url()}test")
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
