# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings

if 'django_select2' in settings.INSTALLED_APPS:
    from django_select2.fields import AutoModelSelect2Field

    class PageSearchField(AutoModelSelect2Field):
        site = None
        search_fields = [
            'title_set__title__icontains',
            'title_set__menu_title__icontains',
            'title_set__slug__icontains'
        ]

        def get_queryset(self):
            from cms.models import Page
            if self.site:
                return Page.objects.drafts().on_site(self.site)
            else:
                return Page.objects.drafts()

        def security_check(self, request, *args, **kwargs):
            user = request.user
            if user and not user.is_anonymous() and user.is_staff:
                return True
            return False

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
            return super(UserSearchField, self).prepare_value(value)
