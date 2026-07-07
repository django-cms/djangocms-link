from django.contrib import admin

from tests.utils.models import AnotherLinkableModel, ThirdPartyModel


@admin.register(ThirdPartyModel)
class ThirdPartyAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(AnotherLinkableModel)
class AnotherLinkableAdmin(admin.ModelAdmin):
    search_fields = ("title", "slug")
