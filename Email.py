import smtplib
from email.mime.text import MIMEText
import getpass


class Email():
    def __init__(self, subject, message, sender, recipients):
        self.subject = subject
        self.message = message
        self.recipients = recipients
        self.sender = sender

    def build_and_send(self):
        msg = MIMEText(self.message)
        msg['Subject'] = self.subject
        s = smtplib.SMTP('localhost')
        msg['From'] = '%s <%s>' % (getpass.getuser(), self.sender)
        msg['To'] = self.recipients
        try:
            s.sendmail('"%s <%s>"' % (getpass.getuser(), self.sender), self.recipients.replace(';',',').split(','), msg.as_string())
        except Exception as e:
            print e
        s.quit()
