import logging
log = logging.getLogger("m2a."+__name__)

class ChangeReport(object):
    def __init__(self):
        self.events = []

    def add_event(self, name, nick, args):
        self.events.append([name, nick, args])

    def publish(self):
        self._report_row("Changes in this run:")
        for e in self.events:
            self._report_row(e)
        self._report_row("run report complete.")

    def _report_row(self, *args):
        if len(args) == 1:
            message = args[0]
        else:
            message = args[0] % args[1:]
        log.info(message)