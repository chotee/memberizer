__author__ = 'chotee'

import re
import logging
log = logging.getLogger('m2a.' + __name__)

import gnupg
import py

from memberizer.config import Config
from memberizer.exc import *

class GpgCrypto(object):
    def __init__(self, keyring=None):
        self._c = Config()
        if keyring is None:
            keyring = self._c.gpg.keyring
        if keyring:
            log.info("Using GnuPG keyring %s", keyring)
            if not py.path.local(keyring).check(dir=1):
                raise CryptoException("Keyring '%s' is not a directory. Set gpg.keyring" % keyring)
        else:
            log.info("Using default GnuPG keyring")
        gpgbinary = self._c.gpg.gpg_binary if self._c.gpg.gpg_binary else "gpg"
        self._gpg = gnupg.GPG(gnupghome=keyring, gpgbinary=gpgbinary)

    def check_sanity(self, keyring=None):
        gpg_my_id = self._c.gpg.my_id
        for key in self._gpg.list_keys(secret=True): # iter over the secret keys available in the ring
            if key['fingerprint'] == gpg_my_id:
                return
        raise SecretKeyNotInKeyringException("In keyring '%s' No key found with fingerprint '%s'" % (self._gpg.gnupghome,
                                                                                                     gpg_my_id))

    def decrypt_and_verify(self, member_filename, keyring=None):
        """I use GPG to decrypt the file and verify that it is to be trusted."""
        assert member_filename is not None
        log.info("Reading member file %s", member_filename)
        member_fd = open(member_filename, 'rb') if member_filename is not None else None
        dec_data = self._gpg.decrypt_file(member_fd)
        log.debug("Done.")
        if not dec_data.ok:
            raise DecryptionFailedException("Cannot decrypt file '%s'. Was it properly encrypted with key '%s'?" % (member_filename, self._c.gpg.my_id))
        if not dec_data.valid:
            raise UnknownSignatureException("Signed with unknown ID: %s" % dec_data.key_id)
        if dec_data.trust_level < dec_data.TRUST_FULLY:
            raise KeyNotTrustedException("Document is singed by %s. This key is in the keyring, but not trusted." % self._key_id(dec_data))
            ### Okay, it's a validly signed file. Now lets see if this signer is allowed to update member data.
        if not self._is_allowed(dec_data):
            raise SignerIsNotAllowedException("Document is singed by %s. However this key is not allowed to update member data. Check the gpg.signer_ids setting." % self._key_id(dec_data))
        log.info("Member document valid! Encrypted and signed by %s", self._key_id(dec_data))
        signer_email = self._get_signer_email(dec_data)
        return dec_data.data, signer_email

    def encrypt_and_sign(self, message, receptor_fingerprint):
        receptor_fingerprint = receptor_fingerprint.replace(' ', '')
        signed_message = self._gpg.sign('foo').data
        encrypted_message = self._gpg.encrypt(signed_message, [receptor_fingerprint])
        if encrypted_message.status != 'encryption ok':
            raise EncryptingFailedException("Cannot encrypt message with key '%s': '%s'." % (
                                            receptor_fingerprint, encrypted_message.status))
        return encrypted_message.data

    def _get_signer_email(self, dec):
        return re.search('<(.*)>', dec.username).groups()[0]

    def _key_id(self, dec):
        return "%s (%s)" % (dec.pubkey_fingerprint, dec.username)

    def _is_allowed(self, dec_data):
        for fpr in Config().gpg.signer_ids:
            canonical_fpr = fpr.replace(' ', '')
            if canonical_fpr == dec_data.pubkey_fingerprint:
                return True
        return False
