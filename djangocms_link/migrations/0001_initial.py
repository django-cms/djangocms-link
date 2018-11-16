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
                ('cmsplugin_ptr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, serialize=False, parent_link=True, auto_created=True, to='cms.CMSPlugin', primary_key=True)),
                ('name', models.CharField(verbose_name='name', max_length=256)),
                ('url', models.URLField(verbose_name='link', blank=True, null=True)),
                ('anchor', models.CharField(help_text='This applies only to page and text links.', blank=True, default='', max_length=128, verbose_name='anchor')),
                ('mailto', models.EmailField(help_text='An email address has priority over a text link.', blank=True, null=True, max_length=75, verbose_name='mailto')),
                ('phone', models.CharField(help_text='A phone number has priority over a mailto link.', blank=True, null=True, max_length=40, verbose_name='Phone')),
                ('target', models.CharField(verbose_name='target', blank=True, max_length=100, choices=[('', 'same window'), ('_blank', 'new window'), ('_parent', 'parent window'), ('_top', 'topmost frame')])),
                ('page_link', models.ForeignKey(help_text='A link to a page has priority over a text link.', on_delete=django.db.models.deletion.SET_NULL, blank=True, verbose_name='page', to='cms.Page', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
