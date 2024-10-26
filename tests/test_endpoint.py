from cms.api import create_page
from cms.models import Page
from cms.test_utils.testcases import CMSTestCase
from cms.utils.urlutils import admin_reverse

from djangocms_link.models import Link


class LinkModelTestCase(CMSTestCase):
    def setUp(self):
        self.root_page = create_page(
            title="root",
            template="page.html",
            language="en",
        )
        create_page(
            title="child 1",
            template="page.html",
            language="en",
            parent=self.root_page,
        )
        create_page(
            title="child 2",
            template="page.html",
            language="en",
            parent=self.root_page,
        )
        self.subling = create_page(
            title="sibling",
            template="page.html",
            language="en",
        )
        from django.contrib.admin import site

        LinkAdmin = site._registry[Link]
        self.endpoint = admin_reverse(LinkAdmin.link_url_name)

    def tearDown(self):
        self.root_page.delete()
        self.subling.delete()

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

                pages = data["results"][0]
                self.assertEqual(pages["text"], "Pages")
                for page in pages["children"]:
                    self.assertIn("id", page)
                    self.assertIn("text", page)
                    self.assertIn("url", page)
                    _, pk = page["id"].split(":")
                    db_page = Page.objects.get(pk=pk)
                    self.assertEqual(page["text"], str(db_page))

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
        self.assertEqual(len(data["results"]), 1)
        self.assertIn("pagination", data)
        self.assertEqual(data["pagination"]["more"], False)
        pages = data["results"][0]
        self.assertEqual(pages, {})

    def test_site_selector(self):
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.endpoint + "?app_label=2")
            self.assertEqual(response.status_code, 200)
            data = response.json()

        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1)
        self.assertIn("pagination", data)
        self.assertEqual(data["pagination"]["more"], False)
        pages = data["results"][0]
        self.assertEqual(pages, {})

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
