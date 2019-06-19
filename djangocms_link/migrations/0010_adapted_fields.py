# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models

import djangocms_attributes_field.fields

from djangocms_link.models import get_templates


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_link', '0009_auto_20160705_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='template',
            field=models.CharField(default=get_templates()[0][0], max_length=255, verbose_name='Template', choices=get_templates()),
        ),
        migrations.RenameField(
            model_name='link',
            old_name='url',
            new_name='external_link',
        ),
        migrations.RenameField(
            model_name='link',
            old_name='page_link',
            new_name='internal_link',
        ),
        migrations.AlterField(
            model_name='link',
            name='anchor',
            field=models.CharField(help_text='Appends the value only after the internal or external link. Do <em>not</em> include a preceding "#" symbol.', max_length=255, verbose_name='Anchor', blank=True),
        ),
        migrations.AlterField(
            model_name='link',
            name='attributes',
            field=djangocms_attributes_field.fields.AttributesField(default=dict, verbose_name='Attributes', blank=True),
        ),
        migrations.AlterField(
            model_name='link',
            name='internal_link',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='cms.Page', help_text='If provided, overrides the external link.', null=True, verbose_name='Internal link'),
        ),
        migrations.AlterField(
            model_name='link',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Display name', blank=True),
        ),
        migrations.AlterField(
            model_name='link',
            name='target',
            field=models.CharField(blank=True, max_length=255, verbose_name='Target', choices=[('_blank', 'Open in new window'), ('_self', 'Open in same window'), ('_parent', 'Delegate to parent'), ('_top', 'Delegate to top')]),
        ),
    ]
