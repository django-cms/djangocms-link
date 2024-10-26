from django.test import TestCase

from djangocms_link.models import HOSTNAME
from djangocms_link.validators import ExtendedURLValidator


class LinkValidatorTestCase(TestCase):
    def assertValidates(self, validator, value):
        try:
            validator(value)
        except Exception as e:
            self.fail(f"Validation of {value} failed with {e}")

    def assertDoesNotValidate(self, validator, value):
        try:
            validator(value)
            self.fail(f"Validation of {value} unexpectedly did not fail")
        except Exception:
            pass

    def test_intranet_host_re(self):
        host = r'[a-z,0-9,-]{1,15}'
        host_re = (
            '(' + ExtendedURLValidator.hostname_re
            + ExtendedURLValidator.domain_re
            + ExtendedURLValidator.tld_re +
            '|' + host + '|localhost)'
        )
        validator = ExtendedURLValidator(
            intranet_host_re=host,
        )
        self.assertEqual(validator.host_re, host_re)
        self.assertIsNone(HOSTNAME)

    def test_tel_validation(self):
        validator = ExtendedURLValidator()

        self.assertValidates(validator, "tel:0123456789")
        self.assertValidates(validator, "tel:01 234 567 89")
        self.assertValidates(validator, "tel:+01 234 567 89")
        self.assertDoesNotValidate(validator, "tel:")
        self.assertDoesNotValidate(validator, "tel:0800-django-cms")
        self.assertDoesNotValidate(validator, "tel:info@django-cms.org")

    def test_mailto_validation(self):
        validator = ExtendedURLValidator()

        self.assertValidates(validator, "mailto:info@django-cms.org")
        self.assertValidates(validator, "mailto:test@long.subdomain.path.email.com")
        self.assertDoesNotValidate(validator, "mailto:info@localhost")
        self.assertDoesNotValidate(validator, "mailto:")
        self.assertDoesNotValidate(validator, "mailto: info@django-cms.org")

    def test_wrong_type_fails(self):
        validator = ExtendedURLValidator()

        self.assertDoesNotValidate(validator, "\n")
        self.assertDoesNotValidate(validator, 42)

    def test_anchor(self):
        validator = ExtendedURLValidator()
        self.assertValidates(validator, "#anchor")
        self.assertValidates(validator, "#anchor-1")
        self.assertValidates(validator, "#anchor_1")
        self.assertDoesNotValidate(validator, "#anchor!")
        self.assertDoesNotValidate(validator, "#anchor with spaces")
        self.assertValidates(validator, "#" + "a" * (100 - 1))
        self.assertDoesNotValidate(validator, "#" + "a" * 101)
        self.assertValidates(validator, "#")
