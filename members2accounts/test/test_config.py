__author__ = 'chotee'

import pytest
import py

from config import Config_set

class Test_SetConfig(object):
    def test_init(self):
        config = Config_set([])
        assert config.ldap.base_dn == "dc=techinc,dc=nl"

    def test_custom_config_file(self):
        cmd_line = "-C %s" % py.path.local(__file__).join('..').join('config_custom.conf').realpath()
        config = Config_set(cmd_line.split())
        assert config.ldap.base_dn == 'dc=techinc,dc=nl'

    @pytest.mark.xfail
    def test_write_config_to_file(self):
        # Must still implement
        assert False