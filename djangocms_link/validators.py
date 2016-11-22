# -*- coding: utf-8 -*-
import re

from django.core.validators import URLValidator


class IntranetURLValidator(URLValidator):
    """
    This is essentially the normal, Django URL Validator, but allows for
    "internal" machine-name only "hostnames" as defined by the RegEx pattern
    defined in settings as well as normal, FQD-based hostnames.

    Some examples:
    RFC1123 Pattern
        DJANGOCMS_LINK_INTRANET_HOSTNAME_PATTERN = r'[a-z,0-9,-]{1,15}'
    """

    ul = '\u00a1-\uffff'  # unicode letters range (must be a unicode string, not a raw string)

    # IP patterns
    ipv4_re = r'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'
    ipv6_re = r'\[[0-9a-f:\.]+\]'  # (simple regex, validated later)

    # Host patterns
    hostname_re = r'[a-z' + ul + r'0-9](?:[a-z' + ul + r'0-9-]*[a-z' + ul + r'0-9])?'
    domain_re = r'(?:\.[a-z' + ul + r'0-9]+(?:[a-z' + ul + r'0-9-]*[a-z' + ul + r'0-9]+)*)*'
    tld_re = r'\.[a-z' + ul + r']{2,}\.?'
    host_re = '(' + hostname_re + domain_re + tld_re + '|localhost)'

    def __init__(self, intranet_host_re=None, **kwargs):
        super(IntranetURLValidator, self).__init__(**kwargs)
        if intranet_host_re:
            self.host_re = (
                '(' + self.hostname_re + self.domain_re + self.tld_re +
                '|' + intranet_host_re + '|localhost)'
            )
            self.regex = re.compile(
                r'^(?:[a-z0-9\.\-]*)://'
                r'(?:\S+(?::\S*)?@)?'
                r'(?:' + self.ipv4_re + '|' + self.ipv6_re + '|' + self.host_re + ')'
                r'(?::\d{2,5})?'
                r'(?:[/?#][^\s]*)?'
                r'$', re.IGNORECASE)
