import smtplib
import logging

from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr

from alerter.default_setting import (DEFAULT_EMAIL_USER,
                                     DEFAULT_EMAIL_PASS,
                                     DEFAULT_EMAIL_SERVER)


class MailServer:
    def __init__(self):
        self.server = smtplib.SMTP(DEFAULT_EMAIL_SERVER, 25)
        self.server.set_debuglevel(1)
        self._from_address = DEFAULT_EMAIL_USER
        self._password = DEFAULT_EMAIL_PASS

        self.server_login()

    def server_login(self):
        self.server.login(self._from_address, self._password)

    def server_exit(self):
        self.server.quit()

    def mail_send(self, address, message):
        try:
            msg = self._build_msg(address, message)
            self.server.sendmail(self._from_address,
                                 address if isinstance(address, list) else [address, ],
                                 msg.as_string())
        except smtplib.SMTPException as error_:
            logging.error(str(error_))

    def _build_msg(self, to_address, message):
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = self.format_address("zhxfei's Ease monitor alert <%s>" % self._from_address)
        msg['To'] = self.format_address('adminnistor <%s>' % to_address)
        msg['Subject'] = Header('Ease monitor', 'utf-8').encode()
        return msg

    @staticmethod
    def format_address(s):
        name, address = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), address))
