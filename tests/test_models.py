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
        self.link = Link.objects.create(
            template="default",
            name="My Link",
            internal_link=self.page,
            external_link="http://www.divio.com",
            file_link=self.file,
            anchor="some_id",
            mailto="test@email.com",
            phone="+01 234 567 89",
            target=TARGET_CHOICES[0][0],
            attributes="{'data-type', 'link'}",
        )

    def tearDown(self):
        self.file.delete()
        self.page.delete()

    def test_link_instance(self):
        instance = self.link
        instance = Link.objects.all()
        self.assertEqual(instance.count(), 1)
        instance = Link.objects.first()
        self.assertEqual(instance.template, "default")
        self.assertEqual(instance.name, "My Link")
        self.assertEqual(instance.external_link, "http://www.divio.com")
        self.assertEqual(instance.anchor, "some_id")
        self.assertEqual(instance.mailto, "test@email.com")
        self.assertEqual(instance.phone, "+01 234 567 89")
        self.assertEqual(instance.target, "_blank")
        self.assertEqual(instance.attributes, "{'data-type', 'link'}")
        # test strings
        self.assertEqual(str(instance), "My Link")
        # we test these later in get_link
        instance.internal_link = None
        instance.file_link = None
        self.assertEqual(
            instance.get_short_description(),
            "My Link (http://www.divio.com)",
        )
        instance.name = None
        self.assertEqual(str(instance), "1")
        self.assertEqual(instance.get_short_description(), "http://www.divio.com")
        instance.external_link = None
        instance.internal_link = None
        instance.file_link = None
        instance.phone = None
        instance.mailto = None
        instance.anchor = None
        self.assertEqual(instance.get_short_description(), "<link is missing>")

    def test_get_link(self):
        instance = self.link
        with self.assertRaises(ValidationError):
            # should throw an error as too many values are provided
            instance.clean()
        self.assertEqual(instance.get_link(), "//example.com" + self.page.get_absolute_url())
        instance.internal_link = None
        self.assertEqual(instance.get_link(), self.file.url)
        instance.file_link = None
        self.assertEqual(instance.get_link(), "http://www.divio.com")
        instance.external_link = None
        self.assertEqual(instance.get_link(), "tel:+0123456789")
        instance.phone = None
        self.assertEqual(instance.get_link(), "mailto:test@email.com")
        instance.mailto = None
        self.assertEqual(instance.get_link(), "#some_id")
        # by now the configuration is good again
        instance.clean()
        instance.anchor = None
        with self.assertRaises(ValidationError):
            # this should error again as no link is defined
            instance.clean()
        # now we allow the link to be empty
        instance.link_is_optional = True
        instance.clean()

    def test_not_allowed_attributes(self):
        instance = self.link
        instance.internal_link = None
        instance.external_link = None
        instance.phone = None
        instance.file_link = None
        with self.assertRaises(ValidationError):
            # anchor is not compatible with all fields (e.g. phone, mailto)
            instance.clean()
        instance.mailto = None
        instance.clean()
