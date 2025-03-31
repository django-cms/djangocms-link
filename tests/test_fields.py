from django import forms
from django.test import TestCase

from cms.api import create_page

from djangocms_link.fields import LinkFormField, LinkWidget
from tests.helpers import get_filer_file


class LinkFieldTestCase(TestCase):
    def setUp(self):
        self.page = create_page(
            title="django CMS is fun",
            template="page.html",
            language="en",
        )
        self.file = get_filer_file()

    def test_form_field_rendering(self):
        class LinkForm(forms.Form):
            link_field = LinkFormField(required=True)

        form = LinkForm()
        form_html = str(form)

        # Render widget
        self.assertIn(
            '<div name="link_field" class="link-widget widget" required id="id_link_field">',
            form_html,
        )
        # Render selector
        self.assertIn(
            '<select name="link_field_0" class="js-link-widget-selector" data-help="No destination selected. '
            'Use the dropdown to select a destination." required id="id_link_field_0">'
            '<option value="internal_link">Internal link</option>'
            '<option value="external_link">External link/anchor</option>'
            '<option value="file_link">File link</option></select>',
            form_html,
        )
        # Render internal URL field
        self.assertIn(
            '<select name="link_field_2" widget="internal_link" '
            'data-help="Select from available internal destinations. Optionally, add an anchor to scroll to." '
            'data-placeholder="" required id="id_link_field_2" class="admin-autocomplete" data-ajax--cache="true" '
            'data-ajax--delay="250" data-ajax--type="GET" data-ajax--url="/en/admin/djangocms_link/link/urls" '
            'data-theme="admin-autocomplete" data-allow-clear="true" '
            'data-minimum-input-length="0" lang="en">'
            '<option value=""></option><option value="" selected>None</option>'
            "</select>",
            form_html,
        )
        # Render external URL field
        self.assertIn(
            '<input type="url" name="link_field_1" widget="external_link" '
            'placeholder="https://example.com or #anchor" '
            'data-help="Provide a link to an external URL, including the schema such as &#x27;https://&#x27;, '
            '&#x27;tel:&#x27;, or &#x27;mailto:&#x27;. Optionally, add an #anchor (including the #) to scroll to." '
            'required id="id_link_field_1">',
            form_html,
        )

        class LinkNotRequiredForm(forms.Form):
            link_field = LinkFormField(required=False)

        # Render selector with empty option
        self.assertIn(
            '<select name="link_field_0" class="js-link-widget-selector" data-help="No destination selected. '
            'Use the dropdown to select a destination." id="id_link_field_0">'
            '<option value="empty">---------</option>'
            '<option value="internal_link">Internal link</option>'
            '<option value="external_link">External link/anchor</option>'
            '<option value="file_link">File link</option></select>',
            str(LinkNotRequiredForm()),
        )

    def prepare_value(self, form, value):
        return form.fields["link_field"].prepare_value(value)

    def test_form_field_transparency(self):
        class LinkForm(forms.Form):
            link_field = LinkFormField(required=False)

        def check_value(value):
            # Creates submission data for value and checks if the form returns the submitted value
            data = {
                f"link_field_{i}": item
                for i, item in enumerate(self.prepare_value(LinkForm(), value))
            }
            form = LinkForm(data=data)
            self.assertTrue(form.is_valid(), form.errors)
            self.assertEqual(form.cleaned_data["link_field"], value)

        check_value({"internal_link": f"cms.page:{self.page.id}", "anchor": "#anchor"})
        check_value({"external_link": "https://example.com"})
        check_value({"external_link": "#anchor"})
        check_value({"file_link": str(self.file.id)})
        check_value({})

    def test_form_field_initial_works_internal(self):
        class LinkForm(forms.Form):
            link_field = LinkFormField(required=False)

        form = LinkForm(initial={"link_field": {"internal_link": f"cms.page:{self.page.id}"}})
        self.assertEqual(form["link_field"].value(), ["internal_link", None, f"cms.page:{self.page.id}", "", None])

    def test_form_field_initial_works_external(self):
        class LinkForm(forms.Form):
            link_field = LinkFormField(required=False)

        some_string = "https://example.com"
        form = LinkForm(initial={"link_field": {"external_link": some_string}})
        self.assertEqual(form["link_field"].value(), ["external_link", some_string, None, None, None])

    def test_widget_renders_selection(self):
        widget = LinkWidget()
        pre_select_page = len(widget.widgets) * [None]
        pre_select_page[0] = "internal_link"
        pre_select_page[2] = f"cms.page:{self.page.id}"
        rendered_widget = widget.render(
            "link_field", pre_select_page, attrs={"id": "id_link_field"}
        )

        self.assertIn(
            '<option value="cms.page:1" selected>django CMS is fun</option>',
            rendered_widget,
        )

    def test_widget_renders_site_selector(self):
        widget = LinkWidget(site_selector=True)
        pre_select_page = len(widget.widgets) * [None]
        pre_select_page[0] = "internal_link"
        pre_select_page[2] = f"cms.page:{self.page.id}"
        rendered_widget = widget.render(
            "link_field", pre_select_page, attrs={"id": "id_link_field"}
        )

        # Subwidget is present
        self.assertIn(
            '<select name="link_field_2" class="js-link-site-widget admin-autocomplete" widget="site"',
            rendered_widget,
        )
        # Current site is pre-selected
        self.assertIn(
            '<option value="1" selected>example.com</option>', rendered_widget
        )
        # Site selector uses django admin autocomplete
        self.assertIn('data-ajax--url="/en/admin/autocomplete/"', rendered_widget)
