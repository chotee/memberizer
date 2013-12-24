#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='memberizer',
    version='5',
    description='Take a member file and create LDAP accounts',
    long_description="Load in a JSON file with members and create LDAP accounts with the member groups.",
    url='https://www.github.com/chotee/memberizer',
    license='GNU General Public License v3 or later (GPLv3+)',
    author='Chotee',
    author_email='chotee@openended.eu',
    packages = find_packages(exclude=['*.test']),
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
    },
    install_requires=['py', 'python-gnupg', 'python-ldap', 'passlib'],
    tests_require=['pytest', 'fakeldap'],
    entry_points = {
        'console_scripts': [
            'memberizer = memberizer.m2a:main'
        ]
    }
)
