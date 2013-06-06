__author__ = 'chotee'

from datetime import date

from members2accounts.exc import AccountDoesNotExistException

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
    def decrypt_and_verify(self): pass
    def list_members(self):
        return [
            Mock_Member("exists","exists@member.nl", date(2012,01,15)),
            Mock_Member("new","new@member.nl", date(2013,6,4)),
        ]

class Mock_Member():
    def __init__(self, nickname, email, paid_until):
        self.nickname = nickname
        self.email = email
        self.paid_until = paid_until
