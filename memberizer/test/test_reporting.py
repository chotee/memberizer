__author__ = 'Chotee'

import py

from reporting import ChangeReport
from mocks import Mock_smtplib_SMTP
import smtplib

def fixture_file(name):
    """I return a string with the absolute path to a fixture file"""
    return unicode(py.path.local(__file__).join('..').join(name).realpath())

class TestChangeReport(object):
    def test_init(self):
        cr = ChangeReport()

    def test_record(self):
        cr = ChangeReport()
        cr.add_event("Foo", 'nick', ["bar", "quux"])
        assert cr.events[0] == ["Foo", 'nick',["bar", "quux"]]

    def test_pubish(self, monkeypatch):
        monkeypatch.setattr(smtplib, "SMTP", Mock_smtplib_SMTP)
        cr = ChangeReport(keyring=fixture_file('test_keyring'))
        cr.publish("80449D3E6EACE4D9C4D2A5D76752C3BC94DA7C30")
