__author__ = 'chotee'

from config import Config_set

class Test_SetConfig(object):
    def test_init(self):
        config = Config_set([])
        assert config.base_dn == "dc=techinc,dc=nl"

    def test_custom_config(self):
        pass