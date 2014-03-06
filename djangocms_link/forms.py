from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from djangocms_link.models import Link
from cms.models import Page
from django.forms.widgets import Media


class LinkForm(ModelForm):
    try:
        from djangocms_link.fields import PageSearchField
        page_link = PageSearchField(queryset=Page.objects.drafts(), label=_("page"), required=False)
    except ImportError:
        from cms.forms.fields import PageSelectFormField
        page_link = PageSelectFormField(queryset=Page.objects.drafts(), label=_("page"), required=False)

    def for_site(self, site):
        # override the page_link fields queryset to containt just pages for
        # current site
        from cms.models import Page
        self.fields['page_link'].queryset = Page.objects.drafts().on_site(site)

    class Meta:
        model = Link
        exclude = ('page', 'position', 'placeholder', 'language', 'plugin_type')

    def _get_media(self):
        """
        Provide a description of all media required to render the widgets on this form
        """
        media = Media()
        for field in self.fields.values():
            media = media + field.widget.media
        media._js = ['cms/js/libs/jquery.min.js'] + media._js
        return media
    media = property(_get_media)
