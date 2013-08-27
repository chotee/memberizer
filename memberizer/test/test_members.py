__author__ = 'chotee'

from copy import deepcopy
import py
import pytest

from memberizer.members import Members, Member
from memberizer.config import Config, Defaults, Config_reset
from memberizer.exc import *

def fixture_file(name):
    """I return a string with the absolute path to a fixture file"""
    return unicode(py.path.local(__file__).join('..').join(name).realpath())

def fixture_stream(name):
    return open(fixture_file(name), 'rb').read()

@pytest.fixture
def Set_GPG_Test_Fingerprints():
    Config_reset()
    data = deepcopy(Defaults)
    data['gpg']['my_id'] = '7C7F 7435 140C E92E BB33  6CF7 8367 1848 9BB7 D7C7' # Fingerprint of the key that the automation uses to decrypt and sign
    data['gpg']['signer_ids'] = [
            '8044 9D3E 6EAC E4D9 C4D2  A5D7 6752 C3BC 94DA 7C30',
        ] # IDs of Keys that we see as valid signers of member lists. Keys must be imported and trusted!
    Config(custom_data=data)

@pytest.mark.usefixtures("Set_GPG_Test_Fingerprints")
class TestMembers(object):
    def test_load_member_data(self):
        m = Members()
        assert 3 == len(m.load_member_data(fixture_stream('test_members.json')))
        assert 3 == len(m.load_member_data(fixture_stream('test_members-2.json')))

    def test_load_member_data_missing_file(self):
        pytest.raises(IOError, Members, 'does-not-exist')

    def test_check_sanity(self):
        m = Members()
        m.check_sanity(fixture_file('test_keyring'))

    def test_decrypt_and_verify(self):
        m = Members()
        assert True == m.decrypt_and_verify(fixture_file('test_keyring'), member_filename=fixture_file('test_members.json.gpg'))
        assert m.signer_fingerprint is not None

    def test_member_edgecases(self):
        m = Members(fixture_file("test_members_edgecases.json"), encrypted=False)
        members = m.list_members()
        assert ['', 'madness', 'upcased', 'withspaces'] == sorted([m.nickname for m in members])

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

    def test_nickname_raw(self):
        data = {
            'nickname': 'Strange Nick!',
            'email': 'test@somedomain.com',
            'paid_until': '2012-03-12'
        }
        m = Member(data)
        assert 'Strange Nick!' == m.nickname_raw
        assert 'strangenick' == m.nickname
