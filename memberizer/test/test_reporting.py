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

    def test_pubish_multiple(self, monkeypatch):
        monkeypatch.setattr(smtplib, "SMTP", Mock_smtplib_SMTP)
        cr = ChangeReport(keyring=fixture_file('test_keyring'))
        cr.publish(["80449D3E6EACE4D9C4D2A5D76752C3BC94DA7C30",
                    "80449D3E6EACE4D9C4D2A5D76752C3BC94DA7C30"])

    def test_report_row(self):
        cr = ChangeReport()
        assert "foo" == cr.report_row("foo")
        assert "foo|bar" == cr.report_row("foo|%s", "bar")
        assert "foo|bar#quux" == cr.report_row("foo|%s#%s", "bar", "quux")

    def test_compose_message(self):
        cr = ChangeReport()
        assert "Changes in this run:\nrun report complete." == cr.compose_message()
        cr.add_event("Name", "Nick", "Args")
        assert "Changes in this run:\nName: 'Nick' Args\nrun report complete." == cr.compose_message()
        cr = ChangeReport()
        cr.add_event("Name", "Nick", ["Arg1", "Arg2"])
        assert "Changes in this run:\nName: 'Nick' ['Arg1', 'Arg2']\nrun report complete." == cr.compose_message()
