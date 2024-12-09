from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.db.models import Count, Sum, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import make_aware, now
from django.views import generic
from django.views.decorators.http import require_POST
from QuanDao_1.academy.models import MartialArtsClass, Enrollment, Schedule, Feedback
from QuanDao_1.accounts.models import Profile


class AboutPage(generic.TemplateView):
    template_name = 'academy/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instructors'] = Profile.objects.filter(role=Profile.INSTRUCTOR)
        return context


class ClassesOverviewView(generic.ListView):
    model = MartialArtsClass
    template_name = 'academy/classes_overview.html'
    context_object_name = 'classes'
    paginate_by = 10  # Optional pagination

    def get_queryset(self):
        queryset = MartialArtsClass.objects.all().annotate(
            total_enrolled=Sum('schedules__enrollments')  # Aggregate total enrolled count for each class
        )
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add can_add_class variable to the context based on user role
        context['can_add_class'] = (
                self.request.user.is_authenticated and
                (self.request.user.is_staff or getattr(self.request.user.profile, 'role', None) == 'instructor')
        )

        # Annotate schedules with enrollment counts
        for martial_arts_class in context['classes']:
            martial_arts_class.schedules_list = martial_arts_class.schedules.annotate(
                enrolled_count=Count('enrollments')
            )

        return context


class ClassDetailView(generic.DetailView):
    model = MartialArtsClass
    template_name = 'academy/class_details.html'
    context_object_name = 'class'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Annotate schedules with enrollment counts
        schedules = self.object.schedules.annotate(
            enrolled_count=Count('enrollments')
        )

        # Default values for unauthenticated users
        context['is_enrolled'] = False
        context['enrolled_schedules'] = []
        context['schedules_for_feedback_ids'] = []
        context['feedbacks'] = Feedback.objects.filter(class_instance=self.object)

        if user.is_authenticated:
            if not user.profile.is_complete():
                context['profile_incomplete'] = True
            else:
                context['profile_incomplete'] = False

            # User's enrolled schedules
            enrolled_schedules = Enrollment.objects.filter(
                user=user,
                martial_arts_class=self.object
            ).values_list('schedule', flat=True)

            context['is_enrolled'] = len(enrolled_schedules) == schedules.count()
            context['enrolled_schedules'] = enrolled_schedules

            # Determine schedules eligible for feedback
            feedback_schedules = Feedback.objects.filter(
                user=user,
                class_instance=self.object
            ).values_list('schedule_id', flat=True)

            schedules_for_feedback = schedules.filter(
                id__in=enrolled_schedules
            ).exclude(id__in=feedback_schedules).filter(
                Q(date__lt=now().date()) |
                Q(date=now().date(), end_time__lt=now().time())
            )
            context['schedules_for_feedback_ids'] = schedules_for_feedback.values_list('id', flat=True)

        future_schedules = schedules.filter(
            Q(date__gt=now().date()) |
            Q(date=now().date(), start_time__gt=now().time())
        )
        context['all_schedules_future'] = future_schedules.count() == schedules.count()

        # Check if all schedules are full
        context['all_schedules_full'] = all(
            schedule.enrolled_count >= self.object.max_capacity for schedule in schedules
        )

        context['schedules'] = schedules
        return context


