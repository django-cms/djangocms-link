import re

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, URLValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _


class IntranetURLValidator(URLValidator):
    """
    This is essentially the normal, Django URL Validator, but allows for
    "internal" machine-name only "hostnames" as defined by the RegEx pattern
    defined in settings as well as normal, FQD-based hostnames.

    Some examples:
    RFC1123 Pattern
        DJANGOCMS_LINK_INTRANET_HOSTNAME_PATTERN = r'[a-z,0-9,-]{1,15}'
    """

    ul = "\u00a1-\uffff"  # unicode letters range (must be a unicode string, not a raw string)

    # IP patterns
    ipv4_re = (
        r"(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}"
    )
    ipv6_re = r"\[[0-9a-f:\.]+\]"  # (simple regex, validated later)

    # Host patterns
    hostname_re = r"[a-z" + ul + r"0-9](?:[a-z" + ul + r"0-9-]*[a-z" + ul + r"0-9])?"
    domain_re = (
        r"(?:\.[a-z" + ul + r"0-9]+(?:[a-z" + ul + r"0-9-]*[a-z" + ul + r"0-9]+)*)*"
    )
    tld_re = r"\.[a-z" + ul + r"]{2,}\.?"
    host_re = "(" + hostname_re + domain_re + tld_re + "|localhost)"

    def __init__(self, intranet_host_re=None, **kwargs):
        super().__init__(**kwargs)
        if intranet_host_re:
            self.host_re = (
                "("
                + self.hostname_re
                + self.domain_re
                + self.tld_re
                + "|"
                + intranet_host_re
                + "|localhost)"
            )
            self.regex = re.compile(
                r"^(?:[a-z0-9\.\-]*)://"
                r"(?:\S+(?::\S*)?@)?"
                r"(?:" + self.ipv4_re + "|" + self.ipv6_re + "|" + self.host_re + ")"
                r"(?::\d{2,5})?"
                r"(?:[/?#][^\s]*)?"
                r"$",
                re.IGNORECASE,
            )


@deconstructible
class AnchorValidator:
    message = _("Enter a valid anchor")
    code = "invalid"

    def __call__(self, value: str):
        value = value.lstrip("#")
        if not value:
            return value
        if not isinstance(value, str) or len(value) > 100:
            raise ValidationError(self.message, code=self.code, params={"value": value})

        if not re.match(r"^[a-zA-Z0-9_\-]+$", value):
            raise ValidationError(self.message, code=self.code, params={"value": value})
        return value


class ExtendedURLValidator(IntranetURLValidator):
    # Phone numbers don't match the host regex in Django's validator,
    # so we test for a simple alternative.
    tel_re = r"^tel\:[0-9 \#\*\-\.\(\)\+]+$"

    def __init__(self, allowed_link_types: list = None, **kwargs):
        self.allowed_link_types = allowed_link_types
        super().__init__(**kwargs)

    def __call__(self, value: str):
        if not isinstance(value, str) or len(value) > self.max_length:
            raise ValidationError(self.message, code=self.code, params={"value": value})
        if self.unsafe_chars.intersection(value):
            raise ValidationError(self.message, code=self.code, params={"value": value})
        # Check if just an anchor
        if value.startswith("#") and (
            self.allowed_link_types is None or "anchor" in self.allowed_link_types
        ):
            return AnchorValidator()(value)
        # Check if the scheme is valid.
        scheme = value.split(":")[0].lower()
        if scheme == "tel" and (
            self.allowed_link_types is None or "tel" in self.allowed_link_types
        ):
            if re.match(self.tel_re, value):
                return
            else:
                raise ValidationError(
                    _("Enter a valid phone number"),
                    code=self.code,
                    params={"value": value},
                )
        if scheme == "mailto" and (
            self.allowed_link_types is None or "mailto" in self.allowed_link_types
        ):
            return EmailValidator()(value[7:])
        return super().__call__(value)
