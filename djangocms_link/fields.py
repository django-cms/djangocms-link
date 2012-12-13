
try:
    from django_select2.fields import AutoModelSelect2Field
    from django_select2 import AutoHeavySelect2Widget
    from django_select2.util import JSFunction


    class SearchWidget(AutoHeavySelect2Widget):
        def init_options(self):
            super(SearchWidget, self).init_options()
            self.options['minimumInputLength'] = 1  # search right away
            self.options['formatResult'] = JSFunction('''function(object, container, query){return object.path + '<br/><strong style="font-size: 14px;">' + object.text + '</strong>';}''')
            self.options['formatSelection'] = JSFunction('''function(object, container){return object.text;}''')
            self.options['width'] = '30em'


    class PageSearchField(AutoModelSelect2Field):
        search_fields = ['title_set__title__icontains', 'title_set__menu_title__icontains', 'title_set__slug__icontains']
        widget = SearchWidget

        def __init__(self, *args, **kwargs):
            super(PageSearchField, self).__init__(*args, **kwargs)
            self.max_results = 50  # will load 50 results at a time and will fetch more when scrolling down.

        def security_check(self, request, *args, **kwargs):
            user = request.user
            if user and not user.is_anonymous() and user.is_staff:
                return True
            return False

        def extra_data_from_instance(self, obj):
            breadcrumbs = [p.get_menu_title() for p in obj.get_ancestors()]
            path = u" | ".join(breadcrumbs)
            return {
                'breadcrumbs': breadcrumbs,
                'path': path,
            }

    class UserSearchField(AutoModelSelect2Field):
        search_fields = ['username__icontains', 'firstname__icontains', 'lastname__icontains']

        def security_check(self, request, *args, **kwargs):
            user = request.user
            if user and not user.is_anonymous() and user.is_staff:
                return True
            return False
except ImportError:
    pass
