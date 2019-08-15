# -*- coding: utf-8 -*-
from django.test import TestCase
from django.conf import settings

from djangocms_link.validators import IntranetURLValidator


class LinkValidatorTestCase(TestCase):

    def test_intranet_host_re(self):
        self.assertIsNone(settings.DJANGOCMS_LINK_INTRANET_HOSTNAME_PATTERN)
        HOSTNAME = r'[a-z,0-9,-]{1,15}'
        host_re = (
            '(' + IntranetURLValidator.hostname_re
            + IntranetURLValidator.domain_re
            + IntranetURLValidator.tld_re +
            '|' + HOSTNAME + '|localhost)'
        )
        validator = IntranetURLValidator(
            intranet_host_re=HOSTNAME,
        )
        self.assertEqual(validator.host_re, host_re)
