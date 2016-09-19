# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def reset_null_values(apps, schema_editor):
    Link = apps.get_model('djangocms_link', 'Link')
    plugins = Link.objects.all()
    plugins.filter(external_link__isnull=True).update(external_link='')
    plugins.filter(mailto__isnull=True).update(mailto='')
    plugins.filter(phone__isnull=True).update(phone='')


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_link', '0010_adapted_fields'),
    ]

    operations = [
        migrations.RunPython(reset_null_values),
    ]
