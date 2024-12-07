from django.http import JsonResponse
from django.views import generic
from QuanDao_1.academy.models import MartialArtsClass


class HomePage(generic.TemplateView):
    template_name = 'common/home-page.html'

def search(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = MartialArtsClass.objects.filter(name__icontains=query).values('id', 'name', 'description')

    return JsonResponse({'query': query, 'results': list(results)})

