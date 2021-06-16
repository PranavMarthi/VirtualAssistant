# import smtplib
# import time
#
#
# def send_email(subject, msg):
#     # email = input("Enter a email address: ")
#
#     email = input("What email ?")
#
#     try:
#
#         import config
#
#         server = smtplib.SMTP('smtp.gmail.com:587')
#         server.ehlo()
#         server.starttls()
#         server.login(config.EMAIL_ADDRESS, config.PASSWORD)
#         message = 'Subject: {}\n\n{}'.format(subject, msg)
#         server.sendmail(email, email, message)
#         server.quit()
#         print("Success: Email sent!")
#         time.sleep(60)
#     except:
#
#         print("Email failed to send.")
#
#
# subject = "Test subject"
# msg = "Hello there, how are you today?"
# send_email(subject, msg)
import randfacts

x = randfacts.getFact()
print(x)