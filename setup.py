#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
from djangocms_link import __version__


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Communications',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Message Boards',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
]

def read(fname):
    readme_file = os.path.join(os.path.dirname(__file__), fname)
    return os.popen('[ -x "$(which pandoc 2>/dev/null)" ] && pandoc -t rst {0} || cat {0}'.format(readme_file)).read()

setup(
    name='djangocms-link',
    version=__version__,
    description='Link Plugin for django CMS',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/divio/djangocms-link',
    packages=['djangocms_link', 'djangocms_link.migrations', 'djangocms_link.migrations_django'],
    install_requires=['django-select2>=4.3'],
    license='LICENSE.txt',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    long_description=read('README.md'),
    include_package_data=True,
    zip_safe=False
)
