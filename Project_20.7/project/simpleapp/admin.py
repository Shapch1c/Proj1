from django.contrib import admin
from .models import Post, Category, Author, PostCategory
from modeltranslation.admin import TranslationAdmin # импортируем модель админки (вспоминаем модуль про переопределение стандартных админ-инструментов)
from ckeditor.widgets import CKEditorWidget
from django import forms



# Форма для редактирования Post в админке с CKEditor
class PostAdminForm(forms.ModelForm):
    text = forms.CharField(widget=CKEditorWidget())  # Используем CKEditor

    class Meta:
        model = Post
        fields = '__all__'

class PostCategoryInline(admin.TabularInline):
    model = PostCategory
    extra = 1  # Количество пустых строк для добавления новых связей


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Поля для отображения в форме редактирования
    fields = ('author', 'post_type', 'title', 'text')
    readonly_fields = ('post_time',)  # Поле, доступное только для чтения
    list_display = ('title', 'text', 'author', 'post_type')  # Поля для отображения в списке объектов
    inlines = [PostCategoryInline]  # Связь через промежуточную модель

admin.site.register(Author)



class CategoryAdmin(TranslationAdmin):
    model = Category

admin.site.register(Category)




from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from .models import EmailList
from .tasks import send_email_to_all_users

class EmailListAdmin(admin.ModelAdmin):
    list_display = ('email',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send-emails/', self.send_emails, name='send_emails'),
        ]
        return custom_urls + urls

    def send_emails(self, request):
        emails = list(EmailList.objects.values_list('email', flat=True))  # Получаем все email'ы

        if emails:
            for email in emails:
                send_email_to_all_users.delay(
                    "Административное сообщение",
                    "Привет, это тестовая рассылка.",
                    email  # Передаём email каждому пользователю
                )

            self.message_user(request, f"Рассылка запущена! Отправлено {len(emails)} писем.", messages.SUCCESS)
        else:
            self.message_user(request, "Нет email'ов для рассылки.", messages.WARNING)

        return redirect("..")

    def send_mass_email_button(self, obj):
        return format_html('<a class="button" href="send-emails/">Отправить письма</a>')

    send_mass_email_button.short_description = "Массовая рассылка"

admin.site.register(EmailList, EmailListAdmin)





