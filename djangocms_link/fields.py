try:
    from django_select2.fields import AutoModelSelect2Field

    class PageSearchField(AutoModelSelect2Field):
        search_fields = ['title_set__title__icontains', 'title_set__menu_title__icontains', 'title_set__slug__icontains']

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
except ImportError:
    pass
