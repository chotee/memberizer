import ldap
from ldap.filter import filter_format

import datetime

import logging
logging.basicConfig()
log = logging.getLogger(__file__)

from members2accounts.config import Config
from members2accounts.exc import AccountDoesNotExistException, MultipleResultsException, OperationNotSupported

class Accounts(object):
    def __init__(self, ldap_conn=None):
        log.debug("Connecting")
        self._c = Config()
        if ldap_conn:
            self._conn = ldap_conn
        else:
            self._conn = ldap.initialize(self._c['server_uri'])
        self._conn.simple_bind_s(self._c['admin_user'], self._c['admin_pass'])
        log.info("Connected to %s %s as %s", self._c['server_uri'], self._c['base_dn'], self._c['admin_user'])
        self._listeners = []

    def verify_connection(self):
        self._conn.search_s(self._c['people_dn'],ldap.SCOPE_BASE)

    def publish_changes_to(self, report):
        self._listeners.append(report)

    def new_account(self):
        return Account(self._conn)

    def get_all_member_accounts(self):
        pass


class Account(object):
    def __init__(self, conn):
        self._c = Config()
        self._conn = conn
        self._email = None
        self._nickname = None
        self._paid_until = None
        self._ldap_dn = None
        self._dirty = set()

    def load_from_ldap_account_info(self, account_info):
        """I take the results of a ldap entry and load the account object with the data."""
        self._ldap_dn = account_info[0]
        attributes = account_info[1]
        self.email = attributes['mail'][0]
        self.nickname = attributes['cn'][0]
        self.paid_until = datetime.datetime.strptime(attributes['telexNumber'][0], "%Y-%m-%d").date()

    def load_from_ldap_by_nickname(self, nickname=None):
        nickname = self.nickname if nickname is None else nickname
        nickname_filter = filter_format('(&(objectClass=inetOrgPerson)(cn=%s))', [nickname])
        res = self._ldap_search_one(self._c['people_dn'], ldap.SCOPE_ONELEVEL, nickname_filter)
        self.load_from_ldap_account_info(res)

    def load_account_from_member(self, member):
        """I take a member object and create a proper Account object from it."""
        self.nickname = member.nickname
        self.email = member.email
        self.paid_until = member.paid_until

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
            self.update()
        else:
            try:
                self.load_from_ldap_by_nickname()
                self.update()
            except AccountDoesNotExistException:
                self.create()
        self._dirty.clear()

    def create(self):
        self._ldap_dn = self._account_dn(self.nickname)
        home_directory = ''.join([self._c['home_base'], self.nickname])
        (uid, gid) = self._grab_unique_ids()
        member_record = [
            ('cn', self.nickname),
            ('sn', self.nickname),
            ('uid', self.nickname),
            ('uidNumber', str(uid)),
            ('gidNumber', str(gid)),
            ('homeDirectory', home_directory),
            ('mail', self.email),
            ('telexNumber', str(self.paid_until)) # Abuse, I know.
            # Don't complain. If you write a proper schema you get a beer!
        ]
        member_record = [(item[0], ldap.filter.escape_filter_chars(item[1])) for item in member_record]
        member_record.append(('object_class', ['inetOrgPerson', 'posixAccount', 'top']))
        self._conn.add_s(self._ldap_dn, member_record)
        self._dirty.clear()

    def update(self):
        pass

    @property
    def nickname(self):
        return self._nickname
    @nickname.setter
    def nickname(self, value):
        if self._nickname != value and self._nickname is not None:
            raise OperationNotSupported("Nickname cannot be changed.")
        self._nickname = value
        self._dirty.add("nickname")
        return self._nickname

    @property
    def email(self):
        return self._email
    @email.setter
    def email(self, value):
        self._email= value
        self._dirty.add("email")
        return self._email

    @property
    def paid_until(self):
        return self._paid_until
    @paid_until.setter
    def paid_until(self, value):
        self._paid_until = value
        self._dirty.add("paid_until")
        return self._paid_until

    @property
    def in_ldap(self):
        """Is this account in ldap (as far as the account knows)."""
        return self._ldap_dn is not None

    @property
    def is_dirty(self):
        if not self._dirty:
            return False
        return True

    @property
    def is_member(self):
        pass

    def _grab_unique_ids(self):
        # TODO: Remove race conditions!
        res = self._conn.search_s(self._c['free_id_dn'], ldap.SCOPE_BASE)
        uid = res[0][1]['uidNumber'][0]
        gid = res[0][1]['gidNumber'][0]
        update_res = [
            (ldap.MOD_REPLACE, 'uidNumber', str(int(uid)+1)),
            (ldap.MOD_REPLACE, 'gidNumber', str(int(gid)+1)),
        ]
        self._conn.modify_s(self._c['free_id_dn'], update_res)
        return uid, gid

    def _account_dn(self, nickname):
        return filter_format('cn=%s,%s', [nickname, self._c['people_dn']])

