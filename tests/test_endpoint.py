from django.contrib import admin
from django.contrib.sites.models import Site

from cms.api import create_page, create_title
from cms.models import Page
from cms.test_utils.testcases import CMSTestCase
from cms.utils.urlutils import admin_reverse

from djangocms_link.admin import UNICODE_SPACE
from djangocms_link.models import Link
from tests.utils.models import ThirdPartyModel


class LinkEndpointTestCase(CMSTestCase):
    def setUp(self):
        from django.contrib.admin import site

        self.root_page = create_page(
            title="root",
            template="page.html",
            language="en",
        )
        create_title("fr", "racine", self.root_page)

        create_page(
            title="child 1",
            template="page.html",
            language="en",
            parent=self.root_page,
        )
        create_title("fr", "enfant 1", self.root_page.get_children()[0])

        create_page(
            title="child 2",
            template="page.html",
            language="en",
            parent=self.root_page,
        )
        create_title("fr", "enfant 2", self.root_page.get_children()[1])

        self.sibling = create_page(
            title="sibling",
            template="page.html",
            language="en",
        )
        create_title("fr", "frère", self.sibling)

        LinkAdmin = site._registry[Link]
        self.endpoint = admin_reverse(LinkAdmin.global_link_url_name)

    def tearDown(self):
        self.root_page.delete()
        self.sibling.delete()

    def test_api_endpoint(self):
        from djangocms_link import admin

        registered = admin.REGISTERED_ADMIN
        admin.REGISTERED_ADMIN = []
        for query_params in ("", "?app_label=1", "?language=fr"):
            with self.subTest(query_params=query_params):
                with self.login_user_context(self.get_superuser()):
                    response = self.client.get(self.endpoint + query_params)
                    self.assertEqual(response.status_code, 200)
                    data = response.json()

                self.assertIn("results", data)
                self.assertEqual(len(data["results"]), 1)
                self.assertIn("pagination", data)
                self.assertEqual(data["pagination"]["more"], False)
                pages = data["results"][0]
                self.assertEqual(pages["text"], "Pages")
                for page in pages["children"]:
                    self.assertIn("id", page)
                    self.assertIn("text", page)
                    self.assertIn("url", page)
                    _, pk = page["id"].split(":")
                    db_page = Page.objects.get(pk=pk)
                    try:
                        language = query_params.split("language=")[-1]
                        if language == query_params:
                            language = "en"
                        expected = str(db_page.get_admin_content(language).title)
                    except AttributeError:
                        expected = str(db_page)
                    self.assertEqual(page["text"].strip(UNICODE_SPACE), expected)
        admin.REGISTERED_ADMIN = registered

    def test_filter(self):
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.endpoint + "?term=child")
            self.assertEqual(response.status_code, 200)
            data = response.json()

        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1)
        self.assertIn("pagination", data)
        self.assertEqual(data["pagination"]["more"], False)

        pages = data["results"][0]
        self.assertEqual(len(pages["children"]), 2)

    def test_filter_with_empty_result(self):
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.endpoint + "?term=DJANGOCMS")
            self.assertEqual(response.status_code, 200)
            data = response.json()

        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 0)
        self.assertIn("pagination", data)
        self.assertEqual(data["pagination"]["more"], False)

    def test_site_selector(self):
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.endpoint + "?app_label=2")
            self.assertEqual(response.status_code, 200)
            data = response.json()

        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 0)
        self.assertIn("pagination", data)
        self.assertEqual(data["pagination"]["more"], False)

    def test_get_reference(self):
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.endpoint + "?g=cms.page:1")
            self.assertEqual(response.status_code, 200)
            data = response.json()

        self.assertIn("id", data)
        self.assertIn("text", data)
        self.assertIn("url", data)
        self.assertEqual(data["id"], "cms.page:1")
        self.assertEqual(data["text"], "root")
        self.assertEqual(data["url"], self.root_page.get_absolute_url())

    def test_get_reference_different_language(self):
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(f"{self.endpoint}?g=cms.page:1&language=fr")
            self.assertEqual(response.status_code, 200)
            data = response.json()

        self.assertIn("id", data)
        self.assertIn("text", data)
        self.assertIn("url", data)
        self.assertEqual(data["id"], "cms.page:1")
        self.assertEqual(data["text"], "racine")
        self.assertEqual(data["url"], self.root_page.get_absolute_url())

    def test_outdated_reference(self):
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.endpoint + "?g=cms.page:0")
            self.assertEqual(response.status_code, 200)
            data = response.json()

        self.assertIn("error", data)
        self.assertEqual(data["error"], "Page matching query does not exist.")


