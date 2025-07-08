from django.core.mail import send_mail
from celery import shared_task

from django.conf import settings



#sendig email
@shared_task
def email_send(subject,message,email_host,user_email):

    send_mail(subject,message,email_host,user_email)
    print("done it")