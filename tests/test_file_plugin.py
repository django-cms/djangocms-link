# -*- coding: utf-8 -*-
import os

from django.conf import settings
from django.core.files import File as DjangoFile

from cms.api import add_plugin, create_page

from djangocms_helper.base_test import BaseTestCase
from filer.models.filemodels import File as FilerFile
from filer.utils.compatibility import PILImage, PILImageDraw


# from https://github.com/divio/django-filer/blob/develop/tests/helpers.py#L46-L52
def create_image(mode="RGB", size=(800, 600)):
    image = PILImage.new(mode, size)
    draw = PILImageDraw.Draw(image)
    x_bit, y_bit = size[0] // 10, size[1] // 10
    draw.rectangle((x_bit, y_bit * 2, x_bit * 7, y_bit * 3), "red")
    draw.rectangle((x_bit * 2, y_bit, x_bit * 3, y_bit * 8), "red")
    return image


class LinkTestCase(BaseTestCase):
    def setUp(self):
        self.page = create_page(
            title="help",
            template="page.html",
            language="en",
        )

        self.img = create_image()
        self.image_name = "test_file.jpg"
        self.filename = os.path.join(settings.FILE_UPLOAD_TEMP_DIR, self.image_name)
        self.img.save(self.filename, "JPEG")

    def tearDown(self):
        os.remove(self.filename)
        for f in FilerFile.objects.all():
            f.delete()
        pass

    def create_filer_file(self):
        filer_file = DjangoFile(open(self.filename, "rb"), name=self.image_name)
        return FilerFile.objects.create(
            original_filename=self.image_name,
            file=filer_file,
        )

    def test_file(self):
        sample_file = self.create_filer_file()

        plugin = add_plugin(
            self.page.placeholders.get(slot="content"),
            "LinkPlugin",
            "en",
            file_link=sample_file
        )
        self.assertIn("test_file.jpg", plugin.get_link())
        self.assertIn("/media/filer_public/", plugin.get_link())
