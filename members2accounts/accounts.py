#from ldapom import LdapConnection
import ldap

import logging
logging.basicConfig()
log = logging.getLogger(__file__)

from config import Config

class Accounts(object):
    def __init__(self):
        log.debug("Connecting")
        self._c = Config()
        #self._conn = LdapConnection(uri=self._c['server_uri'], base=self._c['base_dn'], login=self._c['admin_user'], password=self._c['admin_pass'])
        self._conn = ldap.initialize(self._c['server_uri'])
        self._conn.simple_bind_s(self._c['admin_user'], self._c['admin_pass'])
        log.info("Connected to %s %s as %s", self._c['server_uri'], self._c['base_dn'], self._c['admin_user'])
        self._listeners = []

    def verify_connection(self):
        self._conn.search_s(self._c['people_dn'],ldap.SCOPE_SUBTREE)

    def publish_changes_to(self, report):
        self._listeners.append(report)

    def get_all_members(self):
        pass

    def fetch(self, member):
        pass

    def update(self, member):
        pass

    def create(self, member):
        pass

    def revoke_membership(self, member):
        pass

class Account(object):
    def is_member(self):
        pass