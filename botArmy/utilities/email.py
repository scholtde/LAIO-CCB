import smtplib
import ssl

port = 465  # For SSL
password = "laio#com"
smtp_server = "smtp.yandex.com"
sender_email = "laiocommunity@yandex.com"  # Enter your address
receiver_email = "laiocommunity@yandex.com"  # Enter receiver address

# Create a secure SSL context
context = ssl.create_default_context()

message = """\
Subject: Hi there

This message is sent from Python."""


with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
