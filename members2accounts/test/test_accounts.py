__author__ = 'chotee'

import pytest

from members2accounts.accounts import Accounts

import ldap
from fakeldap import MockLDAP

@pytest.fixture
def fake_accounts(monkeypatch):
    mock_ldap = MockLDAP
    monkeypatch.setattr(ldap, 'initialize', mock_ldap)
    a = Accounts()
    a._conn.set_return_value('search_s',
                             #(base, scope, filterstr, attrlist, attrsonly),
                             ('ou=people,dc=techinc,dc=nl', ldap.SCOPE_SUBTREE, '(objectClass=*)', None, 0),
                             [('ou=people,dc=techinc,dc=nl',
                              {'objectClass': ['organizationalUnit', 'top'], 'ou': ['people']})]
    )
    return a

class TestAccounts():
    def test_verify_connection(self, fake_accounts):
        a = fake_accounts
        a.verify_connection()
#    def test_create_user(self):
