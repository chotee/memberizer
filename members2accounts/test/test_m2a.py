__author__ = 'chotee'

from members2accounts.m2a import Members2Accounts, AccountDoesNotExistException

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

class Mock_Accounts():
    def verify_connection(self): pass
    def publish_changes_to(self, report): pass
    def get_all_member_emails(self): return ["exists@member.nl",]
    def fetch(self, member):
        if member == 'new@member.nl':
            raise AccountDoesNotExistException()
        return Mock_Account(member)
    def update(self, member): pass
    def create(self, member):
        return Mock_Account(member)

class Mock_Account():
    def __init__(self, email):
        self._email = email
    def is_member(self):
        if self._email == "exists@member.nl":
            return True
        return False
    def make_member(self):
        pass

class Mock_Members():
    def verify_validity(self): pass
    def list_members(self):
        return [
            Mock_Member(email="exists@member.nl"),
            Mock_Member(email="new@member.nl"),
        ]

class Mock_Member():
    def __init__(self, email):
        self.email = email
