#!/usr/bin/env python
import os
import sys

import django
from django.conf import global_settings, settings
from django.test.utils import get_runner

from tests.settings import HELPER_SETTINGS


CMS_APP = [
    "cms",
    "menus",
    "easy_thumbnails",
    "treebeard",
    "sekizai",
    "djangocms_link",
]
CMS_APP_STYLE = []
CMS_PROCESSORS = []
CMS_MIDDLEWARE = [
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
]

INSTALLED_APPS = (
    [
        "django.contrib.contenttypes",
        "django.contrib.auth",
        "django.contrib.sessions",
        "django.contrib.sites",
        "django.contrib.staticfiles",
    ]
    + CMS_APP_STYLE
    + ["django.contrib.admin", "django.contrib.messages"]
    + CMS_APP
)
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
TEMPLATE_CONTEXT_PROCESSORS = [
    "django.template.context_processors.debug",
    "django.template.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
] + CMS_PROCESSORS
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(os.path.dirname(__file__), "templates"),
            # insert your TEMPLATE_DIRS here
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": TEMPLATE_CONTEXT_PROCESSORS,
        },
    },
]
MIDDLEWARE = [
    "django.middleware.http.ConditionalGetMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
] + CMS_MIDDLEWARE
SITE_ID = 1
LANGUAGE_CODE = "en"
LANGUAGES = (("en", "English"),)
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MIGRATION_MODULES = {}
URL_CONF = "tests.utils.urls"


def pytest_configure():
    INSTALLED_APPS.extend(HELPER_SETTINGS.pop("INSTALLED_APPS"))

    settings.configure(
        default_settings=global_settings,
        **{
            **dict(
                INSTALLED_APPS=INSTALLED_APPS,
                TEMPLATES=TEMPLATES,
                DATABASES=DATABASES,
                SITE_ID=SITE_ID,
                LANGUAGE_CODE=LANGUAGE_CODE,
                LANGUAGES=LANGUAGES,
                MIGRATION_MODULES=MIGRATION_MODULES,
                ROOT_URLCONF=URL_CONF,
                STATIC_URL=STATIC_URL,
                MEDIA_URL=MEDIA_URL,
                SECRET_KEY="Secret!",
                MIDDLEWARE=MIDDLEWARE,
            ),
            **HELPER_SETTINGS,
        }
    )
    django.setup()


if __name__ == "__main__":
    pytest_configure()

    argv = ["tests"] if sys.argv is None else sys.argv
    tests = argv[1:] if len(argv) > 1 else ["tests"]
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(tests)
    sys.exit(bool(failures))
