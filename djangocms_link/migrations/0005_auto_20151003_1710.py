from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_link', '0004_auto_20150708_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='mailto',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address', null=True, help_text='An email address has priority over a text link.'),
        ),
    ]
