#!/usr/bin/env python
from tempfile import mkdtemp


HELPER_SETTINGS = {
    "INSTALLED_APPS": [
        "filer",
        "tests.utils",
    ],
    "CMS_LANGUAGES": {
        1: [
            {
                "code": "en",
                "name": "English",
            }
        ]
    },
    "LANGUAGE_CODE": "en",
    "THUMBNAIL_PROCESSORS": (
        "easy_thumbnails.processors.colorspace",
        "easy_thumbnails.processors.autocrop",
        "filer.thumbnail_processors.scale_and_crop_with_subject_location",
        "easy_thumbnails.processors.filters",
    ),
    "ALLOWED_HOSTS": ["localhost"],
    "CMS_TEMPLATES": (
        ("page.html", "Normal page"),
        ("static_placeholder.html", "Page with static placeholder"),
    ),
    "FILE_UPLOAD_TEMP_DIR": mkdtemp(),
    "CMS_CONFIRM_VERSION4": True,
    "DJANGOCMS_LINKABLE_MODELS": ["utils.thirdpartymodel"],
}


def run():
    from app_helper import runner

    runner.cms("djangocms_link")


if __name__ == "__main__":
    run()
