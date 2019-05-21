#-*- coding: utf-8 -*-
import os
import re
import smtplib
import mimetypes
import logging
import csv
import pathlib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email import encoders

from jinja2 import Environment, FileSystemLoader

from env import ACCOUNT, PASSWORD, SENDER, CC_MAIL


logger = logging.getLogger(__name__)


class SMTP(object):
    """SMTP class to be used by other program, not to be use by directly
    This base class provides loging to Google smtp mail server by google's Account.
    * connect  : connect to google smtp server, __init__() atut execute.
    * add_file : attachment file by this function, sending mail from here
    * send     : main function
    * close    : should be close after finish this class, after 1.01c auto execute by __del__()
    """

    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.sender = f'{SENDER}'
        log_msg = f"parameter: {self.server}, {self.username}, {self.sender}"
        logger.debug(log_msg)
        self.connect()
        self.attach = []

    def __del__(self):
        self.smt.quit()

    def connect(self):
        """Connect mail server with given information
        """
        # Close existing connection
        try:
            smtplib.SMTP(self.server, 587).quit()
        except Exception as ex:
            pass
        try:
            # might need to switch to STARTTLS authentication, and loging.
            smt = smtplib.SMTP(self.server, 587)
            smt.set_debuglevel(0)
            smt.ehlo()
            smt.starttls()
            smt.ehlo
            smt.login(self.username, self.password)
            self.smt = smt
        except smtplib.SMTPException as ex:
            log_msg = f"smtplib.SMTPException failed: {ex.args}"
            logger.error(log_msg)
            raise ex
        except Exception as ex:
            log_msg = f"smtp failed: {ex.args}"
            logger.error(log_msg)
            raise ex

    def send(self, recipients, cc, title, text_source):
        """main function, send mail from here
        """
        # Check type of text_source, if it is file then read it into a string
        if os.path.isfile(text_source):
            fp = open(text_source, "r")
            content = fp.read()
            fp.close()
        else:
            content = text_source
        # Split recipients into list
        receiver = self.split_recipients(recipients)
        # Mail description
        strMessage = MIMEMultipart()
        strMessage['Subject'] = title
        strMessage['From'] = self.sender
        # multiple recipints
        strMessage['To'] = ", ".join(receiver)
        strMessage['Cc'] = ", ".join(cc)
        #strMessage.attach(MIMEText(content, "plain"))
        strMessage.attach(MIMEText(content, "html"))
        # Attach others into mail
        for item in self.attach:
            strMessage.attach(item)
        self.smt.sendmail(self.sender, receiver, strMessage.as_string())
        logger.info("Success send mail to " + ", ".join(receiver))

    def add_file(self, path):
        """check file exist
        """
        if not os.path.exists(path):
            raise IOError(f"please check file '{path}' exist")
        # Add attached file into mail
        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'image':
            fp = open(path, 'rb')
            msg_file = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == 'audio':
            fp = open(path, 'rb')
            msg_file = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(path, 'rb')
            msg_file = MIMEBase(maintype, subtype)
            msg_file.set_payload(fp.read())
            fp.close()
            # Encode the payload using Base64
            encoders.encode_base64(msg_file)
        # Set the filename parameter
        msg_file.add_header('Content-Disposition', 'attachment', filename=path)
        self.attach.append(msg_file)

    def split_recipients(self, recipients):
        """If recipients is string then split it into list """
        if isinstance(recipients, list):
            return recipients
        else:
            receiver = re.split(",|;| ", recipients) # ---> good
            receiver_list = [item.strip() for item in receiver]
            return receiver_list

    def remove(self):
        """Remove attach list
        """
        self.attach = []

    def close(self):
        """Quit SMTP connection
        """
        self.smt.quit()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s')

    # create engine
    template_path = f"{pathlib.Path(__file__).resolve().parent}/templates/"
    loader = FileSystemLoader(template_path)
    env = Environment(loader=loader)

    template_zh = env.get_template('zh.html')
    template_en = env.get_template('en.html')

    years = ''  # 2019
    talk_proposal = ''  # TalkProposal-2017-04-26.csv
    doodle = ''  # http://doodle.com/poll/kt8a77geefxyinz4
    registration_date = ''  # Jun 20
    question_date = ''  # May 30
    speakers = []

    # because is text file so need use 'rt' open not 'rb'
    with open(talk_proposal, 'rt') as csvfile:
        talks = csv.DictReader(csvfile)
        for talk in talks:
            speakers.append([talk['name'], talk['title'], talk['email']])
            logger.info(f"作者, {talk['name']}, 題目： {talk['title']}")

            zh_content = template_zh.render(years=years, name=talk['name'], title=talk['title'],
                                            doodle=doodle, registration_date=registration_date,
                                            question_date=question_date)

            en_content = template_en.render(years=years, name=talk['name'], title=talk['title'],
                                            doodle=doodle, registration_date=registration_date,
                                            question_date=question_date)

            try:
                cc = [
                    f'{CC_MAIL}'
                ]
                server = 'smtp.gmail.com'
                username = f'{ACCOUNT}'
                password = f'{PASSWORD}'
                smtp = SMTP(server=server, username=username,
                            password=password)
                smtp.send(
                    recipients=[talk['email']],
                    cc=cc,
                    title='[PyConTW2019] Call for Proposals Acceptance letter', # 統一用英文 '[PyConTW2018] 投稿錄取通知信',
                    text_source=zh_content + en_content
                )

            except Exception as ex:
                raise ex

            finally:
                del smtp
