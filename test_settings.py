# -*- coding: utf-8 -*-
from distutils.version import LooseVersion
import sys
from tempfile import mkdtemp
import django

gettext = lambda s: s

HELPER_SETTINGS = {
    'INSTALLED_APPS': [
        'django_select2',
        'djangocms_text_ckeditor',
    ],
    'LANGUAGE_CODE': 'en',
    'LANGUAGES': (
        ('en', gettext('English')),
        ('fr', gettext('French')),
        ('it', gettext('Italiano')),
    ),
    'CMS_LANGUAGES': {
        1: [
            {
                'code': 'en',
                'name': gettext('English'),
                'public': True,
            },
            {
                'code': 'it',
                'name': gettext('Italiano'),
                'public': True,
            },
            {
                'code': 'fr',
                'name': gettext('French'),
                'public': True,
            },
        ],
        'default': {
            'hide_untranslated': False,
        },
    },
    'CMS_PERMISSION': True,
    'FILE_UPLOAD_TEMP_DIR': mkdtemp(),
    'SITE_ID': 1
}


def run():
    from djangocms_helper import runner
    runner.cms('djangocms_link')

if __name__ == "__main__":
    run()

