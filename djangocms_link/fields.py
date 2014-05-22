from django.conf import settings
# to enable django_select2:
# - the app must be in the installed apps
# - the setting DJANGOCMS_LINK_ENABLE_SELECT2 must be set to True

if 'django_select2' in settings.INSTALLED_APPS and getattr(settings, "DJANGOCMS_LINK_ENABLE_SELECT2", False):
    try:

        from django_select2.fields import AutoModelSelect2Field

        class PageSearchField(AutoModelSelect2Field):
            empty_value = []
            search_fields = ['title_set__title__icontains', 'title_set__menu_title__icontains', 'title_set__slug__icontains']

            def security_check(self, request, *args, **kwargs):
                user = request.user
                if user and not user.is_anonymous() and user.is_staff:
                    return True
                return False

            def prepare_value(self, value):
                if not value:
                    return None
                return super(PageSearchField, self).prepare_value(value)

        class UserSearchField(AutoModelSelect2Field):
            search_fields = ['username__icontains', 'firstname__icontains', 'lastname__icontains']

            def security_check(self, request, *args, **kwargs):
                user = request.user
                if user and not user.is_anonymous() and user.is_staff:
                    return True
                return False

            def prepare_value(self, value):
                if not value:
                    return None
                return super(PageSearchField, self).prepare_value(value)

    except ImportError:
        pass

