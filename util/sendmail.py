# -*- coding: utf-8 -*-
# @Time    : 2021/3/27 9:51
# @Author  : zfk
# @Email   : fangkai_zhang@163.com
# @File    : sendmail.py
import smtplib

from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header


def sendmail(content):
    mail_host = "smtp.163.com"
    mail_user = "fangkai_zhang@163.com"
    mail_pass = "CJORHBYLPSOZGTED"
    receivers = "fangkai_zhang@163.com"
    message = MIMEText("hello，fangkai, today result as following\n"+content, 'plain', 'utf-8')
    subject = u'stock'
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = SMTP_SSL(mail_host)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(mail_user, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

if __name__ == "__main__":
    sendmail("test content")
