from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from ..mixins import IsInstructorMixin
from ..models import Schedule, MartialArtsClass
from ..forms import ScheduleCreateForm, ScheduleEditForm


class ScheduleListView(LoginRequiredMixin, IsInstructorMixin, ListView):
    model = Schedule
    template_name = 'academy/schedule_list.html'
    context_object_name = 'schedules'

    def get_queryset(self):
        queryset = Schedule.objects.filter(instructor=self.request.user)
        class_filter = self.request.GET.get('class')
        date_filter = self.request.GET.get('date')

        if class_filter:
            queryset = queryset.filter(martial_arts_class_id=class_filter)
        if date_filter:
            queryset = queryset.filter(date=date_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['classes'] = MartialArtsClass.objects.filter(instructor=self.request.user)
        return context


class ScheduleCreateView(LoginRequiredMixin, IsInstructorMixin, CreateView):

    model = Schedule
    form_class = ScheduleCreateForm
    template_name = 'academy/schedule_form.html'
    success_url = reverse_lazy('schedule-list')

    def get_form(self, *args, **kwargs):
        form = super().get_form(*args, **kwargs)
        form.fields['martial_arts_class'].queryset = MartialArtsClass.objects.filter(instructor=self.request.user)
        return form

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        messages.success(self.request, "Schedule created successfully!")
        return super().form_valid(form)


class ScheduleUpdateView(LoginRequiredMixin, IsInstructorMixin, UpdateView):

    model = Schedule
    form_class = ScheduleEditForm
    template_name = 'academy/schedule_form.html'
    success_url = reverse_lazy('schedule-list')

    def get_queryset(self):
        return Schedule.objects.filter(instructor=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Schedule updated successfully!")
        return super().form_valid(form)


class ScheduleDeleteView(LoginRequiredMixin, IsInstructorMixin, DeleteView):
    model = Schedule
    template_name = 'academy/schedule_confirm_delete.html'
    success_url = reverse_lazy('schedule-list')

    def get_queryset(self):
        return Schedule.objects.filter(instructor=self.request.user)

    def delete(self, request, *args, **kwargs):
        schedule = self.get_object()
        messages.success(request, f"Schedule for {schedule.martial_arts_class.name} on {schedule.date} deleted.")
        return super().delete(request, *args, **kwargs)
