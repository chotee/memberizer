#!/usr/bin/env python

from distutils.core import setup

setup(name='memberizer',
    version='1',
    description='Take a member file and create LDAP accounts',
    long_description="Load in a JSON file with members and create LDAP accounts with the member groups.",
    url='https://www.github.com/chotee/memberizer',
    license='GNU General Public License v3 or later (GPLv3+)',
    author='Chotee',
    author_email='chotee@openended.eu',
    packages=['memberizer'],
)
