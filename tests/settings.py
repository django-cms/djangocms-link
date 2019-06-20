#!/usr/bin/env python
# -*- coding: utf-8 -*-
HELPER_SETTINGS = {
    'INSTALLED_APPS': [
        'django_select2',
        'djangocms_text_ckeditor',
        'tests.utils',
    ],
    'CMS_LANGUAGES': {
        1: [{
            'code': 'en',
            'name': 'English',
        }]
    },
    'LANGUAGE_CODE': 'en',
    'ALLOWED_HOSTS': ['localhost'],
    'DJANGOCMS_LINK_USE_SELECT2': True,
    'CMS_TEMPLATES': (
        ('page.html', 'Normal page'),
        ('static_placeholder.html', 'Page with static placeholder'),
    ),
}


def run():
    from djangocms_helper import runner
    runner.cms('djangocms_link')


if __name__ == '__main__':
    run()
