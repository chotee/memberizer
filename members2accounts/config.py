_CONFIG_INST = None
def Config():
    global _CONFIG_INST
    if _CONFIG_INST is None:
        _CONFIG_INST = _Config()
    return _CONFIG_INST

class _Config(dict):
    def __init__(self):
        self.update({
            'server_uri': 'ldap://192.168.122.224',
            'base_dn': 'dc=techinc,dc=nl',
            'admin_user': 'cn=admin,dc=techinc,dc=nl',
            'admin_pass': 'SomeThingSecret',
            'people_dn': 'ou=people,dc=techinc,dc=nl',
            'groups_dn': 'ou=groups,dc=techinc,dc=nl',
            'member_group': 'members',
        })
