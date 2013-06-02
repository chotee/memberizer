__author__ = 'chotee'

import py
import pytest

from members2accounts.members import Members, Member
from members2accounts.config import Config

def fixture_file(name):
    """I return a string with the absolute path to a fixture file"""
    return unicode(py.path.local(__file__).join('..').join(name).realpath())

def fixture_stream(name):
    return open(fixture_file(name), 'rb')

class TestMembers(object):
    def test_load_member_data(self):
        m = Members()
        assert 3 == len(m.load_member_data(fixture_stream('test_members.json')))

    def test_load_member_data_missing_file(self):
        pytest.raises(IOError, Members, 'does-not-exist')

    def test_load_member_data_broken_json(self):
        pytest.raises(ValueError, Members().load_member_data, fixture_stream('test_members_broken.json'))

class TestMember(object):
    def test_init(self):
        data = {'email': 'test@somedomain.com',
                'nickname': 'testtest',
                'paid_until': '2012-03-12'}
        m = Member(data)
        assert m.email == 'test@somedomain.com'
        try:
            m.doesnotexist
        except AttributeError:
            pass
        else:
            assert False, "Should have thrown"