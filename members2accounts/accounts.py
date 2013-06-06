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
        self._conn.search_s(self._c['people_dn'],ldap.SCOPE_BASE)

    def publish_changes_to(self, report):
        self._listeners.append(report)

    def get_all_members(self):
        pass

    def fetch(self, member):
        pass

    def update(self, member):
        pass

    def create(self, member):
        (uid, gid) = self._grab_unique_ids()
        nickname = member.nickname
        member_dn = 'cn=%s,%s' % (nickname, self._c['people_dn'])
        home_directory = ''.join([self._c['home_base'], nickname])
        member_record = [
            ('object_class', ['inetOrgPerson', 'posixAccount', 'top']),
            ('cn', [nickname]),
            ('sn', [nickname]),
            ('uid', [nickname]),
            ('uidNumber', [str(uid)]),
            ('gidNumber', [str(gid)]),
            ('homeDirectory', [home_directory]),
            ('mail', [member.email]),
            ('telexNumber', [str(member.paid_until)]) # Abuse, I know.
            # Don't complain. If you write a proper Schema and IOU a beer!
        ]
        self._conn.add_s(member_dn, member_record)
        return member_dn

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

    def revoke_membership(self, member):
        pass

class Account(object):
    def is_member(self):
        pass