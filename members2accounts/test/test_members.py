__author__ = 'chotee'

import py

from members2accounts.members import Members
from members2accounts.config import Config

class TestMembers(object):
    def test_init(self):
        Members()

    def test_list_members(self, monkeypatch):
        Config()['members.json'] = py.path.local(__file__).join('../test_members.json').realpath()
        assert Config()['members.json'] == 'foo'