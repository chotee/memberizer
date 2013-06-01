
import json
from members2accounts.config import Config

class Members(object):
    def __init__(self):
        self.member_data = None
    def verify_validity(self):
        pass

    def list_members(self):
        if self.member_data is None:
            self.member_data = self.load_member_data()
        return self.member_data

    def load_member_data(self):
        json_stream = open(Config()['members.json'])
        return json.load(json_stream)

class Member(dict):
    def __getattr__(self, item):
        if item not in self:
            raise AttributeError(item)
        return self[item]