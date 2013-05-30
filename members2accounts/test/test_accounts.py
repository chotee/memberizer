__author__ = 'chotee'

from members2accounts.accounts import Accounts

import ldap
from fakeldap import MockLDAP

class TestAccounts():
    def test_Init(self, monkeypatch):
        monkeypatch.setattr(ldap, 'initialize', MockLDAP)
        Accounts()
