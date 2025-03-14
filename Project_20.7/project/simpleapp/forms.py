from django import forms
from .models import Post, Category, Response

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = {'title', 'text', 'post_type'}

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = {'name'}


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['text']  # Только текстовое поле
        widgets = {
            'text': forms.Textarea(attrs={'placeholder': 'Введите ваш отклик...'}),
        }


class NewsletterForm(forms.Form):
    subject = forms.CharField(label="Тема", max_length=255)
    message = forms.CharField(label="Сообщение", widget=forms.Textarea)



