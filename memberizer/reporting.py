import smtplib
from email.mime.text import MIMEText

import logging
log = logging.getLogger("m2a."+__name__)

from config import Config
from gpgcrypto import GpgCrypto

class ChangeReport(object):
    def __init__(self, keyring=None):
        self.events = []
        self._c = Config()
        self._gpg = GpgCrypto(keyring)

    def add_event(self, name, nick, args):
        self.events.append([name, nick, args])

    def publish(self, receiver_fingerprint):
        message = []
        message.append(self._report_row("Changes in this run:"))
        for e in self.events:
            message.append(self._report_row(e))
        message.append(self._report_row("run report complete."))
        message = "\n".join(message)
        enc_message = self._gpg.encrypt_and_sign(message, receiver_fingerprint)
        receiver_email = self._gpg.email_from_fingerprint(receiver_fingerprint)
        self._send_email(enc_message, receiver_email)

    def _report_row(self, *args):
        if len(args) == 1:
            message = args[0]
        else:
            message = args[0] % args[1:]
        return message

    def _send_email(self, message, receiver_email):
        email_msg = MIMEText(message)
        email_msg['Subject'] = "Member update report."
        email_msg['From'] = self._c.report.sender
        email_msg['To'] = receiver_email
        import pdb; pdb.set_trace()
        s = smtplib.SMTP(self._c.report.smtp_host, int(self._c.report.smtp_port))
        if self._c.report.smtp_user:
            s.login(self._c.report.smtp_user, self._c.report.smtp_pass)
        s.sendmail(self._c.report.sender, [receiver_email], email_msg.as_string())
        s.quit()