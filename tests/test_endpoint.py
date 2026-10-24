import re
from unittest import skipIf
from unittest.mock import patch

from django.contrib import admin
from django.contrib.sites.models import Site

from cms import __version__
from cms.api import create_page
from cms.models import Page
from cms.test_utils.testcases import CMSTestCase
from cms.utils.urlutils import admin_reverse

from djangocms_link.admin import UNICODE_SPACE, AdminUrlsView
from djangocms_link.models import Link
from tests.utils.models import ThirdPartyModel


try:
    from cms.api import create_page_content as create_title
except ImportError:
    from cms.api import create_title


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
        create_title("fr", "enfant 1", self.root_page.get_child_pages()[0])

        create_page(
            title="child 2",
            template="page.html",
            language="en",
            parent=self.root_page,
        )
        create_title("fr", "enfant 2", self.root_page.get_child_pages()[1])

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

    @skipIf(hasattr(Page, "get_admin_content"), "CMS 3.11 title cache")
    def test_prefetched_titles_need_no_serialization_queries(self):
        page = create_page("English only", "page.html", "en")
        for language in ("en", "fr"):
            with self.subTest(language=language):
                view = AdminUrlsView()
                view.term, view.language, view.site = "", language, None
                obj = view.get_queryset().get(pk=page.pk)

                with self.assertNumQueries(0):
                    result = view.serialize_result(obj)

                self.assertEqual(result["text"].strip(UNICODE_SPACE), "English only")
                self.assertIn("/en/", result["url"])

    @skipIf(int(__version__.split(".")[0]) < 5, "CMS 5.x URL prefetch")
    def test_prefetched_pages_need_no_serialization_queries(self):
        page = create_page("English only", "page.html", "en")
        for language in ("en", "fr"):
            with self.subTest(language=language):
                view = AdminUrlsView()
                view.term, view.language, view.site = "", language, None
                with self.assertNumQueries(3):
                    objects = list(view.get_queryset())

                with self.assertNumQueries(0):
                    results = {obj.pk: view.serialize_result(obj) for obj in objects}

                self.assertEqual(len(results), 5)
                self.assertEqual(results[page.pk]["text"].strip(UNICODE_SPACE), "English only")
                self.assertIn("/en/", results[page.pk]["url"])
                self.assertEqual(results[self.sibling.pk]["text"], "frère" if language == "fr" else "sibling")
                self.assertIn(f"/{language}/", results[self.sibling.pk]["url"])

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
                        # No language specified? -> default to 'en'
                        language = "en" if language == query_params else language
                        expected = str(db_page.get_admin_content(language).title)
                    except AttributeError:
                        expected = str(db_page.get_title(language, fallback=True))
                    self.assertEqual(page["text"].strip(UNICODE_SPACE), expected)

                    # Check that the number of leading UNICODE_SPACE characters matches the page depth
                    leading_spaces = re.search(
                        f"[^{UNICODE_SPACE}]", page["text"]
                    ).start()
                    depth = db_page.depth if hasattr(db_page, "depth") else db_page.node.depth
                    self.assertEqual(
                        leading_spaces,
                        depth - 1,
                        f"Expected {depth - 1} leading UNICODE_SPACE chars, got {leading_spaces}",
                    )
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

    def test_language_selector_includes_requested_language_and_fallback(self):
        french_page = create_page(
            title="French only",
            template="page.html",
            language="fr",
        )
        english_page = create_page(
            title="English only",
            template="page.html",
            language="en",
        )
        french_url = french_page.get_absolute_url("fr")
        english_url = english_page.get_absolute_url("en")
        try:
            with self.login_user_context(self.get_superuser()):
                response = self.client.get(self.endpoint + "?language=fr")
                self.assertEqual(response.status_code, 200)
                data = response.json()
        finally:
            french_page.delete()
            english_page.delete()

        pages = data["results"][0]["children"]
        page_by_id = {page["id"]: page for page in pages}

        french_result = page_by_id[f"cms.page:{french_page.pk}"]
        english_result = page_by_id[f"cms.page:{english_page.pk}"]
        self.assertEqual(french_result["text"], "French only")
        self.assertEqual(french_result["url"], french_url)
        self.assertEqual(english_result["text"], "English only")
        self.assertEqual(english_result["url"], english_url)

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
        self.assertEqual(data["url"], self.root_page.get_absolute_url("fr"))

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

    def test_pagination(self):
        from djangocms_link.admin import AdminUrlsView

        old_pagination = AdminUrlsView.paginate_by
        try:
            AdminUrlsView.paginate_by = 1
            with self.login_user_context(self.get_superuser()):
                response = self.client.get(self.endpoint + "?page=1")
                self.assertEqual(response.status_code, 200)
                data = response.json()
        finally:
            AdminUrlsView.paginate_by = old_pagination

        self.assertIn("results", data)
        self.assertEqual(len(data["results"]), 1)
        self.assertIn("pagination", data)
        self.assertEqual(data["pagination"]["more"], True)

        destinations = data["results"][0]
        self.assertEqual(destinations["text"], "Third party models")
        self.assertEqual(len(destinations["children"]), 1)

    def test_multi_queryset_pagination_stops_after_page_limit(self):
        first_qs = ThirdPartyModel.objects.order_by("pk")
        second_qs = ThirdPartyModel.objects.order_by("pk")
        view = AdminUrlsView()
        view.request = None
        view.paginate_by = 1
        view.kwargs = {"page": 1}
        view.has_perm = lambda request, obj=None: True

        with patch.object(ThirdPartyModel, "from_db", wraps=ThirdPartyModel.from_db) as from_db:
            with self.assertNumQueries(1):
                objects = view.get_paginated_multi_qs([first_qs, second_qs])

        self.assertEqual(objects, list(self.items[:2]))
        self.assertEqual(from_db.call_count, 2)
        self.assertIsNone(first_qs._result_cache)
        self.assertIsNone(second_qs._result_cache)

    def test_multi_queryset_pagination_skips_denied_objects_across_batches(self):
        view = AdminUrlsView()
        view.request = None
        view.paginate_by = 1
        view.kwargs = {"page": 1}
        view.has_perm = lambda request, obj=None: obj.pk in {self.items[1].pk, self.items[3].pk}
        qs = ThirdPartyModel.objects.order_by("pk").prefetch_related("site")

        objects = view.get_paginated_multi_qs([qs, ThirdPartyModel.objects.none()])

        self.assertEqual(objects, [self.items[1], self.items[3]])
        with self.assertNumQueries(0):
            self.assertEqual(objects[0].site, self.items[1].site)
            self.assertIsNone(objects[1].site)

    def test_multi_queryset_pagination_continues_into_next_queryset(self):
        view = AdminUrlsView()
        view.request = None
        view.paginate_by = 1
        view.kwargs = {"page": 2}
        view.has_perm = lambda request, obj=None: True
        qs_list = [
            ThirdPartyModel.objects.filter(pk=self.items[0].pk),
            ThirdPartyModel.objects.exclude(pk=self.items[0].pk).order_by("pk"),
        ]

        objects = view.get_paginated_multi_qs(qs_list)

        self.assertEqual(objects, list(self.items[:3]))

    def test_multi_queryset_pagination_scans_denied_rows_with_one_query(self):
        view = AdminUrlsView()
        view.request = None
        view.paginate_by = 1
        view.kwargs = {"page": 1}
        view.has_perm = lambda request, obj=None: False

        with self.assertNumQueries(1):
            objects = view.get_paginated_multi_qs([
                ThirdPartyModel.objects.all(), ThirdPartyModel.objects.none(),
            ])

        self.assertEqual(objects, [])

    def test_multi_queryset_pagination_preserves_ordering_with_pk_tiebreaker(self):
        view = AdminUrlsView()
        view.request = None
        view.paginate_by = 1
        view.kwargs = {"page": 2}
        view.has_perm = lambda request, obj=None: True
        ThirdPartyModel.objects.filter(pk__in=[obj.pk for obj in self.items[1:]]).update(name="Same")
        for ordering in ((), ("-name",)):
            for default_ordering in ((), ("-name",)):
                with self.subTest(ordering=ordering, default_ordering=default_ordering):
                    with patch.object(ThirdPartyModel._meta, "ordering", default_ordering):
                        qs = ThirdPartyModel.objects.all()
                        if ordering:
                            qs = qs.order_by(*ordering)
                        objects = view.get_paginated_multi_qs([qs, ThirdPartyModel.objects.none()])

                    expected = self.items[1:] if ordering or default_ordering else self.items[:3]
                    self.assertEqual(objects, list(expected))

    def test_multi_queryset_pagination_does_not_skip_after_deletion(self):
        view = AdminUrlsView()
        view.request = None
        view.paginate_by = 1
        view.kwargs = {"page": 1}
        deleted_pk = self.items[0].pk

        def has_perm(request, obj=None):
            if obj.pk == self.items[1].pk:
                ThirdPartyModel.objects.filter(pk=deleted_pk).delete()
            return obj.pk not in {deleted_pk, self.items[1].pk}

        view.has_perm = has_perm
        objects = view.get_paginated_multi_qs([
            ThirdPartyModel.objects.order_by("pk"), ThirdPartyModel.objects.none(),
        ])

        self.assertEqual(objects, list(self.items[2:]))

    def test_serialization_only_uses_string_when_link_text_is_empty(self):
        view = AdminUrlsView()
        obj = self.items[0]
        obj.__link_text__ = "Custom title"
        with patch.object(ThirdPartyModel, "__str__", return_value="Fallback title") as to_string:
            self.assertEqual(view.serialize_result(obj)["text"], "Custom title")
            to_string.assert_not_called()

            obj.__link_text__ = ""
            self.assertEqual(view.serialize_result(obj)["text"], "Fallback title")
            to_string.assert_called_once_with()

    def test_invalid_page_number(self):
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.endpoint + "?page=999")
            self.assertEqual(response.status_code, 404)

    def test_missing_permissions(self):
        with self.login_user_context(self.get_staff_user_with_no_permissions()):
            response = self.client.get(self.endpoint)
            self.assertEqual(response.status_code, 200)
            data = response.json()

        # Empty results as the user has no permissions
        self.assertEqual(data, {"results": [], "pagination": {"more": False}})


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

    def test_filter_omits_models_without_matches(self):
        for term, heading in (("root", "Pages"), ("First", "Third party models")):
            with self.subTest(term=term):
                with self.login_user_context(self.get_superuser()):
                    response = self.client.get(self.endpoint, {"term": term})

                self.assertEqual(response.status_code, 200)
                data = response.json()
                self.assertEqual([group["text"] for group in data["results"]], [heading])
                self.assertEqual(len(data["results"][0]["children"]), 1)
                self.assertFalse(data["pagination"]["more"])

    def test_omits_models_without_usable_links(self):
        ThirdPartyModel.objects.update(path="")

        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.endpoint)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual([group["text"] for group in data["results"]], ["Pages"])
        self.assertEqual(len(data["results"][0]["children"]), 1)
        self.assertFalse(data["pagination"]["more"])

    def test_empty_results_when_matches_have_no_usable_links(self):
        ThirdPartyModel.objects.update(path="")

        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.endpoint, {"term": "First"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"results": [], "pagination": {"more": False}})
