__author__ = 'chotee'

from datetime import date

from memberizer.exc import AccountDoesNotExistException

class Mock_Accounts():
    def connect(self): pass
    def verify_connection(self): pass
    def publish_changes_to(self, report): pass
    def get_all_member_accounts(self): return [Mock_Account("exists@member.nl"),]
    def set_reporting(self, report): pass
    def new_account(self):
        return Mock_Account()
    # def fetch(self, member):
    #     if member == 'new@member.nl':
    #         raise AccountDoesNotExistException()
    #     return Mock_Account(member)
    # def create(self, member):
    #     return Mock_Account(member)
    # def revoke_membership(self, member):
    #     pass

class Mock_Account():
    def __init__(self, email=None):
        if email:
            self.email = email
            self.nickname = email[:email.index('@')]
    def load_account_from_member(self, member):
        self.email = member.email
        self.nickname = member.nickname
        self.paid_until = member.paid_until
    def is_member(self):
        if self.email == "exists@member.nl":
            return True
        return False
    def grant_membership(self):
        pass
    def save(self):
        pass

class Mock_Members():
    def check_sanity(self): pass
    def decrypt_and_verify(self): pass
    def list_members(self):
        return [
            Mock_Member("exists","exists@member.nl", date(2012,1,15)),
            Mock_Member("new","new@member.nl", date(2013,6,4)),
        ]

class Mock_Member():
    def __init__(self, nickname, email, paid_until):
        self.nickname = nickname
        self.email = email
        self.paid_until = paid_until
