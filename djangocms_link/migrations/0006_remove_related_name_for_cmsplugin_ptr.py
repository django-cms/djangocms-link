# Generated by Django 1.9.2 on 2016-02-26 14:19
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_link', '0005_auto_20151003_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='cmsplugin_ptr',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='+', serialize=False, to='cms.CMSPlugin'),
        ),
    ]
