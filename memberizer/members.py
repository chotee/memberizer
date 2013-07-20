import json
import logging
log = logging.getLogger('m2a.' + __name__)

#log.setLevel(logging.DEBUG)
import py
from config import Config
from gpgcrypto import GpgCrypto

class Members(object):
    """I represent all current members"""
    def __init__(self, member_filename=None):
        self.member_filename = member_filename
        if self.member_filename is not None:
            open(self.member_filename, 'rb').close() # Just to provoke IOError on missing file.
        self.json_data = None
        self.member_data = None
        self.signer_fingerprint = None
        self._c = Config()
        self._gpg = None

    def decrypt_and_verify(self, keyring=None, member_filename=None):
        if member_filename is None:
            member_filename = self.member_filename
        self.json_data, self.signer_fingerprint = GpgCrypto(keyring).decrypt_and_verify(member_filename)
        return True

    def check_sanity(self, keyring=None):
        return GpgCrypto(keyring).check_sanity()

    def list_members(self):
        """I return the list of all members."""
        if self.member_data is None:
            self.member_data = self.load_member_data(self.json_data)
        log.info("The member file contained %d members.", len(self.member_data))
        return self.member_data

    def load_member_data(self, json_stream):
        """I read a json data-stream and return a list of member objects."""
        log.debug("starting JSON load of member file.")
        data = json.loads(json_stream, encoding='utf-8')
        log.debug("Done.")
        return [Member(item) for item in data]

    def signer_email(self, keyring=None):
        if self.signer_fingerprint is None:
            return None
        return GpgCrypto(keyring).email_from_fingerprint(self.signer_fingerprint)

class Member(dict):
    """I represent one member"""
    def __getattr__(self, item):
        if item not in self:
            raise AttributeError(item)
        return self[item]