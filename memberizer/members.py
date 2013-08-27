import json
import logging
log = logging.getLogger('m2a.' + __name__)

import re
from config import Config
from gpgcrypto import GpgCrypto

class Members(object):
    """I represent all current members"""
    def __init__(self, member_filename=None, encrypted=True):
        self.member_filename = member_filename
        self.encrypted = encrypted
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
        if json_stream is None and self.encrypted == False:
            json_stream = open(self.member_filename, 'rb').read()
        data = json.loads(json_stream, encoding='utf-8')
        log.debug("Done.")
        return [Member(item) for item in data]

class Member(dict):
    """I represent one member"""
    def __getattr__(self, item):
        if item not in self:
            raise AttributeError(item)
        return self[item]

    @property
    def nickname(self):
        """I make sure the nicks are somewhat normal, stripping off all non alphanumeric chars and lowercasing."""
        nick = self['nickname']
        nick = re.sub('[^a-zA-Z0-9]', '',nick).lower()
        return nick

    @property
    def nickname_raw(self):
        return self['nickname']