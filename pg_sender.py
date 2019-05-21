#-*- coding: utf-8 -*-
import os
import re
import smtplib
import mimetypes
import logging
import csv

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email import encoders

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
    
    years = '2019'
    talk_proposal = '' # TalkProposal-2017-04-26.csv
    doodle = '' # http://doodle.com/poll/kt8a77geefxyinz4
    registration_date = '' # Jun 20
    question_date = '' # May 30
    speakers = []

    with open(talk_proposal, 'rt') as csvfile: # because is text file so need use 'rt' open not 'rb'
        talks = csv.DictReader(csvfile)
        for talk in talks:
            speakers.append([talk['name'], talk['title'], talk['email']])
            logger.info(f"作者, {talk['name']}, 題目： {talk['title']}")
            
            zh_content = """
            <div style="border:2px #ccc solid;padding:15px;margin-top:15px;font-family:sans-serif;">
                <p> English Below </p>
                
                <p>親愛的 %(name)s 您好，</p>

                <p>
                    恭喜！我們很高興通知，您的投稿 <strong>%(title)s</strong> 經過  PyCon 臺灣 %(years)s 審查委員們的最終審查後決議投稿為<strong>錄取</strong>。
                </p>
                <p>
                    議程組正在進行議程安排，各位講者如有偏好的演講時間，邀請您至 %(doodle)s 
                    網站以投稿信箱作為使用者名稱登記並勾選對應時間，假如需要修改請重新進入網站再次填寫，將以最新記錄為主。
                    如果沒有進入系統填寫，議程組將會主動幫您安排時間。最終議程還是會以大會公告為主。
                </p>
                <p>
                    註冊組在稍早前也已經寄送<font color="green">投稿貢獻邀請碼（Submission, 投稿鼓勵票）</font>給您，請您務必在 %(registration_date)s 前完成購票，
                    <u>如果您臨時需要撤稿也請您回覆告知我們以方便議程安排。</u> 
                </p>
                <p>
                    同時也通知各位講者，如果您在交通或是門票上需要協助也誠摯歡迎您申請今年財務補助方案，只要您提出需要 PyConTW 都會盡最大力量。
                    申請的辦法是進入財務補助網站填寫<a href="https://tw.pycon.org/%(years)s/zh-hant/registration/financial-aid/">申請表單</a>。
                </p>
                <p>
                    以上是議程組與您提醒的相關細節與事項，如果有任何問題請您於 <strong>%(question_date)s</strong> 號前來信 organizers@pycon.tw 與我們聯繫。
                </p>
                <p>
                    再次恭喜您，期待我們今年會議會場見。<br>
                </p>
                <p>
                    Best Regards,<br>
                    PyCon TW %(years)s Program Committee
                </p>
            </div>
            """%{
                'years': years,
                'name': talk['name'],
                'title': talk['title'],
                'doodle': doodle,
                'registration_date': registration_date,
                'question_date': question_date
            }
            #%(talk['name'], talk['title'], doodle, registration_date, question_date)


            en_content = """
            <div style="border:2px #ccc solid;padding:15px;margin-top:15px;font-family:sans-serif;">

                <p>Dear Author %(name)s,</p>

                <p>
                    Congratulations!
                </p>

                <p>
                    We are pleased to inform you that your proposal <strong>%(title)s</strong> has been <strong>Accepted</strong> by the Programme Committee of the PyCon Taiwan %(years)s.
                </p>
                <p>
                    The program team is going to plan the full program schedule for PyCon Taiwan %(years)s, 
                    we invite you to access this website, %(doodle)s, 
                    and select date and time (please leave your email in “Your name” input box) 
                    if you have a preferred session time. If you do not have a preferred session time though, 
                    the program team will take the initiative to decide. 
                    The final schedule will be based on the General Assembly announcement.
                </p>
                <p>
                    Earlier, the registration team has already sent an <font color="green">invitation code </font>for you, 
                    so you can always buy the ticket with early bird price, 
                    please complete the ticket purchase before %(registration_date)s. 
                    <u>And if for some reason you have to withdraw your proposal, please also notify us through a reply.</u>
                </p>
                <p>
                    PyCon Taiwan has announced this year’s Financial Aid Program, which is for helping those who aren’t able to totally 
                    afford transport or registration fee to join PyCon TW. As long as you need a financial support, 
                    please simply apply for the <a href="https://tw.pycon.org/%(years)s/en-us/registration/financial-aid/">Financial Aid Program</a>.
                </p>
                <p>
                    The above is the relevant details and matters from the program team. 
                    If have any please mail to <strong>organizers@pycon.tw</strong> before %(question_date)s.
                </p>
                <p>
                    Congratulations again, and we’re looking forward to meeting you at this year's conference!<br>
                </p>
                <p>
                    Best Regards,<br>
                    PyCon TW %(years)s Program Committee
                </p>
            </div>
            """%{
                'years': years,
                'name': talk['name'],
                'title': talk['title'],
                'doodle': doodle,
                'registration_date': registration_date,
                'question_date': question_date
            }
            #(talk['name'], talk['title'], doodle, registration_date, question_date)
            
            try:
                cc = [
                    f'{CC_MAIL}'
                ]
                server = 'smtp.gmail.com'
                username = f'{ACCOUNT}'
                password = f'{PASSWORD}'
                smtp = SMTP(server=server, username=username, password=password)
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