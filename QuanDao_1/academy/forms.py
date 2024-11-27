from django import forms
from django.core.exceptions import ValidationError
from .models import Schedule
from django.db.models import Q

class ScheduleBaseForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['martial_arts_class', 'instructor', 'date', 'start_time', 'end_time']

    def clean(self):
        cleaned_data = super().clean()
        martial_arts_class = cleaned_data.get('martial_arts_class')
        instructor = cleaned_data.get('instructor')
        date = cleaned_data.get('date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        # Ensure no overlapping schedules for the same class or instructor
        overlapping_schedules = Schedule.objects.filter(
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
        ).filter(
            Q(martial_arts_class=martial_arts_class) | Q(instructor=instructor)
        )
        if self.instance.pk:
            overlapping_schedules = overlapping_schedules.exclude(pk=self.instance.pk)

        if overlapping_schedules.exists():
            raise ValidationError("This schedule conflicts with an existing one.")

        return cleaned_data

class ScheduleCreateForm(ScheduleBaseForm):
    pass

class ScheduleEditForm(ScheduleBaseForm):
    pass

