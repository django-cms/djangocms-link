# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

import djangocms_link.validators


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_link', '0011_fixed_null_values'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='external_link',
            field=models.URLField(default='', validators=[djangocms_link.validators.IntranetURLValidator(intranet_host_re=None)], max_length=2040, blank=True, help_text='Provide a valid URL to an external website.', verbose_name='External link'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='link',
            name='mailto',
            field=models.EmailField(default='', max_length=255, verbose_name='Email address', blank=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='link',
            name='phone',
            field=models.CharField(default='', max_length=255, verbose_name='Phone', blank=True),
            preserve_default=False,
        ),
    ]
