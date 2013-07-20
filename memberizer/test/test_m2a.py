__author__ = 'chotee'

from memberizer.m2a import Members2Accounts
from memberizer.test.mocks import *

#from memberizer.members import Member
#from memberizer.accounts import Account

class Test_Member2Account(object):
    def test_init(self):
        assert isinstance(Members2Accounts(), Members2Accounts)

    def test_go(self):
        mock_accounts = Mock_Accounts()
        mock_members = Mock_Members()
        m2a = Members2Accounts()
        m2a.memberize(mock_accounts, mock_members)

#    def test_make_accounts_non_members():
#        pass

