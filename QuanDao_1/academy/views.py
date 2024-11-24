from django.views import generic
from QuanDao_1.accounts.models import Profile


class AboutPage(generic.TemplateView):
    template_name = 'academy/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instructors'] = Profile.objects.filter(role=Profile.INSTRUCTOR)
        return context
