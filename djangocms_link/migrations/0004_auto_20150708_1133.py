# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import djangocms_link.validators


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_link', '0003_auto_20150212_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='anchor',
            field=models.CharField(help_text='This applies only to page and text links. Do <em>not</em> include a preceding "#" symbol.', max_length=128, verbose_name='anchor', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='link',
            name='url',
            field=models.CharField(blank=True, max_length=2048, null=True, verbose_name='link', validators=[djangocms_link.validators.IntranetURLValidator(intranet_host_re=None)]),
            preserve_default=True,
        ),
    ]
