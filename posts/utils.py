import string
import random

def get_random_slug():
    letters_and_digits = string.hexdigits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(14)))
    return result_str



from django.core.mail import EmailMessage


import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()
