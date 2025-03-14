from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:  # Проверяем, что пользователь только что создан
        send_mail(
            subject="Добро пожаловать!",
            message=f"Здравствуйте, {instance.username}! Спасибо за регистрацию на нашем сайте!",
            from_email='Shapch1c@yandex.ru',  # Убедитесь, что этот параметр настроен в settings.py
            recipient_list=[instance.email],  # Письмо отправляется на email пользователя
        )