from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from datetime import datetime
from email import encoders
from time import time
import smtplib


def timestamp():
    t = time()
    session_date = datetime.fromtimestamp(t).strftime('_%Y%m%d_%H_%M_%S')
    return session_date


# Create timestamp for outfile naming convention
session_timestamp = timestamp()


def send_email(send_from, password, send_to, attachment, filename, body, subject):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    p = MIMEBase('application', 'octet-stream')
    p.set_payload(attachment.read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(send_from, password)
    s.sendmail(send_from, send_to, msg.as_string())
    s.quit()


def report(send_from, password, send_to, file_path):
    attachment = file_path.open("rb")

    bargain_message = "New bargain list executed"
    subject = "Pricelist executed at" + session_timestamp

    send_email(send_from, password, send_to, attachment, file_path, bargain_message, subject)