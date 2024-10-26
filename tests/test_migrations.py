# original from
# http://tech.octopus.energy/news/2016/01/21/testing-for-missing-migrations-in-django.html
from io import StringIO
from unittest import skipIf

from django.core.management import call_command
from django.forms import model_to_dict
from django.test import TestCase, override_settings

from cms.api import create_page

from django_test_migrations.contrib.unittest_case import MigratorTestCase

from djangocms_link import __version__
from djangocms_link.helpers import get_link
from tests.helpers import get_filer_file


class MigrationTestCase(TestCase):
    @override_settings(MIGRATION_MODULES={})
    def test_for_missing_migrations(self):
        output = StringIO()
        options = {
            'interactive': False,
            'dry_run': True,
            'stdout': output,
            'check_changes': True,
        }

        try:
            call_command('makemigrations', **options)
        except SystemExit as e:
            status_code = str(e)
        else:
            # the "no changes" exit code is 0
            status_code = '0'

        if status_code == '1' and "djangocms_link" in output:
            self.fail(f'There are missing migrations:\n {output.getvalue()}')

# @skipIf(__version__ >= '5', "Migration has already been tested before releasing version 5")
class MigrationToVersion5(MigratorTestCase):
    migrate_from = ('djangocms_link', '0016_alter_link_cmsplugin_ptr')
    migrate_to = ('djangocms_link', '0018_remove_link_anchor_remove_link_external_link_and_more')

    def setUp(self):
        self.page = model_to_dict(create_page(
            title='test',
            template='page.html',
            language='en',
        ))
        if hasattr(self.page, "node"):
            self.node = model_to_dict(self.page.node)
        self.file = model_to_dict(get_filer_file())
        super().setUp()

    def prepare(self):
        Link = self.old_state.apps.get_model('djangocms_link', 'Link')
        Page = self.old_state.apps.get_model('cms', 'Page')
        File = self.old_state.apps.get_model('filer', 'File')

        self.links = [
            # Link.objects.create(
            #     template="default",
            #     name="My Link",
            #     internal_link=self.page,
            #     anchor="some_id",
            # ),
            Link.objects.create(
                template="default",
                name="My Link",
                external_link="http://www.django-cms.com",
            ),
            # Link.objects.create(
            #     template="default",
            #     name="My Link",
            #     file_link=self.file,
            # ),
            Link.objects.create(
                template="default",
                name="My Link",
                mailto="test@email.com",
            ),
            Link.objects.create(
                template="default",
                name="My Link",
                phone="+01 234 567 89",
            ),
        ]
        self.urls = ["http://www.django-cms.com", "mailto:test@email.com", "tel:+0123456789"]

    def test_tags_migrated(self):
        Link = self.new_state.apps.get_model('djangocms_link', 'Link')
        links = Link.objects.all()

        for link, url in zip(links, self.urls):
            with self.subTest(link=link, url=url):
                self.assertEqual(get_link(link.link), url)

