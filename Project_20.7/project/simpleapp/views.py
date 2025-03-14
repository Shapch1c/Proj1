from django.shortcuts import render,get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .filters import PostFilter
from .forms import PostForm
from django.views import View
from .models import Author
from django.http import HttpResponse
from django.conf import settings
LANGUAGE_SESSION_KEY = settings.LANGUAGE_COOKIE_NAME
from django.utils import timezone
import pytz
from django.core.cache import cache
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import Post, Category
import random
import string
import datetime
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils.timezone import now
from .models import OneTimeCode, User
from django.contrib.auth import login, get_backends
from django.core.mail import send_mail
from .models import Post, Response
from .forms import ResponseForm
from .models import Subscriber
class PostsList(ListView):
    model = Post
    ordering = '-post_time'
    template_name = 'post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

    def get_template_names(self):
        if self.request.path == '':
            self.template_name = 'post_list.html'
        elif self.request.path == '/search/':
            self.template_name = 'search.html'
        return self.template_name


class PostsDetail(DetailView):
    model = Post
    template_name = 'post_detail.html'
    context_object_name = 'post'

    def get_object(self, *args, **kwargs):  # переопределяем метод получения объекта, как ни странно

        obj = cache.get(f'news-{self.kwargs["pk"]}',None)  # кэш очень похож на словарь, и метод get действует так же. Он забирает значение по ключу, если его нет, то забирает None.

        # если объекта нет в кэше, то получаем его и записываем в кэш

        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'news-{self.kwargs["pk"]}', obj)
        return obj

class PostsSearch(ListView):
    model = Post
    ordering = '-post_time'
    template_name = 'search.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostsCreate(LoginRequiredMixin, CreateView):
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'
    login_url = '/register/'
    redirect_field_name = 'next'


    def form_valid(self, form):
        user = self.request.user

        # Пытаемся найти объект Author, если нет — создаем новый
        author_instance, created = Author.objects.get_or_create(user=user)

        form.instance.author = author_instance
        return super().form_valid(form)

class PostsUpdate(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'post_edit.html'
    login_url = '/accounts/login/'
    redirect_field_name = 'next'



class PostsDelete(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')
    login_url = '/register/'
    redirect_field_name = 'next'


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'protect/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_premium'] = not self.request.user.groups.filter(name='premium').exists()
        return context


class Index(View):
    def get(self, request):
        curent_time = timezone.now()

        # .  Translators: This message appears on the home page only
        models = Category.objects.all()

        context = {
            'models': models,
            'current_time': timezone.now(),
            'timezones': pytz.common_timezones  # добавляем в контекст все доступные часовые пояса
        }

        return HttpResponse(render(request, 'test_gettext.html', context))

    #  по пост-запросу будем добавлять в сессию часовой пояс, который и будет обрабатываться написанным нами ранее middleware
    def post(self, request):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/news/test')


@login_required
def user_responses(request):
    author = Author.objects.get(user=request.user)  # Получаем автора, связанного с пользователем
    responses = Response.objects.filter(post__author=author)  # Используем объект Author

    post_id = request.GET.get('post')
    if post_id:
        responses = responses.filter(post_id=post_id)

    return render(request, 'responses.html', {'responses': responses})


@login_required
def create_response(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = ResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.post = post
            response.user = request.user
            response.save()

            # 📩 Отправляем email автору объявления
            send_mail(
                'Новый отклик на ваше объявление',
                f'Здравствуйте, {post.author.user.username}!\n\n'
                f'Пользователь {request.user.username} оставил отклик на ваше объявление "{post.title}".\n\n'
                f'Текст отклика:\n"{response.text}"\n\n'
                f'Просмотреть отклики можно на сайте.',
                'Shapch1c@yandex.ru',  # Здесь укажи свою почту-отправителя
                [post.author.user.email],  # Email получателя (автор объявления)
                fail_silently=False,
            )

            return redirect('index')  # Перенаправляем обратно
    else:
        form = ResponseForm()

    return render(request, 'create_response.html', {'form': form, 'post': post})




@login_required
def accept_response(request, response_id):
    """Принимает отклик и отправляет email пользователю"""
    response = get_object_or_404(Response, id=response_id, post__author=request.user.author)

    if not response.accepted:
        response.accept()  # Вызов метода accept(), который отправит email

    return redirect('user_responses')  # Перенаправляем на страницу откликов

@login_required
def delete_response(request, response_id):
    response = get_object_or_404(Response, id=response_id, post__author=request.user.author)
    response.delete()
    return redirect('user_responses')


def index(request):
    posts = Post.objects.all()
    return render(request, 'index.html', {'posts': posts})







User = get_user_model()

# Время жизни кода (например, 10 минут)
CODE_EXPIRATION_MINUTES = 10


def generate_code(length=6):
    """Генерирует случайный код подтверждения."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def send_verification_email(email, code):
    """Отправка письма с кодом подтверждения."""
    send_mail(
        subject="Ваш код подтверждения",
        message=f"Ваш код подтверждения регистрации: {code}",
        from_email=None,  # Django автоматически возьмёт DEFAULT_FROM_EMAIL
        recipient_list=[email],
        fail_silently=False,
    )

def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email:
            return JsonResponse({"error": "Введите email"}, status=400)

        # Добавляем email в подписчиков
        Subscriber.objects.get_or_create(email=email)

        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email, "is_active": False}
        )

        code = generate_code()
        OneTimeCode.objects.create(code=code, user=user, created_at=now())

        send_verification_email(email, code)

        # Сохраняем email в сессии
        request.session["email"] = email

        return redirect("verify")  # Редирект на страницу подтверждения

    return render(request, "register.html")



def verify_email_view(request):
    if request.method == "POST":
        email = request.session.get("email")  # Берём email из сессии
        code = request.POST.get("code")

        if not email:
            return JsonResponse({"error": "Сессия истекла, попробуйте снова."}, status=400)

        try:
            user = User.objects.get(email=email)
            otp = OneTimeCode.objects.filter(user=user, code=code).first()

            if otp:
                if (now() - otp.created_at).total_seconds() > 600:
                    return JsonResponse({"error": "Код истёк."}, status=400)

                user.is_active = True
                user.save()
                otp.delete()

                # ✅ Указываем backend перед login
                user.backend = get_backends()[0].__module__ + "." + get_backends()[0].__class__.__name__
                login(request, user)

                return redirect("/")

            return JsonResponse({"error": "Неверный код."}, status=400)

        except User.DoesNotExist:
            return JsonResponse({"error": "Пользователь не найден."}, status=400)

    return render(request, "verify.html")  # ✅ return теперь в конце!



def cleanup_expired_codes():
    """Очистка просроченных кодов."""
    expiration_time = now() - datetime.timedelta(minutes=CODE_EXPIRATION_MINUTES)
    OneTimeCode.objects.filter(created_at__lt=expiration_time).delete()








from django.http import JsonResponse
from .tasks import send_email_to_all_users
from .models import EmailList
def send_mass_email(request):
    emails = list(EmailList.objects.values_list('email', flat=True))  # Получаем список email

    valid_emails = [email for email in emails if email]  # Исключаем пустые email

    if valid_emails:
        for email in valid_emails:  # Отправляем каждому отдельно
            send_email_to_all_users.delay(
                subject="Привет от Антона",
                message="Это тест celery в моем проекте",
                recipient=email  # Передаём email в задачу
            )
        return JsonResponse({"status": "Рассылка запущена!"})
    else:
        return JsonResponse({"status": "Нет валидных email-адресов!"})




