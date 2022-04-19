from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """Формирование страницы об авторе проекта."""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """Формирование страницы об использованных технологиях."""

    template_name = 'about/tech.html'
