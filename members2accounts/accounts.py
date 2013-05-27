from ldapom import LdapConnection

from config import Config

class Accounts(object):
    def __init__(self):
        log.debug("Connecting")
        self._c = Config()
        self._conn = LdapConnection(uri=self._c['server_url'], base=self._c['base_dn'], login=self._c['admin_user'], password=self._c['admin_pass'])
        log.info("Connected to %s %s as %s", self._c['server_url'], self._c['base_dn'], self._c['admin_user'])
        self._listeners = []

    def verify_connection(self):
        self._conn.get_ldap_node(self._c['people_dn'])

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
