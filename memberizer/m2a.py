#!/usr/bin/env python
import sys
import py
import logging
import traceback

#logging.basicConfig()
log = logging.getLogger('m2a')
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
#ch.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
log.addHandler(ch)

from accounts import Accounts, Account
from members import  Members
from watcher import directory_watcher
#from exc import CryptoException, AccountDoesNotExistException
#from reporting import ChangeReporter, PublishReport
from config import Config, Config_sanity


class Members2Accounts():
    def add_or_update_accounts(self, accounts, members):
        """I create accounts for members. I return a list with any accounts that are no longer members.
        :param accounts: Access to the accounts (this is what we will be modifying)
        :param members: List of all the current members.
        """
        pending_members =  dict([(a.nickname, a) for a in accounts.get_all_member_accounts()]) # Get the nicknames of accounts that are already member.
        for member in members.list_members(): # Loop over the members
            account = accounts.new_account()
            account.load_account_from_member(member)
            account.save()
            if not account.is_member:
                account.grant_membership()
            if member.nickname in pending_members:
                pending_members.pop(member.nickname)
        return pending_members # this is a list of accounts that used to be members, but are not now.

    def make_accounts_non_members(self, accounts, accounts_not_current_members):
        """I make all of the accounts_not_current_members non members in the accounts object.
        :param accounts: Access to the accounts
        :param accounts_not_current_members: List of accounts that should nolonger be members.
        """
        for member in accounts_not_current_members.itervalues(): # All the accounts that were not in the member list.
            account = accounts.new_account()
            account.load_account_from_member(member)
            account.revoke_membership() # Remove their membership attributes.

    def go(self, accounts, members):
        """I Run the main update routine.
        :param accounts: Access to the accounts (this is what we will be modifying)
        :param members: List of all the current members.
        """
        accounts.connect()
        accounts.verify_connection() # Pre-flight test of member database

        members.check_sanity()
        members.decrypt_and_verify() # Check that the member change document is trustable.

#        report = ChangeReporter() # Object that receives the changes for reporting it.

        accounts_not_current_members = self.add_or_update_accounts(accounts, members)

        self.make_accounts_non_members(accounts, accounts_not_current_members)

#        PublishReport(report.generate_overview()) # Lets publish a report with the changes.

def main():
    """I run the main program routine."""
    log.info("Starting")
    config = Config(cmd_line=sys.argv[1:])
    Config_sanity(config)
    m2a = Members2Accounts()
    if config.run.dir_watch:
        while 42:
            member_file = directory_watcher(config.run.dir_watch) # This blocks until a file is changed.
            if not member_file:
                log.info("False alarm. Keeping watching")
                continue
            log.info("Found file '%s'. Using it as member file.", member_file)
            try:
                m2a.go(Accounts(), Members(unicode(member_file)))
            except RuntimeError:
                for tb in traceback.format_exception_only(sys.exc_type, sys.exc_value):
                    log.fatal(tb)
                log.fatal("Got fatal exception. Aborting processing")

    else:
        m2a.go(Accounts(), Members(config.members_file))
    log.info("End.")

if __name__ == "__main__":
    main()
