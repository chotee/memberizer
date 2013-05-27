__author__ = 'chotee'

from members2accounts.m2a import Members2Accounts

class Test_Member2Account(object):
    def test_init(self):
        assert isinstance(Members2Accounts(), Members2Accounts)

    def test_go(self):
        mock_accounts = Mock_Accounts()
        mock_members = Mock_Members()
        m2a = Members2Accounts()
        m2a.go(mock_accounts, mock_members)


class Mock_Accounts():
    def verify_connection(self): pass
    def publish_changes_to(self, report): pass
    def get_all_members(self): return []

class Mock_Members():
    def verify_validity(self):
        pass
    def __iter__(self):
        return [].__iter__()