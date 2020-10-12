from email.mime.text import MIMEText
import smtplib


class EmailSender:

    def send_height_data_email(self, name, email, height):
        from_email = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        from_pass = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
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
