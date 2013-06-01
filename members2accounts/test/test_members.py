__author__ = 'chotee'

import py
import pytest

from members2accounts.members import Members, Member
from members2accounts.config import Config

def fixture_file(name):
    """I return a string with the absolute path to a fixture file"""
    return unicode(py.path.local(__file__).join('..').join(name).realpath())

@pytest.fixture
def test_json(request):
    Config()['members.json'] = fixture_file('test_members.json')

@pytest.fixture
def test_json_broken(request):
    Config()['members.json'] = fixture_file('test_members_broken.json')

class TestMembers(object):
    def test_init(self):
        Members()

    def test_load_member_data(self, test_json):
        assert Config()['members.json'] == fixture_file('test_members.json')
        m = Members()
        assert 3 == len(m.load_member_data())

    def test_load_member_data_missing_file(self):
        Config()['members.json'] = 'doesnotexist.'
        pytest.raises(IOError, Members().load_member_data)

    def test_load_member_data_broken_json(self, test_json_broken):
        pytest.raises(ValueError, Members().load_member_data)

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