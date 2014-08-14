# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('name', models.CharField(max_length=256, verbose_name='name')),
                ('url', models.URLField(null=True, verbose_name='link', blank=True)),
                ('mailto', models.EmailField(help_text='An email address has priority over a text link.', max_length=75, null=True, verbose_name='email address', blank=True)),
                ('phone', models.CharField(help_text='A phone number has priority over a mailto link.', max_length=40, null=True, verbose_name='Phone', blank=True)),
                ('target', models.CharField(blank=True, max_length=100, verbose_name='target', choices=[(b'', 'same window'), (b'_blank', 'new window'), (b'_parent', 'parent window'), (b'_top', 'topmost frame')])),
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('page_link', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='cms.Page', help_text='A link to a page has priority over a text link.', null=True, verbose_name='page')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
