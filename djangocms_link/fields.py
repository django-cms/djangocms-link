from distutils.version import LooseVersion

from django.conf import settings

ENABLE_SELECT2 = getattr(settings, 'DJANGOCMS_LINK_USE_SELECT2', False)

if ENABLE_SELECT2 and 'django_select2' in settings.INSTALLED_APPS:
    import django_select2

    select2_version = LooseVersion(django_select2.__version__)
    if select2_version >= LooseVersion('5'):
        from djangocms_link.fields_select2 import Select2PageSearchField as PageSearchField
    else:
        from djangocms_link.fields_select2_legacy import Select2LegacyPageSearchField as PageSearchField
else:
    from cms.forms.fields import PageSelectFormField as PageSearchField
