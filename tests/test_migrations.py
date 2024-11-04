# original from
# http://tech.octopus.energy/news/2016/01/21/testing-for-missing-migrations-in-django.html
from io import StringIO
from unittest import skipIf

from django.core.management import call_command
from django.test import TestCase, override_settings

from cms import __version__ as cms_version

from django_test_migrations.contrib.unittest_case import MigratorTestCase

from djangocms_link import __version__
from djangocms_link.helpers import get_link


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

@skipIf(
    __version__[0] > '5' or cms_version < "4",
    "Migration has already been tested before releasing version 5",
)
class MigrationToVersion5(MigratorTestCase):
    migrate_from = ('djangocms_link', '0016_alter_link_cmsplugin_ptr')
    migrate_to = ('djangocms_link', '0018_remove_link_anchor_remove_link_external_link_and_more')

    def prepare(self):
        Link = self.old_state.apps.get_model('djangocms_link', 'Link')
        Page = self.old_state.apps.get_model('cms', 'Page')
        PageContent = self.old_state.apps.get_model('cms', 'PageContent')
        PageUrl = self.old_state.apps.get_model('cms', 'PageUrl')
        TreeNode = self.old_state.apps.get_model('cms', 'TreeNode')
        Site = self.old_state.apps.get_model('sites', 'Site')

        # First create a Site at this stage in migration
        site = Site.objects.create(
            domain='example.com',
            name='example.com',
        )
        # ... then a node
        node = TreeNode.objects.create(
            path='0001',
            depth=1,
            numchild=0,
            parent=None,
            site=site,
        )
        # ... a page
        self.page = Page.objects.create(
            node=node,
        )
        # ... and finally a page content object
        PageContent.objects.create(
            title='My Page',
            page=self.page,
            language='en',
        )
        PageUrl.objects.create(
            page=self.page,
            language='en',
            path='my-page',
        )
        self.links = [
            Link.objects.create(
                template="default",
                name="My Link",
                internal_link=self.page,
                anchor="some_id",
            ),
            Link.objects.create(
                template="default",
                name="My Link",
                external_link="https://www.django-cms.com",
            ),
            Link.objects.create(
                template="default",
                name="My Link",
                external_link="https://www.django-cms.com/",
                anchor="some_id",
            ),
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
            Link.objects.create(
                template="default",
                name="My Link",
                anchor="anchor",
            ),
        ]
        self.urls = [
            "/en/my-page/#some_id",
            "https://www.django-cms.com",
            "https://www.django-cms.com/#some_id",
            "mailto:test@email.com",
            "tel:+0123456789",
            "#anchor",
        ]

    def test_tags_migrated(self):
        Link = self.new_state.apps.get_model('djangocms_link', 'Link')
        links = Link.objects.all()

        for link, url in zip(links, self.urls):
            with self.subTest(link=link, url=url):
                self.assertEqual(get_link(link.link, site_id=1), url)

