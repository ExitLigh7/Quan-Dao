from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Count, Sum, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
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

from django.utils.timezone import now

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
            # Check if the user has completed their profile
            if not user.profile.is_complete():  # Assuming `is_complete` is a method in the Profile model
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

        # Check if all schedules are in the future
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

@login_required
def enroll_in_class(request, pk, slug):
    martial_arts_class = get_object_or_404(MartialArtsClass, pk=pk, slug=slug)
    schedule_id = request.POST.get('schedule')

    # Check if the user's profile is complete
    if not request.user.profile.is_complete():
        messages.warning(request, "Please complete your profile before enrolling in a class.")
        # Redirect to profile-edit and pass the user's pk
        return redirect('profile-edit', pk=request.user.profile.pk)  # Include user pk here

    # If cancel button is pressed, cancel enrollment
    if 'cancel_enrollment' in request.POST:
        schedule_id = request.POST.get('schedule_id')  # Get the schedule to cancel
        if schedule_id:
            schedule = get_object_or_404(Schedule, pk=schedule_id, martial_arts_class=martial_arts_class)
            # Check if the user is enrolled in the class
            enrollment = Enrollment.objects.filter(user=request.user, schedule=schedule).first()
            if enrollment:
                enrollment.delete()  # Remove the enrollment
                messages.success(request, f"You have successfully canceled your enrollment for {schedule.date}.")
            else:
                messages.error(request, "You are not enrolled in this class.")
        else:
            messages.error(request, "Invalid schedule to cancel.")
        return redirect('class-detail', pk=pk, slug=slug)

    # If enrolling in a class
    if not schedule_id:
        messages.error(request, "Please select a schedule to enroll.")
        return redirect('class-detail', pk=pk, slug=slug)

    # Validate the schedule
    schedule = Schedule.objects.filter(pk=schedule_id, martial_arts_class=martial_arts_class).first()
    if not schedule:
        messages.error(request, "Invalid schedule selected.")
        return redirect('class-detail', pk=pk, slug=slug)

    # Check if the user is already enrolled in the same schedule
    if Enrollment.objects.filter(user=request.user, schedule=schedule).exists():
        messages.info(request, f"You are already enrolled in the schedule for {schedule.date}.")
        return redirect('class-detail', pk=pk, slug=slug)

    # Check if the schedule is full
    if schedule.enrollments.count() >= martial_arts_class.max_capacity:
        messages.error(request, f"The schedule for {schedule.date} is fully booked.")
        return redirect('class-detail', pk=pk, slug=slug)

    # Create the enrollment
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

    # Get schedules the user is enrolled in
    enrolled_schedules = Schedule.objects.filter(
        martial_arts_class=martial_arts_class,
        enrollments__user=request.user
    ).distinct()

    # Exclude schedules where feedback has already been provided
    feedback_schedules = Feedback.objects.filter(user=request.user).values_list('schedule_id', flat=True)
    schedules_for_feedback = enrolled_schedules.exclude(id__in=feedback_schedules)

    # Get POST data
    schedule_id = request.POST.get('schedule')
    rating = request.POST.get('rating')
    comment = request.POST.get('comment', '').strip()

    # Validate schedule selection
    try:
        schedule = schedules_for_feedback.get(pk=schedule_id)
    except Schedule.DoesNotExist:
        messages.error(request, "You have either already reviewed this schedule or it's no longer available for feedback.")
        return redirect('class-detail', pk=pk, slug=slug)

    # Validate rating
    if not rating or not rating.isdigit() or int(rating) not in range(1, 6):
        messages.error(request, "Please provide a valid rating (1-5).")
        return redirect('class-detail', pk=pk, slug=slug)

    # Check if feedback is already given
    if Feedback.objects.filter(user=request.user, schedule=schedule).exists():
        messages.error(request, "You have already provided feedback for this schedule.")
        return redirect('class-detail', pk=pk, slug=slug)

    # Ensure feedback is only allowed after schedule end time
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

    # Enrollments for the user
    enrollments = Enrollment.objects.filter(user=user).select_related('schedule', 'schedule__martial_arts_class')

    # Separate upcoming and past schedules
    upcoming_classes = enrollments.filter(
        Q(schedule__date__gt=now().date()) |
        Q(schedule__date=now().date(), schedule__start_time__gt=now().time())
    )
    past_classes = enrollments.filter(
        Q(schedule__date__lt=now().date()) |
        Q(schedule__date=now().date(), schedule__end_time__lt=now().time())
    )

    # Handle cancellation if the form is submitted
    if request.method == "POST":
        enrollment_id = request.POST.get("enrollment_id")
        if enrollment_id:
            # Get the enrollment object
            enrollment = get_object_or_404(Enrollment, pk=enrollment_id, user=user)
            enrollment.delete()
            messages.success(request, "Your enrollment has been successfully canceled.")
            return redirect('my-classes')  # Redirect to the same page after cancellation

    # Render context
    context = {
        'upcoming_classes': upcoming_classes,
        'past_classes': past_classes,
    }
    return render(request, 'academy/user_classes.html', context)

