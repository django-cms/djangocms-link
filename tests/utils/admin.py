from django.contrib import admin

from tests.utils.models import ThirdPartyModel


@admin.register(ThirdPartyModel)
class ThirdPartyAdmin(admin.ModelAdmin):
    search_fields = ("name",)