class ClassCreateView(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = MartialArtsClass
    template_name = 'academy/class_form.html'
    fields = ['name', 'description', 'level', 'max_capacity']

    def test_func(self):
        # Allow only staff or instructors to create classes
        return self.request.user.is_staff or (
                    hasattr(self.request.user, 'profile') and self.request.user.profile.role == 'instructor')

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
        martial_arts_class = self.get_object()
        return martial_arts_class.instructor == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to edit this class.")
        raise PermissionDenied("You are not allowed to edit this class.")

    def get_success_url(self):
        messages.success(self.request, "Class updated successfully.")
        return reverse_lazy('classes-overview')


class ClassDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = MartialArtsClass
    template_name = 'academy/class_confirm_delete.html'
    context_object_name = 'class'

    def test_func(self):
        """Only allow the instructor or staff to delete the class"""
        martial_arts_class = self.get_object()
        return martial_arts_class.instructor == self.request.user

    def get_success_url(self):
        messages.success(self.request, "Class successfully deleted.")
        return reverse_lazy('classes-overview')



@login_required
def enroll_in_class(request, pk, slug):
    martial_arts_class = get_object_or_404(MartialArtsClass, pk=pk, slug=slug)
    schedule_id = request.POST.get('schedule')

    if not request.user.profile.is_complete():
        messages.warning(request, "Please complete your profile before enrolling in a class.")
        return redirect('profile-edit', pk=request.user.profile.pk)

    # Cancel enrollment logic
    if 'cancel_enrollment' in request.POST:
        schedule_id = request.POST.get('schedule_id')
        if schedule_id:
            schedule = get_object_or_404(Schedule, pk=schedule_id, martial_arts_class=martial_arts_class)
            enrollment = Enrollment.objects.filter(user=request.user, schedule=schedule).first()
            if enrollment:
                enrollment.delete()
                messages.success(request, f"You have successfully canceled your enrollment for {schedule.date}.")
            else:
                messages.error(request, "You are not enrolled in this class.")
        else:
            messages.error(request, "Invalid schedule to cancel.")
        return redirect('class-detail', pk=pk, slug=slug)

    if not schedule_id:
        messages.error(request, "Please select a schedule to enroll.")
        return redirect('class-detail', pk=pk, slug=slug)

    # Validate the schedule
    schedule = Schedule.objects.filter(pk=schedule_id, martial_arts_class=martial_arts_class).first()
    if not schedule:
        messages.error(request, "Invalid schedule selected.")
        return redirect('class-detail', pk=pk, slug=slug)

    # Restrict enrollment for past schedules
    schedule_datetime_naive = datetime.combine(schedule.date, schedule.start_time)
    schedule_datetime = make_aware(schedule_datetime_naive)
    if schedule_datetime < now():
        messages.error(request,
                       f"Cannot enroll in past classes. The selected schedule ({schedule.date}) has already occurred.")
        return redirect('class-detail', pk=pk, slug=slug)

    if Enrollment.objects.filter(user=request.user, schedule=schedule).exists():
        messages.info(request, f"You are already enrolled in the schedule for {schedule.date}.")
        return redirect('class-detail', pk=pk, slug=slug)

    if schedule.enrollments.count() >= martial_arts_class.max_capacity:
        messages.error(request, f"The schedule for {schedule.date} is fully booked.")
        return redirect('class-detail', pk=pk, slug=slug)

    try:
        Enrollment.objects.create(
            user=request.user,
            martial_arts_class=martial_arts_class,
            schedule=schedule
        )
        messages.success(request, f"You have successfully enrolled in {martial_arts_class.name} for {schedule.date}.")
    except IntegrityError:
        messages.error(request, "An error occurred while processing your enrollment. Please try again.")

    return redirect('class-detail', pk=pk, slug=slug)


@require_POST
@login_required
def submit_feedback(request, pk, slug):
    martial_arts_class = get_object_or_404(MartialArtsClass, pk=pk, slug=slug)

    enrolled_schedules = Schedule.objects.filter(
        martial_arts_class=martial_arts_class,
        enrollments__user=request.user
    ).distinct()

    feedback_schedules = Feedback.objects.filter(user=request.user).values_list('schedule_id', flat=True)
    schedules_for_feedback = enrolled_schedules.exclude(id__in=feedback_schedules)

    schedule_id = request.POST.get('schedule')
    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()

    try:
        schedule = schedules_for_feedback.get(pk=schedule_id)
    except Schedule.DoesNotExist:
        messages.error(request,
                       "You have either already reviewed this schedule or it's no longer available for feedback.")
        return redirect('class-detail', pk=pk, slug=slug)

    if not rating or not rating.isdigit() or int(rating) not in range(1, 6):
        messages.error(request, "Please provide a valid rating (1-5).")
        return redirect('class-detail', pk=pk, slug=slug)

    if Feedback.objects.filter(user=request.user, schedule=schedule).exists():
        messages.error(request, "You have already provided feedback for this schedule.")
        return redirect('class-detail', pk=pk, slug=slug)

    now = timezone.now()
    schedule_end = timezone.make_aware(datetime.combine(schedule.date, schedule.end_time))
    if now < schedule_end:
        messages.error(request, "You can only leave feedback after the schedule has ended.")
        return redirect('class-detail', pk=pk, slug=slug)

    # Create feedback
    Feedback.objects.create(
        class_instance=martial_arts_class,
        schedule=schedule,
        user=request.user,
        rating=int(rating),
        comment=comment
    )

    messages.success(request, "Thank you for your feedback!")
    return redirect('class-detail', pk=pk, slug=slug)


@login_required
def my_classes(request):
    user = request.user

    enrollments = Enrollment.objects.filter(user=user).select_related('schedule', 'schedule__martial_arts_class')

    upcoming_classes = enrollments.filter(
        Q(schedule__date__gt=now().date()) |
        Q(schedule__date=now().date(), schedule__start_time__gt=now().time())
    )
    past_classes = enrollments.filter(
        Q(schedule__date__lt=now().date()) |
        Q(schedule__date=now().date(), schedule__end_time__lt=now().time())
    )

    if request.method == "POST":
        enrollment_id = request.POST.get("enrollment_id")
        if enrollment_id:
            enrollment = get_object_or_404(Enrollment, pk=enrollment_id, user=user)
            enrollment.delete()
            messages.success(request, "Your enrollment has been successfully canceled.")
            return redirect('my-classes')  # Redirect to the same page after cancellation

    context = {
        'upcoming_classes': upcoming_classes,
        'past_classes': past_classes,
    }
    return render(request, 'academy/user_classes.html', context)
