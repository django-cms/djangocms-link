#!/usr/bin/env python
from tempfile import mkdtemp


HELPER_SETTINGS = {
    'INSTALLED_APPS': [
        'filer',
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
    'THUMBNAIL_PROCESSORS': (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.filters',
    ),
    'ALLOWED_HOSTS': ['localhost'],
    'DJANGOCMS_LINK_USE_SELECT2': True,
    'CMS_TEMPLATES': (
        ('page.html', 'Normal page'),
        ('static_placeholder.html', 'Page with static placeholder'),
    ),
    'FILE_UPLOAD_TEMP_DIR': mkdtemp(),
}


def run():
    from app_helper import runner
    runner.cms('djangocms_link')


if __name__ == '__main__':
    run()
