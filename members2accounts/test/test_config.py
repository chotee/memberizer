__author__ = 'chotee'

import pytest
import py

from config import Config, Config_reset

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

    def test_write_config_to_file(self, clean_config, tmpdir):
        config_fn = tmpdir.join("config.json")
        cmd_line = "-W %s" % config_fn
        config = Config(cmd_line=cmd_line.split())
        fd = config_fn.open()

