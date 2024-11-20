from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog
from django.views.static import serve


admin.autodiscover()

urlpatterns = [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT, "show_indexes": True}),  # NOQA
    re_path(r"^jsi18n/(?P<packages>\S+?)/$", JavaScriptCatalog.as_view()),  # NOQA
]
i18n_urls = [
    re_path(r"^admin/", admin.site.urls),
]

i18n_urls.append(path("", include("cms.urls")))  # NOQA

urlpatterns += i18n_patterns(*i18n_urls)
urlpatterns += staticfiles_urlpatterns()
