# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_link', '0004_auto_20150708_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='anchor',
            field=models.CharField(help_text='This applies only to page and text links.Do <em>not</em> include a preceding "#" symbol.', max_length=128, verbose_name='anchor', blank=True),
        ),
        migrations.AlterField(
            model_name='link',
            name='mailto',
            field=models.EmailField(help_text='An email address has priority over a text link.', max_length=254, null=True, verbose_name='mailto', blank=True),
        ),
    ]
