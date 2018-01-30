from distutils.version import LooseVersion

from django.conf import settings

ENABLE_SELECT2 = getattr(settings, 'DJANGOCMS_LINK_USE_SELECT2', False)

if ENABLE_SELECT2 and 'django_select2' in settings.INSTALLED_APPS:
    from djangocms_link.fields_select2 import Select2PageSearchField as PageSearchField
else:
    from cms.forms.fields import PageSelectFormField as PageSearchField
