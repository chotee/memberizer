import json
import gnupg
import logging
log = logging.getLogger(__name__)

from config import Config
from exc import DecryptionFailedException, UnknownSignatureException, \
    KeyNotTrustedException, SignerIsNotAllowedException, SecretKeyNotInKeyringException

class Members(object):
    """I represent all current members"""
    def __init__(self, member_filename=None):
        self.member_filename = member_filename
        self.member_fd = open(self.member_filename, 'rb') if member_filename is not None else None
        self.json_data = None
        self.member_data = None
        self._c = Config()

    def _make_gpg_instance(self, keyring):
        if keyring is None:
            keyring = self._c.gpg.keyring
        log.info("Using GnuPG keyring %s", keyring)
        gpg = gnupg.GPG(gnupghome=keyring)
        return gpg

    def check_sanity(self, keyring=None):
        gpg = self._make_gpg_instance(keyring)
        for key in gpg.list_keys(secret=True): # iter over the secret keys avialable in the ring
            if key['fingerprint'] == self._c.gpg.my_id:
                return
        raise SecretKeyNotInKeyringException("In keyring '%s' No key found with fingerprint '%s'" % (gpg.gnupghome, self._c.gpg.my_id))

    def decrypt_and_verify(self, keyring=None):
        """I use GPG to decrypt the file and verify that it is to be trusted."""
        gpg = self._make_gpg_instance(keyring)

        assert self.member_fd is not None
        dec_data = gpg.decrypt_file(self.member_fd)
        if not dec_data.ok:
            raise DecryptionFailedException("Cannot decrypt file '%s'. Was it properly encrypted with key '%s'?" % (self.member_filename, self._c.gpg.my_id))
        if not dec_data.valid:
            raise UnknownSignatureException("Signed with unknown ID: %s" % dec_data.key_id)
        if dec_data.trust_level < dec_data.TRUST_FULLY:
            raise KeyNotTrustedException("Document is singed by %s (%s). This key is in the keyring, but not trusted." % (dec_data.pubkey_fingerprint, dec_data.username))
        ### Okay, it's a validly signed file. Now lets see if this signer is allowed to update member data.
        if not self._is_allowed(dec_data):
            raise SignerIsNotAllowedException("Document is singed by %s (%s). However this key is not allowed to update member data. Check the gpg.signer_ids setting." % (
                dec_data.pubkey_fingerprint, dec_data.username))
        return True

    def _is_allowed(self, dec_data):
        for fpr in Config().gpg.signer_ids:
            canonical_fpr = fpr.replace(' ', '')
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