class LinkEndpointThirdPartyTestCase(CMSTestCase):
    def setUp(self):
        LinkAdmin = admin.site._registry[Link]
        self.endpoint = admin_reverse(LinkAdmin.global_link_url_name)

        self.second_site = Site.objects.create(
            domain="second",
            name="second",
        )

        self.items = (
            ThirdPartyModel.objects.create(name="First", path="/first", site_id=1),
            ThirdPartyModel.objects.create(
                name="Second", path="/second", site=self.second_site
            ),
            ThirdPartyModel.objects.create(name="django CMS", path="/django-cms"),
            ThirdPartyModel.objects.create(
                name="django CMS rocks", path="/django-cms-2"
            ),
        )

    def test_auto_config(self):
        from djangocms_link.admin import REGISTERED_ADMIN
        from tests.utils.admin import ThirdPartyAdmin

        for registered_admin in REGISTERED_ADMIN:
            if isinstance(registered_admin, ThirdPartyAdmin):
                break
        else:
            self.assertFail("ThirdPartyAdmin not found in REGISTERED_ADMIN")

    def test_api_endpoint(self):
        for query_params in ("", "?app_label=1"):
            with self.subTest(query_params=query_params):
                with self.login_user_context(self.get_superuser()):
                    response = self.client.get(self.endpoint + query_params)
                    self.assertEqual(response.status_code, 200)
                    data = response.json()

                self.assertIn("results", data)
                self.assertEqual(len(data["results"]), 1)
                self.assertIn("pagination", data)
                self.assertEqual(data["pagination"]["more"], False)
                destinations = data["results"][0]
                self.assertEqual(destinations["text"], "Third party models")
                for destination in destinations["children"]:
                    self.assertIn("id", destination)
                    self.assertIn("text", destination)
                    self.assertIn("url", destination)
                    _, pk = destination["id"].split(":")
                    db_obj = ThirdPartyModel.objects.get(pk=pk)
                    self.assertEqual(destination["text"], str(db_obj))

    def test_filter(self):
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.endpoint + "?term=CMS")
            self.assertEqual(response.status_code, 200)
            data = response.json()

        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1)
        self.assertIn("pagination", data)
        self.assertEqual(data["pagination"]["more"], False)

        pages = data["results"][0]
        self.assertEqual(len(pages["children"]), 2)

    def test_site_selector(self):
        for site_id in (1, 2):
            with self.subTest(site_id=site_id):
                with self.login_user_context(self.get_superuser()):
                    response = self.client.get(self.endpoint + f"?app_label={site_id}")
                    self.assertEqual(response.status_code, 200)
                    data = response.json()

                self.assertIn("results", data)
                self.assertEqual(len(data["results"]), 1)
                self.assertIn("pagination", data)
                self.assertEqual(data["pagination"]["more"], False)
                destinations = data["results"][0]
                self.assertEqual(destinations["text"], "Third party models")
                # One site-specific item, two all-sites items
                self.assertEqual(len(destinations["children"]), 3)

                # Specific site item
                if site_id == 1:
                    self.assertIn(
                        {
                            "id": "utils.thirdpartymodel:1",
                            "text": "First",
                            "url": "/first",
                            "verbose_name": ThirdPartyModel._meta.verbose_name.capitalize(),
                        },
                        destinations["children"],
                    )
                else:
                    self.assertIn(
                        {
                            "id": "utils.thirdpartymodel:2",
                            "text": "Second",
                            "url": "/second",
                            "verbose_name": ThirdPartyModel._meta.verbose_name.capitalize(),
                        },
                        destinations["children"],
                    )
                # All-sites items
                self.assertIn(
                    {
                        "id": "utils.thirdpartymodel:3",
                        "text": "django CMS",
                        "url": "/django-cms",
                        "verbose_name": ThirdPartyModel._meta.verbose_name.capitalize(),
                    },
                    destinations["children"],
                )
                self.assertIn(
                    {
                        "id": "utils.thirdpartymodel:4",
                        "text": "django CMS rocks",
                        "url": "/django-cms-2",
                        "verbose_name": ThirdPartyModel._meta.verbose_name.capitalize(),
                    },
                    destinations["children"],
                )

    def test_get_reference(self):
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.endpoint + "?g=utils.thirdpartymodel:1")
            self.assertEqual(response.status_code, 200)
            data = response.json()

        self.assertIn("id", data)
        self.assertIn("text", data)
        self.assertIn("url", data)
        self.assertEqual(data["id"], "utils.thirdpartymodel:1")
        self.assertEqual(data["text"], "First")
        self.assertEqual(data["url"], self.items[0].get_absolute_url())


class LinkEndpointMultiModelTestCase(CMSTestCase):
    def setUp(self):
        LinkAdmin = admin.site._registry[Link]

        self.endpoint = admin_reverse(LinkAdmin.global_link_url_name)
        self.root_page = create_page(
            title="root",
            template="page.html",
            language="en",
        )
        self.items = (
            ThirdPartyModel.objects.create(name="First", path="/first"),
            ThirdPartyModel.objects.create(name="Second", path="/second"),
        )

    def test_api_endpoint(self):
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            data = response.json()

        self.assertIn("results", data)
        self.assertIn("pagination", data)
        self.assertEqual(data["pagination"]["more"], False)

        # Two optgroups:
        # 1. Pages (always first)
        # 2. Third party models
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["text"], "Pages")
        self.assertEqual(data["results"][1]["text"], "Third party models")
