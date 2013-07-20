__author__ = 'chotee'

from copy import deepcopy
import py
import pytest

from memberizer.config import Config, Defaults, Config_reset
from memberizer.gpgcrypto import GpgCrypto
from memberizer.exc import SecretKeyNotInKeyringException, CryptoException, DecryptionFailedException, \
    UnknownSignatureException, KeyNotTrustedException, SignerIsNotAllowedException, EncryptingFailedException
from memberizer.members import Members

@pytest.fixture
def Set_GPG_Test_Fingerprints():
    Config_reset()
    data = deepcopy(Defaults)
    data['gpg']['my_id'] = '7C7F 7435 140C E92E BB33  6CF7 8367 1848 9BB7 D7C7' # Fingerprint of the key that the automation uses to decrypt and sign
    data['gpg']['signer_ids'] = [
            '8044 9D3E 6EAC E4D9 C4D2  A5D7 6752 C3BC 94DA 7C30',
        ] # IDs of Keys that we see as valid signers of member lists. Keys must be imported and trusted!
    Config(custom_data=data)

def fixture_file(name):
    """I return a string with the absolute path to a fixture file"""
    return unicode(py.path.local(__file__).join('..').join(name).realpath())

def fixture_stream(name):
    return open(fixture_file(name), 'rb').read()


@pytest.mark.usefixtures("Set_GPG_Test_Fingerprints")
class TestGpgCrypto(object):

    def test_check_sanity(self):
        g = GpgCrypto(fixture_file('test_keyring'))
        g.check_sanity()

    def test_check_sanity_missing_keyring(self, tmpdir):
        '''I test what happens when a file is not the expected keyring directory'''
        g = GpgCrypto(str(tmpdir))
        pytest.raises(SecretKeyNotInKeyringException, g.check_sanity)
        pytest.raises(CryptoException, g.check_sanity, str(tmpdir.join("does_not_exist")))
        str(tmpdir.join("some_file.txt").open('a').close())
        pytest.raises(CryptoException, g.check_sanity, str(tmpdir.join("does_not_exist")))

    def test_decrypt_and_verify(self):
        m = Members(fixture_file('test_members.json.gpg'))
        assert True == m.decrypt_and_verify(fixture_file('test_keyring'))
        assert "8A50260EBB0E2600DB367AEB15D393C7675E522F" == m.signer_fingerprint

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

    def test_encrypt_and_sign(self):
        g = GpgCrypto(fixture_file('test_keyring'))
        g.check_sanity()
        message = g.encrypt_and_sign("Test", "8044 9D3E 6EAC E4D9 C4D2  A5D7 6752 C3BC 94DA 7C30")
        assert '' != message
        pytest.raises(EncryptingFailedException, g.encrypt_and_sign, "Test", "failed identity")

    def test_email_from_fingerprint(self):
        g = GpgCrypto(fixture_file('test_keyring'))
        email = g.email_from_fingerprint("8044 9D3E 6EAC E4D9 C4D2  A5D7 6752 C3BC 94DA 7C30")
        assert 'chotee@openended.eu' == email
        pytest.raises(UnknownSignatureException, g.email_from_fingerprint, "fail")