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
        assert config.ldap.base_dn == 'dc=test,dc=com'

    @pytest.mark.xfail
    def test_write_config_to_file(self):
        # Must still implement
        assert False