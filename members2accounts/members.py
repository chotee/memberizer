
import json
import gnupg
from members2accounts.config import Config
from members2accounts.exc import DecryptionFailedException, UnknownSignatureException, \
    KeyNotTrustedException, SignerIsNotAllowedException

class Members(object):
    """I represent all current members"""
    def __init__(self, member_filename=None):
        self.member_filename = member_filename
        if member_filename is not None:
            self.member_fd = open(self.member_filename, 'rb')
        self.json_data = None
        self.member_data = None

    def decrypt_and_verify(self):
        """I use GPG to decrypt the file and verify that it is to be trusted."""
        gpg = gnupg.GPG(Config['gpg_keyring'])
        dec_data = gpg.decrypt_file(self.member_fd)
        if not dec_data.ok:
            raise DecryptionFailedException("filename: %s" % self.member_filename)
        if not dec_data.valid:
            raise UnknownSignatureException("Signed with unknown ID: %s" % dec_data.key_id)
        if dec_data.trust_level < dec_data.TRUST_FULLY:
            raise KeyNotTrustedException("Key %s [%s] is in the keyring, but not trusted" % (dec_data.username,
                                                                                                dec_data.pubkey_fingerprint[-8:]))
        ### Okay, it's a validly signed file. Now lets see if this signer is allowed to update member data.
        if not self._is_allowed(dec_data):
            raise SignerIsNotAllowedException("Key %s [%s] is trusted, but not allowed to update member data" % (dec_data.username, pubkey_fingerprint[-8:]))

        return True

    def _is_allowed(self, dec_data):
        for fpr in Config()['gpg_allowed_ids']:
            canonical_fpr = key.replace(' ', '')
            if canonical_fpr == dec_data.pubkey_fingerprint:
                return True
        return False

    def list_members(self):
        """I return the list of all members."""
        if self.member_data is None:
            self.member_data = self.load_member_data(json_data)
        return self.member_data

    def load_member_data(self, json_stream):
        """I read a json data-stream and return a list of member objects."""
        data = json.load(json_stream)
        return [Member(item) for item in data]


class Member(dict):
    """I represent one member"""
    def __getattr__(self, item):
        if item not in self:
            raise AttributeError(item)
        return self[item]