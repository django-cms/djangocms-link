from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from models import Link
from cms.models import Page

class LinkForm(ModelForm):
    try:
        from .fields import PageSearchField
        page_link = PageSearchField(label=_("page"), queryset=Page.objects.drafts(), required=False)
    except ImportError:
        from cms.forms.fields import PageSelectFormField
        page_link = PageSelectFormField (label=_("page"), queryset=Page.objects.drafts(), required=False)

    def for_site(self, site):
        # override the page_link fields queryset to containt just pages for
        # current site
        self.fields['page_link'].queryset = Page.objects.drafts().on_site(site)

    class Meta:
        model = Link
        exclude = ('page', 'position', 'placeholder', 'language', 'plugin_type')
