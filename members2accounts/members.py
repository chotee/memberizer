
import json
from members2accounts.config import Config

class Members(object):
    """I represent all current members"""
    def __init__(self):
        self.member_data = None
    def verify_validity(self):
        pass

    def list_members(self):
        """I return the list of all members."""
        if self.member_data is None:
            self.member_data = self.load_member_data()
        return self.member_data

    def load_member_data(self):
        """I read a data stream and create member objects."""
        json_stream = open(Config()['members.json'])
        data = json.load(json_stream)
        return [Member(item) for item in data]


class Member(dict):
    """I represent one member"""
    def __getattr__(self, item):
        if item not in self:
            raise AttributeError(item)
        return self[item]