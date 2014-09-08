from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, NoReverseMatch
from django.core.validators import URLValidator
from django.db import models
from django.shortcuts import resolve_url
from django.utils.translation import ugettext_lazy as _
from cms.models import CMSPlugin, Page

def validate_url_or_viewname(value):
    # Try a reverse URL resolution.
    try:
        return reverse(value)
    except NoReverseMatch:
        # If this doesn't "feel" like a URL, re-raise.
        if '/' not in value and '.' not in value:
            raise ValidationError(_('Enter a valid view name.'), code='invalid')
        
    # Validate url
    URLValidator()(value)

class Link(CMSPlugin):
    """
    A link to an other page or to an external website
    """
    name = models.CharField(_("name"), max_length=256)
    url = models.CharField(_("link"), max_length=200, blank=True, null=True, validators=[validate_url_or_viewname], help_text=_("URL or view name."))
    page_link = models.ForeignKey(Page, verbose_name=_("page"), blank=True, null=True, help_text=_("A link to a page has priority over a text link."), on_delete=models.SET_NULL)
    anchor = models.CharField(_("anchor"), max_length=128, blank=True, default='', help_text=_("This applies only to page and text links."))
    mailto = models.EmailField(_("mailto"), blank=True, null=True, help_text=_("An email adress has priority over a text link."))
    phone = models.CharField(_('Phone'), blank=True, null=True, max_length=40,
                             help_text=_('A phone number has priority over a mailto link.'))
    target = models.CharField(_("target"), blank=True, max_length=100, choices=((
        ("", _("same window")),
        ("_blank", _("new window")),
        ("_parent", _("parent window")),
        ("_top", _("topmost frame")),
    )))

    def link(self):
        if self.phone:
            link = u"tel://%s" % self.phone
        elif self.mailto:
            link = u"mailto:%s" % self.mailto
        elif self.url:
            try: 
                link = resolve_url(self.url)
            except:
                link = ""
        elif self.page_link:
            link = self.page_link.get_absolute_url()
        else:
            link = ""
        if (self.url or self.page_link) and self.anchor:
            link += '#' + self.anchor
        return link

    def __unicode__(self):
        return self.name

    search_fields = ('name',)

