from email.mime.text import MIMEText
import smtplib
import os


class EmailSender:
    @staticmethod
    def send_height_data_email(name, email, height):
        from_email = os.environ.get('EMAIL_USER')
        from_pass = os.environ.get('EMAIL_PASS')
        to_email = email

        subject = "Height Data"
        message = "Hi %s, your height is %s." %(name, height)

        msg = MIMEText(message, 'html')
        msg['Subject'] = subject
        msg['To'] = to_email
        msg['From'] = from_email

        gmail = smtplib.SMTP('smtp.gmail.com', 587)
        # gmail.echo()
        gmail.starttls()
        gmail.login(from_email, from_pass)
        gmail.send_message(msg)
