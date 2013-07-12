import sys
import ldap
from ldap.filter import filter_format, escape_filter_chars

import datetime

import logging
log = logging.getLogger("m2a."+__name__)

from config import Config
from exc import AccountDoesNotExistException, MultipleResultsException, OperationNotSupported, LDAPConnectionException

class Accounts(object):
    def __init__(self, ldap_conn=None):
        self._c = Config().ldap
        if ldap_conn is not None:
            self.connect(ldap_conn)

    def connect(self, ldap_conn=None):
        log.debug("Connecting")
        if ldap_conn:
            self._conn = ldap_conn
        else:
            self._conn = ldap.initialize(self._c.uri)
        log.info("Trying LDAP '%s' (base: '%s') as '%s'", self._c.uri, self._c.base_dn, self._c.user)
        try:
            self._conn.simple_bind_s(self._c.user, self._c.passwd)
        except ldap.SERVER_DOWN:
            log.fatal("Could not log into %s as %s", self._c.uri, self._c.user)
            raise LDAPConnectionException()
        except ldap.INVALID_DN_SYNTAX:
            log.fatal("Invalid DN syntax: %s", self._c.user)
            raise LDAPConnectionException()
        except ldap.INVALID_CREDENTIALS:
            log.fatal("Username or password incorrect for %s user %s", self._c.uri, self._c.user)
            raise LDAPConnectionException()
        log.info("Connected to LDAP!")

    def verify_connection(self):
        self._conn.search_s(self._c.people_dn,ldap.SCOPE_BASE)

    def new_account(self):
        return Account(self._conn)

    def get_all_member_accounts(self):
        """I return a list of Account objects for all member-accounts in LDAP"""
        member_group_filter = '(cn=%s)' % self._c.member_group
        member_cns = self._conn.search_s(self._c.groups_dn, ldap.SCOPE_ONELEVEL, member_group_filter)[0][1]['memberUid']
        member_filter = "(|(cn=" + ")(cn=".join(member_cns) + '))'
        log.debug("base: %s Filter: %s", self._c.people_dn, member_filter)
        list_of_account_data = self._conn.search_s(self._c.people_dn, ldap.SCOPE_ONELEVEL, member_filter)
        list_of_accounts = []
        for account_data in list_of_account_data:
            account = Account(self._conn)
            account.load_from_ldap_account_info(account_data)
            list_of_accounts.append(account)
        log.info("There are %d member accounts", len(list_of_accounts))
        return list_of_accounts

    def _members_dn(self):
        members_dn = "cn=%s,%s" % (self._c.member_group, self._c.groups_dn)
        return members_dn

