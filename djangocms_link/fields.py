from django.conf import settings


def is_select2_enabled():
    use_select2 = getattr(settings, 'DJANGOCMS_LINK_USE_SELECT2', False)
    is_installed = 'django_select2' in settings.INSTALLED_APPS
    return use_select2 and is_installed


if is_select2_enabled():
    from djangocms_link.fields_select2 import Select2PageSearchField as PageSearchField  # noqa
else:
    from cms.forms.fields import PageSelectFormField as PageSearchField  # noqa
