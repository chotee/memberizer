import sys
from copy import deepcopy
import json
import argparse
from ast import literal_eval
import py

import logging
log = logging.getLogger('m2a.'+__name__)

Defaults = {
    'run': {
        'dir_watch': None,
        'send_report': True
    },
    'gpg': { # GPG elements.
        'gpg_binary': 'gpg',
        'keyring': None, # directory with the GPG keyring. None will give the default location for the user.
        'my_id': 'FINGERPRINT OF UPDATE PROCESS', # Fingerprint of the key that the automation uses to decrypt and sign
        'signer_ids' : [
            'FINGERPRINTS THAT SIGN UPDATES',
        ], # IDs of Keys that we see as valid signers of member lists. Keys must be imported and trusted!
    },
    'ldap': {
        # LDAP server access..
        'uri': '',#'ldap://192.168.122.224', # URL for the LDAP server.
        'user': '',#'cn=root,dc=techinc,dc=nl', # User to use with the LDAP server to make the changes.
        'passwd': '',#'test', # Password of the ldap user
        # LDAP Structure.
        'base_dn': 'dc=techinc,dc=nl', # base DN for the LDAP tree.
        'people_dn': 'ou=people,dc=techinc,dc=nl', # Where are people stored?
        'groups_dn': 'ou=groups,dc=techinc,dc=nl', # Where are the groups stored.
        'free_id_dn': 'cn=NextFreeUnixId,dc=techinc,dc=nl', # Where is the record that keeps track of given userids.
        'member_group': 'members', # The name of the group that contain the members.
        'default_group': 'everybody', # The name of a group that contains everybody (new members are added to this,
                                      # but non-members are not removed. Use None for none.
        'home_base': '/home/', # base for the home directory. Will append the nickname to this.
       },
}

_CONFIG_INST = None
def Config(**kwargs):
    global _CONFIG_INST
    if _CONFIG_INST is None:
        _CONFIG_INST = Config_set(**kwargs)
    return _CONFIG_INST

def Config_reset():
    global  _CONFIG_INST
    _CONFIG_INST = None

def _config_read_json_file(data, res):
    fd = open(res.config_file, 'rb')
    log.info("Reading from configuration file %s", res.config_file)
    config_file_settings = json.load(fd)
    for section_name, section_items in config_file_settings.iteritems():
        data.setdefault(section_name, {}).update(section_items)
    log.debug("Finished config file read.")


def _config_cmdline_options(parser, data):
    parser.add_argument('members_file', metavar="MEMBERS-FILE", help="The GPG signed members file JSON format", nargs="?")
    parser.add_argument('-C', '--config-file', metavar="JSON-FILE", help="The JSON configuration file to use")
    parser.add_argument('-W', '--write-config', metavar="JSON-FILE", help="Write current configuration to JSON FILE")
    for section_name, section_value in data.iteritems():
        for option_name, option_value in section_value.iteritems():
            cmd_option_name = "--%s.%s" % (section_name, option_name)
            help_value = "default: %s" % option_value
            parser.add_argument(cmd_option_name, metavar=option_name.upper(), help=help_value)

def _config_handle_cmdline_options(data, res):
    for cmd_name, cmd_value in vars(res).iteritems():
        if cmd_value is None: continue
        if '.' in cmd_name:
            section, option = cmd_name.split('.')
            try:
                try:
                    value = literal_eval(cmd_value)
                except ValueError:
                    value = cmd_value
            except SyntaxError:
                value = literal_eval(repr(cmd_value))
            data[section][option] = value

def _config_write_file(data, res):
    fref = py.path.local(res.write_config)
    if fref.check() == True:
        log.fatal("%s already exists. Refusing to overwrite!", fref)
    else:
        with fref.open('wb') as fd:
            log.info("Writing configuration to %s", res.write_config)
            json.dump(data, fd,
                      sort_keys=True, indent=4, separators=(',', ': '))
        log.debug("Done.")
    sys.exit()


def _sanitize_settings(data):
    def canonical_fingerprint(fpr):
        return fpr.replace(' ', '')
    data['gpg']['my_id'] = canonical_fingerprint(data['gpg']['my_id'])
    ids = []
    for id in data['gpg']['signer_ids']:
        ids.append(canonical_fingerprint(id))
    data['gpg']['signer_ids'] = ids

def Config_set(cmd_line=None, custom_data=None):
    """I create the configuration object."""
    if not custom_data:
        data = deepcopy(Defaults)
    else:
        data = custom_data
    if cmd_line is None:
         cmd_line = []
    parser = argparse.ArgumentParser(
        description="I read a properly signed json file with memberdata and create the accounts in LDAP.")
    _config_cmdline_options(parser, data)
    res = parser.parse_args(args=cmd_line)
    if res.config_file:
        _config_read_json_file(data, res)
    _config_handle_cmdline_options(data, res)
    if res.write_config:
        _config_write_file(data, res)
    data['members_file'] = res.members_file
    _sanitize_settings(data)
    config = _config_section(data)
    config.setHelp(parser.format_help())
    return config

def _config_section(settings):
    data = {}
    for option_name, option_value in settings.iteritems():
        if isinstance(option_value, dict):
            option_value = _config_section(option_value)
        data[option_name] = option_value
    return _Config(data)

def fatal(*args, **kwargs):
    if kwargs.get('help') is not None:
        log.info("Showing help: \n%s", kwargs['help'])
    log.fatal(*args)
    sys.exit(1)

def Config_sanity(config):
    """I Check that the configuration has minimal sanity."""
    if config.run.dir_watch: # we are going to watch a directory
        watch_dir = py.path.local(config.run.dir_watch)
        if watch_dir.check() == False:
            fatal("Directory '%s' does not exist", watch_dir)
        if watch_dir.check(dir=1) == False:
            fatal("'%s' is not a directory!", watch_dir)
    else:
        if not config.members_file:
            fatal("Missing members file.", help=config.help)
    if not config.ldap.uri:
        fatal("Missing LDAP URI. Set --ldap.uri .")
    elif ":" not in config.ldap.uri:
        fatal("LDAP credentials '%s' not in the URI format. Must be scheme:location", config.ldap.uri)
    if not config.ldap.user or not config.ldap.passwd:
        fatal("Missing LDAP credentials.. Set --ldap.user and --ldap.passwd")


class _Config(object):
    def __init__(self, data):
        self._data = data
        self.help = "Help not set."

    def __getattr__(self, item):
        try:
            return self._data[item]
        except KeyError:
            raise AttributeError(item)

    def setHelp(self, help_string):
        self.help = help_string
