try:
    from django_select2.fields import AutoModelSelect2Field

    class PageSearchField(AutoModelSelect2Field):
        search_fields = ['title_set__title']

    class UserSearchField(AutoModelSelect2Field):
        search_fields = ['username', 'firstname', 'lastname']
except:
    pass
