
from django.urls import reverse
from django.core.cache import cache
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
class Author(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text=_('category name'))

    def __str__(self):
        return self.name


class Post(models.Model):

    tanks = 'TS'
    healers = 'HE'
    dd = 'DD'
    merchants = 'ME'
    guild_masters = 'GM'
    quest_givers = 'QG'
    blacksmiths = 'BL'
    tanners = 'TA'
    zelvars = 'ZE'
    spellmasters = 'SM'

    POST_TYPES = [
        (tanks, 'Танки'),
        (healers, 'Хилы'),
        (dd, 'ДД'),
        (merchants, 'Торговцы'),
        (guild_masters, 'Гилдмастеры'),
        (quest_givers, 'Квестгиверы'),
        (blacksmiths, 'Кузнецы'),
        (tanners, 'Кожевники'),
        (zelvars, 'Зельевары'),
        (spellmasters, 'Мастера заклинаний'),
    ]


    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    post_type = models.CharField(max_length=2, choices=POST_TYPES)
    post_time = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = RichTextUploadingField()

    def preview(self):
        if len(self.text) > 124:
            return self.text[0:124] + '...'
        else:
            return self.text 

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.title.title()}:{self.preview()}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # сначала вызываем метод родителя, чтобы объект сохранился
        cache.delete(f'news-{self.pk}')  # затем удаляем его из кэша, чтобы сбросить его


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.category.name




class Response(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='responses')  # Связь с объявлением
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='user_responses')  # Связь с автором отклика
    text = models.TextField()  # Обычный текст отклика
    text = models.TextField()  # Обычный текст без сложных форматов
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
    accepted = models.BooleanField(default=False)  # Принятие отклика

    def accept(self):
        """Принятие отклика и отправка уведомления пользователю"""
        self.accepted = True
        self.save()

        # 📩 Отправляем email пользователю, оставившему отклик
        send_mail(
            'Ваш отклик принят!',
            f'Здравствуйте, {self.user.username}!\n\n'
            f'Ваш отклик на объявление "{self.post.title}" был принят автором.\n\n'
            f'Поздравляем!',
            'Shapch1c@yandex.ru',  # Почта отправителя
            [self.user.email],  # Почта пользователя, оставившего отклик
            fail_silently=False,
        )

    def __str__(self):
        return f'Отклик от {self.user.username} на {self.post.title}'



User = get_user_model()

class OneTimeCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.code}"





class EmailList(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email


class Subscriber(models.Model):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email