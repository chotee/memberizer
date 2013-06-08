__author__ = 'chotee'

import pytest
from datetime import date

from members2accounts.accounts import Accounts

import ldap
from fakeldap import MockLDAP
from mocks import Mock_Member

from members2accounts.exc import *

@pytest.fixture
def fake_accounts(monkeypatch):
    mock_ldap = MockLDAP
    monkeypatch.setattr(ldap, 'initialize', mock_ldap)
    a = Accounts()
    a._conn.set_return_value('search_s',
        #(base, scope, filterstr, attrlist, attrsonly),
        ('ou=people,dc=techinc,dc=nl', ldap.SCOPE_BASE , '(objectClass=*)', None, 0),
            [
                ('ou=people,dc=techinc,dc=nl',
                {'objectClass': ['organizationalUnit', 'top'],
                 'ou': ['people']})
            ]
    )
    a._conn.set_return_value('search_s',
        ('ou=people,dc=techinc,dc=nl', ldap.SCOPE_ONELEVEL, '(&(mail=existing@techinc.nl)(objectClass=inetOrgPerson))',
         None, 0),
        [
            ('cn=existing,ou=people,dc=techinc,dc=nl',
             {
                'objectClass': ['inetOrgPerson', 'posixAccount', 'top'],
                'cn': ['existing'], 'sn': ['existing'], 'uid': ['existing'],
                'homeDirectory': ['/home/existing'],
                'mail': ['existing@techinc.nl'],
                'telexNumber': ['2013-12-01'],
                'uidNumber': ['501'], 'gidNumber': ['500'],
             })
        ]
    )
    a._conn.set_return_value('search_s',
        ('ou=people,dc=techinc,dc=nl', ldap.SCOPE_ONELEVEL, '(&(mail=doesnotexist@techinc.nl)(objectClass=inetOrgPerson))',
         None, 0),
        []
    )
    a._conn.set_return_value('search_s',
        ('cn=NextFreeUnixId,dc=techinc,dc=nl', ldap.SCOPE_BASE, '(objectClass=*)', None, 0),
        [
            ('cn=NextFreeUnixId,dc=techinc,dc=nl',
             {'cn': ['NextFreeUnixId'],
              'gidNumber': ['777'],
              'objectClass': ['inetOrgPerson', 'sambaUnixIdPool'],
              'sn': ['NextFreeUnixId'],
              'uidNumber': ['666']}
            )
        ]
    )
    return a

class TestAccounts():
    def test_verify_connection(self, fake_accounts):
        a = fake_accounts
        a.verify_connection()
#    def test_create_user(self):

    def test_create(self, fake_accounts):
        a = fake_accounts
        member = Mock_Member(nickname="testcreate", email="test@techinc.nl", paid_until=date(2013, 8, 12))
        a.create(member)

    def test_fetch(self, fake_accounts):
        a = fake_accounts
        pytest.raises(AccountDoesNotExistException, a.fetch, "doesnotexist@techinc.nl")

        account = a.fetch("existing@techinc.nl")
        assert account.email == "existing@techinc.nl"
        assert account.nickname == 'existing'
        assert account.paid_until == date(2013, 12, 1)

