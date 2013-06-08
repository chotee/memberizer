import sys
import logging

logging.basicConfig()
log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)

from members2accounts.accounts import Accounts, Account
from members2accounts.members import  Members
from members2accounts.exc import CryptoException, AccountDoesNotExistException
from members2accounts.reporting import ChangeReporter, PublishReport


class Members2Accounts():
    def add_or_update_accounts(self, accounts, members):
        """I create accounts for members. I return a list with any accounts that are no longer members.
        :param accounts: Access to the accounts (this is what we will be modifying)
        :param members: List of all the current members.
        """
        pending_members = set(accounts.get_all_member_emails()) # Get all the accounts that are already member.
        # for member in members.list_members(): # Loop over the members
        #     account = Accounts().new_account()
        #     try:
        #         account = accounts.fetch(member.email) # lets get the member
        #         pending_members.remove(member.email) # remove it from the pending set since we saw this account
        #                                              # in the list of members.
        #     except AccountDoesNotExistException:
        #         account = accounts.create(member) # The member doesn't exist. Create it!
        #     account.update(member) # Update the data of the member.
        #     if not account.is_member(): # Is the account not yet a member?
        #         account.make_member() # Lets make it one!
        return pending_members # this is a list of accounts that used to be members, but are not now.

    def make_accounts_non_members(self, accounts, accounts_not_current_members):
        """I make all of the accounts_not_current_members non members in the accounts object.
        :param accounts: Access to the accounts
        :param accounts_not_current_members: List of accounts that should nolonger be members.
        """
        for member in accounts_not_current_members: # All the accounts that were not in the member list.
            accounts.revoke_membership(member) # Remove their membership attributes.

    def go(self, accounts, members):
        """I Run the main update routine.
        :param accounts: Access to the accounts (this is what we will be modifying)
        :param members: List of all the current members.
        """
        accounts.verify_connection() # Pre-flight test of member database

        members.decrypt_and_verify() # Check that the member change document is trustable.

        report = ChangeReporter() # Object that receives the changes for reporting it.
        accounts.publish_changes_to(report)

        accounts_not_current_members = self.add_or_update_accounts(accounts, members)

        self.make_accounts_non_members(accounts, accounts_not_current_members)

        PublishReport(report.generate_overview()) # Lets publish a report with the changes.

if __name__ == "__main__":
    member_file = sys.argv[1]
    Members2Accounts.go(Accounts(), Members(member_file))