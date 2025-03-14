# from django_filters import FilterSet
# from .models import Post, Category
#
#
# class PostFilter(FilterSet):
#    class Meta:
#        model = Post
#        fields = {
#            # поиск по названию
#            'title': ['icontains'],
#            'author': ['exact'],
#            'post_time': ['gt'],  # дата должна быть больше
#        }
#
# class CategoryFilter(FilterSet):
#    class Meta:
#        model = Category
#        fields = {
#            # поиск по названию
#            'name': ['icontains'],
#        }


from django_filters import FilterSet, CharFilter, DateFilter, ChoiceFilter
from .models import Post
from django.forms import DateInput

class PostFilter(FilterSet):
    title = CharFilter(field_name='title', lookup_expr='icontains', label='Заголовок')
    text = CharFilter(field_name='text', lookup_expr='icontains', label='Содержание')
    post_time = DateFilter(
        field_name='post_time',
        lookup_expr='date__gte',
        label='Дата (с)',
        widget=DateInput(attrs={'type': 'date'})  # Виджет календаря
    )
    post_type = ChoiceFilter(field_name='post_type', choices=Post.POST_TYPES, label='Категория')

    class Meta:
        model = Post
        fields = ['title', 'text', 'post_time', 'post_type']