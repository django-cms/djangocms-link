# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djangocms_link.validators
from djangocms_link.models import HOSTNAME


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_link', '0012_removed_null'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='external_link',
            field=models.URLField(blank=True, help_text='Provide a valid URL to an external website.', max_length=2040, verbose_name='External link', validators=[djangocms_link.validators.IntranetURLValidator(intranet_host_re=HOSTNAME)]),
        ),
    ]
