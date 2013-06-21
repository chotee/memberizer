__author__ = 'chotee'

import pytest
import py

from config import Config, Config_reset, Config_sanity

@pytest.fixture
def clean_config():
    Config_reset()

class Test_SetConfig(object):
    def test_init(self):
        config = Config()
        assert config.ldap.base_dn == "dc=techinc,dc=nl"

    def test_custom_config_file(self, clean_config):
        cmd_line = "-C %s" % py.path.local(__file__).join('..').join('config_custom.json').realpath()
        config = Config(cmd_line=cmd_line.split())
        assert 'dc=test,dc=com' == config.ldap.base_dn

    def test_custom_cmd_line(self, clean_config):
        cmd_line = "--ldap.uri ldaps://ldap.example.com"
        config = Config(cmd_line=cmd_line.split())
        assert "ldaps://ldap.example.com" == config.ldap.uri

    def test_canonical_fingerprints(self, clean_config):
        cmd_line = ["--gpg.my_id", '12 33 66 AA BB']
        config = Config(cmd_line=cmd_line)
        assert "123366AABB" == config.gpg.my_id


    def test_member_file(self, clean_config):
        cmd_line = 'members.json'
        config = Config(cmd_line=cmd_line.split())
        assert 'members.json' == config.members_file

    def test_no_member_file(self, clean_config):
        cmd_line = ''
        config = Config(cmd_line=cmd_line.split())
        assert None == config.members_file
        pytest.raises(SystemExit, Config_sanity, config)

    def test_write_config_to_file(self, clean_config, tmpdir):
        config_fn = tmpdir.join("config.json")
        cmd_line = "-W %s" % config_fn
        pytest.raises(SystemExit, Config, cmd_line=cmd_line.split())
        fd = config_fn.open()

    def test_config_sanity_file(self, clean_config):
#        Config_reset()
        cmd_line = 'fake.json'
        config = Config(cmd_line=cmd_line.split())
        pytest.raises(SystemExit, Config_sanity, config)
    #        Config_sanity(config)

    def test_config_sanity_ldap(self, clean_config):
        cmd_line = 'fake.json --ldap.user=test --ldap.passwd=secret --ldap.uri=foo:bar'
        config = Config(cmd_line=cmd_line.split())
        Config_sanity(config)
        assert config.ldap.uri == "foo:bar"
