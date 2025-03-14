from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail

@shared_task
def send_new_post_notifications(subscribers_emails, subject, text_content, html_content):
    from_email = 'Shapch1c@yandex.ru'
    msg = EmailMultiAlternatives(subject, text_content, from_email, subscribers_emails)
    msg.attach_alternative(html_content, "text/html")
    msg.send()



import logging

logger = logging.getLogger(__name__)

@shared_task
def send_email_to_all_users(subject, message, recipient):
    try:
        send_mail(
            subject,
            message,
            'Shapch1c@yandex.ru',
            [recipient],
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")