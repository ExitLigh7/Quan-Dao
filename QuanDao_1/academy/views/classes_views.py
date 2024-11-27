from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import generic
from QuanDao_1.academy.models import MartialArtsClass
from QuanDao_1.accounts.models import Profile


class AboutPage(generic.TemplateView):
    template_name = 'academy/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instructors'] = Profile.objects.filter(role=Profile.INSTRUCTOR)
        return context

class ClassesOverviewView(generic.ListView):
    model = MartialArtsClass
    template_name = 'academy/classes-overview.html'
    context_object_name = 'classes'
    paginate_by = 10  # Optional pagination

    def get_queryset(self):
        queryset = MartialArtsClass.objects.all()
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)
        return queryset

    def get_context_data(self, **kwargs):
        # Get the default context
        context = super().get_context_data(**kwargs)

        # Add can_add_class variable to the context based on user role
        context['can_add_class'] = (
                self.request.user.is_authenticated and
                (self.request.user.is_staff or getattr(self.request.user.profile, 'role', None) == 'instructor')
        )
        return context

class ClassDetailView(generic.DetailView):
    model = MartialArtsClass
    template_name = 'academy/class-details.html'
    context_object_name = 'class'

class ClassCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = MartialArtsClass
    template_name = 'academy/class_form.html'
    fields = ['name', 'description', 'level', 'max_capacity']

    def test_func(self):
        # Allow only staff or instructors to create classes
        return self.request.user.is_staff or (hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'instructor')

    def form_valid(self, form):
        # Automatically set the instructor to the current user
        form.instance.instructor = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('classes-overview')


class ClassUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = MartialArtsClass
    template_name = 'academy/class_form.html'
    fields = ['name', 'description', 'level', 'max_capacity']

    def test_func(self):
        # Allow only staff or the class instructor to edit
        martial_arts_class = self.get_object()
        return self.request.user.is_staff or martial_arts_class.instructor == self.request.user

    def get_success_url(self):
        return reverse_lazy('classes-overview')

class ClassDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = MartialArtsClass
    template_name = 'academy/class_confirm_delete.html'

    def test_func(self):
        martial_arts_class = self.get_object()
        return self.request.user.is_staff or martial_arts_class.instructor == self.request.user

    def get_success_url(self):
        return reverse_lazy('classes-overview')