class Account(object):
    def __init__(self, conn):
        self._c = Config()
        self._conn = conn
        self._email = None
        self._nickname = None
        self._paid_until = None
        self._ldap_dn = None
        self._groups = None
        self._dirty = set()

    def load_from_ldap_account_info(self, account_info):
        """I take the results of a ldap entry and load the account object with the data."""
        self._ldap_dn = account_info[0]
        attributes = account_info[1]
        self.email = attributes['mail'][0]
        self.nickname = attributes['cn'][0]
        if 'telexNumber' in attributes:
            self.paid_until = datetime.datetime.strptime(attributes['telexNumber'][0], "%Y-%m-%d").date()
        self._dirty.clear()

    def load_from_ldap_by_nickname(self, nickname=None):
        nickname = self.nickname if nickname is None else nickname
        nickname_filter = filter_format('(&(objectClass=inetOrgPerson)(cn=%s))', [nickname])
        res = self._ldap_search_one(self._c.ldap.people_dn, ldap.SCOPE_ONELEVEL, nickname_filter)
        self.load_from_ldap_account_info(res)

    def load_account_from_member(self, member):
        """I take a member object and create a proper Account object from it."""
        self.nickname = member.nickname
        self.email = member.email
        try:
            self.paid_until = member.paid_until
        except AttributeError:
            self.paid_until = None

    def _ldap_search_one(self, *args):
        """I do a LDAP search and make sure I only get one result and return only that one result."""
        res = self._conn.search_s(*args)
        if len(res) == 0:
            raise AccountDoesNotExistException(self.nickname)
        if len(res) > 1:
            raise MultipleResultsException(self.nickname)
        return res[0]

    def save(self):
        """I save the current Account to LDAP. I update exiting accounts and create new ones."""
        if self._ldap_dn:
            if self.is_dirty:
                self.update()
        else:
            try:
                self.load_from_ldap_by_nickname()
                if self.is_dirty:
                    self.update()
            except AccountDoesNotExistException:
                self.create()
        self._dirty.clear()

    def create(self):
        self._ldap_dn = self._account_dn(self.nickname)
        uid, gid = self._grab_unique_ids()
        self._create_account(gid, uid)
        self._create_group(gid)
        if self._c.ldap.default_group:
            self.add_to_group(self._c.ldap.default_group)
        self._dirty.clear()

    def _create_account(self, gid, uid):
        """I create the people entry for the account in LDAP."""
        member_record = [
            ('cn', self.nickname),
            ('sn', self.nickname),
            ('uid', self.nickname),
            ('homeDirectory', ''.join([self._c.ldap.home_base, self.nickname.encode()])),
            ('uidNumber', str(uid)),
            ('gidNumber', str(gid)),
        ]
        member_record.extend(self._ldap_account_structure())
        member_record = [(item[0], ldap.filter.escape_filter_chars(item[1]).encode('utf-8')) for item in member_record]
        member_record.append(('objectClass', ['inetOrgPerson', 'posixAccount', 'top']))
        log.info("Adding account %s", self._ldap_dn)
        log.debug("with attributes: %s", member_record)
        self._conn.add_s(self._ldap_dn, member_record)
        log.debug("Added.")

    def _create_group(self, gid):
        """I create the group entry for the account in LDAP."""
        group_name = self.nickname.encode()
        group_dn = filter_format("cn=%s,%s", [group_name, self._c.ldap.groups_dn])

        group_record = [
            ('cn', group_name),
            ('gidNumber', str(gid)),
        ]
        group_record= [(item[0], ldap.filter.escape_filter_chars(item[1])) for item in group_record]
        group_record.append(('objectClass', ['posixGroup', 'top']))
        log.info("Adding group %s", group_dn)
        log.debug("with attributes: %s", group_record)
        try:
            self._conn.add_s(group_dn, group_record)
            log.debug("Added.")
        except ldap.ALREADY_EXISTS:
            log.warn("The group %s already exists!", group_dn)
        finally:
            self.add_to_group(group_name)

    def update(self):
        """I Assume a account has been previously created. For easy synchronisation use the save method."""
        assert self._ldap_dn is not None
        mods = [(ldap.MOD_REPLACE, e[0], ldap.filter.escape_filter_chars(e[1])) for e in self._ldap_account_structure() ]
        log.info("Update account '%s', dirty attributes: %s", self.nickname, self._dirty)
        log.debug("Change: %s -> %s", self._ldap_dn, mods)
        self._conn.modify_s(self._ldap_dn, mods)
        log.debug("Changed.")

    def _ldap_account_structure(self):
        '''I represent the parts of the LDAP structure that can be changed after '''
        a = [
            ('mail', self.email.encode()),
        ]
        if self.paid_until:
            a.append(
                ('telexNumber', str(self.paid_until)) # Abuse, I know.
                            # If you write a proper schema I'll get you a beer.
            )
        return a

    def _group_dn(self, group_name):
        dn = "cn=%s,%s" % (group_name, self._c.ldap.groups_dn)
        return dn

    def grant_membership(self):
        return self.add_to_group(self._c.ldap.member_group)

    def revoke_membership(self):
        self.remove_from_group(self._c.ldap.member_group)

    def add_to_group(self, group_name):
        group_dn = self._group_dn(group_name)
        change = (
            (ldap.MOD_ADD, 'memberUid', (self.nickname.encode(),)),
        )
        log.info("Adding %s to group %s", self.nickname, group_dn)
        log.debug("Change: %s", change)
        try:
            self._conn.modify_s(group_dn, change)
            log.debug("Granted.")
        except ldap.TYPE_OR_VALUE_EXISTS:
            log.warn("Group %s already had a '%s' entry. Skipping", group_dn, self.nickname)

    def remove_from_group(self, group_name):
        group_dn = self._group_dn(group_name)
        change = (
            (ldap.MOD_DELETE, 'memberUid', (self.nickname.encode(),)),
        )
        log.info("Removing %s from group %s", self.nickname, group_dn)
        log.debug("Change: %s", change)
        self._conn.modify_s(group_dn, change)
        log.debug("Revoked.")

    @property
    def nickname(self):
        return self._nickname
    @nickname.setter
    def nickname(self, value):
        if self._nickname != value and self._nickname is not None:
            raise OperationNotSupported("Nickname cannot be changed.")
        if self._nickname != value:
            self._nickname = value
            self._dirty.add("nickname")
        return self._nickname

    @property
    def email(self):
        return self._email
    @email.setter
    def email(self, value):
        if self._email != value:
            self._email= value
            self._dirty.add("email")
        return self._email

    @property
    def paid_until(self):
        return self._paid_until
    @paid_until.setter
    def paid_until(self, value):
        if self._paid_until != value:
            self._paid_until = value
            self._dirty.add("paid_until")
        return self._paid_until

    @property
    def in_ldap(self):
        """Is this account in ldap (as far as the account knows)."""
        return self._ldap_dn is not None

    @property
    def is_dirty(self):
        if self._dirty:
            return True
        return False

    @property
    def is_member(self):
        if self._groups is None:
            self._load_groups_from_ldap()
        return self._c.ldap.member_group in self._groups

    def _grab_unique_ids(self):
        # TODO: Remove race conditions!
        res = self._conn.search_s(self._c.ldap.free_id_dn, ldap.SCOPE_BASE)
        uid = res[0][1]['uidNumber'][0]
        gid = res[0][1]['gidNumber'][0]
        update_res = [
            (ldap.MOD_REPLACE, 'uidNumber', str(int(uid)+1)),
            (ldap.MOD_REPLACE, 'gidNumber', str(int(gid)+1)),
        ]
        self._conn.modify_s(self._c.ldap.free_id_dn, update_res)
        return uid, gid

    def _account_dn(self, nickname):
        return filter_format('cn=%s,%s', [nickname, self._c.ldap.people_dn])

    def _load_groups_from_ldap(self):
        filter = filter_format('(memberUid=%s)', [self.nickname])
        res = self._conn.search_s(self._c.ldap.groups_dn, ldap.SCOPE_ONELEVEL, filter)
        self._groups = [group[1]['cn'][0] for group in res] # store the group names in a list
