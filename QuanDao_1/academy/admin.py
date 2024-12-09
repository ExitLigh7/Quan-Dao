from django.contrib import admin

from QuanDao_1.academy.models import MartialArtsClass, Schedule, Enrollment, Feedback


@admin.register(MartialArtsClass)
class MartialArtsClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'max_capacity', 'instructor')
    list_filter = ('level', 'instructor')
    search_fields = ('name', 'description', 'instructor__username')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name', 'level')

    # Limit the queryset based on the logged-in user
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_staff:
            # Staff can see all classes
            return qs
        else:
            # Instructors only see their own classes
            return qs.filter(instructor=request.user)

    # Optionally restrict the actions available to instructors (if needed)
    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return obj.instructor == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            return obj.instructor == request.user
        return super().has_delete_permission(request, obj)



@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('martial_arts_class', 'date', 'start_time', 'end_time', 'instructor')
    list_filter = ('date', 'martial_arts_class', 'instructor')
    search_fields = ('martial_arts_class__name', 'instructor__username')
    ordering = ('date', 'start_time')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_staff:
            return qs
        else:
            # Instructors only see schedules for their own classes
            return qs.filter(martial_arts_class__instructor=request.user)

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return obj.martial_arts_class.instructor == request.user
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            return obj.martial_arts_class.instructor == request.user
        return super().has_delete_permission(request, obj)



@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'martial_arts_class', 'schedule', 'enrollment_date')
    list_filter = ('martial_arts_class', 'schedule')
    search_fields = ('user__username', 'martial_arts_class__name')
    ordering = ('-enrollment_date',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'class_instance', 'schedule', 'rating', 'created_on')
    list_filter = ('rating', 'class_instance', 'schedule')
    search_fields = ('user__username', 'class_instance__name', 'schedule__martial_arts_class__name')

    ordering = ('-created_on',)
