__author__ = 'chotee'

import pytest
import py

from config import Config_set, Config

class Test_SetConfig(object):
    def test_init(self):
        Config_set([])
        config = Config()
        assert config.ldap.base_dn == "dc=techinc,dc=nl"

    def test_custom_config_file(self):
        cmd_line = "-C %s" % py.path.local(__file__).join('..').join('config_custom.json').realpath()
        config = Config_set(cmd_line.split())
        config = Config()
        assert config.ldap.base_dn == 'dc=foo,dc=bar'

    @pytest.mark.xfail
    def test_write_config_to_file(self):
        # Must still implement
        assert False