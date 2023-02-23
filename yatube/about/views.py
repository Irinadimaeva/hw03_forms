from django.views.generic.base import TemplateView


class AboutAuthorStaticPage(TemplateView):
    # В переменной template_name обязательно указывается имя шаблона,
    # на основе которого будет создана возвращаемая страница
    template_name = 'about/author.html'


class AboutTechStaticPage(TemplateView):
    template_name = 'about/tech.html'
