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

    def test_check_sanity(self):
        m = Members()
        m.check_sanity(fixture_file('test_keyring'))

    def test_check_sanity_missing_keyring(self, tmpdir):
        '''I test what happens when a file is not the expected keyring directory'''
        m = Members()
        pytest.raises(SecretKeyNotInKeyringException, m.check_sanity, str(tmpdir))
        pytest.raises(CryptoException, m.check_sanity, str(tmpdir.join("does_not_exist")))
        str(tmpdir.join("some_file.txt").open('a').close())
        pytest.raises(CryptoException, m.check_sanity, str(tmpdir.join("does_not_exist")))

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
        monkeypatch.setattr(Config().gpg, 'signer_ids', [])
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