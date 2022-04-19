from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Пользовательский фильтр для добавления класса css."""
    return field.as_widget(attrs={'class': css})
