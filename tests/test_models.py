from django.core.exceptions import ValidationError
from django.test import TestCase

from cms.api import create_page

from djangocms_link.models import TARGET_CHOICES, Link

from .helpers import get_filer_file


class LinkModelTestCase(TestCase):

    def setUp(self):
        self.page = create_page(
            title='help',
            template='page.html',
            language='en',
        )
        self.file = get_filer_file()
        self.internal_link = Link.objects.create(
            template="default",
            name="My Link",
            link={"internal_link": f"cms.page:{self.page.pk}", "anchor": "#some_id"},
            target=TARGET_CHOICES[0][0],
            attributes="{'data-type', 'link'}",
        )
        self.external_link = Link.objects.create(
            template="default",
            name="My Link",
            link={"external_link": "https://www.django-cms.org/#some_id"},
            target=TARGET_CHOICES[0][0],
            attributes="{'data-type', 'link'}",
        )
        self.phone_link = Link.objects.create(
            template="default",
            name="My Link",
            link={"external_link": "tel:+01 234 567 89"},
            target=TARGET_CHOICES[0][0],
            attributes="{'data-type', 'link'}",
        )
        self.mail_link = Link.objects.create(
            template="default",
            name="My Link",
            link={"external_link": "mailto:test@email.com"},
            target=TARGET_CHOICES[0][0],
            attributes="{'data-type', 'link'}",
        )
        self.anchor_link = Link.objects.create(
            template="default",
            name="My Link",
            link={"external_link": "#some_id"},
            target=TARGET_CHOICES[0][0],
            attributes="{'data-type', 'link'}",
        )
        self.file_link = Link.objects.create(
            template="default",
            name="My Link",
            link={"file_link": self.file.pk},
            target=TARGET_CHOICES[0][0],
            attributes="{'data-type', 'link'}",
        )

    def tearDown(self):
        self.file.delete()
        self.page.delete()

    def test_link_instance(self):
        instances = Link.objects.all()
        self.assertEqual(instances.count(), 6)  # 4 instances created in setUp

        instance = Link.objects.first()
        self.assertEqual(instance.template, "default")
        self.assertEqual(instance.name, "My Link")
        self.assertEqual(instance.target, "_blank")
        self.assertEqual(instance.attributes, "{'data-type', 'link'}")

        # test strings
        self.assertEqual(str(instance), "My Link")

    def test_get_short_description(self):
        """"""
        instance = self.external_link
        self.assertEqual(
            instance.get_short_description(),
            "My Link (https://www.django-cms.org/#some_id)",
        )
        instance.name = None
        self.assertEqual(str(instance), str(instance.pk))
        self.assertEqual(instance.get_short_description(), "https://www.django-cms.org/#some_id")

        instance.link = {}
        self.assertEqual(instance.get_short_description(), "<link is missing>")

    def test_get_link(self):
        self.assertEqual(self.internal_link.get_link(), self.page.get_absolute_url() + "#some_id")
        self.assertEqual(self.file_link.get_link(), self.file.url)
        self.assertEqual(self.external_link.get_link(), "https://www.django-cms.org/#some_id")
        self.assertEqual(self.phone_link.get_link(), "tel:+0123456789")
        self.assertEqual(self.mail_link.get_link(), "mailto:test@email.com")
        self.assertEqual(self.anchor_link.get_link(), "#some_id")

    def test_get_url_template_tag(self):
        from djangocms_link.templatetags.djangocms_link_tags import to_url

        self.assertEqual(
            to_url(self.internal_link.link),
            self.page.get_absolute_url() + "#some_id"
        )
        self.assertEqual(to_url(self.file_link.link), self.file.url)
        self.assertEqual(to_url(self.external_link.link), "https://www.django-cms.org/#some_id")
        self.assertEqual(to_url(self.phone_link.link), "tel:+0123456789")
        self.assertEqual(to_url(self.mail_link.link), "mailto:test@email.com")
        self.assertEqual(to_url(self.anchor_link.link), "#some_id")
        self.assertEqual(to_url(None), "")
        self.assertEqual(to_url({}), "")

    def test_to_link_template_tag(self):
        from djangocms_link.templatetags.djangocms_link_tags import to_link

        self.assertEqual(to_link(self.file), {"file_link": self.file.pk})
        self.assertEqual(to_link(self.page), {"internal_link": f"cms.page:{self.page.pk}"})
        self.assertEqual(
            to_link("https://www.django-cms.org/#some_id"),
            {"external_link": "https://www.django-cms.org/#some_id"}
        )

    def test_respect_link_is_optional(self):
        # by now the configuration is good again
        instance = self.internal_link
        instance.clean()
        instance.link = {}
        with self.assertRaises(ValidationError):
            # this should error again as no link is defined
            instance.clean()
        # now we allow the link to be empty
        instance.link_is_optional = True
        instance.clean()
