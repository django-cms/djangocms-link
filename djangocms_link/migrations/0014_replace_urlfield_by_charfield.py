# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djangocms_link.validators


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_link', '0013_fix_hostname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='external_link',
            field=models.CharField(blank=True, help_text='Provide a valid URL to an external website.', max_length=2040, verbose_name='External link', validators=[djangocms_link.validators.IntranetURLValidator(intranet_host_re=None)]),
        ),
    ]
