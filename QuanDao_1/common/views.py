from django.views import generic


class HomePage(generic.TemplateView):
    template_name = 'common/home-page.html'

