import sys
import argparse
from ConfigParser import SafeConfigParser

_CONFIG_INST = None
def Config(custom_values=None):
    global _CONFIG_INST
    if _CONFIG_INST is None:
        _CONFIG_INST = Defaults(custom_values)
    return _CONFIG_INST

def Config_reset():
    global  _CONFIG_INST
    _CONFIG_INST = None

def Config_set(cmd_line=None):
    c = SafeConfigParser(Defaults())
    if cmd_line is None:
        cmd_line = sys.argv[1:]
    parser = argparse.ArgumentParser(description="I read a properly signed json file with memberdata and create the accounts in LDAP.")
    parser.add_argument('-C', '--config-file')
    parser.add_argument('-W', '--write-config', metavar="FILE", help="Write current configuration to FILE")
    res = parser.parse_args(args=cmd_line)
    if res.config_file:
        fd = open(res.config_file, 'rb')
        c.readfp(fd, res.config_file)
#    if res.config:
#        ConfigParser(defaults)
    return Config()

class DictArgs(dict):
    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError(item)

class Defaults(DictArgs):
    def __init__(self, custom_values=None):
        self.update({
            'gpg': DictArgs({ # GPG elements.
                'keyring': None, # directory with the GPG keyring. None will give the default location for the user.
                'my_id': '7C7F 7435 140C E92E BB33  6CF7 8367 1848 9BB7 D7C7', # Fingerprint of the key that the automation uses to decrypt and sign
                'allowed_ids' : [
                    '8044 9D3E 6EAC E4D9 C4D2  A5D7 6752 C3BC 94DA 7C30',
                ], # IDs of Keys that we see as valid signers of member lists. Keys must be imported and trusted!
            }),
            'ldap': DictArgs({
                # LDAP server access..
                'server_uri': '',#'ldap://192.168.122.224',
                'admin_user': '',#'cn=root,dc=techinc,dc=nl',
                'admin_pass': '',#'test',
                # LDAP Structure.
                'base_dn': 'dc=techinc,dc=nl',
                'people_dn': 'ou=people,dc=techinc,dc=nl', #
                'groups_dn': 'ou=groups,dc=techinc,dc=nl',
                'free_id_dn': 'cn=NextFreeUnixId,dc=techinc,dc=nl',
                'member_group': 'members',
                'home_base': '/home/' # base for the home directory. Will append the nickname to this.
                                      # These keys also have to be added to the keyring.
               }),
        })
        if custom_values:
            self.update(custom_values)
