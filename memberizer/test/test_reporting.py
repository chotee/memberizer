__author__ = 'Chotee'

from reporting import ChangeReport

class TestChangeReport(object):
    def test_init(self):
        cr = ChangeReport()
    def test_record(self):
        cr = ChangeReport()
        cr.add_event("Foo", 'nick', ["bar", "quux"])
        assert cr.events[0] == ["Foo", 'nick',["bar", "quux"]]

    def test_pubish(self):
        cr = ChangeReport()
        cr.publish()