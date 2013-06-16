__author__ = 'chotee'

import py
import pytest

from members2accounts.members import Members, Member
from members2accounts.config import Config, Defaults
from members2accounts.exc import *

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

    def test_decrypt_and_verify(self):
        m = Members(fixture_file('test_members.json.gpg'))
        assert True == m.decrypt_and_verify(fixture_file('test_keyring'))

    def test_decrypt_and_verify_non_gpg_file(self):
        m = Members(fixture_file('test_members.json'))
        pytest.raises(DecryptionFailedException, m.decrypt_and_verify, fixture_file('test_keyring'))

    def test_decrypt_and_verify_no_key(self):
        m = Members(fixture_file('test_members.json.gpg'))
        pytest.raises(UnknownSignatureException, m.decrypt_and_verify, fixture_file('test_keyring_no_key'))

    def test_decrypt_and_verify_no_trust(self):
        m = Members(fixture_file('test_members.json.gpg'))
        pytest.raises(KeyNotTrustedException, m.decrypt_and_verify, fixture_file('test_keyring_not_trusted'))

    def test_decrypt_and_verify_not_allowed(self, monkeypatch):
        monkeypatch.setattr(Config().gpg, 'allowed_ids', [])
        m = Members(fixture_file('test_members.json.gpg'))
        pytest.raises(SignerIsNotAllowedException, m.decrypt_and_verify, fixture_file('test_keyring'))

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