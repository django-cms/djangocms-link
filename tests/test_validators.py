from django.test import TestCase

from djangocms_link.models import HOSTNAME
from djangocms_link.validators import IntranetURLValidator


class LinkValidatorTestCase(TestCase):

    def test_intranet_host_re(self):
        host = r'[a-z,0-9,-]{1,15}'
        host_re = (
            '(' + IntranetURLValidator.hostname_re
            + IntranetURLValidator.domain_re
            + IntranetURLValidator.tld_re +
            '|' + host + '|localhost)'
        )
        validator = IntranetURLValidator(
            intranet_host_re=host,
        )
        self.assertEqual(validator.host_re, host_re)
        self.assertIsNone(HOSTNAME)
