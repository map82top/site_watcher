from plugins.Plugin import Plugin
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import logging


logger = logging.getLogger(__name__)


class MailPlugin(Plugin):
    server = smtplib.SMTP('smtp.gmail.com: 587')
    account = "iptestmessage@gmail.com"
    password = 'Testpwd1'

    def run(self, data):
        msg = MIMEMultipart()
        message = 'New update for site {0} Changes {1} Match keys: {2}'.format(data['site'].name,
                                                                               data['version'].count_changes,
                                                                               data['version'].count_match_keys)
        msg['From'] = MailPlugin.account
        msg['To'] = "iptestmessage@gmail.com"
        msg['Subject'] = "Site watcher update"
        msg.attach(MIMEText(message, 'plain'))

        MailPlugin.server.starttls()
        MailPlugin.server.login(MailPlugin.account, MailPlugin.password)
        MailPlugin.server.sendmail(MailPlugin.account, msg['To'], msg.as_string())
        MailPlugin.server.quit()
        logger.debug('Send email message for version {0} site'.format(data['site'].name))