_CONFIG_INST = None
def Config(custom_values=None):
    global _CONFIG_INST
    if _CONFIG_INST is None:
        _CONFIG_INST = _Config(custom_values)
    return _CONFIG_INST

def Config_reset():
    global  _CONFIG_INST
    _CONFIG_INST = None

class _Config(dict):
    def __init__(self, custom_values=None):
        self.update({
            # GPG elements.
            'gpg_keyring': None, # directory with the GPG keyring. None will give the default location for the user.
            'gpg_my_id': '7C7F 7435 140C E92E BB33  6CF7 8367 1848 9BB7 D7C7', # Fingerprint of the key that the automation uses to decrypt and sign
            'gpg_allowed_ids' : [
                '8044 9D3E 6EAC E4D9 C4D2  A5D7 6752 C3BC 94DA 7C30',
            ], # IDs of Keys that we see as valid signers of member lists. Keys must be imported and trusted!

            # LDAP server access..
            'server_uri': None, #'ldap://192.168.122.224',
            'admin_user': '', #'cn=admin,dc=techinc,dc=nl',
            'admin_pass': '', #'SomeThingSecret',
            # LDAP Structure.
            'base_dn': 'dc=techinc,dc=nl',
            'people_dn': 'ou=people,dc=techinc,dc=nl', #
            'groups_dn': 'ou=groups,dc=techinc,dc=nl',
            'member_group': 'members',
            'home_base': '/home/' # base for the home directory. Will append the nickname to this.
                                             # These keys also have to be added to the keyring.
        })
        if custom_values:
            self.update(custom_values)
