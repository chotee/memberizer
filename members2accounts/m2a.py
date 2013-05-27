import logging

logging.basicConfig()
log = logging.getLogger(__file__)
log.setLevel(logging.DEBUG)

from accounts import Accounts
from members import  Members
from reporting import ChangeReporter, PublishReport

class AccountDoesNotExistException(RuntimeError):
    pass

class Members2Accounts():
    def go(self, accounts, members):
        accounts.verify_connection() # Preflight test.

        members.verify_validity() # Check that the document is trustable.

        report = ChangeReporter() # Object that receives the changes for reporting it.
        accounts.publish_changes_to(report)

        pending_members =  set(accounts.get_all_members()) # Get all the accounts that are already member.
        for member in members: # Loop over the members
            try:
                account = accounts.fetch(member) # lets get the member
            except AccountDoesNotExistException(member):
                account = accounts.create(member) # The member doesn't exist. Create it!
            accounts.update(member) # Update the data of the member.
            if not account.is_member(): # Is the account not yet a member?
                account.make_member() # Lets make it one!
            pending_members.remove(member) # remove it from the pending set since we saw this account in the list of members.

        for member in pending_members: # All the accounts that were not in the member list.
            accounts.revoke_membership(member) # Remove their membership attributes.

        PublishReport(report.generate_overview()) # Lets publish a report with the changes.

if __name__ == "__main__":
    Members2Accounts.go(Accounts(), Members())