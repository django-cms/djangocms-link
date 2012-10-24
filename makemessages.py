#!/usr/bin/env python
# -*- coding: utf-8 -*-
from optparse import OptionParser
import os

WORKING_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'djangocms_link'))

def makemessages(lang=None):
    from django.core.management import call_command
    os.chdir(WORKING_DIR)
    if lang:
        kwargs = {'locale': lang}
    else:
        kwargs = {'all': True}
    call_command('makemessages', **kwargs)
    call_command('compilemessages')

if __name__ == "__main__":
    parser = OptionParser()
    options, args = parser.parse_args()
    if args:
        lang = args[0]
    else:
        lang = None
    makemessages(lang)
