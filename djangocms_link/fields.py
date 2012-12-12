try:
    from django_select2.fields import AutoModelSelect2Field

    class PageSearchField(AutoModelSelect2Field):
        search_fields = ['title_set__title__icontains', 'title_set__menu_title__icontains', 'title_set__slug__icontains']

    class UserSearchField(AutoModelSelect2Field):
        search_fields = ['username__icontains', 'firstname__icontains', 'lastname__icontains']
except ImportError:
    pass
