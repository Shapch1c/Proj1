from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string
from .models import PostCategory, Response
from .tasks import send_new_post_notifications
from django.db.models.signals import post_save
from django.core.mail import send_mail

@receiver(m2m_changed, sender=PostCategory)
def notify_subscribers(sender, instance, action, **kwargs):
    if action == "post_add":
        categories = instance.category.all()

        # Собираем подписчиков
        subscribers_emails = set()
        for category in categories:
            subscribers_emails.update(category.subscribers.values_list('email', flat=True))

        # Если есть подписчики, отправляем уведомления
        if subscribers_emails:
            subject = f"Новый пост в категории: {', '.join([cat.name for cat in categories])}"
            from_email = 'Shapch1c@yandex.ru'

            # Генерация HTML и текстовой версии письма
            html_content = render_to_string(
                'category/follow/email/new_post_notification.html',
                {'post': instance, 'categories': categories}
            )
            text_content = f"Заголовок: {instance.title}\n\n" \
                           f"Краткое описание: {instance.preview()}\n\n" \
                           f"Ссылка: http://127.0.0.1:8000{instance.get_absolute_url()}"

            # Создание и отправка email-сообщения
            send_new_post_notifications.delay(
                list(subscribers_emails), subject, text_content, html_content)


@receiver(post_save, sender=Response)
def notify_post_author(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'Новый отклик на ваше объявление',
            f'У вас новый отклик на объявление "{instance.post.title}".',
            'Shapch1c@yandex.ru',
            [instance.post.author.user.email],
            fail_silently=False,
        )



from django.contrib.auth.models import User
from .models import EmailList


@receiver(post_save, sender=User)
def save_user_email(sender, instance, created, **kwargs):
    if instance.email:  # Проверяем, что email есть
        email_obj, created = EmailList.objects.get_or_create(email=instance.email)

        if created:
            print(f"Добавлен новый email: {instance.email}")  # Для отладки в консоли
