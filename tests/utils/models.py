from django.db import models


class ThirdPartyModel(models.Model):
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    site = models.ForeignKey("sites.Site", on_delete=models.SET_NULL, null=True)

    def get_absolute_url(self):
        return self.path

    def __str__(self):
        return self.name


class AnotherLinkableModel(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    site = models.ForeignKey("sites.Site", on_delete=models.SET_NULL, null=True)

    def get_absolute_url(self):
        return f"/another/{self.slug}/"

    def __str__(self):
        return self.title
