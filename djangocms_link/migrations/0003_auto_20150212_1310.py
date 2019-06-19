# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_link', '0002_auto_20140929_1705'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='mailto',
            field=models.EmailField(help_text='An email address has priority over a text link.', max_length=75, null=True, verbose_name='email address', blank=True),
            preserve_default=True,
        ),
    ]
