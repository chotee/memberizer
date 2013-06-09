__author__ = 'chotee'

from members2accounts.m2a import Members2Accounts
from members2accounts.test.mocks import *

#from members2accounts.members import Member
#from members2accounts.accounts import Account

class Test_Member2Account(object):
    def test_init(self):
        assert isinstance(Members2Accounts(), Members2Accounts)

    def test_go(self):
        mock_accounts = Mock_Accounts()
        mock_members = Mock_Members()
        m2a = Members2Accounts()
        m2a.go(mock_accounts, mock_members)

#    def test_make_accounts_non_members():
#        pass

