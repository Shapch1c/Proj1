from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter()
def censor(value):
    words_to_censor = ['плохое', 'слово', 'блин']
    if not isinstance(value, str):
        raise ValueError("Значение должно быть строкой")

    for word in words_to_censor:
        value = value.replace(word, word[0] + '*' * len(word))

    return mark_safe(value)