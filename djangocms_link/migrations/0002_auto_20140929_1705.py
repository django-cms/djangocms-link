# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_link', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='anchor',
            field=models.CharField(help_text='This applies only to page and text links.', max_length=128, verbose_name='anchor', blank=True),
        ),
    ]
